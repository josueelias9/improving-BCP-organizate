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


# ============================================================================
# CATEGORY CRUD OPERATIONS
# ============================================================================
