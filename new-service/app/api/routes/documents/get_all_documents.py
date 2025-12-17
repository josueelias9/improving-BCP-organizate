from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any

import logging

from api.deps import SessionDep
from src.Aframework.gateway.db.document import DocumentDbGateway
from src.Aframework.gateway.db.document_type import DocumentTypeDbGateway
from src.Capplication.use_cases.document.get_all_documents import GetAllDocumentsUseCase
from src.Capplication.DTO.document_dto import (
    DTOGetAllDocumentsResponse,
    DTOGetAllDocumentsRequest,
)


logger = logging.getLogger(__name__)

# Crear router para rutas de procesamiento de PDF
router = APIRouter(prefix="/api", tags=["PDF Processing"])


def presenter(dto_response: DTOGetAllDocumentsResponse):
    return {
        "documents": dto_response.documents,
        "total_returned": dto_response.total_returned,
        "skip": dto_response.skip,
        "limit": dto_response.limit,
    }


def controller(session, skip, limit):
    document_gateway = DocumentDbGateway(session)
    document_type_gateway = DocumentTypeDbGateway(session)

    # Create request DTO
    dto_request = DTOGetAllDocumentsRequest(skip=skip, limit=limit)

    # Inject gateways into use case
    use_case = GetAllDocumentsUseCase(document_gateway, document_type_gateway)

    # Execute use case
    dto_response = use_case.execute(dto_request)

    # Map domain result to HTTP response
    return presenter(dto_response)


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
    - id, unique_identifier
    - processed status, user_id, document_type_id
    - transactions count
    """
    try:
        return controller(session, skip, limit)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving documents: {str(e)}"
        )
