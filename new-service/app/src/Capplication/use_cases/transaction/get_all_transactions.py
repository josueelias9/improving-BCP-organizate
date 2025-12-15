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

        # Get all categories to build a map of category_id to category_name
        all_categories = self.category_gateway.get_all()
        categories_map = {cat.id: cat.name for cat in all_categories}

        # Get all document_ids from transactions
        document_ids = {entity.document_id for entity in entities if entity.document_id}

        # Build map of document_id to document_type_id
        documents_map = {}
        for doc_id in document_ids:
            try:
                document = self.document_gateway.get_by_id(doc_id)
                documents_map[doc_id] = document.document_type_id
            except ValueError:
                # Document not found, skip
                pass

        # Get all document types to build a map of document_type_id to name
        all_document_types = self.document_type_gateway.get_all()
        document_types_map = {dt.id: dt.name for dt in all_document_types}

        # Map to dicts, adding category_name and document_type_name from maps
        transaction_dicts = []
        for entity in entities:
            # Get category name from the map
            category_name = (
                categories_map.get(entity.category_id) if entity.category_id else None
            )

            # Get document_type_name through document_id
            document_type_name = None
            if entity.document_id and entity.document_id in documents_map:
                document_type_id = documents_map[entity.document_id]
                document_type_name = document_types_map.get(document_type_id)

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
                "document_type_name": document_type_name,
            }
            transaction_dicts.append(transaction_dict)

        return DTOGetAllTransactionsResponse(transactions=transaction_dicts)
