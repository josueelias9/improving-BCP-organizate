"""
Document Type Routes - HTTP Interface
Delegates to application layer use cases
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Dict, Any
import logging

from api.deps import get_db_session
from src.Aframework.gateway.db.document_type import DocumentTypeDbGateway
from src.Capplication.use_cases.document_type.get_all_document_types import (
    GetAllDocumentTypesUseCase,
)
from src.Capplication.DTO.document_type_dto import DTOGetAllDocumentTypesResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=Dict[str, Any])
def get_all_document_types(
    session: Session = Depends(get_db_session),
) -> Dict[str, Any]:
    """
    Get all document types

    Returns:
        List of all document types with their details
    """
    try:
        return controller(session)

    except Exception as e:
        logger.error(f"Error retrieving document types: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving document types: {str(e)}"
        )


def controller(session: Session):

    document_type_gateway = DocumentTypeDbGateway(session)

    # Inject gateway into use case
    use_case = GetAllDocumentTypesUseCase(document_type_gateway)

    result = use_case.execute()

    return presenter(result)


def presenter(dto: DTOGetAllDocumentTypesResponse) -> Dict[str, Any]:
    """
    Presenter function to convert DTO to response dict

    Args:
        dto: DTOGetAllDocumentTypesResponse from use case

    Returns:
        Dict suitable for JSON response
    """
    return {
        "document_types": dto.document_types,
        "total_count": dto.total_count,
    }
