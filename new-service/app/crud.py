"""
CRUD operations - Main entry point
Implements all CRUD functions directly using SQLModel
"""
import uuid
from typing import Optional, List
from sqlmodel import Session, select
from models import (
    User, UserCreate, UserUpdate,
    Document, DocumentCreate, DocumentUpdate,
    Transaction, TransactionCreate, TransactionUpdate,
    Category, CategoryCreate, CategoryUpdate
)


# ============================================================================
# USER CRUD OPERATIONS
# ============================================================================

def create_user(session: Session, user_create: UserCreate) -> User:
    """Create a new user"""
    db_user = User.model_validate(user_create)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user(session: Session, user_id: uuid.UUID) -> Optional[User]:
    """Get user by ID"""
    return session.get(User, user_id)


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """Get user by email"""
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_all_users(session: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users with pagination"""
    statement = select(User).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def update_user(session: Session, user_id: uuid.UUID, user_update: UserUpdate) -> Optional[User]:
    """Update user"""
    db_user = session.get(User, user_id)
    if not db_user:
        return None
    
    user_data = user_update.model_dump(exclude_unset=True)
    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def delete_user(session: Session, user_id: uuid.UUID) -> bool:
    """Delete user"""
    db_user = session.get(User, user_id)
    if not db_user:
        return False
    
    session.delete(db_user)
    session.commit()
    return True


def user_exists(session: Session, email: str) -> bool:
    """Check if user exists by email"""
    statement = select(User).where(User.email == email)
    return session.exec(statement).first() is not None


# ============================================================================
# DOCUMENT CRUD OPERATIONS
# ============================================================================

def create_document(session: Session, document_create: DocumentCreate) -> Document:
    """Create a new document"""
    db_document = Document.model_validate(document_create)
    session.add(db_document)
    session.commit()
    session.refresh(db_document)
    return db_document


def get_document(session: Session, document_id: uuid.UUID) -> Optional[Document]:
    """Get document by ID"""
    return session.get(Document, document_id)


def get_documents_by_user(session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Document]:
    """Get all documents for a specific user"""
    statement = select(Document).where(Document.user_id == user_id).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_document_by_filename(session: Session, filename: str) -> Optional[Document]:
    """Get document by filename from JSON data"""
    statement = select(Document).where(Document.data["filename"].astext == filename)
    return session.exec(statement).first()


def get_documents_by_type(session: Session, document_type: str, skip: int = 0, limit: int = 100) -> List[Document]:
    """Get documents by type"""
    statement = select(Document).where(Document.type == document_type).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_all_documents(session: Session, skip: int = 0, limit: int = 100) -> List[Document]:
    """Get all documents with pagination"""
    statement = select(Document).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def update_document(session: Session, document_id: uuid.UUID, document_update: DocumentUpdate) -> Optional[Document]:
    """Update document"""
    db_document = session.get(Document, document_id)
    if not db_document:
        return None
    
    document_data = document_update.model_dump(exclude_unset=True)
    db_document.sqlmodel_update(document_data)
    session.add(db_document)
    session.commit()
    session.refresh(db_document)
    return db_document


def delete_document(session: Session, document_id: uuid.UUID) -> bool:
    """Delete document"""
    db_document = session.get(Document, document_id)
    if not db_document:
        return False
    
    session.delete(db_document)
    session.commit()
    return True


# ============================================================================
# TRANSACTION CRUD OPERATIONS
# ============================================================================

def create_transaction(session: Session, transaction_create: TransactionCreate) -> Transaction:
    """Create a new transaction"""
    db_transaction = Transaction.model_validate(transaction_create)
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction


def create_transactions_bulk(session: Session, transactions_create: List[TransactionCreate]) -> List[Transaction]:
    """Create multiple transactions at once"""
    db_transactions = [Transaction.model_validate(t) for t in transactions_create]
    session.add_all(db_transactions)
    session.commit()
    for db_transaction in db_transactions:
        session.refresh(db_transaction)
    return db_transactions


def get_transaction(session: Session, transaction_id: uuid.UUID) -> Optional[Transaction]:
    """Get transaction by ID"""
    return session.get(Transaction, transaction_id)


def get_transactions_by_user(session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Transaction]:
    """Get all transactions for a user"""
    statement = select(Transaction).where(Transaction.user_id == user_id).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_transactions_by_document(session: Session, document_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Transaction]:
    """Get all transactions for a document"""
    statement = select(Transaction).where(Transaction.document_id == document_id).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_transactions_by_category(session: Session, category_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Transaction]:
    """Get all transactions for a category"""
    statement = select(Transaction).where(Transaction.category_id == category_id).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def update_transaction(session: Session, transaction_id: uuid.UUID, transaction_update: TransactionUpdate) -> Optional[Transaction]:
    """Update transaction"""
    db_transaction = session.get(Transaction, transaction_id)
    if not db_transaction:
        return None
    
    transaction_data = transaction_update.model_dump(exclude_unset=True)
    db_transaction.sqlmodel_update(transaction_data)
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


def get_transaction_by_name(session: Session, name: str) -> Optional[Transaction]:
    """Get transaction by name (unique ID)"""
    statement = select(Transaction).where(Transaction.name == name)
    return session.exec(statement).first()


# ============================================================================
# CATEGORY CRUD OPERATIONS
# ============================================================================

def create_category(session: Session, category_create: CategoryCreate) -> Category:
    """Create a new category"""
    db_category = Category.model_validate(category_create)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


def get_category(session: Session, category_id: uuid.UUID) -> Optional[Category]:
    """Get category by ID"""
    return session.get(Category, category_id)


def get_category_by_name(session: Session, name: str) -> Optional[Category]:
    """Get category by name"""
    statement = select(Category).where(Category.name == name)
    return session.exec(statement).first()


def get_all_categories(session: Session, skip: int = 0, limit: int = 100) -> List[Category]:
    """Get all categories with pagination"""
    statement = select(Category).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_categories_by_parent(session: Session, parent_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Category]:
    """Get subcategories of a parent category"""
    statement = select(Category).where(Category.parent_id == parent_id).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_root_categories(session: Session, skip: int = 0, limit: int = 100) -> List[Category]:
    """Get root categories (no parent)"""
    statement = select(Category).where(Category.parent_id.is_(None)).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def update_category(session: Session, category_id: uuid.UUID, category_update: CategoryUpdate) -> Optional[Category]:
    """Update category"""
    db_category = session.get(Category, category_id)
    if not db_category:
        return None
    
    category_data = category_update.model_dump(exclude_unset=True)
    db_category.sqlmodel_update(category_data)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


def delete_category(session: Session, category_id: uuid.UUID) -> bool:
    """Delete category"""
    db_category = session.get(Category, category_id)
    if not db_category:
        return False
    
    session.delete(db_category)
    session.commit()
    return True


def category_exists(session: Session, name: str) -> bool:
    """Check if category exists by name"""
    statement = select(Category).where(Category.name == name)
    return session.exec(statement).first() is not None
