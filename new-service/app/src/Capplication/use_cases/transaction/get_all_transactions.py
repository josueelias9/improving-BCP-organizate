from src.Capplication.DTO.transaction_dto import DTOGetAllTransactionsResponse
from src.Capplication.gateway.db import (
    ITransactionDbGateway,
    ICategoryDbGateway,
    IDocumentDbGateway,
    IDocumentTypeDbGateway,
)


class GetAllTransactionsUseCase:

    def __init__(
        self,
        transaction_gateway: ITransactionDbGateway,
        category_gateway: ICategoryDbGateway,
        document_gateway: IDocumentDbGateway,
        document_type_gateway: IDocumentTypeDbGateway,
    ):
        self.transaction_gateway = transaction_gateway
        self.category_gateway = category_gateway
        self.document_gateway = document_gateway
        self.document_type_gateway = document_type_gateway

    def execute(self, skip: int = 0, limit: int = 100) -> DTOGetAllTransactionsResponse:
        """Get all transactions with pagination

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            DTOGetAllTransactionsResponse with transactions including category_name
        """
        # Validate limit
        if limit > 1000:
            limit = 1000

        # Get transactions via gateway
        entities = self.transaction_gateway.get_all(skip=skip, limit=limit)

        return DTOGetAllTransactionsResponse(transactions=entities)
