"""
DocumentType Gateway - Interface Adapter Layer
Implements document type persistence operations
"""
import uuid
import logging
from sqlmodel import Session, select

from models import DocumentType

logger = logging.getLogger(__name__)


class DocumentTypeDbGateway:
    """SQLModel implementation of document type gateway"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_name(self, name: str) -> DocumentType | None:
        """Get document type by name"""
        statement = select(DocumentType).where(DocumentType.name == name)
        return self.session.exec(statement).first()
    
    def get_all(self) -> list[DocumentType]:
        """Get all document types"""
        statement = select(DocumentType)
        return list(self.session.exec(statement).all())
