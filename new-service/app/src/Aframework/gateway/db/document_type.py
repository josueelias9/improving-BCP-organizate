
"""DocumentType Gateway - Interface Adapter Layer
Implements document type persistence operations
Maps between SQLModel DocumentType and domain DocumentType entity
"""
import logging
from sqlmodel import Session, select

from models import DocumentType as DocumentTypeModel
from src.Denterprise.entities import DocumentTypeEntity

logger = logging.getLogger(__name__)


class DocumentTypeDbGateway:
    """SQLModel implementation of document type gateway"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_name(self, name: str) -> DocumentTypeEntity | None:
        """Get document type by name and map to domain entity"""
        statement = select(DocumentTypeModel).where(DocumentTypeModel.name == name)
        db_doc_type = self.session.exec(statement).first()
        
        if not db_doc_type:
            return None
        
        # Map to domain entity
        doc_type = DocumentTypeEntity()
        doc_type.name = db_doc_type.name
        return doc_type
    
    def get_all(self) -> list[DocumentTypeEntity]:
        """Get all document types as domain entities"""
        statement = select(DocumentTypeModel)
        db_doc_types = self.session.exec(statement).all()
        
        # Map to domain entities
        doc_types = []
        for db_dt in db_doc_types:
            doc_type = DocumentTypeEntity()
            doc_type.name = db_dt.name
            doc_types.append(doc_type)
        
        return doc_types
