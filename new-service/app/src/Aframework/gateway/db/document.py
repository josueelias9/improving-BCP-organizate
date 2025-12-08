"""
Document Gateway - Interface Adapter Layer
Implements document persistence operations
"""
import uuid
import logging
from sqlmodel import Session, select

from models import Document
from src.Capplication.interfaces.db import IDocumentDbGateway
from src.Capplication.DTO.document_dto import DTODocumentData

logger = logging.getLogger(__name__)


class DocumentDbGateway(IDocumentDbGateway):
    """SQLModel implementation of document gateway"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, document_id: uuid.UUID) -> DTODocumentData:
        """Retrieve document and map to domain model"""
        document = self.session.get(Document, document_id)
        if not document:
            raise ValueError("Document not found")
        
        # Extract transactions list from nested data structure
        transactions_list = []
        if document.data and isinstance(document.data, dict):
            transactions_list = document.data.get("transactions", [])
        
        return DTODocumentData(
            id=str(document.id),
            data=transactions_list,
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
    
    def get_all(self, skip: int = 0, limit: int = 100) -> list[dict]:
        """Get all documents with pagination"""
        statement = select(Document).offset(skip).limit(limit)
        documents = self.session.exec(statement).all()
        
        # Convert to dict with all properties
        result = []
        for doc in documents:
            # Extract important data from nested JSON structure
            data_summary = {}
            
            if doc.data and isinstance(doc.data, dict):
                # Extract metadata but not the full transactions list
                data_summary = {
                    "account_number": doc.data.get("account_number"),
                    "previous_balance": doc.data.get("previous_balance"),
                    "initial_day": doc.data.get("initial_day"),
                    "final_day": doc.data.get("final_day"),
                    "transactions_count": len(doc.data.get("transactions", []))
                }
            
            doc_dict = {
                "id": str(doc.id),
                "data": data_summary,
                "currency": doc.currency,
                "unique_identifier": doc.unique_identifier,
                "processed": doc.processed,
                "user_id": str(doc.user_id),
                "document_type": doc.document_type.name if doc.document_type else None
            }
            result.append(doc_dict)
        
        return result
