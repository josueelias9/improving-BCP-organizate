"""
PDF Processing Controller - Interface Adapter Layer
Processes extraction results and coordinates with application layer
"""

import logging
from typing import BinaryIO

from src.Capplication.use_cases.document.pdf_processing import PDFProcessingUseCase
from src.Capplication.DTO.document_dto import DTOProcessPDFResponse
from src.Capplication.gateway.db import IDocumentDbGateway, IUserDbGateway
from src.Capplication.gateway.pdf_extractor import PDFExtractorGateway
from src.Aframework.gateway.db.document_type import DocumentTypeDbGateway

logger = logging.getLogger(__name__)


class PDFProcessingController:
    """Controller for processing PDF extraction results"""

    def __init__(
        self,
        document_gateway: IDocumentDbGateway,
        user_gateway: IUserDbGateway,
        pdf_extractor_gateway: PDFExtractorGateway,
        document_type_gateway: DocumentTypeDbGateway,
    ):
        """
        Initialize controller with dependency injection

        Args:
            document_gateway: Gateway for document persistence
            user_gateway: Gateway for user persistence
            pdf_extractor_gateway: Gateway for PDF extraction
            document_type_gateway: Gateway for document type persistence
        """
        self.document_gateway = document_gateway
        self.user_gateway = user_gateway
        self.pdf_extractor_gateway = pdf_extractor_gateway
        self.document_type_gateway = document_type_gateway

    def process_and_save_document(
        self, pdf_file: BinaryIO, user_email: str, document_type: str = "BCP_STATEMENT"
    ) -> DTOProcessPDFResponse:
        """
        Process PDF file and save document using application layer

        This controller method receives infrastructure inputs (BinaryIO)
        and returns a DTO for the HTTP response layer.

        Args:
            pdf_file: Binary PDF file content (file stream)
            user_email: Email of the user
            document_type: Type of document (default: BCP_STATEMENT)

        Returns:
            DTOProcessPDFResponse (DTO for HTTP response)

        Raises:
            ValueError: If PDF processing fails
            UnsupportedDocumentTypeException: If document type is not supported
        """
        # Delegate all processing to application layer use case
        use_case = PDFProcessingUseCase(
            self.document_gateway,
            self.user_gateway,
            self.pdf_extractor_gateway,
            self.document_type_gateway,
        )
        # Use case returns DTO for controller response
        result = use_case.execute(
            pdf_file=pdf_file,
            pdf_filename="",  # No longer needed by use case
            user_email=user_email,
            document_type=document_type,
        )

        return result
