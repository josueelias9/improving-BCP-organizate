from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any
from sqlmodel import Session

import uuid
import logging

from api.deps import get_db_session
from src.Aframework.gateway.db.document import DocumentDbGateway
from src.Aframework.gateway.db.transaction import TransactionDbGateway
from src.Capplication.use_cases.document.load_transactions_from_document import LoadTransactionsFromDocumentUseCase
from src.Capplication.DTO.document_dto import DTOLoadTransactionsFromDocumentResponse, DTOLoadTransactionsFromDocumentRequest

logger = logging.getLogger(__name__)

# Crear router para rutas de procesamiento de PDF
router = APIRouter(prefix="/api", tags=["PDF Processing"])


# Modelos Pydantic para request body
class PDFProcessRequest(BaseModel):
    pdf_filename: str
    type: str  # "debit" o "credit"
    user_email: str = "admin@bcpextractor.com"

    class Config:
        json_schema_extra = {
            "example": {
                "pdf_filename": "files/EECC102025_09745280.PDF",
                "type": "debit",
                "user_email": "admin@bcpextractor.com",
            }
        }


def presenter(result: DTOLoadTransactionsFromDocumentResponse):
    return {
            "document_id": result.document_id,
            "total_records": result.total_records,
            "loaded": result.loaded_count,
            "skipped": result.skipped_count,
            "errors": result.errors if result.errors else None,
            "processed": True,
        }





def controller(session,document_id):

    # Instantiate concrete gateways
    document_gateway = DocumentDbGateway(session)
    transaction_gateway = TransactionDbGateway(session)

    # Inject gateways into use case
    use_case = LoadTransactionsFromDocumentUseCase(
        document_gateway, transaction_gateway
    )

    dto_request = DTOLoadTransactionsFromDocumentRequest(document_id=document_id)
    # Execute use case
    dto_response = use_case.execute(dto_request)

    return presenter(dto_response)




@router.post("/load-from-document/{document_id}", response_model=Dict[str, Any])
def load_transactions_from_document(
    document_id: uuid.UUID, session: Session = Depends(get_db_session)
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

        return controller(session,document_id)

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
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
