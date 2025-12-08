from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlmodel import Session

import uuid
import os
import logging

from api.deps import SessionDep, get_db_session
from src.Binterface.pdf_processing_controller import PDFProcessingController
from src.Aframework.gateway.db.document import DocumentDbGateway
from src.Aframework.gateway.db.user import UserDbGateway
from src.Aframework.gateway.db.document_type import DocumentTypeDbGateway
from src.Aframework.gateway.pdf_extractor import PDFExtractorGateway
from src.Aframework.gateway.db.transaction import TransactionDbGateway
from src.Denterprise.exceptions import UnsupportedDocumentTypeException
from src.Capplication.use_cases.document.load_transactions_from_document import LoadTransactionsFromDocumentUseCase




logger = logging.getLogger(__name__)

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


@router.get("/documents/")
async def get_all_documents(
    session: SessionDep,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return")
) -> List[Dict[str, Any]]:
    """
    Get all documents with pagination
    
    Returns all documents with their properties including:
    - id, account_number, type, currency
    - previous_balance, initial_day, final_day
    - unique_identifier, processed status
    - user_id and transaction count
    """
    try:
        # Use gateway to retrieve documents
        document_gateway = DocumentDbGateway(session)
        return document_gateway.get_all(skip=skip, limit=limit)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving documents: {str(e)}"
        )


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
        document_type_gateway = DocumentTypeDbGateway(session)
        pdf_extractor_gateway = PDFExtractorGateway()
        
        # Create controller with injected dependencies
        controller = PDFProcessingController(
            document_gateway=document_gateway,
            user_gateway=user_gateway,
            pdf_extractor_gateway=pdf_extractor_gateway,
            document_type_gateway=document_type_gateway
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
    


@router.post("/load-from-document/{document_id}", response_model=Dict[str, Any])
def load_transactions_from_document(
    document_id: uuid.UUID,
    session: Session = Depends(get_db_session)
) -> Dict[str, Any]:
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
        use_case = LoadTransactionsFromDocumentUseCase(document_gateway, transaction_gateway)
        
        # Execute use case
        result = use_case.execute(document_id)
        
        # Map domain result to HTTP response
        return {
            "document_id": str(document_id),
            "total_records": result.total_records,
            "loaded": result.loaded_count,
            "skipped": result.skipped_count,
            "errors": result.errors if result.errors else None,
            "processed": True
        }
        
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
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )