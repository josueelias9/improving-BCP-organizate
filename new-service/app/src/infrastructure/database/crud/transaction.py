"""
CRUD operations for Transaction model
"""
import uuid
from typing import Optional, List
from sqlmodel import Session, select
from src.infrastructure.database.models import Transaction, TransactionCreate, TransactionUpdate


def create_transaction(session: Session, transaction_create: TransactionCreate) -> Transaction:
    """Create a new transaction"""
    db_transaction = Transaction.model_validate(transaction_create)
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction


def create_transactions_bulk(session: Session, transactions_create: List[TransactionCreate]) -> List[Transaction]:
    """Create multiple transactions in bulk"""
    db_transactions = []
    for transaction_create in transactions_create:
        db_transaction = Transaction.model_validate(transaction_create)
        session.add(db_transaction)
        db_transactions.append(db_transaction)
    
    session.commit()
    for db_transaction in db_transactions:
        session.refresh(db_transaction)
    
    return db_transactions


def get_transaction(session: Session, transaction_id: uuid.UUID) -> Optional[Transaction]:
    """Get transaction by ID"""
    return session.get(Transaction, transaction_id)


def get_transactions_by_user(session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Transaction]:
    """Get transactions by user ID with pagination"""
    statement = select(Transaction).where(Transaction.user_id == user_id).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_transactions_by_document(session: Session, document_id: uuid.UUID) -> List[Transaction]:
    """Get transactions by document ID"""
    statement = select(Transaction).where(Transaction.document_id == document_id)
    return session.exec(statement).all()


def get_transactions_by_category(session: Session, category_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Transaction]:
    """Get transactions by category ID with pagination"""
    statement = select(Transaction).where(Transaction.category_id == category_id).offset(skip).limit(limit)
    return session.exec(statement).all()


def update_transaction(session: Session, transaction_id: uuid.UUID, transaction_update: TransactionUpdate) -> Optional[Transaction]:
    """Update transaction"""
    db_transaction = session.get(Transaction, transaction_id)
    if not db_transaction:
        return None
    
    transaction_data = transaction_update.model_dump(exclude_unset=True)
    for key, value in transaction_data.items():
        setattr(db_transaction, key, value)
    
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction


def delete_transaction(session: Session, transaction_id: uuid.UUID) -> bool:
    """Delete transaction"""
    db_transaction = session.get(Transaction, transaction_id)
    if not db_transaction:
        return False
    
    session.delete(db_transaction)
    session.commit()
    return True


def get_transaction_by_name(session: Session, transaction_name: str) -> Optional[Transaction]:
    """Get transaction by unique name (ID from PDF)"""
    statement = select(Transaction).where(Transaction.name == transaction_name)
    return session.exec(statement).first()