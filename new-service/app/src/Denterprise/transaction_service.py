"""
Transaction Service - Business Logic Layer
Contains core business rules and validations for transaction processing
"""
import logging
from datetime import date
from typing import List

from src.Capplication.DTO.document_dto import DTODocumentData
from src.Capplication.DTO.transaction_dto import DTOTransactionData

logger = logging.getLogger(__name__)


class TransactionService:
    """Service containing business logic for transaction operations"""
    
    @staticmethod
    def validate_document_for_processing(document_data: DTODocumentData) -> None:
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
        document_data: DTODocumentData
    ) -> List[DTOTransactionData]:
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
                # Parse date strings from JSON back to date objects
                fecha_valor = transaction_dict.get("fecha_valor")
                if fecha_valor and isinstance(fecha_valor, str):
                    fecha_valor = date.fromisoformat(fecha_valor)
                
                # Determine type and amount based on cargos/abonos
                cargos = float(transaction_dict.get("cargos", 0.0))
                abonos = float(transaction_dict.get("abonos", 0.0))
                
                if cargos == 0.0:
                    transaction_type = "income"
                    amount = abonos
                else:
                    transaction_type = "expense"
                    amount = cargos
                
                transaction = DTOTransactionData(
                    order=idx + 1,
                    description=transaction_dict.get("description", ""),
                    history=transaction_dict.get("history"),
                    amount=amount,
                    transaction_type=transaction_type,
                    transaction_date=fecha_valor,
                    unique_identifier=None  # Will be set by gateway
                )
                transactions.append(transaction)
                
            except Exception as e:
                logger.error(f"Error transforming transaction at index {idx}: {str(e)}")
                raise ValueError(f"Invalid transaction data at index {idx}: {str(e)}")
        
        return transactions
    