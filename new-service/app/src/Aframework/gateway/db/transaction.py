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
        self, transactions: List[TransactionEntity], document_id: uuid.UUID
    ) -> Tuple[int, int, List[str]]:
        """Save multiple transactions from domain entities to database"""
        loaded_count = 0
        skipped_count = 0
        errors = []

        for transaction_entity in transactions:
            try:
                # Generate unique_identifier using entity method
                unique_id = transaction_entity.generate_unique_identifier()

                # Map domain entity to database model
                db_transaction = TransactionModel(
                    order=transaction_entity.order,
                    description=transaction_entity.description,
                    history=transaction_entity.history,
                    amount=transaction_entity.amount,
                    transaction_type=transaction_entity.transaction_type,
                    transaction_date=transaction_entity.transaction_date,
                    currency=transaction_entity.currency,
                    unique_identifier=unique_id,
                    document_id=document_id,
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

    def get_all(self, skip: int = 0, limit: int = 100) -> List[TransactionEntity]:
        """Get all transactions with pagination

        Returns:
            List of TransactionEntity
        """
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
                    # category_name=transaction.category.name,
                    document_type_name=transaction.document.document_type.name if transaction.document else "",
                    document_unique_identifier=transaction.document.unique_identifier
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
        
        # TODO: create a single model -> entity mapper for all functions
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

    def get_all_filtered(
        self, month: Optional[str] = None, document_id: Optional[uuid.UUID] = None
    ) -> List[Dict[str, Any]]:
        """Get all transactions with optional filters, including category name"""
        # Build query
        statement = select(TransactionModel).options(
            joinedload(TransactionModel.category)
        )

        # Apply document_id filter if provided
        if document_id:
            statement = statement.where(TransactionModel.document_id == document_id)

        # Apply month filter if provided (filters by date field)
        if month:
            # Extract year and month from the date field
            year, month_num = month.split("-")
            statement = statement.where(
                TransactionModel.date.isnot(None),
            )
            # Filter using SQL extract for year and month
            from sqlalchemy import extract

            statement = statement.where(
                extract("year", TransactionModel.date) == int(year),
                extract("month", TransactionModel.date) == int(month_num),
            )

        # Execute query
        transactions = self.session.exec(statement).all()

        # Convert to dict and add category_name
        result = []
        for t in transactions:
            t_dict = t.model_dump()
            t_dict["category_name"] = t.category.name if t.category else None
            result.append(t_dict)

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
        )
