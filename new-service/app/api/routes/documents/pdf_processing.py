from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

import logging

from api.deps import SessionDep

from src.Aframework.gateway.db.document import DocumentDbGateway
from src.Aframework.gateway.db.user import UserDbGateway
from src.Aframework.gateway.db.document_type import DocumentTypeDbGateway
from src.Aframework.gateway.pdf_extractor import PDFExtractorGateway
from src.Aframework.gateway.file_system import FileSystemGateway
from src.Denterprise.exceptions import UnsupportedDocumentTypeException
from src.Capplication.use_cases.document.pdf_processing import PDFProcessingUseCase
from src.Capplication.DTO.document_dto import (
    DTOPdfProcessingResponse,
    DTOPdfProcessingRequest,
)


logger = logging.getLogger(__name__)

# Crear router para rutas de procesamiento de PDF
router = APIRouter(prefix="/api", tags=["PDF Processing"])


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


def presenter(dto_response: DTOPdfProcessingResponse):
    # Return response based on result
    if dto_response.already_exists:
        return {
            "message": dto_response.message,
            "unique_identifier": dto_response.unique_identifier,
            "document_id": dto_response.document_id,
        }

    return {
        "success": True,
        "message": dto_response.message,
        "document_id": dto_response.document_id,
        "transactions_count": dto_response.transactions_count,
    }


def controller(
    pdf_filepath: str,
    user_email: str,
    session: Session,
    document_type: str,
):
    """
    Process PDF file and save document using application layer

    This controller method receives simple data types and delegates
    all processing orchestration to the use case.

    Args:
        pdf_filepath: Path to the PDF file
        user_email: Email of the user
        document_type: Type of document

    Returns:
        DTOPdfProcessingResponse (DTO for HTTP response)

    Raises:
        ValueError: If PDF processing fails
        FileNotFoundError: If file not found
        UnsupportedDocumentTypeException: If document type is not supported
    """

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

    dto_request = DTOPdfProcessingRequest(
        pdf_filepath=pdf_filepath,
        user_email=user_email,
        document_type=document_type,
    )
    # Use case returns DTO for controller response
    dto_response = use_case.execute(dto_request)

    return presenter(dto_response)


@router.post("/pdf-processing")
async def pdf_processing(request: PDFProcessRequest, session: SessionDep):
    """
    Process a PDF file and save extracted data to the Documents table

    - **pdf_filename**: PDF file path (e.g., "files/document.pdf")
    - **type**: Account type ("debit" or "credit")
    - **user_email**: User email (optional, defaults to admin@bcpextractor.com)
    - Extracted data is saved as JSON in the 'data' column of the Documents table
    """
    try:
        # Delegate to controller with simple data types
        # Use case will orchestrate file operations via FileSystemGateway
        result = controller(
            pdf_filepath=request.pdf_filename,
            user_email=request.user_email,
            session=session,
            document_type=request.type,
        )

        return result

    except UnsupportedDocumentTypeException as e:
        # Adapt business exception to HTTP response
        raise HTTPException(status_code=501, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
