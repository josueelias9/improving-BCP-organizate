from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any

import logging

from api.deps import SessionDep
from src.Aframework.gateway.db.document import DocumentDbGateway
from src.Capplication.use_cases.document.get_all_documents import (
    GetAllDocumentsUseCase,
    GetAllDocumentsRequest,
)

from src.Capplication.DTO.document_dto import DTOGetAllDocumentsResponse


logger = logging.getLogger(__name__)

# Crear router para rutas de procesamiento de PDF
router = APIRouter(prefix="/api", tags=["PDF Processing"])


def presenter(result: DTOGetAllDocumentsResponse):
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


def controller(session, skip, limit):
    document_gateway = DocumentDbGateway(session)

    # Create request DTO
    request = GetAllDocumentsRequest(skip=skip, limit=limit)

    # Inject gateway into use case
    use_case = GetAllDocumentsUseCase(document_gateway)

    # Execute use case
    result = use_case.execute(request)

    # Map domain result to HTTP response
    return presenter(result)


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
        return controller(session, skip, limit)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving documents: {str(e)}"
        )
