from src.Capplication.DTO.account_dto import (
    DTOCreateAccountHistoriesResponse,
    DTOCreateAccountHistoryResponse,
)
from src.Capplication.gateway.content_extractor import IStatementParser
from src.Capplication.gateway.db import (
    IAccountDbGateway,
    IDocumentDbGateway,
    IHistoryDbGateway,
)
from src.Denterprise.entities import HistoryEntity


class CreateAccountHistoryUseCase:
    def __init__(
        self,
        account_gateway: IAccountDbGateway,
        history_gateway: IHistoryDbGateway,
        document_gateway: IDocumentDbGateway,
        parsers: dict[str, IStatementParser],
    ):
        self.account_gateway = account_gateway
        self.history_gateway = history_gateway
        self.document_gateway = document_gateway
        self.parsers = parsers

    def execute(self, account_id: str) -> DTOCreateAccountHistoriesResponse:
        # The account must already exist. We do not create it here because the
        # account lifecycle is a separate concern from the balance snapshot flow.
        if self.account_gateway.get_by_id(account_id) is None:
            raise ValueError(f"Account '{account_id}' does not exist")

        # We only want to generate histories from the documents that belong to
        # this account. If there are no documents, there is nothing to derive.
        documents = self.document_gateway.get_by_account_id(account_id)

        if not documents:
            raise ValueError(f"No documents found for account '{account_id}'")

        histories: list[DTOCreateAccountHistoryResponse] = []

        # For each document, extract the balance and its registration date from
        # the file content. A history is understood as a snapshot of the account
        # at a specific date and amount.
        for document in documents:
            if not document.plain_text:
                continue

            parser = self.parsers.get(document.document_format_name)
            if parser is None:
                continue

            balance = parser.get_balance(document.plain_text)
            if balance is None:
                continue

            registration_date = parser.get_initial_day(document.plain_text)
            if registration_date is None:
                continue

            # This validation belongs to the infrastructure layer so duplicate
            # entries are detected at the persistence boundary using the same
            # identifier tuple: account + balance + date.
            if self.history_gateway.exists(account_id, balance, registration_date):
                continue

            history = HistoryEntity(
                account_id=account_id,
                balance=balance,
                registration_date=registration_date,
            )
            created_history = self.history_gateway.create(history)
            histories.append(
                DTOCreateAccountHistoryResponse(
                    id=created_history.id,
                    account_id=created_history.account_id,
                    balance=created_history.balance,
                    registration_date=created_history.registration_date,
                )
            )

        # If no valid snapshot could be created, the operation is considered
        # unsuccessful and the caller receives a clear business error.
        # TODO: when all the histories are duplicates, should we return an empty list or raise an error? The current behavior is to raise an error. FIX
        if not histories:
            raise ValueError(
                f"No history could be generated from the documents of account '{account_id}'"
            )

        return DTOCreateAccountHistoriesResponse(
            histories=histories,
            total_count=len(histories),
        )
