from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlmodel import Session

import uuid
import os
import logging

from api.deps import SessionDep, get_db_session
from src.Aframework.gateway.db.document import DocumentDbGateway
from src.Aframework.gateway.db.user import UserDbGateway
from src.Aframework.gateway.db.document_type import DocumentTypeDbGateway
from src.Aframework.gateway.pdf_extractor import PDFExtractorGateway
from src.Aframework.gateway.db.transaction import TransactionDbGateway
from src.Denterprise.exceptions import UnsupportedDocumentTypeException
from src.Capplication.use_cases.document.load_transactions_from_document import (
    LoadTransactionsFromDocumentUseCase,
)
from src.Capplication.use_cases.document.get_all_documents import (
    GetAllDocumentsUseCase,
    GetAllDocumentsRequest,
)
from src.Capplication.use_cases.document.pdf_processing import PDFProcessingUseCase
from src.Capplication.DTO.document_dto import DTOPdfProcessingResponse

from typing import BinaryIO

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


@router.get("/documents/")
async def get_all_documents(
    session: SessionDep,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
) -> Dict[str, Any]:
    """
    Get all documents with pagination

    Returns all documents with their properties including:
    - id, currency, unique_identifier
    - processed status, user_id, document_type_id
    - transactions count
    """
    try:
        # Instantiate gateway
        document_gateway = DocumentDbGateway(session)

        # Create request DTO
        request = GetAllDocumentsRequest(skip=skip, limit=limit)

        # Inject gateway into use case
        use_case = GetAllDocumentsUseCase(document_gateway)

        # Execute use case
        result = use_case.execute(request)

        # Map domain result to HTTP response
        return {
            "documents": [
                {
                    "id": doc.id,
                    "currency": doc.currency,
                    "unique_identifier": doc.unique_identifier,
                    "processed": doc.processed,
                    "user_id": doc.user_id,
                    "document_type_id": doc.document_type_id,
                    "transactions_count": doc.transactions_count,
                }
                for doc in result.documents
            ],
            "total_returned": result.total_returned,
            "skip": result.skip,
            "limit": result.limit,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving documents: {str(e)}"
        )






# =============================================================================================================================================


# =============================================================================================================================================


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
        # Instantiate concrete gateways
        document_gateway = DocumentDbGateway(session)
        transaction_gateway = TransactionDbGateway(session)

        # Inject gateways into use case
        use_case = LoadTransactionsFromDocumentUseCase(
            document_gateway, transaction_gateway
        )

        # Execute use case
        result = use_case.execute(document_id)

        # Map domain result to HTTP response
        return {
            "document_id": str(document_id),
            "total_records": result.total_records,
            "loaded": result.loaded_count,
            "skipped": result.skipped_count,
            "errors": result.errors if result.errors else None,
            "processed": True,
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
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
