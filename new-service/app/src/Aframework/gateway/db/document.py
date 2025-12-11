"""Document Gateway - Interface Adapter Layer
Implements document persistence operations
Maps between SQLModel Document and domain Document entity
"""

import uuid
import logging
from sqlmodel import Session, select
from typing import Optional

from models import Document as DocumentModel
from src.Denterprise.entities import DocumentEntity
from src.Capplication.gateway.db import IDocumentDbGateway

logger = logging.getLogger(__name__)


class DocumentDbGateway(IDocumentDbGateway):
    """SQLModel implementation of document gateway"""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, document_id: uuid.UUID) -> DocumentEntity:
        """Retrieve document and map to domain entity"""
        db_document = self.session.get(DocumentModel, document_id)
        if not db_document:
            raise ValueError("Document not found")

        # Map to domain entity
        return self._map_to_entity(db_document)

    def mark_as_processed(self, document_id: uuid.UUID) -> None:
        """Mark document as processed"""
        db_document = self.session.get(DocumentModel, document_id)
        if db_document:
            db_document.processed = True
            self.session.add(db_document)
            self.session.commit()
            logger.info(f"Document {document_id} marked as processed")

    def get_by_unique_identifier(
        self, unique_identifier: str
    ) -> Optional[DocumentEntity]:
        """Get document by unique_identifier and map to domain entity"""
        statement = select(DocumentModel).where(
            DocumentModel.unique_identifier == unique_identifier
        )
        db_document = self.session.exec(statement).first()

        if not db_document:
            return None

        return self._map_to_entity(db_document)

    def create(self, document: DocumentEntity) -> DocumentEntity:
        """Create a new document from domain entity"""
        # Map domain entity to database model
        db_document = DocumentModel(
            data=document.data,
            currency=document.currency,
            unique_identifier=document.unique_identifier,
            processed=document.processed,
            user_id=document.user_id,
            document_type_id=document.document_type_id,
        )

        self.session.add(db_document)
        self.session.commit()
        self.session.refresh(db_document)

        # Map back to domain entity with ID
        return self._map_to_entity(db_document)

    def get_all_as_entities(
        self, skip: int = 0, limit: int = 100
    ) -> list[DocumentEntity]:
        """Get all documents as domain entities with pagination"""
        statement = select(DocumentModel).offset(skip).limit(limit)
        documents = self.session.exec(statement).all()

        # Map all documents to domain entities
        return [self._map_to_entity(doc) for doc in documents]

    def _map_to_entity(self, db_document: DocumentModel) -> DocumentEntity:
        """Map database model to domain entity"""
        # Extract transactions from nested JSON structure
        transactions_data = []
        if db_document.data and isinstance(db_document.data, dict):
            transactions_data = db_document.data.get("transactions", [])

        return DocumentEntity(
            id=db_document.id,
            data=transactions_data,
            currency=db_document.currency,
            unique_identifier=db_document.unique_identifier,
            processed=db_document.processed,
            user_id=db_document.user_id,
            document_type_id=db_document.document_type_id,
        )
