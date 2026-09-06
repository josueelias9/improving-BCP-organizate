import logging
from pathlib import Path

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
from src.Aframework.gateway.db.document_format import DocumentFormatDbGateway
from src.Aframework.gateway.db.user import UserDbGateway
from src.Aframework.gateway.db.account import AccountDbGateway
from src.Aframework.gateway.content_extractor.bcp_credit_parser import BCPCreditParser
from src.Aframework.gateway.content_extractor.bcp_debit_parser import BCPDebitParser
from src.Aframework.gateway.content_extractor.yape_parser import YapeParser
from src.Aframework.gateway.content_extractor.scotiabank_parser import ScotiabankParser
from src.Aframework.gateway.file_extractor import FileExtractorGateway

logger = logging.getLogger(__name__)

# Crear router para rutas de procesamiento de PDF
router = APIRouter(prefix="/documents", tags=["document management"])


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
    - id (SHA256 hash of plain text), processed status, user_id, document_type_id
    - transactions count
    """
    try:
        # Create use case
        document_gateway = DocumentDbGateway(session)
        document_format_gateway = DocumentFormatDbGateway(session)
        use_case = GetDocumentsUseCase(document_gateway, document_format_gateway)

        # Create request DTO
        dto_request = DTOGetDocumentsRequest(skip=skip, limit=limit)

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
    - **document_format**: Account type ("debit" or "credit")
    - **user_email**: User email (optional, defaults to admin@bcpextractor.com)
    - Extracted data is saved as JSON in the 'data' column of the Documents table
    """
    try:
        # Initialize all gateways (infrastructure layer)

        document_format_name = Path(dto_request.pdf_filepath).parent.name
        parser_map = {
            "bcp_credit": BCPCreditParser(),
            "bcp_debit": BCPDebitParser(),
            "yape": YapeParser(),
            "Scotiabank": ScotiabankParser(),
        }
        parser_gateway = parser_map.get(document_format_name)
        if parser_gateway is None:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown document format: '{document_format_name}'",
            )

        # Delegate all processing to application layer use case
        use_case = CreateDocumentUseCase(
            document_gateway=DocumentDbGateway(session),
            user_gateway=UserDbGateway(session),
            document_format_gateway=DocumentFormatDbGateway(session),
            file_extractor_gateway=FileExtractorGateway(),
            parser_gateway=parser_gateway,
            account_gateway=AccountDbGateway(session),
        )

        # Use case returns DTO for controller response
        return use_case.execute(dto_request)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@router.delete("/{document_id}")
def delete_document(session: SessionDep, document_id: str) -> dict:
    document_db_gateway = DocumentDbGateway(session)
    delete_document_use_case = DeleteDocumentUseCase(document_db_gateway)
    delete_document_use_case.execute(document_id)
    return {
        "message": f"Document {document_id} deleted successfully",
        "status": "success",
    }
