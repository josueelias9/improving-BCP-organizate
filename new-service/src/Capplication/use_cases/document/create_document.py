"""
Process document Use Case - Application Layer
Orchestrates the flow of processing a file and creating a document
"""

import logging
from pathlib import Path

from src.Denterprise.entities import (
    DocumentEntity,
    HistoryEntity,
)
from src.Capplication.DTO.document_dto import (
    DTOCreateDocumentResponse,
    DTOCreateDocumentRequest,
)
from src.Capplication.gateway.db import (
    IDocumentDbGateway,
    IUserDbGateway,
    IAccountDbGateway,
    IHistoryDbGateway,
)
from src.Capplication.gateway.content_extractor import IStatementParser
from src.Capplication.gateway.file_extractor import IFileExtractorGateway
from src.Aframework.gateway.db.document_format import IDocumentTypeDbGateway

logger = logging.getLogger(__name__)


class CreateDocumentUseCase:
    """Use case for processing PDF and creating document"""

    def __init__(
        self,
        document_gateway: IDocumentDbGateway,
        user_gateway: IUserDbGateway,
        document_type_gateway: IDocumentTypeDbGateway,
        file_extractor_gateway: IFileExtractorGateway,
        parser_gateway: IStatementParser,
        account_gateway: IAccountDbGateway,
        history_gateway: IHistoryDbGateway,
    ):
        self.document_gateway = document_gateway
        self.user_gateway = user_gateway
        self.document_type_gateway = document_type_gateway
        self.file_extractor_gateway = file_extractor_gateway
        self.parser_gateway = parser_gateway
        self.account_gateway = account_gateway
        self.history_gateway = history_gateway

    def execute(self, request: DTOCreateDocumentRequest) -> DTOCreateDocumentResponse:
        """
        Process PDF file: get/create user, extract transactions, and create document

        Args:
            request: DTOCreateDocumentRequest containing:
                - pdf_filepath: Path to the PDF file
                - user_email: Email of the user
                - document_format: Type of document

        Returns:
            DTOCreateDocumentRequest (DTO for controller response)

        Raises:
            ValueError: If validation fails
            FileNotFoundError: If PDF file not found
        """

        pdf_filepath = request.pdf_filepath
        user_email = request.user_email
        document_format = Path(pdf_filepath).parent.name

        try:
            # Check if file exists using file system gateway
            if not self.file_extractor_gateway.file_exists(pdf_filepath):
                raise FileNotFoundError(f"File '{pdf_filepath}' not found")

            # Get document type entity from database
            doc_type = self.document_type_gateway.get_by_name(document_format)

            if not doc_type:
                raise ValueError(
                    f"Document type '{document_format}' not found in database"
                )

            # Read and extract text using the parser (format-specific)
            file_binary = self.file_extractor_gateway.read_binary_file(pdf_filepath)
            full_text = self.parser_gateway.read_file(file_binary)

            initial_day = self.parser_gateway.get_initial_day(full_text)

            document = DocumentEntity(
                account_id=self.parser_gateway.get_account(full_text),
                processed=False,
                plain_text=full_text,
                document_format_name=doc_type.name,
            )

            # Get user entity
            user = self.user_gateway.get_by_email(user_email)
            if not user:
                raise ValueError(
                    f"User with email '{user_email}' not found. Please create the user first."
                )

            # Set user_id and document_type_id on the entity
            document.user_id = user.id
            document.document_type_id = doc_type.id

            # Ensure Account exists (get or create)
            if document.account_id:
                self.account_gateway.get_or_create(document.account_id)

            # Create document via gateway
            result_document, created = self.document_gateway.get_or_create(document)

            # TODO: It means that if the document already exists, no history will be recorded? This is a bug
            if not created:
                logger.info(f"Document already exists with ID: {result_document.id}")
                return DTOCreateDocumentResponse(
                    success=True,
                    document_id=str(result_document.id),
                    already_exists=True,
                    transactions_count=0,
                    document_processed=result_document.processed,
                )

            logger.info(f"Created new document with ID: {result_document.id}")

            # Record balance snapshot only once per new document
            if document.account_id:
                balance = self.parser_gateway.get_balance(full_text)
                if balance is not None:
                    self.history_gateway.create(
                        HistoryEntity(
                            account_id=document.account_id,
                            balance=balance,
                            registration_date=initial_day,
                        )
                    )

            return DTOCreateDocumentResponse(
                success=True,
                document_id=str(result_document.id),
                already_exists=False,
                transactions_count=0,
                document_processed=result_document.processed,
            )

        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            raise
