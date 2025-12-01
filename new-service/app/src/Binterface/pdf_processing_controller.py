"""
PDF Processing Controller - Interface Adapter Layer
Processes extraction results and coordinates with application layer
"""
import logging
import uuid
from typing import BinaryIO
from sqlmodel import Session

from src.Capplication.pdf_processing_use_case import PDFProcessingUseCase, ProcessPDFResult
from src.Binterface.document_gateway import DocumentGateway
from src.Binterface.user_gateway import UserGateway
from src.Binterface.pdf_extractor_gateway import BCPPDFExtractorGateway

logger = logging.getLogger(__name__)


class PDFProcessingController:
    """Controller for processing PDF extraction results"""
    
    def __init__(self, session: Session):
        self.session = session
        self.document_gateway = DocumentGateway(session)
        self.user_gateway = UserGateway(session)
        self.pdf_extractor_gateway = BCPPDFExtractorGateway()
    
    def process_and_save_document(
        self,
        pdf_file: BinaryIO,
        pdf_filename: str,
        user_email: str,
        document_type: str = "BCP_STATEMENT"
    ) -> ProcessPDFResult:
        """
        Process PDF file and save document using application layer
        
        Args:
            pdf_file: Binary PDF file content
            pdf_filename: Name of the PDF file
            user_email: Email of the user
            document_type: Type of document (default: BCP_STATEMENT)
            
        Returns:
            ProcessPDFResult with operation details
            
        Raises:
            ValueError: If PDF processing fails
        """
        # Delegate all processing to application layer use case
        use_case = PDFProcessingUseCase(
            self.document_gateway,
            self.user_gateway,
            self.pdf_extractor_gateway
        )
        result = use_case.execute(
            pdf_file=pdf_file,
            pdf_filename=pdf_filename,
            user_email=user_email,
            document_type=document_type
        )
        
        return result
