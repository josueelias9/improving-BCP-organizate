"""
Load Transactions Use Case - Application Layer
Orchestrates the flow of loading transactions from a document
"""

import logging
from datetime import date
from typing import List
from src.Denterprise.entities import DocumentEntity, TransactionEntity
from src.Capplication.DTO.transaction_dto import (
    DTOCreateTransactionsResponse,
    DTOCreateTransactionsRequest,
)
from src.Capplication.gateway.db import IDocumentDbGateway, ITransactionDbGateway

logger = logging.getLogger(__name__)


class CreateTransactionsUseCase:
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
        self.transaction_gateway = (
            transaction_gateway  # TODO: should be transaction_db_gateway
        )

    def execute(
        self, request: DTOCreateTransactionsRequest
    ) -> DTOCreateTransactionsResponse:
        """
        Execute the use case: load transactions from document

        Args:
            document_id: UUID of the document to process

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

            # 3. Transform data to transaction entities (business logic)
            transaction_entities = self.transform_document_data_to_transactions(
                document
            )

            # 4. Persist transactions (via gateway)
            loaded_count, skipped_count, errors = self.transaction_gateway.save_batch(
                transaction_entities, document_id
            )

            # 5. Mark document as processed (via gateway)
            self.document_gateway.mark_as_processed(document_id)

            # 6. Return result DTO (for controller)
            return DTOCreateTransactionsResponse(
                success=True,
                loaded_count=loaded_count,
                skipped_count=skipped_count,
                errors=errors,
                total_records=len(document.data),
                document_id=str(document_id),
            )
        except Exception as e:
            logger.error(f"Error loading transactions from document: {str(e)}")
            # Return error DTO instead of raising exception
            return DTOCreateTransactionsResponse(
                success=False,
                loaded_count=0,
                skipped_count=0,
                errors=[str(e)],
                total_records=0,
                document_id=str(request.document_id),
            )

    def transform_document_data_to_transactions(
        self,
        document: DocumentEntity,
    ) -> List[TransactionEntity]:
        """
        Transform document data into transaction entities

        Args:
            document: Document entity containing transaction data

        Returns:
            List of TransactionEntity objects
        """
        transactions = []

        # Extract currency from document data
        # TODO: Analyize if this is feasible, because it works with debit documents but not with credit ones, where there are multiple currencies.
        # if that is the case, maybe we will need to have CreateTransactionsUseCase per document type.
        # one workaround could be to have a fixed dict structure for all document_types.
        currency = document.data.get("currency", "")

        for idx, transaction_dict in enumerate(document.data["transactions"]):
            try:
                # Parse date strings from JSON back to date objects
                fecha_valor = transaction_dict.get("fecha_valor")
                if fecha_valor and isinstance(fecha_valor, str):
                    fecha_valor = date.fromisoformat(fecha_valor)

                # Determine type and amount based on cargos/abonos
                cargos = float(transaction_dict.get("cargos", 0.0))
                abonos = float(transaction_dict.get("abonos", 0.0))

                if cargos == 0.0:
                    transaction_type = "income"
                    amount = abonos
                else:
                    transaction_type = "expense"
                    amount = cargos

                transaction = TransactionEntity(
                    order=idx + 1,
                    description=transaction_dict.get("description", ""),
                    history=transaction_dict.get("history"),
                    amount=amount,
                    transaction_type=transaction_type,
                    transaction_date=fecha_valor,
                    currency=currency,
                    unique_identifier=None,  # Will be set by gateway
                )
                transactions.append(transaction)

            except Exception as e:
                logger.error(f"Error transforming transaction at index {idx}: {str(e)}")
                raise ValueError(f"Invalid transaction data at index {idx}: {str(e)}")

        return transactions

    def validate_document_for_processing(self, document: DocumentEntity) -> None:
        """
        Validate that a document can be processed

        Args:
            document: Document entity to validate

        Raises:
            ValueError: If document is invalid or already processed
        """
        if document.processed:
            raise ValueError(
                "Document has already been processed. Transactions already loaded."
            )

        if not document.data or len(document.data["transactions"]) == 0:
            raise ValueError("Document has no transaction data to load")
