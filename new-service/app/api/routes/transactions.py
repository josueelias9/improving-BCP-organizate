from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Dict, Any
import uuid
import logging

from api.deps import get_db_session
from models import Document, Transaction

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/load-from-document/{document_id}", response_model=Dict[str, Any])
def load_transactions_from_document(
    document_id: uuid.UUID,
    session: Session = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Load transactions from a document's data column into the transactions table.
    
    Args:
        document_id: The UUID of the document to load transactions from
        session: Database session
        
    Returns:
        Summary of loaded transactions
    """
    # Get the document
    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if document is already processed
    if document.processed:
        raise HTTPException(
            status_code=400,
            detail="Document has already been processed. Transactions already loaded."
        )
    
    # Check if document has data
    if not document.data or len(document.data) == 0:
        raise HTTPException(
            status_code=400, 
            detail="Document has no transaction data to load"
        )
    
    # Load transactions
    loaded_count = 0
    skipped_count = 0
    errors = []
    
    for idx, transaction_data in enumerate(document.data):
        try:
            # Create transaction from document data
            transaction = Transaction(
                description=transaction_data.get("description", ""),
                cargos=float(transaction_data.get("cargos", 0.0)),
                abonos=float(transaction_data.get("abonos", 0.0)),
                currency=document.currency,
                fecha_proceso=transaction_data.get("fecha_proceso"),
                fecha_consumo=transaction_data.get("fecha_consumo"),
                internal_transaction=transaction_data.get("internal_transaction") == "*" ,
                type=transaction_data.get("type", "unknown"),
                document_id=document.id
            )
            
            session.add(transaction)
            loaded_count += 1
            
        except Exception as e:
            error_msg = f"Error loading transaction {idx}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            skipped_count += 1
    
    # Commit all transactions
    try:
        session.commit()
        logger.info(f"Successfully loaded {loaded_count} transactions from document {document_id}")
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error committing transactions to database: {str(e)}"
        )
    
    # Mark document as processed
    try:
        document.processed = True
        session.add(document)
        session.commit()
        logger.info(f"Document {document_id} marked as processed")
    except Exception as e:
        logger.error(f"Error marking document as processed: {str(e)}")
        # Don't raise exception since transactions were already committed successfully
    
    return {
        "document_id": str(document_id),
        "total_records": len(document.data),
        "loaded": loaded_count,
        "skipped": skipped_count,
        "errors": errors if errors else None,
        "processed": document.processed
    }
