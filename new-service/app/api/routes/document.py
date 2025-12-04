from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.deps import SessionDep
from src.Binterface.pdf_processing_controller import PDFProcessingController
from src.Binterface.gateway.db.document import DocumentDbGateway
from src.Binterface.gateway.db.user import UserDbGateway
from src.Binterface.gateway.pdf_extractor import PDFExtractorGateway
from src.Denterprise.exceptions import UnsupportedDocumentTypeException
import os

# Crear router para rutas de procesamiento de PDF
router = APIRouter(prefix="/api", tags=["PDF Processing"])

# Modelos Pydantic para request body
class PDFProcessRequest(BaseModel):
    pdf_filename: str
    type: str  # "debit" o "credit"
    user_email: str = "admin@bcpextractor.com"
    
    class Config:
        json_schema_extra = {
            "example": {
                "pdf_filename": "files/EECC102025_09745280.PDF",
                "type": "debit",
                "user_email": "admin@bcpextractor.com"
            }
        }


@router.post("/pdf-processing")
async def pdf_processing(
    request: PDFProcessRequest, 
    session: SessionDep
):
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
                status_code=404, 
                detail=f"File '{request.pdf_filename}' not found"
            )
        
        # Map request type to document type
        document_type_map = {
            "debit": "BCP_STATEMENT",
            "credit": "CREDIT_STATEMENT"
        }
        
        document_type = document_type_map.get(request.type.lower())
        if not document_type:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid PDF type '{request.type}'. Use 'debit' or 'credit'."
            )
        
        # Initialize gateways (dependency injection at composition root)
        document_gateway = DocumentDbGateway(session)
        user_gateway = UserDbGateway(session)
        pdf_extractor_gateway = PDFExtractorGateway()
        
        # Create controller with injected dependencies
        controller = PDFProcessingController(
            document_gateway=document_gateway,
            user_gateway=user_gateway,
            pdf_extractor_gateway=pdf_extractor_gateway
        )
        
        # Open file and pass binary content to controller
        with open(request.pdf_filename, 'rb') as pdf_file:
            result = controller.process_and_save_document(
                pdf_file=pdf_file,
                user_email=request.user_email,
                document_type=document_type
            )
        
        # Return response based on result
        if result.already_exists:
            return {
                "detail": result.message,
                "unique_identifier": result.unique_identifier,
                "document_id": result.document_id
            }
        
        return {
            "success": True,
            "message": result.message,
            "document_id": result.document_id,
            "transactions_count": result.transactions_count
        }
        
    except UnsupportedDocumentTypeException as e:
        # Adapt business exception to HTTP response
        raise HTTPException(
            status_code=501,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )