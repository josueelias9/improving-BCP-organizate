import uuid
from typing import Optional

from src.Capplication.DTO.transaction_dto import DTOGetTransactionsResponse
from src.Capplication.gateway.db import ITransactionDbGateway


class GetTransactionsUseCase:

    def __init__(
        self,
        transaction_gateway: ITransactionDbGateway,
    ):
        self.transaction_gateway = transaction_gateway

    def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        document_id: Optional[uuid.UUID] = None,
    ) -> DTOGetTransactionsResponse:
        """Get transactions with pagination and optional document filter

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            document_id: Optional document UUID to filter transactions

        Returns:
            DTOGetTransactionsResponse with transactions including category_name
        """
        if limit > 1000:
            limit = 1000

        entities = self.transaction_gateway.get_all(
            skip=skip, limit=limit, document_id=document_id
        )

        return DTOGetTransactionsResponse(transactions=entities)
