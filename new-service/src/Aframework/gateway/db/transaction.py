"""
Transaction Gateway - Interface Adapter Layer
Implements transaction persistence operations
Maps between SQLModel Transaction and domain Transaction entity
"""

import uuid
import logging
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload

from models import Transaction as TransactionModel
from src.Denterprise.entities import TransactionEntity
from src.Capplication.gateway.db import ITransactionDbGateway

logger = logging.getLogger(__name__)


class TransactionDbGateway(ITransactionDbGateway):
    """SQLModel implementation of transaction gateway"""

    def __init__(self, session: Session):
        self.session = session

    def save_batch(
        self, transactions: List[TransactionEntity], account_id: str
    ) -> Tuple[int, int, List[str]]:
        """Save multiple transactions from domain entities to database"""
        loaded_count = 0
        skipped_count = 0
        errors = []

        for transaction_entity in transactions:
            try:
                transaction_entity.account_id = account_id
                transaction_entity.generate_unique_identifier()

                # Map domain entity to database model
                db_transaction = TransactionModel(
                    order=transaction_entity.order,
                    description=transaction_entity.description,
                    history=transaction_entity.history,
                    amount=transaction_entity.amount,
                    transaction_type=transaction_entity.transaction_type,
                    transaction_date=transaction_entity.transaction_date,
                    currency=transaction_entity.currency,
                    unique_identifier=transaction_entity.unique_identifier,
                    account_id=account_id,
                )

                self.session.add(db_transaction)
                loaded_count += 1

            except Exception as e:
                error_msg = (
                    f"Error saving transaction {transaction_entity.order}: {str(e)}"
                )
                logger.error(error_msg)
                errors.append(error_msg)
                skipped_count += 1

        # Commit all
        try:
            self.session.commit()
            logger.info(f"Successfully saved {loaded_count} transactions")
        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Error committing transactions: {str(e)}")

        return loaded_count, skipped_count, errors

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        account_id: Optional[str] = None,
    ) -> List[TransactionEntity]:
        """Get all transactions with pagination and optional account filter"""

        if account_id:
            statement = (
                select(TransactionModel)
                .where(TransactionModel.account_id == account_id)
                .offset(skip)
                .limit(limit)
            )
        else:
            statement = select(TransactionModel).offset(skip).limit(limit)
        transactions = self.session.exec(statement).all()

        # Map to domain entities
        entities = []

        for transaction in transactions:
            try:
                entity = TransactionEntity(
                    id=transaction.id,
                    order=transaction.order,
                    description=transaction.description,
                    history=transaction.history,
                    amount=transaction.amount,
                    transaction_type=transaction.transaction_type,
                    transaction_date=transaction.transaction_date,
                    currency=transaction.currency,
                    unique_identifier=transaction.unique_identifier,
                    category_name=transaction.category.name,
                    account_id=transaction.account_id,
                )
                entities.append(entity)
            except Exception as e:
                logger.error(
                    f"Error mapping transaction {transaction.id} to entity: {str(e)}"
                )

        return entities

    def get_by_id(self, transaction_id: uuid.UUID) -> Optional[TransactionEntity]:
        """Get transaction by ID and map to domain entity"""
        statement = select(TransactionModel).where(
            TransactionModel.id == transaction_id
        )
        db_transaction = self.session.exec(statement).first()

        if not db_transaction:
            return None

        # Map to domain entity
        return TransactionEntity(
            id=db_transaction.id,
            order=db_transaction.order,
            description=db_transaction.description,
            history=db_transaction.history,
            amount=db_transaction.amount,
            transaction_type=db_transaction.transaction_type,
            transaction_date=db_transaction.transaction_date,
            currency=db_transaction.currency,
            unique_identifier=db_transaction.unique_identifier,
            category_id=db_transaction.category_id,
            account_id=db_transaction.account_id,
        )

    def update(self, transaction_id: uuid.UUID, update_data: Dict[str, Any]) -> bool:
        """Update transaction by ID - only history and category_id fields can be updated"""
        statement = select(TransactionModel).where(
            TransactionModel.id == transaction_id
        )
        transaction = self.session.exec(statement).first()

        if not transaction:
            return False

        # Update history field if provided
        if "history" in update_data:
            transaction.history = update_data["history"]

        # Update category_id if provided
        if "category_id" in update_data:
            transaction.category_id = update_data["category_id"]

        transaction.updated_at = datetime.utcnow()

        try:
            self.session.add(transaction)
            self.session.commit()
            logger.info(f"Successfully updated transaction {transaction_id}")
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating transaction {transaction_id}: {str(e)}")
            raise ValueError(f"Error updating transaction: {str(e)}")

    def get_by_account_id(self, account_id: str) -> List[TransactionEntity]:
        """Get all transactions for a given account, including category name"""
        statement = (
            select(TransactionModel)
            .options(joinedload(TransactionModel.category))
            .where(TransactionModel.account_id == account_id)
            .order_by(TransactionModel.transaction_date.asc())
        )
        transactions = self.session.exec(statement).all()

        result = []
        for t in transactions:
            entity = TransactionEntity(
                id=t.id,
                order=t.order,
                description=t.description,
                history=t.history,
                amount=t.amount,
                transaction_type=t.transaction_type,
                transaction_date=t.transaction_date,
                currency=t.currency,
                unique_identifier=t.unique_identifier,
                category_name=t.category.name if t.category else None,
                account_id=t.account_id,
            )
            result.append(entity)

        return result

    def get_by_unique_identifier(
        self, unique_identifier: str
    ) -> Optional[TransactionEntity]:
        """Get transaction by unique_identifier and map to domain entity"""
        statement = select(TransactionModel).where(
            TransactionModel.unique_identifier == unique_identifier
        )
        db_transaction = self.session.exec(statement).first()

        if not db_transaction:
            return None

        # Map to domain entity
        return TransactionEntity(
            id=db_transaction.id,
            order=db_transaction.order,
            description=db_transaction.description,
            history=db_transaction.history,
            amount=db_transaction.amount,
            transaction_type=db_transaction.transaction_type,
            transaction_date=db_transaction.transaction_date,
            currency=db_transaction.currency,
            unique_identifier=db_transaction.unique_identifier,
            category_id=db_transaction.category_id,
            account_id=db_transaction.account_id,
        )
