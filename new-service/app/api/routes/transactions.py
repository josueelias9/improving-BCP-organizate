"""
Transaction Routes - HTTP Interface
Delegates to application layer use cases
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Dict, Any, List
import uuid
import logging

from api.deps import get_db_session
from models import TransactionUpdate, TransactionBatchUpdate
from src.Capplication.load_transactions_from_document_use_case import LoadTransactionsFromDocumentUseCase
from src.Capplication.update_transaction_use_case import UpdateTransactionUseCase
from src.Capplication.batch_update_transactions_use_case import (
    BatchUpdateTransactionsUseCase,
    BatchUpdateItem
)
from src.Binterface.gateway.db.document_gateway import DocumentGateway
from src.Binterface.gateway.db.transaction_gateway import TransactionGateway
from src.Binterface.gateway.db.category_gateway import CategoryGateway

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
        transaction_gateway = TransactionGateway(session)
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
        document_gateway = DocumentGateway(session)
        transaction_gateway = TransactionGateway(session)
        
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
        transaction_gateway = TransactionGateway(session)
        category_gateway = CategoryGateway(session)
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
        transaction_gateway = TransactionGateway(session)
        category_gateway = CategoryGateway(session)
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
