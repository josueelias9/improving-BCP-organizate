"""
Load Transactions Use Case - Application Layer
Orchestrates the flow of loading transactions from a document
"""

import logging

from src.Denterprise.transaction_service import TransactionService
from src.Capplication.DTO.document_dto import (
    DTOLoadTransactionsFromDocumentResponse,
    DTOLoadTransactionsFromDocumentRequest,
)
from src.Capplication.gateway.db import IDocumentDbGateway, ITransactionDbGateway

logger = logging.getLogger(__name__)


class LoadTransactionsFromDocumentUseCase:
    """Use case for loading transactions from document data into transaction table"""

    def __init__(
        self,
        document_gateway: IDocumentDbGateway,
        transaction_gateway: ITransactionDbGateway,
    ):
        """
        Initialize use case with gateway dependencies

        Args:
            document_gateway: Document gateway interface
            transaction_gateway: Transaction gateway interface
        """
        self.document_gateway = document_gateway
        self.transaction_gateway = transaction_gateway
        self.service = TransactionService()

    def execute(
        self, request: DTOLoadTransactionsFromDocumentRequest
    ) -> DTOLoadTransactionsFromDocumentResponse:
        """
        Execute the use case: load transactions from document

        Args:
            document_id: UUID of the document to process

        Returns:
            DTOLoadTransactionsFromDocumentResponse (DTO for controller response)

        Raises:
            ValueError: If document not found or validation fails
        """
        document_id = request.document_id
        # 1. Retrieve document entity (from gateway)
        document = self.document_gateway.get_by_id(document_id)

        # 2. Validate document (business logic)
        self.service.validate_document_for_processing(document)

        # 3. Transform data to transaction entities (business logic)
        transaction_entities = self.service.transform_document_data_to_transactions(
            document
        )

        # 4. Persist transactions (via gateway)
        loaded_count, skipped_count, errors = self.transaction_gateway.save_batch(
            transaction_entities, document_id
        )

        # 5. Mark document as processed (via gateway)
        self.document_gateway.mark_as_processed(document_id)

        # 6. Return result DTO (for controller)
        return DTOLoadTransactionsFromDocumentResponse(
            success=True,
            loaded_count=loaded_count,
            skipped_count=skipped_count,
            errors=errors,
            total_records=len(document.data),
            document_id=str(document_id),
        )
