import logging
import uuid

from fastapi import APIRouter, HTTPException, Query
from api.deps import SessionDep

from src.Capplication.use_cases.document.get_all_documents import GetDocumentsUseCase
from src.Capplication.use_cases.document.create_document import CreateDocumentUseCase
from src.Capplication.use_cases.document.delete_document import DeleteDocumentUseCase
from src.Capplication.DTO.document_dto import (
    DTOGetDocumentsRequest,
    DTOGetDocumentsResponse,
    DTOPdfProcessingRequest,
    DTOPdfProcessingResponse,
)
from src.Aframework.gateway.db.document import DocumentDbGateway
from src.Aframework.gateway.db.document_type import DocumentTypeDbGateway
from src.Aframework.gateway.db.user import UserDbGateway
from src.Aframework.gateway.content_extractor import ContentExtractorGateway
from src.Aframework.gateway.file_extractor import FileExtractorGateway
from src.Denterprise.exceptions import UnsupportedDocumentTypeException

logger = logging.getLogger(__name__)

# Crear router para rutas de procesamiento de PDF
router = APIRouter(prefix="/document", tags=["document management"])


# CRUD


@router.get("/", response_model=DTOGetDocumentsResponse)
async def get_documents(
    session: SessionDep,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
) -> DTOGetDocumentsResponse:
    """
    Get all documents with pagination

    Returns all documents with their properties including:
    - id, unique_identifier
    - processed status, user_id, document_type_id
    - transactions count
    """
    try:
        document_gateway = DocumentDbGateway(session)
        document_type_gateway = DocumentTypeDbGateway(session)

        # Create request DTO
        dto_request = DTOGetDocumentsRequest(skip=skip, limit=limit)

        # Inject gateways into use case
        use_case = GetDocumentsUseCase(document_gateway, document_type_gateway)

        # Execute use case
        dto_response = use_case.execute(dto_request)

        return dto_response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving documents: {str(e)}"
        )


@router.delete("/{document_id}")
def delete_document(session: SessionDep, document_id: uuid.UUID):
    document_db_gateway = DocumentDbGateway(session)
    delete_document_use_case = DeleteDocumentUseCase(document_db_gateway)
    delete_document_use_case.execute(document_id)
    return {
        "message": f"Document {document_id} deleted successfully",
        "status": "success",
    }


@router.post("/")
async def create_document(
    dto_request: DTOPdfProcessingRequest, session: SessionDep
) -> DTOPdfProcessingResponse:
    """
    Process a PDF file and save extracted data to the Documents table

    - **pdf_filepath**: PDF file path (e.g., "files/document.pdf")
    - **document_type**: Account type ("debit" or "credit")
    - **user_email**: User email (optional, defaults to admin@bcpextractor.com)
    - Extracted data is saved as JSON in the 'data' column of the Documents table
    """
    try:
        # Initialize all gateways (infrastructure layer)
        document_gateway = DocumentDbGateway(session)
        user_gateway = UserDbGateway(session)
        document_type_gateway = DocumentTypeDbGateway(session)
        content_extractor_gateway = ContentExtractorGateway()
        file_extractor_gateway = FileExtractorGateway()

        # Delegate all processing to application layer use case
        use_case = CreateDocumentUseCase(
            document_gateway,
            user_gateway,
            content_extractor_gateway,
            document_type_gateway,
            file_extractor_gateway,
        )

        # Use case returns DTO for controller response
        dto_response = use_case.execute(dto_request)

        return dto_response

    except UnsupportedDocumentTypeException as e:
        # Adapt business exception to HTTP response
        raise HTTPException(status_code=501, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


# other
