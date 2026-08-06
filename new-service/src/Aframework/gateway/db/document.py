"""Document Gateway - Interface Adapter Layer
Implements document persistence operations
Maps between SQLModel Document and domain Document entity
"""

import logging
from sqlmodel import Session, select
from typing import Optional

from models import Document as DocumentModel, Transaction as TransactionModel
from src.Denterprise.entities import DocumentEntity
from src.Capplication.gateway.db import IDocumentDbGateway

logger = logging.getLogger(__name__)


class DocumentDbGateway(IDocumentDbGateway):
    """SQLModel implementation of document gateway"""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, document_id: str) -> DocumentEntity:
        """Retrieve document and map to domain entity"""
        db_document = self.session.get(DocumentModel, document_id)
        if not db_document:
            raise ValueError("Document not found")

        # Map to domain entity
        return DocumentEntity(
            id=db_document.id,
            processed=db_document.processed,
            start_date=db_document.start_date,
            end_date=db_document.end_date,
            plain_text=db_document.plain_text,
            user_id=db_document.user_id,
            document_format_name=db_document.document_format.name,
        )

    def mark_as_processed(self, document_id: str) -> None:
        """Mark document as processed"""
        db_document = self.session.get(DocumentModel, document_id)
        if db_document:
            db_document.processed = True
            self.session.add(db_document)
            self.session.commit()
            logger.info(f"Document {document_id} marked as processed")

    def get_or_create(self, document: DocumentEntity):
        """Return existing document or create a new one."""
        document.generate_id()

        db_document = self.session.get(DocumentModel, document.id)

        if db_document:
            return self._map_to_entity(db_document), False

        db_document = DocumentModel(
            id=document.id,
            account=document.account,
            balance=document.balance,
            processed=document.processed,
            start_date=document.start_date,
            end_date=document.end_date,
            user_id=document.user_id,
            document_type_id=document.document_type_id,
            plain_text=document.plain_text,
        )

        self.session.add(db_document)
        self.session.commit()
        self.session.refresh(db_document)

        return self._map_to_entity(db_document), True

    def get_all_as_entities(
        self, skip: int = 0, limit: int = 100
    ) -> list[DocumentEntity]:
        """Get all documents as domain entities with pagination"""
        statement = (
            select(DocumentModel).order_by(DocumentModel.id).offset(skip).limit(limit)
        )
        documents = self.session.exec(statement).all()

        # Map all documents to domain entities
        return [self._map_to_entity(doc) for doc in documents]

    def delete(self, document_id: str) -> None:
        """Delete document and its associated transactions by ID"""
        db_document = self.session.get(DocumentModel, document_id)
        if db_document:
            for transaction in db_document.transactions:
                self.session.delete(transaction)
            self.session.delete(db_document)
            self.session.commit()
            logger.info(f"Document {document_id} and its transactions deleted")

    def _map_to_entity(self, db_document: DocumentModel) -> DocumentEntity:
        """Map database model to domain entity"""
        return DocumentEntity(
            id=db_document.id,
            account=db_document.account,
            balance=db_document.balance,
            processed=db_document.processed,
            start_date=db_document.start_date,
            end_date=db_document.end_date,
            plain_text=db_document.plain_text,
            user_id=db_document.user_id,
            document_format_name=db_document.document_format.name,
        )
