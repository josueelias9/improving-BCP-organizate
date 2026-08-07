import uuid
from typing import Optional

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

    def execute(
        self,
        skip: int = 0,
        limit: int = 1000,
        account_id: Optional[str] = None,
    ) -> DTOReadTransactionsResponse:
        """Get transactions with pagination and optional account filter

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            account_id: Optional account ID to filter transactions

        Returns:
            DTOReadTransactionsResponse with transactions including category_name
        """
        if limit > 1000:
            limit = 1000

        entities = self.transaction_gateway.get_all(
            skip=skip, limit=limit, account_id=account_id
        )
        # https://pydantic.dev/docs/validation/dev/concepts/models/#nested-attributes
        return DTOReadTransactionsResponse(
            transactions=[DTOTransaction.model_validate(e) for e in entities]
        )
