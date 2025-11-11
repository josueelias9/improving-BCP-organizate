"""
CRUD operations for Document model
"""
import uuid
from typing import Optional, List
from sqlmodel import Session, select
from src.infrastructure.database.models import Document, DocumentCreate, DocumentUpdate


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
    """Get documents by user ID with pagination"""
    statement = select(Document).where(Document.user_id == user_id).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_document_by_filename(session: Session, filename: str) -> Optional[Document]:
    """Get document by filename"""
    statement = select(Document).where(Document.filename == filename)
    return session.exec(statement).first()


def get_documents_by_type(session: Session, document_type: str, skip: int = 0, limit: int = 100) -> List[Document]:
    """Get documents by type with pagination"""
    statement = select(Document).where(Document.document_type == document_type).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_all_documents(session: Session, skip: int = 0, limit: int = 100) -> List[Document]:
    """Get all documents with pagination"""
    statement = select(Document).offset(skip).limit(limit)
    return session.exec(statement).all()


def update_document(session: Session, document_id: uuid.UUID, document_update: DocumentUpdate) -> Optional[Document]:
    """Update document"""
    db_document = session.get(Document, document_id)
    if not db_document:
        return None
    
    document_data = document_update.model_dump(exclude_unset=True)
    for key, value in document_data.items():
        setattr(db_document, key, value)
    
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