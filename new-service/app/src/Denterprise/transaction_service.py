"""
Transaction Service - Business Logic Layer
Contains core business rules and validations for transaction processing
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TransactionData:
    """Data structure for transaction information"""
    description: str
    cargos: float
    abonos: float
    currency: str
    fecha_proceso: Optional[str]
    fecha_consumo: Optional[str]
    internal_transaction: bool
    type: Optional[str]
    order: int


@dataclass
class DocumentData:
    """Data structure for document information"""
    id: str
    data: List[Dict[str, Any]]
    currency: str
    processed: bool


@dataclass
class LoadTransactionsResult:
    """Result of loading transactions operation"""
    success: bool
    loaded_count: int
    skipped_count: int
    errors: List[str]
    total_records: int


class TransactionService:
    """Service containing business logic for transaction operations"""
    
    @staticmethod
    def validate_document_for_processing(document_data: DocumentData) -> None:
        """
        Validate that a document can be processed
        
        Args:
            document_data: Document information to validate
            
        Raises:
            ValueError: If document is invalid or already processed
        """
        if document_data.processed:
            raise ValueError("Document has already been processed. Transactions already loaded.")
        
        if not document_data.data or len(document_data.data) == 0:
            raise ValueError("Document has no transaction data to load")
    
    @staticmethod
    def transform_document_data_to_transactions(
        document_data: DocumentData
    ) -> List[TransactionData]:
        """
        Transform document data into transaction entities
        
        Args:
            document_data: Document containing transaction data
            
        Returns:
            List of TransactionData objects
        """
        transactions = []
        
        for idx, transaction_dict in enumerate(document_data.data):
            try:
                transaction = TransactionData(
                    description=transaction_dict.get("description", ""),
                    cargos=float(transaction_dict.get("cargos", 0.0)),
                    abonos=float(transaction_dict.get("abonos", 0.0)),
                    currency=document_data.currency,
                    fecha_proceso=transaction_dict.get("fecha_proceso"),
                    fecha_consumo=transaction_dict.get("fecha_consumo"),
                    internal_transaction=transaction_dict.get("internal_transaction") == "*",
                    type=transaction_dict.get("type", "unknown"),
                    order=idx + 1
                )
                transactions.append(transaction)
                
            except Exception as e:
                logger.error(f"Error transforming transaction at index {idx}: {str(e)}")
                raise ValueError(f"Invalid transaction data at index {idx}: {str(e)}")
        
        return transactions
    
    @staticmethod
    def validate_transaction_data(transaction: TransactionData) -> bool:
        """
        Validate transaction business rules
        
        Args:
            transaction: Transaction to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Business rule: description should not be empty
        if not transaction.description or not transaction.description.strip():
            logger.warning(f"Transaction with empty description at order {transaction.order}")
            return False
        
        # Business rule: at least one of cargos or abonos should be non-zero
        if transaction.cargos == 0.0 and transaction.abonos == 0.0:
            logger.warning(f"Transaction with zero amounts at order {transaction.order}")
            return False
        
        return True
