import logging
import uuid

from fastapi import APIRouter, HTTPException, Query, Depends
from api.deps import SessionDep, get_db_session
from sqlmodel import Session

from src.Capplication.use_cases.document.load_transactions_from_document import (
    LoadTransactionsFromDocumentUseCase,
)
from src.Capplication.use_cases.document.get_all_documents import GetAllDocumentsUseCase
from src.Capplication.use_cases.document.pdf_processing import PDFProcessingUseCase
from src.Capplication.DTO.document_dto import (
    DTOGetAllDocumentsRequest,
    DTOGetAllDocumentsResponse,
    DTOLoadTransactionsFromDocumentRequest,
    DTOLoadTransactionsFromDocumentResponse,
    DTOPdfProcessingRequest,
    DTOPdfProcessingResponse,
)
from src.Aframework.gateway.db.document import DocumentDbGateway
from src.Aframework.gateway.db.document_type import DocumentTypeDbGateway
from src.Aframework.gateway.db.transaction import TransactionDbGateway
from src.Aframework.gateway.db.user import UserDbGateway
from src.Aframework.gateway.pdf_extractor import PDFExtractorGateway
from src.Aframework.gateway.file_system import FileSystemGateway
from src.Denterprise.exceptions import UnsupportedDocumentTypeException

logger = logging.getLogger(__name__)

# Crear router para rutas de procesamiento de PDF
router = APIRouter(prefix="/document", tags=["document management"])


@router.get("/documents/", response_model=DTOGetAllDocumentsResponse)
async def get_all_documents(
    session: SessionDep,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
) -> DTOGetAllDocumentsResponse:
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
        dto_request = DTOGetAllDocumentsRequest(skip=skip, limit=limit)

        # Inject gateways into use case
        use_case = GetAllDocumentsUseCase(document_gateway, document_type_gateway)

        # Execute use case
        dto_response = use_case.execute(dto_request)

        return dto_response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving documents: {str(e)}"
        )


# ===============================================================================================================


@router.post(
    "/load-from-document/{document_id}",
    response_model=DTOLoadTransactionsFromDocumentResponse,
)
def load_transactions_from_document(
    document_id: uuid.UUID, session: Session = Depends(get_db_session)
) -> DTOLoadTransactionsFromDocumentResponse:
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

        dto_request = DTOLoadTransactionsFromDocumentRequest(document_id=document_id)
        # Execute use case
        dto_response = use_case.execute(dto_request)

        return dto_response

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


# ===============================================================================================================


@router.post("/pdf-processing")
async def pdf_processing(
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
        # Delegate to controller with simple data types
        # Use case will orchestrate file operations via FileSystemGateway

        # Initialize all gateways (infrastructure layer)
        document_gateway = DocumentDbGateway(session)
        user_gateway = UserDbGateway(session)
        document_type_gateway = DocumentTypeDbGateway(session)
        pdf_extractor_gateway = PDFExtractorGateway()
        file_system_gateway = FileSystemGateway()

        # Delegate all processing to application layer use case
        use_case = PDFProcessingUseCase(
            document_gateway,
            user_gateway,
            pdf_extractor_gateway,
            document_type_gateway,
            file_system_gateway,
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
