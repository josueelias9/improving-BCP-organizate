"""
Update Transaction Use Case - Application Layer
Handles the business logic for updating a specific transaction by ID
"""
import uuid
import logging
from typing import Dict, Any

from src.Denterprise.gateways import ITransactionGateway
from src.Denterprise.transaction_service import TransactionData

logger = logging.getLogger(__name__)


class UpdateTransactionUseCase:
    """Use case for updating a transaction by ID"""
    
    def __init__(self, transaction_gateway: ITransactionGateway):
        self.transaction_gateway = transaction_gateway
    
    def execute(self, transaction_id: uuid.UUID, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a transaction by ID
        
        Args:
            transaction_id: UUID of the transaction to update
            update_data: Dictionary containing fields to update
            
        Returns:
            Dictionary with update result
            
        Raises:
            ValueError: If transaction not found or validation fails
        """
        try:
            # Get existing transaction
            existing_transaction = self.transaction_gateway.get_by_id(transaction_id)
            
            if not existing_transaction:
                raise ValueError(f"Transaction with ID {transaction_id} not found")
            
            # Validate and prepare updated transaction data
            updated_transaction = self._prepare_updated_transaction(
                existing_transaction, 
                update_data
            )
            
            # Validate business rules
            self._validate_transaction_data(updated_transaction)
            
            # Update transaction
            success = self.transaction_gateway.update(transaction_id, updated_transaction)
            
            if not success:
                raise ValueError("Failed to update transaction")
            
            return {
                "transaction_id": str(transaction_id),
                "updated": True,
                "message": "Transaction updated successfully"
            }
            
        except ValueError:
            # Re-raise business logic errors
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error updating transaction {transaction_id}: {str(e)}")
            raise ValueError(f"Internal error updating transaction: {str(e)}")
    
    def _prepare_updated_transaction(
        self, 
        existing: TransactionData, 
        updates: Dict[str, Any]
    ) -> TransactionData:
        """
        Prepare updated transaction data by merging existing data with updates
        
        Args:
            existing: Current transaction data
            updates: Fields to update
            
        Returns:
            TransactionData with updated values
        """
        return TransactionData(
            description=updates.get('description', existing.description),
            cargos=updates.get('cargos', existing.cargos),
            abonos=updates.get('abonos', existing.abonos),
            currency=updates.get('currency', existing.currency),
            fecha_proceso=updates.get('fecha_proceso', existing.fecha_proceso),
            fecha_consumo=updates.get('fecha_consumo', existing.fecha_consumo),
            internal_transaction=updates.get('internal_transaction', existing.internal_transaction),
            type=updates.get('type', existing.type),
            order=updates.get('order', existing.order)
        )
    
    def _validate_transaction_data(self, transaction: TransactionData) -> None:
        """
        Validate transaction data according to business rules
        
        Args:
            transaction: Transaction data to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Business rule: Description is required
        if not transaction.description or not transaction.description.strip():
            raise ValueError("Transaction description is required")
        
        # Business rule: At least one of cargos or abonos must be non-zero
        if transaction.cargos == 0.0 and transaction.abonos == 0.0:
            raise ValueError("Transaction must have either cargos or abonos with non-zero value")
        
        # Business rule: Cargos and abonos cannot both be non-zero
        if transaction.cargos != 0.0 and transaction.abonos != 0.0:
            raise ValueError("Transaction cannot have both cargos and abonos with non-zero values")
        
        # Business rule: Currency is required
        if not transaction.currency or not transaction.currency.strip():
            raise ValueError("Transaction currency is required")
        
        # Business rule: Order must be positive
        if transaction.order <= 0:
            raise ValueError("Transaction order must be a positive integer")