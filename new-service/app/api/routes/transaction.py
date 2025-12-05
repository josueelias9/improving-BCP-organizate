"""
Transaction Routes - HTTP Interface
Delegates to application layer use cases
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import Dict, Any, List, Optional
import uuid
import logging
from pathlib import Path

from api.deps import get_db_session
from models import TransactionUpdate, TransactionBatchUpdate
from src.Capplication.DTO import BatchUpdateItem, ExportFilter
from src.Capplication.use_cases.transaction.load_transactions_from_document import LoadTransactionsFromDocumentUseCase
from src.Capplication.use_cases.transaction.update_transaction import UpdateTransactionUseCase
from src.Capplication.use_cases.transaction.batch_update_transactions import BatchUpdateTransactionsUseCase
from src.Capplication.use_cases.transaction.export_transactions import ExportTransactionsUseCase
from src.Capplication.use_cases.transaction.import_transactions_from_csv import ImportTransactionsFromCsvUseCase
from src.Binterface.gateway.db.document import DocumentDbGateway
from src.Binterface.gateway.db.transaction import TransactionDbGateway
from src.Binterface.gateway.db.category import CategoryDbGateway

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[Dict[str, Any]])
def get_all_transactions(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_db_session)
) -> List[Dict[str, Any]]:
    """
    Get all transactions with pagination
    
    Includes category_name field with the name of the associated category.
    
    Args:
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100, max: 1000)
        session: Database session (injected)
        
    Returns:
        List of transactions with category_name included
    """
    try:
        # Validate limit
        if limit > 1000:
            limit = 1000
        
        # Get transactions via gateway (includes category_name)
        transaction_gateway = TransactionDbGateway(session)
        transactions = transaction_gateway.get_all(skip=skip, limit=limit)
        
        return transactions
        
    except Exception as e:
        logger.error(f"Error retrieving transactions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving transactions: {str(e)}"
        )


@router.post("/load-from-document/{document_id}", response_model=Dict[str, Any])
def load_transactions_from_document(
    document_id: uuid.UUID,
    session: Session = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Load transactions from a document's data column into the transactions table.
    
    This endpoint delegates to the application layer use case.
    
    Args:
        document_id: The UUID of the document to load transactions from
        session: Database session (injected)
        
    Returns:
        Summary of loaded transactions
        
    Raises:
        HTTPException: 404 if document not found, 400 for validation errors
    """
    try:
        # Instantiate concrete gateways
        document_gateway = DocumentDbGateway(session)
        transaction_gateway = TransactionDbGateway(session)
        
        # Inject gateways into use case
        use_case = LoadTransactionsFromDocumentUseCase(document_gateway, transaction_gateway)
        
        # Execute use case
        result = use_case.execute(document_id)
        
        # Map domain result to HTTP response
        return {
            "document_id": str(document_id),
            "total_records": result.total_records,
            "loaded": result.loaded_count,
            "skipped": result.skipped_count,
            "errors": result.errors if result.errors else None,
            "processed": True
        }
        
    except ValueError as e:
        # Business validation errors
        error_msg = str(e)
        
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
            
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error loading transactions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/{transaction_id}", response_model=Dict[str, Any])
def update_transaction(
    transaction_id: uuid.UUID,
    transaction_update: TransactionUpdate,
    session: Session = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Update a specific transaction by ID.
    
    This endpoint delegates to the application layer use case.
    
    Args:
        transaction_id: The UUID of the transaction to update
        transaction_update: The fields to update
        session: Database session (injected)
        
    Returns:
        Update result with transaction information
        
    Raises:
        HTTPException: 404 if transaction not found, 400 for validation errors
    """
    try:
        # Instantiate gateways and inject into use case
        transaction_gateway = TransactionDbGateway(session)
        category_gateway = CategoryDbGateway(session)
        use_case = UpdateTransactionUseCase(transaction_gateway, category_gateway)
        
        # Convert Pydantic model to dict, excluding None values
        update_data = transaction_update.model_dump(exclude_unset=True, exclude_none=True)
        
        # Validate that at least one field is being updated
        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="At least one field must be provided for update"
            )
        
        # Execute use case
        result = use_case.execute(transaction_id, update_data)
        
        return result
        
    except ValueError as e:
        # Business validation errors
        error_msg = str(e)
        
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
            
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error updating transaction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.patch("/batch", response_model=Dict[str, Any])
def batch_update_transactions(
    batch_update: TransactionBatchUpdate,
    session: Session = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Update multiple transactions simultaneously.
    
    Only 'history' and 'category_name' fields can be updated for each transaction.
    If category_name is provided, it will be validated against existing categories.
    This endpoint processes all updates and returns a summary of the operation.
    
    Args:
        batch_update: List of transaction updates to apply
        session: Database session (injected)
        
    Returns:
        Summary of batch update operation with success/failure counts
        
    Raises:
        HTTPException: 400 for validation errors
    """
    try:
        # Instantiate gateways and inject into use case
        transaction_gateway = TransactionDbGateway(session)
        category_gateway = CategoryDbGateway(session)
        use_case = BatchUpdateTransactionsUseCase(transaction_gateway, category_gateway)
        
        # Convert Pydantic models to domain objects
        updates = [
            BatchUpdateItem(
                transaction_id=item.transaction_id,
                history=item.history,
                category_name=item.category_name
            )
            for item in batch_update.updates
        ]
        
        # Execute use case
        result = use_case.execute(updates)
        
        return {
            "total": result.total,
            "updated": result.updated,
            "failed": result.failed,
            "errors": result.errors if result.errors else None,
            "message": f"Successfully updated {result.updated}/{result.total} transactions"
        }
        
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error in batch update: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/export/csv")
def export_transactions(
    month: Optional[str] = Query(None, description="Filter by month in format YYYY-MM (e.g., 2025-01)"),
    document_id: Optional[uuid.UUID] = Query(None, description="Filter by document ID"),
    session: Session = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Export transactions to CSV format and save to file
    
    Filters:
        - month: Optional filter by month in format YYYY-MM (e.g., "2025-01")
        - document_id: Optional filter by specific document
        
    Returns:
        JSON with file path, transaction count, and status
        
    Examples:
        - GET /transactions/export/csv - Export all transactions
        - GET /transactions/export/csv?month=2025-01 - Export transactions from January 2025
        - GET /transactions/export/csv?document_id=xxx-xxx-xxx - Export transactions from specific document
        - GET /transactions/export/csv?month=2025-01&document_id=xxx-xxx-xxx - Combined filters
    """
    try:
        # Instantiate gateway and inject into use case
        transaction_gateway = TransactionDbGateway(session)
        use_case = ExportTransactionsUseCase(transaction_gateway)
        
        # Create filter object
        filters = ExportFilter(month=month, document_id=document_id)
        
        # Execute use case
        result = use_case.execute(filters)
        
        if not result.success:
            raise HTTPException(
                status_code=400 if "Invalid" in result.error_message else 404,
                detail=result.error_message
            )
        
        # Save CSV to file in output directory
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        file_path = output_dir / result.filename
        
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            f.write(result.csv_content)
        
        logger.info(f"Exported {result.transaction_count} transactions to CSV: {file_path}")
        
        return {
            "success": True,
            "message": f"Successfully exported {result.transaction_count} transactions",
            "file_path": str(file_path),
            "filename": result.filename,
            "transaction_count": result.transaction_count,
            "filters": {
                "month": month,
                "document_id": str(document_id) if document_id else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting transactions to CSV: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting transactions: {str(e)}"
        )


@router.post("/import/csv")
def import_transactions_from_csv(
    csv_filename: Optional[str] = Query(None, description="Specific CSV filename to import (optional, uses latest if not provided)"),
    session: Session = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Import and update transactions from CSV file
    
    Reads a CSV file from the output/ directory and updates transactions based on unique_identifier.
    Updates the 'history' and 'category_name' fields for matching transactions.
    
    Args:
        csv_filename: Optional specific CSV filename. If not provided, uses the most recent CSV file.
        
    Returns:
        JSON with import summary including updated count, errors, etc.
        
    Examples:
        - POST /transactions/import/csv - Import from latest CSV file
        - POST /transactions/import/csv?csv_filename=transactions_226records_20251205_221111.csv - Import from specific file
    """
    try:
        # Instantiate gateways and inject into use case
        transaction_gateway = TransactionDbGateway(session)
        category_gateway = CategoryDbGateway(session)
        use_case = ImportTransactionsFromCsvUseCase(transaction_gateway, category_gateway)
        
        # Execute use case
        result = use_case.execute(csv_filename)
        
        if not result.success and result.total_rows == 0:
            raise HTTPException(
                status_code=404,
                detail=result.message
            )
        
        logger.info(f"Import completed: {result.updated_count} updated, {result.skipped_count} skipped")
        
        return {
            "success": result.success,
            "message": result.message,
            "updated_count": result.updated_count,
            "skipped_count": result.skipped_count,
            "total_rows": result.total_rows,
            "errors": result.errors[:10] if result.errors else []  # Limit errors to first 10
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing transactions from CSV: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error importing transactions: {str(e)}"
        )
