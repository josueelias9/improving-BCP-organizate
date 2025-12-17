"""
Process PDF Use Case - Application Layer
Orchestrates the flow of processing a PDF and creating a document
"""

import logging

from src.Denterprise.exceptions import UnsupportedDocumentTypeException
from src.Capplication.DTO.document_dto import (
    DTOPdfProcessingResponse,
    DTOPdfProcessingRequest,
)
from src.Capplication.gateway.db import IDocumentDbGateway, IUserDbGateway
from src.Capplication.gateway.pdf_extractor import IPDFExtractorGateway
from src.Capplication.gateway.file_system import IFileSystemGateway
from src.Aframework.gateway.db.document_type import IDocumentTypeDbGateway

logger = logging.getLogger(__name__)


class PDFProcessingUseCase:
    """Use case for processing PDF and creating document"""

    def __init__(
        self,
        document_gateway: IDocumentDbGateway,
        user_gateway: IUserDbGateway,
        pdf_extractor_gateway: IPDFExtractorGateway,
        document_type_gateway: IDocumentTypeDbGateway,
        file_system_gateway: IFileSystemGateway,
    ):
        self.document_gateway = document_gateway
        self.user_gateway = user_gateway
        self.pdf_extractor_gateway = pdf_extractor_gateway
        self.document_type_gateway = document_type_gateway
        self.file_system_gateway = file_system_gateway

    def execute(self, request: DTOPdfProcessingRequest) -> DTOPdfProcessingResponse:
        """
        Process PDF file: get/create user, extract transactions, and create document

        Args:
            request: DTOPdfProcessingRequest containing:
                - pdf_filepath: Path to the PDF file
                - user_email: Email of the user
                - document_type: Type of document

        Returns:
            DTOPdfProcessingResponse (DTO for controller response)

        Raises:
            ValueError: If validation fails
            FileNotFoundError: If PDF file not found
            UnsupportedDocumentTypeException: If document type is not supported
        """

        pdf_filepath = request.pdf_filepath
        user_email = request.user_email
        document_type = request.document_type

        try:
            # Check if file exists using file system gateway
            if not self.file_system_gateway.file_exists(pdf_filepath):
                raise FileNotFoundError(f"File '{pdf_filepath}' not found")

            # Validate document type (business rule)
            self._validate_document_type(document_type)

            # Get or create user entity
            user = self._get_or_create_user(user_email)

            doc_type = self.document_type_gateway.get_by_name(document_type)

            if not doc_type:
                raise ValueError(
                    f"Document type '{document_type}' not found in database"
                )

            # Read PDF file using file system gateway
            pdf_content = self.file_system_gateway.read_binary_file(pdf_filepath)

            # Extract document from PDF content
            document = self.pdf_extractor_gateway.extract_document(
                pdf_content, document_type=doc_type.name
            )

            # Validate document has data
            if not document.data:
                raise ValueError("No transactions extracted from PDF")

            # Check if document already exists with this unique_identifier
            existing_document = self.document_gateway.get_by_unique_identifier(
                document.unique_identifier
            )

            if existing_document:
                logger.info(
                    f"Document already exists with unique_id: {document.unique_identifier}"
                )
                return DTOPdfProcessingResponse(
                    success=True,
                    document_id=str(existing_document.id),
                    unique_identifier=document.unique_identifier,
                    already_exists=True,
                    transactions_count=len(document.data),
                    message="Document already exists",
                )

            # Set user_id and document_type_id on the entity
            document.user_id = user.id
            document.document_type_id = doc_type.id

            # Create document via gateway
            created_document = self.document_gateway.create(document)

            logger.info(f"Created new document with ID: {created_document.id}")

            # Return DTO for controller
            return DTOPdfProcessingResponse(
                success=True,
                document_id=str(created_document.id),
                unique_identifier=document.unique_identifier,
                already_exists=False,
                transactions_count=len(document.data),
                message=f"PDF processed successfully. {len(document.data)} transactions saved.",
            )

        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise

    def _validate_document_type(self, document_type: str) -> None:
        """
        Validate that the document type is supported (business rule)

        Args:
            document_type: Type of document to validate

        Raises:
            UnsupportedDocumentTypeException: If document type is not supported
        """
        # Get all document types from database
        all_doc_types = self.document_type_gateway.get_all()
        supported_types = [dt.name for dt in all_doc_types]

        # Validate against database types
        if document_type not in supported_types:
            raise UnsupportedDocumentTypeException(
                document_type=document_type, supported_types=supported_types
            )

    def _get_or_create_user(self, user_email: str):
        """
        Get existing user entity or create new one

        Args:
            user_email: Email of the user

        Returns:
            UserEntity
        """
        user = self.user_gateway.get_by_email(user_email)
        if not user:
            from models import UserCreate, CustomerType

            user_create = UserCreate(
                email=user_email,
                name="Admin User",
                customer_type=CustomerType.INDIVIDUAL,
            )
            user = self.user_gateway.create(user_create)
            logger.info(f"Created new user with email: {user_email}")

        return user
