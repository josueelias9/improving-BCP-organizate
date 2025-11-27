"""
Transaction Repository - Interface Adapter Layer
Implements transaction persistence operations
"""
import uuid
import logging
from typing import List, Tuple
from sqlmodel import Session, select

from models import Transaction
from src.Denterprise.repositories import ITransactionRepository
from src.Denterprise.transaction_service import TransactionData

logger = logging.getLogger(__name__)


class TransactionRepository(ITransactionRepository):
    """SQLModel implementation of transaction repository"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def save_batch(
        self,
        transactions: List[TransactionData],
        document_id: uuid.UUID
    ) -> Tuple[int, int, List[str]]:
        """Save multiple transactions to database"""
        loaded_count = 0
        skipped_count = 0
        errors = []
        
        for transaction_data in transactions:
            try:
                transaction = Transaction(
                    description=transaction_data.description,
                    cargos=transaction_data.cargos,
                    abonos=transaction_data.abonos,
                    currency=transaction_data.currency,
                    fecha_proceso=transaction_data.fecha_proceso,
                    fecha_consumo=transaction_data.fecha_consumo,
                    internal_transaction=transaction_data.internal_transaction,
                    type=transaction_data.type,
                    document_id=document_id,
                    order=transaction_data.order
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
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Transaction]:
        """Get all transactions with pagination"""
        statement = select(Transaction).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())
