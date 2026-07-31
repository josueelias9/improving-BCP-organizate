# TODO: rename file and class and DTO

from src.Capplication.DTO.transaction_dto import DTOGetTransactionsResponse
from src.Capplication.gateway.db import (
    ITransactionDbGateway,
    ICategoryDbGateway,
    IDocumentDbGateway,
    IDocumentTypeDbGateway,
)


class GetTransactionsUseCase:

    def __init__(
        self,
        transaction_gateway: ITransactionDbGateway,
    ):
        self.transaction_gateway = transaction_gateway

    def execute(self, skip: int = 0, limit: int = 100) -> DTOGetTransactionsResponse:
        """Get all transactions with pagination

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            DTOGetTransactionsResponse with transactions including category_name
        """
        # Validate limit
        if limit > 1000:
            limit = 1000

        # Get transactions via gateway
        entities = self.transaction_gateway.get_all(skip=skip, limit=limit)

        return DTOGetTransactionsResponse(transactions=entities)
