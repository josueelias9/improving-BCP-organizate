"""
Load Transactions Use Case - Application Layer
Orchestrates the flow of loading transactions from a document
"""

import logging
from typing import List
from src.Denterprise.entities import DocumentEntity, TransactionEntity
from src.Capplication.DTO.transaction_dto import (
    DTOCreateTransactionsResponse,
    DTOCreateTransactionsRequest,
)
from src.Capplication.gateway.db import IDocumentDbGateway, ITransactionDbGateway
from src.Capplication.gateway.content_extractor import IStatementParser

logger = logging.getLogger(__name__)


class CreateTransactionsUseCase:
    """Use case for loading transactions from document plain text into the transaction table"""

    def __init__(
        self,
        document_gateway: IDocumentDbGateway,
        transaction_gateway: ITransactionDbGateway,
        parsers: dict[str, IStatementParser],
    ):
        self.document_gateway = document_gateway
        self.transaction_gateway = transaction_gateway
        self.parsers = parsers

    def execute(
        self, request: DTOCreateTransactionsRequest
    ) -> DTOCreateTransactionsResponse:
        """
        Execute the use case: parse plain text and load transactions from document.

        Args:
            request: DTO containing document_id

        Returns:
            DTOCreateTransactionsResponse (DTO for controller response)

        Raises:
            ValueError: If document not found or validation fails
        """
        try:
            document_id = request.document_id
            # 1. Retrieve document entity (from gateway)
            document = self.document_gateway.get_by_id(document_id)

            # 2. Validate document (business logic)
            self.validate_document_for_processing(document)

            # 3. Select parser based on document format and extract transaction entities
            parser = self.parsers.get(document.document_format_name)
            if parser is None:
                raise ValueError(
                    f"No parser registered for document format '{document.document_format_name}'"
                )
            transaction_entities = parser.get_transactions(document.plain_text)

            # 4. Persist transactions (via gateway)
            loaded_count, skipped_count, errors = self.transaction_gateway.save_batch(
                transaction_entities, document.account_id
            )

            # 5. Mark document as processed (via gateway)
            self.document_gateway.mark_as_processed(document_id)

            # 6. Return result DTO (for controller)
            return DTOCreateTransactionsResponse(
                success=True,
                loaded_count=loaded_count,
                skipped_count=skipped_count,
                errors=errors,
                total_records=len(transaction_entities),
                document_id=str(document_id),
            )
        except Exception as e:
            logger.error(f"Error loading transactions from document: {str(e)}")
            return DTOCreateTransactionsResponse(
                success=False,
                loaded_count=0,
                skipped_count=0,
                errors=[str(e)],
                total_records=0,
                document_id=str(request.document_id),
            )

    def validate_document_for_processing(self, document: DocumentEntity) -> None:
        """
        Validate that a document can be processed.

        Raises:
            ValueError: If document is invalid or already processed
        """
        if document.processed:
            raise ValueError(
                "Document has already been processed. Transactions already loaded."
            )

        if not document.plain_text:
            raise ValueError("Document has no plain text content to parse")
