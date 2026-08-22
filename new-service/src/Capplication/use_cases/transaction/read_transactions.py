from src.Capplication.DTO.transaction_dto import (
    DTOReadTransactionsResponse,
    DTOTransaction,
)
from src.Capplication.gateway.db import ITransactionDbGateway


class ReadTransactionsUseCase:

    def __init__(
        self,
        transaction_gateway: ITransactionDbGateway,
    ):
        self.transaction_gateway = transaction_gateway

    def execute(self) -> DTOReadTransactionsResponse:
        """Get all transactions without account filtering."""

        entities = self.transaction_gateway.get_all()
        # https://pydantic.dev/docs/validation/dev/concepts/models/#nested-attributes
        return DTOReadTransactionsResponse(
            transactions=[DTOTransaction.model_validate(e) for e in entities]
        )
