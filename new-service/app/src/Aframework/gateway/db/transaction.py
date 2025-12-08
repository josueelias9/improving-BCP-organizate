"""
Transaction Gateway - Interface Adapter Layer
Implements transaction persistence operations
"""
import uuid
import logging
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload

from models import Transaction
from src.Capplication.interfaces.db import ITransactionDbGateway
from src.Capplication.DTO.transaction_dto import DTOTransactionData

logger = logging.getLogger(__name__)


class TransactionDbGateway(ITransactionDbGateway):
    """SQLModel implementation of transaction gateway"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def save_batch(
        self,
        transactions: List[DTOTransactionData],
        document_id: uuid.UUID
    ) -> Tuple[int, int, List[str]]:
        """Save multiple transactions to database"""
        loaded_count = 0
        skipped_count = 0
        errors = []
        
        for transaction_data in transactions:
            try:
                # Generate unique_identifier: {order}__{transaction_date}__{amount}__{transaction_type}__{description}
                date_str = transaction_data.transaction_date.strftime("%Y-%m-%d") if transaction_data.transaction_date else ""
                unique_id = f"{transaction_data.order}__{date_str}__{transaction_data.amount}__{transaction_data.transaction_type}__{transaction_data.description}"
                
                transaction = Transaction(
                    order=transaction_data.order,
                    description=transaction_data.description,
                    history=transaction_data.history,
                    amount=transaction_data.amount,
                    transaction_type=transaction_data.transaction_type,
                    transaction_date=transaction_data.transaction_date,
                    unique_identifier=unique_id,
                    document_id=document_id
                )
                
                self.session.add(transaction)
                loaded_count += 1
                
            except Exception as e:
                error_msg = f"Error saving transaction {transaction_data.order}: {str(e)}"
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
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all transactions with pagination, including category name"""
        statement = (
            select(Transaction)
            .options(joinedload(Transaction.category))
            .offset(skip)
            .limit(limit)
        )
        transactions = self.session.exec(statement).all()
        
        # Convert to dict and add category_name
        result = []
        for t in transactions:
            t_dict = t.model_dump()
            t_dict['category_name'] = t.category.name if t.category else None
            result.append(t_dict)
        
        return result
    
    def get_by_id(self, transaction_id: uuid.UUID) -> Optional[DTOTransactionData]:
        """Get transaction by ID"""
        statement = select(Transaction).where(Transaction.id == transaction_id)
        transaction = self.session.exec(statement).first()
        
        if not transaction:
            return None
            
        return DTOTransactionData(
            order=transaction.order,
            description=transaction.description,
            history=transaction.history,
            amount=transaction.amount,
            transaction_type=transaction.transaction_type,
            transaction_date=transaction.transaction_date,
            unique_identifier=transaction.unique_identifier
        )
    
    def update(self, transaction_id: uuid.UUID, update_data: Dict[str, Any]) -> bool:
        """Update transaction by ID - only history and category_id fields can be updated"""
        statement = select(Transaction).where(Transaction.id == transaction_id)
        transaction = self.session.exec(statement).first()
        
        if not transaction:
            return False
            
        # Update history field if provided
        if 'history' in update_data:
            transaction.history = update_data['history']
        
        # Update category_id if provided
        if 'category_id' in update_data:
            transaction.category_id = update_data['category_id']
        
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
        self, 
        month: Optional[str] = None,
        document_id: Optional[uuid.UUID] = None
    ) -> List[Dict[str, Any]]:
        """Get all transactions with optional filters, including category name"""
        # Build query
        statement = select(Transaction).options(joinedload(Transaction.category))
        
        # Apply document_id filter if provided
        if document_id:
            statement = statement.where(Transaction.document_id == document_id)
        
        # Apply month filter if provided (filters by date field)
        if month:
            # Extract year and month from the date field
            year, month_num = month.split('-')
            statement = statement.where(
                Transaction.date.isnot(None),
            )
            # Filter using SQL extract for year and month
            from sqlalchemy import extract
            statement = statement.where(
                extract('year', Transaction.date) == int(year),
                extract('month', Transaction.date) == int(month_num)
            )
        
        # Execute query
        transactions = self.session.exec(statement).all()
        
        # Convert to dict and add category_name
        result = []
        for t in transactions:
            t_dict = t.model_dump()
            t_dict['category_name'] = t.category.name if t.category else None
            result.append(t_dict)
        
        return result
    
    def get_by_unique_identifier(self, unique_identifier: str):
        """Get transaction by unique_identifier"""
        statement = select(Transaction).where(Transaction.unique_identifier == unique_identifier)
        transaction = self.session.exec(statement).first()
        return transaction
