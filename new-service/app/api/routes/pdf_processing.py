from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.deps import SessionDep
from pdf_extractor import BCPPDFExtractor
from models import DocumentCreate, DocumentType, UserCreate, CustomerType
import crud
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


@router.post("/process-pdf")
async def process_pdf_endpoint(
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
        
        # Get or create user
        user = crud.get_user_by_email(session, request.user_email)
        if not user:
            user_create = UserCreate(
                email=request.user_email,
                name="Admin User",
                customer_type=CustomerType.INDIVIDUAL
            )
            user = crud.create_user(session, user_create)
        
        # Extract transactions from PDF
        extractor = BCPPDFExtractor()
        with open(request.pdf_filename, 'rb') as pdf_file:
            extraction_result = extractor.extract_transactions(pdf_file, request.pdf_filename)
        
        if not extraction_result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing PDF: {extraction_result.error_message or 'Unknown error'}"
            )
        
        # Convert transactions to dict list
        transactions_list = [t.__dict__ for t in extraction_result.transactions]
        
        unique_id = f"{extraction_result.initial_day}__{extraction_result.final_day}__{extraction_result.account_code}"
        
        # Check if document already exists with this unique_identifier
        existing_document = crud.get_document_by_unique_identifier(session, unique_id)
        if existing_document:
            raise HTTPException(
                status_code=409,
                detail=f"Document already exists with unique_identifier '{unique_id}'. Document ID: {existing_document.id}"
            )
        
        # Create document record in database
        document_create = DocumentCreate(
            account_number=extraction_result.account_code or "UNKNOWN",
            type=DocumentType.BCP_STATEMENT,
            user_id=user.id,
            previous_balance=extraction_result.saldo_anterior,
            initial_day=extraction_result.initial_day,
            final_day=extraction_result.final_day,
            data=transactions_list,
            unique_identifier=unique_id
        )
        document = crud.create_document(session, document_create)
        
        return {
            "success": True,
            "message": f"PDF processed successfully. {len(transactions_list)} transactions saved as JSON in Documents table.",
            "document_id": str(document.id),
            "user_id": str(user.id),
            "account_number": extraction_result.account_code,
            "filename": extraction_result.filename,
            "transactions_count": len(transactions_list)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )