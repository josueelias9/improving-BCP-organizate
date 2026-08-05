"""
Document Type Routes - HTTP Interface
Delegates to application layer use cases
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
import logging
from api.deps import get_db_session
from src.Aframework.gateway.db.document_format import DocumentTypeDbGateway
from src.Capplication.use_cases.document_format.get_all_document_formats import (
    GetAllDocumentFormatsUseCase,
)
from src.Capplication.DTO.document_format_dto import DTOGetAllDocumentFormatsResponse

router = APIRouter(prefix="/document-types", tags=["document types"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=DTOGetAllDocumentFormatsResponse)
def get_all_document_formats(
    session: Session = Depends(get_db_session),
) -> DTOGetAllDocumentFormatsResponse:
    """
    Get all document types

    Returns:
        List of all document types with their details
    """
    try:
        document_type_gateway = DocumentTypeDbGateway(session)

        # Inject gateway into use case
        use_case = GetAllDocumentFormatsUseCase(document_type_gateway)

        return use_case.execute()

    except Exception as e:
        logger.error(f"Error retrieving document types: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving document types: {str(e)}"
        )
