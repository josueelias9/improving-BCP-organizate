import logging

from src.Capplication.DTO.account_dto import (
    DTOCreateAccountTransactionsRequest,
    DTOCreateAccountTransactionsResponse,
)
from src.Capplication.gateway.db import IDocumentDbGateway, ITransactionDbGateway
from src.Capplication.gateway.content_extractor import IStatementParser

logger = logging.getLogger(__name__)


class CreateAccountTransactionsUseCase:
    """Given an account, parse all its unprocessed documents and load their transactions."""

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
        self, request: DTOCreateAccountTransactionsRequest
    ) -> DTOCreateAccountTransactionsResponse:
        account_id = request.account_id
        total_loaded = 0
        total_skipped = 0
        total_records = 0
        documents_processed = 0
        all_errors = []

        try:
            documents = self.document_gateway.get_by_account_id(account_id)

            if not documents:
                raise ValueError(f"No documents found for account '{account_id}'")

            for document in documents:
                if document.processed:
                    logger.info(f"Document {document.id} already processed, skipping")
                    continue

                if not document.plain_text:
                    all_errors.append(
                        f"Document {document.id} has no plain text, skipping"
                    )
                    continue

                parser = self.parsers.get(document.document_format_name)
                if parser is None:
                    all_errors.append(
                        f"No parser for format '{document.document_format_name}' (document {document.id})"
                    )
                    continue

                transaction_entities = parser.get_transactions(document.plain_text)
                total_records += len(transaction_entities)

                loaded, skipped, errors = self.transaction_gateway.save_batch(
                    transaction_entities, account_id
                )
                total_loaded += loaded
                total_skipped += skipped
                all_errors.extend(errors)

                self.document_gateway.mark_as_processed(document.id)
                documents_processed += 1

            return DTOCreateAccountTransactionsResponse(
                success=True,
                loaded_count=total_loaded,
                skipped_count=total_skipped,
                errors=all_errors,
                total_records=total_records,
                documents_processed=documents_processed,
                account_id=account_id,
            )

        except Exception as e:
            logger.error(
                f"Error loading transactions for account {account_id}: {str(e)}"
            )
            return DTOCreateAccountTransactionsResponse(
                success=False,
                loaded_count=total_loaded,
                skipped_count=total_skipped,
                errors=all_errors + [str(e)],
                total_records=total_records,
                documents_processed=documents_processed,
                account_id=account_id,
            )
