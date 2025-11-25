"""
Document repository implementation - Framework layer
"""
import uuid
from typing import Optional, List
from sqlmodel import Session
from models import Document, DocumentCreate, DocumentUpdate
from src.Capplication.repositories import IDocumentRepository
import crud


class DocumentRepository(IDocumentRepository):
    """SQLModel implementation of Document repository - delegates to crud.py"""
    
    def create_document(self, session: Session, document_create: DocumentCreate) -> Document:
        """Create a new document"""
        return crud.create_document(session, document_create)
    
    def get_document(self, session: Session, document_id: uuid.UUID) -> Optional[Document]:
        """Get document by ID"""
        return crud.get_document(session, document_id)
    
    def get_documents_by_user(self, session: Session, user_id: uuid.UUID) -> List[Document]:
        """Get documents by user ID"""
        return crud.get_documents_by_user(session, user_id)
    
    def get_document_by_filename(self, session: Session, filename: str) -> Optional[Document]:
        """Get document by filename (stored in data field)"""
        return crud.get_document_by_filename(session, filename)
    
    def update_document(self, session: Session, document_id: uuid.UUID, document_update: DocumentUpdate) -> Optional[Document]:
        """Update document"""
        return crud.update_document(session, document_id, document_update)
    
    def delete_document(self, session: Session, document_id: uuid.UUID) -> bool:
        """Delete document"""
        return crud.delete_document(session, document_id)