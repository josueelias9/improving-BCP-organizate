from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

import os
import logging
from typing import BinaryIO

from api.deps import SessionDep

from src.Aframework.gateway.db.document import DocumentDbGateway
from src.Aframework.gateway.db.user import UserDbGateway
from src.Aframework.gateway.db.document_type import DocumentTypeDbGateway
from src.Aframework.gateway.pdf_extractor import PDFExtractorGateway
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


def presenter(result: DTOPdfProcessingResponse):
    # Return response based on result
    if result.already_exists:
        return {
            "detail": result.message,
            "unique_identifier": result.unique_identifier,
            "document_id": result.document_id,
        }

    return {
        "success": True,
        "message": result.message,
        "document_id": result.document_id,
        "transactions_count": result.transactions_count,
    }


def controller(
    pdf_file: BinaryIO,
    user_email: str,
    session: Session,
    document_type: str = "BCP_STATEMENT",
):
    """
    Process PDF file and save document using application layer

    This controller method receives infrastructure inputs (BinaryIO)
    and returns a DTO for the HTTP response layer.

    Args:
        pdf_file: Binary PDF file content (file stream)
        user_email: Email of the user
        document_type: Type of document (default: BCP_STATEMENT)

    Returns:
        DTOPdfProcessingResponse (DTO for HTTP response)

    Raises:
        ValueError: If PDF processing fails
        UnsupportedDocumentTypeException: If document type is not supported
    """

    document_gateway = DocumentDbGateway(session)
    user_gateway = UserDbGateway(session)
    document_type_gateway = DocumentTypeDbGateway(session)
    pdf_extractor_gateway = PDFExtractorGateway()

    # Delegate all processing to application layer use case
    use_case = PDFProcessingUseCase(
        document_gateway,
        user_gateway,
        pdf_extractor_gateway,
        document_type_gateway,
    )

    dto_request = DTOPdfProcessingRequest(
        pdf_file=pdf_file,
        pdf_filename="",  # No longer needed by use case
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
        # Verify file exists (infrastructure concern - stays in route)
        if not os.path.exists(request.pdf_filename):
            raise HTTPException(
                status_code=404, detail=f"File '{request.pdf_filename}' not found"
            )

        # Map request type to document type
        document_type_map = {"debit": "BCP_STATEMENT", "credit": "CREDIT_STATEMENT"}

        document_type = document_type_map.get(request.type.lower())
        if not document_type:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid PDF type '{request.type}'. Use 'debit' or 'credit'.",
            )

        # Open file and pass binary content to controller
        with open(request.pdf_filename, "rb") as pdf_file:
            result = controller(
                pdf_file=pdf_file,
                user_email=request.user_email,
                session=session,
                document_type=document_type,
            )

        return result

    except UnsupportedDocumentTypeException as e:
        # Adapt business exception to HTTP response
        raise HTTPException(status_code=501, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
