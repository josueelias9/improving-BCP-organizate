"""
Gateway Interfaces - Application Layer
Defines contracts for data access using domain entities
"""

import uuid
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict, Any
from src.Denterprise.entities import (
    TransactionEntity,
    DocumentEntity,
    UserEntity,
    CategoryEntity,
    DocumentTypeEntity,
)


class IDocumentDbGateway(ABC):
    """Interface for document persistence operations"""

    @abstractmethod
    def get_by_id(self, document_id: str) -> DocumentEntity:
        """
        Retrieve document by ID

        Returns:
            Domain Document entity

        Raises:
            ValueError: If document not found
        """
        pass

    @abstractmethod
    def mark_as_processed(self, document_id: str) -> None:
        """Mark document as processed"""
        pass

    @abstractmethod
    def delete(self, document_id: str) -> None:
        """
        Delete document by ID

        Args:
            document_id: hash-based ID of the document to delete
        """
        pass

    @abstractmethod
    def get_or_create(self, document: DocumentEntity) -> Tuple[DocumentEntity, bool]:
        """
        Return existing document or create a new one.

        Returns:
            (entity, created) — created is False when the document already existed
        """
        pass

    @abstractmethod
    def get_all_as_entities(
        self, skip: int = 0, limit: int = 100
    ) -> List[DocumentEntity]:
        """
        Get all documents with pagination, returning domain entities

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of domain Document entities
        """
        pass


class IUserDbGateway(ABC):
    """Interface for user persistence operations"""

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[UserEntity]:
        """
        Get user by email

        Returns:
            Domain User entity if found, None otherwise
        """
        pass

    @abstractmethod
    def create(self, user_data: UserEntity) -> UserEntity:
        """
        Create a new user

        Returns:
            Created domain User entity
        """
        pass


class ICategoryDbGateway(ABC):
    """Interface for category persistence operations"""

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[CategoryEntity]:
        """
        Get category by name

        Returns:
            Domain Category entity if found, None otherwise
        """
        pass

    @abstractmethod
    def get_all(self) -> List[CategoryEntity]:
        """
        Get all categories

        Returns:
            List of domain Category entities
        """
        pass


class ITransactionDbGateway(ABC):
    """Interface for transaction persistence operations"""

    @abstractmethod
    def save_batch(
        self, transactions: List[TransactionEntity], document_id: uuid.UUID
    ) -> Tuple[int, int, List[str]]:
        """
        Save multiple transactions from domain entities

        Args:
            transactions: List of domain Transaction entities
            document_id: UUID of the document

        Returns:
            Tuple of (loaded_count, skipped_count, errors)
        """
        pass

    @abstractmethod
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        document_id: Optional[uuid.UUID] = None,
    ) -> List[TransactionEntity]:
        """
        Get all transactions with pagination and optional document filter

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            document_id: Optional document UUID to filter transactions

        Returns:
            List of TransactionEntity
        """
        pass

    @abstractmethod
    def get_by_id(self, transaction_id: uuid.UUID) -> Optional[TransactionEntity]:
        """
        Get transaction by ID

        Returns:
            Domain Transaction entity if found, None otherwise
        """
        pass

    @abstractmethod
    def update(self, transaction_id: uuid.UUID, update_data: Dict[str, Any]) -> bool:
        """
        Update transaction by ID

        Args:
            transaction_id: UUID of the transaction
            update_data: Dictionary with fields to update

        Returns:
            True if updated successfully, False if not found
        """
        pass

    @abstractmethod
    def get_by_document_id(
        self, document_id: uuid.UUID = None
    ) -> List[TransactionEntity]:
        """
        Get all transactions with optional filters

        Args:
            document_id: document UUID filter

        Returns:
            List of TransactionEntity including category_name
        """
        pass

    @abstractmethod
    def get_by_unique_identifier(
        self, unique_identifier: str
    ) -> Optional[TransactionEntity]:
        """
        Get transaction by unique_identifier

        Args:
            unique_identifier: Unique identifier string

        Returns:
            Domain Transaction entity if found, None otherwise
        """
        pass


class IDocumentTypeDbGateway(ABC):

    @abstractmethod
    def get_by_name(self, name: str) -> DocumentTypeEntity | None:
        pass

    @abstractmethod
    def get_all(self) -> list[DocumentTypeEntity]:
        pass
