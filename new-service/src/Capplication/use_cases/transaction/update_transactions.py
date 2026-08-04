"""
Batch Update Transactions Use Case - Application Layer
Handles the business logic for updating multiple transactions simultaneously
"""

import logging

from src.Capplication.DTO.transaction_dto import (
    DTOUpdateTransactionsResponse,
    DTOUpdateTransactionsRequest,
)
from src.Capplication.gateway.db import ITransactionDbGateway, ICategoryDbGateway

logger = logging.getLogger(__name__)


class UpdateTransactionsUseCase:
    """Use case for updating multiple transactions simultaneously"""

    def __init__(
        self,
        transaction_gateway: ITransactionDbGateway,
        category_gateway: ICategoryDbGateway,
    ):
        self.transaction_gateway = transaction_gateway
        self.category_gateway = category_gateway

    def execute(
        self, batch_update: DTOUpdateTransactionsRequest
    ) -> DTOUpdateTransactionsResponse:
        """
        Update multiple transactions simultaneously

        Args:
            batch_update: List of transaction updates to apply

        Returns:
            BatchUpdateResult with operation summary
        """
        updates = batch_update.updates

        total = len(updates)
        updated = 0
        failed = 0
        errors = []

        for update_item in updates:
            try:
                # Get existing transaction
                existing_transaction = self.transaction_gateway.get_by_id(
                    update_item.transaction_id
                )

                if not existing_transaction:
                    failed += 1
                    errors.append(
                        {
                            "transaction_id": str(update_item.transaction_id),
                            "error": "Transaction not found",
                        }
                    )
                    continue

                category = self.category_gateway.get_by_name(update_item.category_name)
                if not category:
                    failed += 1
                    errors.append(
                        {
                            "transaction_id": str(update_item.transaction_id),
                            "error": f"Category '{update_item.category_name}' not found",
                        }
                    )
                    continue

                update_data = {"category_id": category.id}

                # Execute update
                success = self.transaction_gateway.update(
                    update_item.transaction_id, update_data
                )

                if success:
                    updated += 1
                else:
                    failed += 1
                    errors.append(
                        {
                            "transaction_id": str(update_item.transaction_id),
                            "error": "Update failed",
                        }
                    )

            except Exception as e:
                failed += 1
                errors.append(
                    {"transaction_id": str(update_item.transaction_id), "error": str(e)}
                )
                logger.error(
                    f"Error updating transaction {update_item.transaction_id}: {str(e)}"
                )

        logger.info(
            f"Batch update completed: {updated}/{total} successful, {failed} failed"
        )

        return DTOUpdateTransactionsResponse(
            total=total,
            updated=updated,
            failed=failed,
            message=f"Successfully updated {updated}/{total} transactions",
            errors=errors if errors else [],
        )
