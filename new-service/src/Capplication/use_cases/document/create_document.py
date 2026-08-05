"""
Process PDF Use Case - Application Layer
Orchestrates the flow of processing a PDF and creating a document
"""

import logging
import os
from pathlib import Path

import fitz
from dotenv import load_dotenv

from src.Denterprise.entities import DocumentEntity, UserEntity
from src.Capplication.DTO.document_dto import (
    DTOCreateDocumentResponse,
    DTOCreateDocumentRequest,
)
from src.Capplication.gateway.db import IDocumentDbGateway, IUserDbGateway
from src.Capplication.gateway.content_extractor import IStatementParser
from src.Capplication.gateway.file_extractor import IFileExtractorGateway
from src.Aframework.gateway.db.document_type import IDocumentTypeDbGateway

load_dotenv()

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
    ):
        self.document_gateway = document_gateway
        self.user_gateway = user_gateway
        self.document_type_gateway = document_type_gateway
        self.file_extractor_gateway = file_extractor_gateway
        self.parser_gateway = parser_gateway

    def execute(self, request: DTOCreateDocumentRequest) -> DTOCreateDocumentResponse:
        """
        Process PDF file: get/create user, extract transactions, and create document

        Args:
            request: DTOCreateDocumentRequest containing:
                - pdf_filepath: Path to the PDF file
                - user_email: Email of the user
                - document_type: Type of document

        Returns:
            DTOCreateDocumentRequest (DTO for controller response)

        Raises:
            ValueError: If validation fails
            FileNotFoundError: If PDF file not found
        """

        pdf_filepath = request.pdf_filepath
        user_email = request.user_email
        document_type = Path(pdf_filepath).parent.name

        try:
            # Check if file exists using file system gateway
            if not self.file_extractor_gateway.file_exists(pdf_filepath):
                raise FileNotFoundError(f"File '{pdf_filepath}' not found")

            # Get document type entity from database
            doc_type = self.document_type_gateway.get_by_name(document_type)

            if not doc_type:
                raise ValueError(
                    f"Document type '{document_type}' not found in database"
                )

            # extract text from PDF file using file system gateway
            pdf_binary = self.file_extractor_gateway.read_binary_file(pdf_filepath)

            password = os.getenv("PDF_PASSWORD")
            full_text = self._extract_text_from_binary(pdf_binary, password)

            document = DocumentEntity(
                account=self.parser_gateway.get_account(full_text),
                balance=self.parser_gateway.get_balance(full_text),
                data=self.parser_gateway.get_data(full_text),
                start_date=self.parser_gateway.get_initial_day(full_text),
                end_date=self.parser_gateway.get_final_day(full_text),
                processed=False,
                plain_text=full_text,
                document_type_name=doc_type.name,
            )

            # Get user entity
            user = self.user_gateway.get_by_email(user_email)
            if not user:
                raise ValueError(f"User with email '{user_email}' not found. Please create the user first.")

            # Set user_id and document_type_id on the entity
            document.user_id = user.id
            document.document_type_id = doc_type.id

            # Create document via gateway
            result_document, created = self.document_gateway.get_or_create(document)

            if not created:
                logger.info(f"Document already exists with ID: {result_document.id}")
                return DTOCreateDocumentResponse(
                    success=True,
                    document_id=str(result_document.id),
                    already_exists=True,
                    transactions_count=len(document.data),
                    document_processed=result_document.processed,
                )

            logger.info(f"Created new document with ID: {result_document.id}")

            return DTOCreateDocumentResponse(
                success=True,
                document_id=str(result_document.id),
                already_exists=False,
                transactions_count=len(document.data),
                document_processed=result_document.processed,
            )

        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise

    # TODO I need to clarify if this works only with pdf. I will start working with csv and plain .txt files
    def _extract_text_from_binary(
        self, pdf_content: bytes, password: str = None
    ) -> str:
        """Extract text from PDF using PyMuPDF"""
        logger.info("Extracting text from PDF")

        try:
            text = ""
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")

            if pdf_document.is_encrypted:
                if password:
                    if pdf_document.authenticate(password):
                        logger.info("PDF decrypted successfully")
                    else:
                        raise ValueError("Incorrect password for PDF")
                else:
                    raise ValueError("PDF is encrypted but no password provided")

            logger.info(f"PDF has {pdf_document.page_count} pages")

            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                page_text = page.get_text()
                if page_text:
                    text += f"\n\n--- PAGE {page_num + 1} ---\n\n{page_text}\n"

            pdf_document.close()
            return text
        except Exception as e:
            logger.error(f"Error with PyMuPDF: {str(e)}")
            raise
