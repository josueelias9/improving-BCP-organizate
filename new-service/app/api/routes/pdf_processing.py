from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.deps import SessionDep
from src.Binterface.pdf_processing_controller import PDFProcessingController
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
        # Verify PDF type
        if request.type.lower() == "credit":
            raise HTTPException(
                status_code=501,
                detail="Credit card PDF processing not implemented yet. Only debit accounts are supported."
            )
        elif request.type.lower() != "debit":
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF type. Use 'debit' or 'credit'."
            )
        
        # Verify file exists
        if not os.path.exists(request.pdf_filename):
            raise HTTPException(
                status_code=404, 
                detail=f"File '{request.pdf_filename}' not found"
            )
        
        # Process PDF using controller (delegates to application layer)
        controller = PDFProcessingController(session)
        
        with open(request.pdf_filename, 'rb') as pdf_file:
            result = controller.process_and_save_document(
                pdf_file=pdf_file,
                pdf_filename=request.pdf_filename,
                user_email=request.user_email,
                document_type="BCP_STATEMENT"
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
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )