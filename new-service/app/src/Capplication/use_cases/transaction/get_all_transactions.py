from src.Capplication.DTO.transaction_dto import DTOGetAllTransactionsResponse
from src.Capplication.gateway.db import ITransactionDbGateway, ICategoryDbGateway


class GetAllTransactionsUseCase:

    def __init__(
        self,
        transaction_gateway: ITransactionDbGateway,
        category_gateway: ICategoryDbGateway,
    ):
        self.transaction_gateway = transaction_gateway
        self.category_gateway = category_gateway

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

        # Get all categories to build a map of category_id to category_name
        all_categories = self.category_gateway.get_all()
        categories_map = {cat.id: cat.name for cat in all_categories}

        # Map to dicts, adding category_name from categories_map
        transaction_dicts = []
        for entity in entities:
            # Get category name from the map
            category_name = (
                categories_map.get(entity.category_id) if entity.category_id else None
            )

            transaction_dict = {
                "id": str(entity.id),
                "order": entity.order,
                "description": entity.description,
                "history": entity.history,
                "amount": entity.amount,
                "transaction_type": entity.transaction_type,
                "transaction_date": (
                    entity.transaction_date.isoformat()
                    if entity.transaction_date
                    else None
                ),
                "unique_identifier": entity.unique_identifier,
                "category_id": str(entity.category_id) if entity.category_id else None,
                "category_name": category_name,
            }
            transaction_dicts.append(transaction_dict)

        return DTOGetAllTransactionsResponse(transactions=transaction_dicts)
