"""
Batch Update Transactions Use Case - Application Layer
Handles the business logic for updating multiple transactions simultaneously
"""
import uuid
import logging
from typing import Dict, Any, List

from src.Capplication.DTO.transaction_dto import BatchUpdateItem, BatchUpdateResult
from src.Capplication.interfaces.db import ITransactionDbGateway, ICategoryDbGateway

logger = logging.getLogger(__name__)


class BatchUpdateTransactionsUseCase:
    """Use case for updating multiple transactions simultaneously"""
    
    def __init__(
        self, 
        transaction_gateway: ITransactionDbGateway,
        category_gateway: ICategoryDbGateway
    ):
        self.transaction_gateway = transaction_gateway
        self.category_gateway = category_gateway
    
    def execute(self, updates: List[BatchUpdateItem]) -> BatchUpdateResult:
        """
        Update multiple transactions simultaneously
        
        Args:
            updates: List of transaction updates to apply
            
        Returns:
            BatchUpdateResult with operation summary
        """
        total = len(updates)
        updated = 0
        failed = 0
        errors = []
        
        for update_item in updates:
            try:
                # Get existing transaction
                existing_transaction = self.transaction_gateway.get_by_id(update_item.transaction_id)
                
                if not existing_transaction:
                    failed += 1
                    errors.append({
                        "transaction_id": str(update_item.transaction_id),
                        "error": "Transaction not found"
                    })
                    continue
                
                # Update only history
                update_data = {"history": update_item.history}
                
                # Handle category if provided
                if update_item.category_name:
                    category = self.category_gateway.get_by_name(update_item.category_name)
                    if category:
                        update_data['category_id'] = category.id
                        logger.info(f"Category '{update_item.category_name}' found for transaction {update_item.transaction_id}")
                    else:
                        logger.warning(f"Category '{update_item.category_name}' not found, skipping category update")
                
                # Execute update
                success = self.transaction_gateway.update(update_item.transaction_id, update_data)
                
                if success:
                    updated += 1
                else:
                    failed += 1
                    errors.append({
                        "transaction_id": str(update_item.transaction_id),
                        "error": "Update failed"
                    })
                    
            except Exception as e:
                failed += 1
                errors.append({
                    "transaction_id": str(update_item.transaction_id),
                    "error": str(e)
                })
                logger.error(f"Error updating transaction {update_item.transaction_id}: {str(e)}")
        
        logger.info(f"Batch update completed: {updated}/{total} successful, {failed} failed")
        
        return BatchUpdateResult(
            total=total,
            updated=updated,
            failed=failed,
            errors=errors if errors else []
        )
