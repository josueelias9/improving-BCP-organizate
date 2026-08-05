import logging
import uuid

from fastapi import APIRouter, HTTPException, Query
from api.deps import SessionDep

from src.Capplication.use_cases.document.get_documents import GetDocumentsUseCase
from src.Capplication.use_cases.document.create_document import CreateDocumentUseCase
from src.Capplication.use_cases.document.delete_document import DeleteDocumentUseCase
from src.Capplication.DTO.document_dto import (
    DTOGetDocumentsRequest,
    DTOGetDocumentsResponse,
    DTOCreateDocumentRequest,
    DTOCreateDocumentResponse,
)
from src.Aframework.gateway.db.document import DocumentDbGateway
from src.Aframework.gateway.db.document_type import DocumentTypeDbGateway
from src.Aframework.gateway.db.user import UserDbGateway
from src.Aframework.gateway.content_extractor.bcp_credit_parser import BCPCreditParser
from src.Aframework.gateway.content_extractor.bcp_debit_parser import BCPDebitParser
from src.Aframework.gateway.file_extractor import FileExtractorGateway

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
):
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

        return use_case.execute(dto_request)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving documents: {str(e)}"
        )


@router.post("/", response_model=DTOCreateDocumentResponse)
async def create_document(dto_request: DTOCreateDocumentRequest, session: SessionDep):
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
        file_extractor_gateway = FileExtractorGateway()

        doc_type = document_type_gateway.get_by_name(dto_request.document_type)
        document_type_name = doc_type.name if doc_type else dto_request.document_type
        parser_gateway = (
            BCPCreditParser()
            if document_type_name == "bcp_credit"
            else BCPDebitParser()
        )

        # Delegate all processing to application layer use case
        use_case = CreateDocumentUseCase(
            document_gateway,
            user_gateway,
            document_type_gateway,
            file_extractor_gateway,
            parser_gateway,
        )

        # Use case returns DTO for controller response
        return use_case.execute(dto_request)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@router.delete("/{document_id}")
def delete_document(session: SessionDep, document_id: uuid.UUID) -> dict:
    document_db_gateway = DocumentDbGateway(session)
    delete_document_use_case = DeleteDocumentUseCase(document_db_gateway)
    delete_document_use_case.execute(document_id)
    return {
        "message": f"Document {document_id} deleted successfully",
        "status": "success",
    }
