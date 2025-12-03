"""
PDF Processing Controller - Interface Adapter Layer
Processes extraction results and coordinates with application layer
"""
import logging
from typing import BinaryIO
from sqlmodel import Session

from src.Capplication.use_cases.pdf_processing import PDFProcessingUseCase, ProcessPDFResult
from src.Binterface.gateway.db.document import DocumentDbGateway
from src.Binterface.gateway.db.user import UserDbGateway
from src.Binterface.gateway.pdf_extractor import PDFExtractorGateway

logger = logging.getLogger(__name__)


class PDFProcessingController:
    """Controller for processing PDF extraction results"""
    
    def __init__(self, session: Session):
        self.session = session
        self.document_gateway = DocumentDbGateway(session)
        self.user_gateway = UserDbGateway(session)
        self.pdf_extractor_gateway = PDFExtractorGateway()
    
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
