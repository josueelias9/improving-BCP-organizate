"""
Load Transactions Use Case - Application Layer
Orchestrates the flow of loading transactions from a document
"""
import logging
import uuid

from src.Denterprise.transaction_service import TransactionService
from src.Capplication.DTO import LoadTransactionsResult
from src.Capplication.interfaces.db import IDocumentDbGateway, ITransactionDbGateway

logger = logging.getLogger(__name__)


class LoadTransactionsFromDocumentUseCase:
    """Use case for loading transactions from document data into transaction table"""
    
    def __init__(
        self,
        document_gateway: IDocumentDbGateway,
        transaction_gateway: ITransactionDbGateway
    ):
        """
        Initialize use case with gateway dependencies
        
        Args:
            document_gateway: Document gateway interface
            transaction_gateway: Transaction gateway interface
        """
        self.document_gateway = document_gateway
        self.transaction_gateway = transaction_gateway
        self.service = TransactionService()
    
    def execute(self, document_id: uuid.UUID) -> LoadTransactionsResult:
        """
        Execute the use case: load transactions from document
        
        Args:
            document_id: UUID of the document to process
            
        Returns:
            LoadTransactionsResult with operation summary
            
        Raises:
            ValueError: If document not found or validation fails
        """
        # 1. Retrieve document (via gateway interface)
        document_data = self.document_gateway.get_by_id(document_id)
        
        # 2. Validate document (business logic)
        self.service.validate_document_for_processing(document_data)
        
        # 3. Transform data to transactions (business logic)
        transaction_data_list = self.service.transform_document_data_to_transactions(document_data)
        
        # 4. Persist transactions (via gateway interface)
        loaded_count, skipped_count, errors = self.transaction_gateway.save_batch(
            transaction_data_list,
            uuid.UUID(document_data.id)
        )
        
        # 5. Mark document as processed (via gateway interface)
        self.document_gateway.mark_as_processed(uuid.UUID(document_data.id))
        
        # 6. Return result
        return LoadTransactionsResult(
            success=True,
            loaded_count=loaded_count,
            skipped_count=skipped_count,
            errors=errors,
            total_records=len(document_data.data)
        )
