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
                # Generate unique_identifier: {fecha_proceso}__{cargos}__{description}
                unique_id = f"{transaction_data.order}__{transaction_data.fecha_proceso}__{transaction_data.cargos}__{transaction_data.abonos}__{transaction_data.description}"
                
                transaction = Transaction(
                    description=transaction_data.description,
                    cargos=transaction_data.cargos,
                    abonos=transaction_data.abonos,
                    currency=transaction_data.currency,
                    fecha_proceso=transaction_data.fecha_proceso,
                    fecha_consumo=transaction_data.fecha_consumo,
                    internal_transaction=transaction_data.internal_transaction,
                    document_id=document_id,
                    order=transaction_data.order,
                    history=transaction_data.history,
                    unique_identifier=unique_id
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
            description=transaction.description,
            cargos=transaction.cargos,
            abonos=transaction.abonos,
            currency=transaction.currency,
            fecha_proceso=transaction.fecha_proceso,
            fecha_consumo=transaction.fecha_consumo,
            internal_transaction=transaction.internal_transaction,
            type='',  # Default empty string since type is not in Transaction model
            order=transaction.order,
            history=transaction.history
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
        
        # Apply month filter if provided
        if month:
            # Filter transactions where fecha_proceso contains the month
            # This works for dates in formats like "DD/MM/YYYY" or "YYYY-MM-DD"
            statement = statement.where(Transaction.fecha_proceso.contains(month))
        
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
