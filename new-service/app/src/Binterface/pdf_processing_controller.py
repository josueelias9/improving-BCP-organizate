"""
PDF Processing Controller - Interface Adapter Layer
Processes extraction results and coordinates with application layer
"""
import logging
import uuid
from sqlmodel import Session

from src.Denterprise.entities import ExtractionResult
from src.Capplication.process_pdf_use_case import ProcessPDFUseCase, ProcessPDFResult
from src.Capplication.pdf_extraction_processor import PDFExtractionProcessor
from src.Binterface.document_gateway import DocumentGateway

logger = logging.getLogger(__name__)


class PDFProcessingController:
    """Controller for processing PDF extraction results"""
    
    def __init__(self, session: Session):
        self.session = session
        self.document_gateway = DocumentGateway(session)
    
    def process_and_save_document(
        self,
        extraction_result: ExtractionResult,
        user_id: uuid.UUID,
        document_type: str = "BCP_STATEMENT"
    ) -> ProcessPDFResult:
        """
        Process extraction result and save document using application layer
        
        Args:
            extraction_result: The result from PDF extraction
            user_id: User ID who owns the document
            document_type: Type of document (default: BCP_STATEMENT)
            
        Returns:
            ProcessPDFResult with operation details
            
        Raises:
            ValueError: If extraction result is invalid
        """
        # Validate and process extraction result using application layer
        unique_id, transactions_list = PDFExtractionProcessor.process_extraction_result(extraction_result)
        
        # Delegate to application layer use case
        use_case = ProcessPDFUseCase(self.document_gateway)
        result = use_case.execute(
            extraction_result=extraction_result,
            unique_id=unique_id,
            transactions_list=transactions_list,
            user_id=user_id,
            document_type=document_type
        )
        
        return result
