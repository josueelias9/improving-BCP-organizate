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
from src.Capplication.interfaces.db import IDocumentDbGateway

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
        document = DocumentEntity()
        document.data = db_document.data
        document.currency = db_document.currency
        document.unique_identifier = db_document.unique_identifier
        document.processed = db_document.processed

        return document

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

        # Map to domain entity
        document = DocumentEntity()
        document.data = db_document.data
        document.currency = db_document.currency
        document.unique_identifier = db_document.unique_identifier
        document.processed = db_document.processed

        return document

    def create(
        self, document: DocumentEntity, user_id: uuid.UUID, document_type_id: uuid.UUID
    ) -> DocumentEntity:
        """Create a new document from domain entity"""
        # Map domain entity to database model
        db_document = DocumentModel(
            data=document.data,
            currency=document.currency,
            unique_identifier=document.unique_identifier,
            processed=document.processed,
            user_id=user_id,
            document_type_id=document_type_id,
        )

        self.session.add(db_document)
        self.session.commit()
        self.session.refresh(db_document)

        # Map back to domain entity
        document.unique_identifier = db_document.unique_identifier
        return document

    def get_all(self, skip: int = 0, limit: int = 100) -> list[dict]:
        """Get all documents with pagination"""
        statement = select(DocumentModel).offset(skip).limit(limit)
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
                    "transactions_count": len(doc.data.get("transactions", [])),
                }

            doc_dict = {
                "id": str(doc.id),
                "data": data_summary,
                "currency": doc.currency,
                "unique_identifier": doc.unique_identifier,
                "processed": doc.processed,
                "user_id": str(doc.user_id),
                "document_type": doc.document_type.name if doc.document_type else None,
            }
            result.append(doc_dict)

        return result
