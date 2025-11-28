"""
Document Gateway - Interface Adapter Layer
Implements document persistence operations
"""
import uuid
import logging
from sqlmodel import Session, select

from models import Document
from src.Capplication.gateways import IDocumentGateway
from src.Denterprise.transaction_service import DocumentData

logger = logging.getLogger(__name__)


class DocumentGateway(IDocumentGateway):
    """SQLModel implementation of document gateway"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, document_id: uuid.UUID) -> DocumentData:
        """Retrieve document and map to domain model"""
        document = self.session.get(Document, document_id)
        if not document:
            raise ValueError("Document not found")
        
        return DocumentData(
            id=str(document.id),
            data=document.data or [],
            currency=document.currency,
            processed=document.processed
        )
    
    def mark_as_processed(self, document_id: uuid.UUID) -> None:
        """Mark document as processed"""
        document = self.session.get(Document, document_id)
        if document:
            document.processed = True
            self.session.add(document)
            self.session.commit()
            logger.info(f"Document {document_id} marked as processed")
    
    def get_by_unique_identifier(self, unique_identifier: str) -> Document | None:
        """Get document by unique_identifier"""
        statement = select(Document).where(Document.unique_identifier == unique_identifier)
        return self.session.exec(statement).first()
    
    def create(self, document: Document) -> Document:
        """Create a new document"""
        self.session.add(document)
        self.session.commit()
        self.session.refresh(document)
        return document
