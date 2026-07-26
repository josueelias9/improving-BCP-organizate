"""
Update Transaction Use Case - Application Layer
Handles the business logic for updating a specific transaction by ID
"""

import uuid
import logging
from typing import Dict, Any

from src.Capplication.gateway.db import ITransactionDbGateway, ICategoryDbGateway
from src.Denterprise.entities import TransactionEntity

logger = logging.getLogger(__name__)


class UpdateTransactionUseCase:
    """Use case for updating a transaction by ID"""

    def __init__(
        self,
        transaction_gateway: ITransactionDbGateway,
        category_gateway: ICategoryDbGateway,
    ):
        self.transaction_gateway = transaction_gateway
        self.category_gateway = category_gateway

    def execute(
        self, transaction_id: uuid.UUID, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a transaction by ID

        Args:
            transaction_id: UUID of the transaction to update
            update_data: Dictionary containing fields to update (from DTO)

        Returns:
            Dictionary with update result (for DTO response)

        Raises:
            ValueError: If transaction not found or validation fails
        """
        try:
            # Get existing transaction entity
            existing_transaction = self.transaction_gateway.get_by_id(transaction_id)

            if not existing_transaction:
                raise ValueError(f"Transaction with ID {transaction_id} not found")

            # Validate and prepare updated transaction data
            updated_transaction = self._prepare_updated_transaction(
                existing_transaction, update_data
            )

            # Validate business rules
            self._validate_transaction_data(updated_transaction)

            # Prepare update dict with history and category_id
            update_dict = {"history": updated_transaction.history}

            # Handle category update if provided
            if "category_name" in update_data and update_data["category_name"]:
                category = self.category_gateway.get_by_name(
                    update_data["category_name"]
                )
                if category:
                    update_dict["category_id"] = category.id
                    logger.info(
                        f"Category '{update_data['category_name']}' found, will update category_id"
                    )
                else:
                    logger.warning(
                        f"Category '{update_data['category_name']}' not found, skipping category update"
                    )

            # Update transaction via gateway
            success = self.transaction_gateway.update(transaction_id, update_dict)

            if not success:
                raise ValueError("Failed to update transaction")

            return {
                "transaction_id": str(transaction_id),
                "updated": True,
                "message": "Transaction updated successfully",
            }

        except ValueError:
            # Re-raise business logic errors
            raise

        except Exception as e:
            logger.error(
                f"Unexpected error updating transaction {transaction_id}: {str(e)}"
            )
            raise ValueError(f"Internal error updating transaction: {str(e)}")

    def _prepare_updated_transaction(
        self, existing: TransactionEntity, updates: Dict[str, Any]
    ) -> TransactionEntity:
        """
        Prepare updated transaction entity - only history can be updated

        Args:
            existing: Current transaction entity
            updates: Fields to update (only 'history' is allowed)

        Returns:
            TransactionEntity with updated history value
        """
        return TransactionEntity(
            id=existing.id,
            order=existing.order,
            description=existing.description,
            history=updates.get(
                "history", existing.history
            ),  # Only history can be updated
            amount=existing.amount,
            transaction_type=existing.transaction_type,
            transaction_date=existing.transaction_date,
            unique_identifier=existing.unique_identifier,
            category_id=existing.category_id,
        )

    def _validate_transaction_data(self, transaction: TransactionEntity) -> None:
        """
        Validate transaction data according to business rules

        Args:
            transaction: Transaction entity to validate

        Raises:
            ValueError: If validation fails
        """
        # Business rule: Description is required
        if not transaction.description or not transaction.description.strip():
            raise ValueError("Transaction description is required")

        # Business rule: Amount must be non-zero
        if transaction.amount == 0.0:
            raise ValueError("Transaction amount must be non-zero")

        # Business rule: Type must be valid
        if transaction.transaction_type not in ["income", "expense"]:
            raise ValueError("Transaction type must be either 'income' or 'expense'")

        # Business rule: Order must be positive
        if transaction.order <= 0:
            raise ValueError("Transaction order must be a positive integer")
