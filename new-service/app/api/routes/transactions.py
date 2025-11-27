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
from src.Capplication.load_transactions_use_case import LoadTransactionsUseCase
from src.Binterface.document_repository import DocumentRepository
from src.Binterface.transaction_repository import TransactionRepository

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
    
    Args:
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100, max: 1000)
        session: Database session (injected)
        
    Returns:
        List of transactions
    """
    try:
        # Validate limit
        if limit > 1000:
            limit = 1000
        
        # Get transactions via repository
        transaction_repo = TransactionRepository(session)
        transactions = transaction_repo.get_all(skip=skip, limit=limit)
        
        # Convert to dict
        return [
            {
                "id": str(t.id),
                "description": t.description,
                "cargos": t.cargos,
                "abonos": t.abonos,
                "currency": t.currency,
                "fecha_proceso": t.fecha_proceso,
                "fecha_consumo": t.fecha_consumo,
                "internal_transaction": t.internal_transaction,
                # "type": t.type,
                "document_id": str(t.document_id),
                "order": t.order,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "updated_at": t.updated_at.isoformat() if t.updated_at else None
            }
            for t in transactions
        ]
        
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
        # Instantiate concrete repositories
        document_repo = DocumentRepository(session)
        transaction_repo = TransactionRepository(session)
        
        # Inject repositories into use case
        use_case = LoadTransactionsUseCase(document_repo, transaction_repo)
        
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
