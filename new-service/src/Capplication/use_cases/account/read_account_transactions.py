from typing import Optional

from src.Capplication.DTO.transaction_dto import (
    DTOReadTransactionsResponse,
    DTOTransaction,
)
from src.Capplication.gateway.db import ITransactionDbGateway


class ReadAccountTransactionsUseCase:
    def __init__(self, transaction_gateway: ITransactionDbGateway):
        self.transaction_gateway = transaction_gateway

    def execute(
        self,
        account_id: Optional[str] = None,
    ) -> DTOReadTransactionsResponse:
        """Read all transactions for an account."""
        entities = self.transaction_gateway.get_all(account_id=account_id)
        return DTOReadTransactionsResponse(
            transactions=[DTOTransaction.model_validate(e) for e in entities]
        )
