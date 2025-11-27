"""
Load Transactions Use Case - Application Layer
Orchestrates the flow of loading transactions from a document
"""
import logging
import uuid

from src.Denterprise.transaction_service import TransactionService, LoadTransactionsResult
from src.Denterprise.repositories import IDocumentRepository, ITransactionRepository

logger = logging.getLogger(__name__)


class LoadTransactionsUseCase:
    """Use case for loading transactions from document data into transaction table"""
    
    def __init__(
        self,
        document_repo: IDocumentRepository,
        transaction_repo: ITransactionRepository
    ):
        """
        Initialize use case with repository dependencies
        
        Args:
            document_repo: Document repository interface
            transaction_repo: Transaction repository interface
        """
        self.document_repo = document_repo
        self.transaction_repo = transaction_repo
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
        # 1. Retrieve document (via repository interface)
        document_data = self.document_repo.get_by_id(document_id)
        
        # 2. Validate document (business logic)
        self.service.validate_document_for_processing(document_data)
        
        # 3. Transform data to transactions (business logic)
        transaction_data_list = self.service.transform_document_data_to_transactions(document_data)
        
        # 4. Persist transactions (via repository interface)
        loaded_count, skipped_count, errors = self.transaction_repo.save_batch(
            transaction_data_list,
            uuid.UUID(document_data.id)
        )
        
        # 5. Mark document as processed (via repository interface)
        self.document_repo.mark_as_processed(uuid.UUID(document_data.id))
        
        # 6. Return result
        return LoadTransactionsResult(
            success=True,
            loaded_count=loaded_count,
            skipped_count=skipped_count,
            errors=errors,
            total_records=len(document_data.data)
        )
