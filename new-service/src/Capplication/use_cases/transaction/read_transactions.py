import uuid
from typing import Optional

from src.Capplication.DTO.transaction_dto import DTOReadTransactionsResponse, DTOTransaction
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
        document_id: Optional[uuid.UUID] = None,
    ) -> DTOReadTransactionsResponse:
        """Get transactions with pagination and optional document filter

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            document_id: Optional document UUID to filter transactions

        Returns:
            DTOReadTransactionsResponse with transactions including category_name
        """
        if limit > 1000:
            limit = 1000

        entities = self.transaction_gateway.get_all(
            skip=skip, limit=limit, document_id=document_id
        )
        # https://pydantic.dev/docs/validation/dev/concepts/models/#nested-attributes
        return DTOReadTransactionsResponse(transactions=[DTOTransaction.model_validate(e) for e in entities])
