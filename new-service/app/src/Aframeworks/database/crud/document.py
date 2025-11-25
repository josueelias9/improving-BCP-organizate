"""
Document repository implementation - Framework layer
"""
import uuid
from typing import Optional, List
from sqlmodel import Session, select
from models import Document, DocumentCreate, DocumentUpdate
from src.Capplication.repositories import IDocumentRepository


class DocumentRepository(IDocumentRepository):
    """SQLModel implementation of Document repository"""
    
    def create_document(self, session: Session, document_create: DocumentCreate) -> Document:
        """Create a new document"""
        db_document = Document.model_validate(document_create)
        session.add(db_document)
        session.commit()
        session.refresh(db_document)
        return db_document
    
    def get_document(self, session: Session, document_id: uuid.UUID) -> Optional[Document]:
        """Get document by ID"""
        return session.get(Document, document_id)
    
    def get_documents_by_user(self, session: Session, user_id: uuid.UUID) -> List[Document]:
        """Get documents by user ID"""
        statement = select(Document).where(Document.user_id == user_id)
        return session.exec(statement).all()
    
    def get_document_by_filename(self, session: Session, filename: str) -> Optional[Document]:
        """Get document by filename (stored in data field)"""
        # Assuming filename is stored in data JSON field
        statement = select(Document).where(Document.data.contains({"filename": filename}))
        return session.exec(statement).first()
    
    def update_document(self, session: Session, document_id: uuid.UUID, document_update: DocumentUpdate) -> Optional[Document]:
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
    
    def delete_document(self, session: Session, document_id: uuid.UUID) -> bool:
        """Delete document"""
        db_document = session.get(Document, document_id)
        if not db_document:
            return False
        
        session.delete(db_document)
        session.commit()
        return True


# Legacy function exports for backward compatibility
def create_document(session: Session, document_create: DocumentCreate) -> Document:
    return DocumentRepository().create_document(session, document_create)

def get_document(session: Session, document_id: uuid.UUID) -> Optional[Document]:
    return DocumentRepository().get_document(session, document_id)

def get_documents_by_user(session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Document]:
    return DocumentRepository().get_documents_by_user(session, user_id)

def get_document_by_filename(session: Session, filename: str) -> Optional[Document]:
    return DocumentRepository().get_document_by_filename(session, filename)

def get_documents_by_type(session: Session, document_type: str, skip: int = 0, limit: int = 100) -> List[Document]:
    """Get documents by type - legacy compatibility"""
    statement = select(Document).where(Document.type == document_type).offset(skip).limit(limit)
    temp_session = session
    return temp_session.exec(statement).all()

def get_all_documents(session: Session, skip: int = 0, limit: int = 100) -> List[Document]:
    """Get all documents - legacy compatibility"""
    statement = select(Document).offset(skip).limit(limit)
    return session.exec(statement).all()

def update_document(session: Session, document_id: uuid.UUID, document_update: DocumentUpdate) -> Optional[Document]:
    return DocumentRepository().update_document(session, document_id, document_update)

def delete_document(session: Session, document_id: uuid.UUID) -> bool:
    return DocumentRepository().delete_document(session, document_id)