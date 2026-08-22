from src.Capplication.DTO.transaction_dto import (
    DTOReadTransactionsResponse,
    DTOTransaction,
)
from src.Capplication.gateway.db import ITransactionDbGateway
from src.Denterprise.entities import TransactionType


class ReadAccountTransactionsUseCase:
    def __init__(self, transaction_gateway: ITransactionDbGateway):
        self.transaction_gateway = transaction_gateway

    def execute(
        self, account_id: str, transaction_type: TransactionType | None = None
    ) -> DTOReadTransactionsResponse:
        """Read all transactions for a specific account, optionally filtered by type."""
        entities = self.transaction_gateway.get_by_account_id(
            account_id, transaction_type=transaction_type
        )
        return DTOReadTransactionsResponse(
            transactions=[DTOTransaction.model_validate(e) for e in entities]
        )
