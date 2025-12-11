"""
Process PDF Use Case - Application Layer
Orchestrates the flow of processing a PDF and creating a document
"""

import logging
from typing import Dict, Any, List, Tuple

from src.Denterprise.entities import DocumentEntity, ExtractionResultEntity
from src.Denterprise.exceptions import UnsupportedDocumentTypeException
from src.Capplication.DTO.document_dto import DTOPdfProcessingResponse, DTOPdfProcessingRequest
from src.Capplication.gateway.db import IDocumentDbGateway, IUserDbGateway
from src.Capplication.gateway.pdf_extractor import PDFExtractorGateway
from src.Aframework.gateway.db.document_type import DocumentTypeDbGateway

logger = logging.getLogger(__name__)


class PDFProcessingUseCase:
    """Use case for processing PDF and creating document"""

    def __init__(
        self,
        document_gateway: IDocumentDbGateway,
        user_gateway: IUserDbGateway,
        pdf_extractor_gateway: PDFExtractorGateway,
        document_type_gateway: DocumentTypeDbGateway,
    ):
        self.document_gateway = document_gateway
        self.user_gateway = user_gateway
        self.pdf_extractor_gateway = pdf_extractor_gateway
        self.document_type_gateway = document_type_gateway


    def execute(self, request: DTOPdfProcessingRequest) -> DTOPdfProcessingResponse:
        """
        Process PDF file: get/create user, extract transactions, and create document

        Args:
            pdf_file: Binary PDF file content
            user_email: Email of the user
            document_type: Type of document (default: BCP_STATEMENT)
            pdf_filename: Optional filename for logging purposes only

        Returns:
            DTOPdfProcessingResponse (DTO for controller response)

        Raises:
            ValueError: If validation fails
            UnsupportedDocumentTypeException: If document type is not supported
        """

        pdf_file = request.pdf_file
        pdf_filename = request.pdf_filename
        user_email = request.user_email
        document_type = request.document_type
        try:
            # Validate document type (business rule)
            self._validate_document_type(document_type)

            # Get or create user entity
            user = self._get_or_create_user(user_email)

            # Extract transactions from PDF (returns entity)
            extraction_result = self.pdf_extractor_gateway.extract_transactions(
                pdf_file, pdf_filename
            )

            # Validate and process extraction result
            unique_id, transactions_list = self._process_extraction_result(
                extraction_result
            )

            # Check if document already exists with this unique_identifier
            existing_document = self.document_gateway.get_by_unique_identifier(
                unique_id
            )

            if existing_document:
                logger.info(f"Document already exists with unique_id: {unique_id}")
                return DTOPdfProcessingResponse(
                    success=True,
                    document_id=str(existing_document.id),
                    unique_identifier=unique_id,
                    already_exists=True,
                    transactions_count=len(transactions_list),
                    message="Document already exists",
                )

            # Create new document
            # Get document type by name
            doc_type_name_map = {
                "BCP_STATEMENT": "bcp_debit",
                "DEBIT_STATEMENT": "bcp_debit",
                "CREDIT_STATEMENT": "bcp_credit",
            }

            doc_type_name = doc_type_name_map.get(document_type, "bcp_debit")
            doc_type = self.document_type_gateway.get_by_name(doc_type_name)

            if not doc_type:
                raise ValueError(
                    f"Document type '{doc_type_name}' not found in database"
                )

            # Structure data as nested JSON
            document_data = {
                "account_number": extraction_result.account_code or "UNKNOWN",
                "previous_balance": extraction_result.saldo_anterior,
                "initial_day": (
                    extraction_result.initial_day.isoformat()
                    if extraction_result.initial_day
                    else None
                ),
                "final_day": (
                    extraction_result.final_day.isoformat()
                    if extraction_result.final_day
                    else None
                ),
                "transactions": transactions_list,
            }

            # Create document entity
            document = DocumentEntity(
                data=document_data,
                currency=extraction_result.currency or "PEN",
                unique_identifier=unique_id,
                user_id=user.id,
                document_type_id=doc_type.id,
            )

            # Create document via gateway
            created_document = self.document_gateway.create(document)

            logger.info(f"Created new document with ID: {created_document.id}")

            # Return DTO for controller
            return DTOPdfProcessingResponse(
                success=True,
                document_id=str(created_document.id),
                unique_identifier=unique_id,
                already_exists=False,
                transactions_count=len(transactions_list),
                message=f"PDF processed successfully. {len(transactions_list)} transactions saved.",
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
        supported_types = ["BCP_STATEMENT", "DEBIT_STATEMENT"]

        # For now, only debit statements are fully implemented
        if document_type not in supported_types:
            raise UnsupportedDocumentTypeException(
                document_type=document_type, supported_types=supported_types
            )

        # Credit card processing not implemented yet
        if document_type == "CREDIT_STATEMENT":
            raise UnsupportedDocumentTypeException(
                document_type="credit", supported_types=["debit"]
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

    @staticmethod
    def _process_extraction_result(
        extraction_result: ExtractionResultEntity,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Process extraction result entity and generate unique identifier and transactions list

        Args:
            extraction_result: The entity from PDF extraction

        Returns:
            Tuple of (unique_id, transactions_list)

        Raises:
            ValueError: If extraction result is invalid
        """
        if not extraction_result.success:
            raise ValueError(
                f"Extraction failed: {extraction_result.error_message or 'Unknown error'}"
            )

        # Validate required fields
        if not extraction_result.initial_day:
            raise ValueError("Missing initial_day in extraction result")

        if not extraction_result.final_day:
            raise ValueError("Missing final_day in extraction result")

        if not extraction_result.account_code:
            raise ValueError("Missing account_code in extraction result")

        if not extraction_result.currency:
            raise ValueError("Missing currency in extraction result")

        # Convert transaction entities to dict list with date serialization
        transactions_list = []
        for t in extraction_result.transactions:
            # Get transaction type and amount based on cargos/abonos
            transaction_type, amount = t.to_transaction_type_and_amount()

            # Convert to dict with new structure
            t_dict = {
                "description": t.description,
                "cargos": t.cargos,  # Keep original for reference
                "abonos": t.abonos,  # Keep original for reference
                "fecha_valor": t.fecha_valor.isoformat() if t.fecha_valor else None,
                "transaction_type": transaction_type,
                "amount": amount,
            }
            transactions_list.append(t_dict)

        # Generate unique identifier with date strings
        initial_day_str = extraction_result.initial_day.isoformat()
        final_day_str = extraction_result.final_day.isoformat()
        unique_id = f"{initial_day_str}__{final_day_str}__{extraction_result.account_code}__{extraction_result.currency}"

        logger.info(
            f"Processed extraction result: {len(transactions_list)} transactions, unique_id: {unique_id}"
        )

        return unique_id, transactions_list
