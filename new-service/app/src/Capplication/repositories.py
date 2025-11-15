"""
Repository interfaces (abstractions) for Clean Architecture
These define contracts that framework implementations must fulfill
"""
import uuid
from abc import ABC, abstractmethod
from typing import List, Optional
from sqlmodel import Session

from models import (
    User, UserCreate, UserUpdate,
    Document, DocumentCreate, DocumentUpdate,
    Category, CategoryCreate, CategoryUpdate,
    Transaction, TransactionCreate, TransactionUpdate
)


class IUserRepository(ABC):
    """User repository interface"""
    
    @abstractmethod
    def create_user(self, session: Session, user_create: UserCreate) -> User:
        pass
    
    @abstractmethod
    def get_user(self, session: Session, user_id: uuid.UUID) -> Optional[User]:
        pass
    
    @abstractmethod
    def get_user_by_email(self, session: Session, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def get_all_users(self, session: Session, skip: int = 0, limit: int = 100) -> List[User]:
        pass
    
    @abstractmethod
    def update_user(self, session: Session, user_id: uuid.UUID, user_update: UserUpdate) -> Optional[User]:
        pass
    
    @abstractmethod
    def delete_user(self, session: Session, user_id: uuid.UUID) -> bool:
        pass
    
    @abstractmethod
    def user_exists(self, session: Session, email: str) -> bool:
        pass


class IDocumentRepository(ABC):
    """Document repository interface"""
    
    @abstractmethod
    def create_document(self, session: Session, document_create: DocumentCreate) -> Document:
        pass
    
    @abstractmethod
    def get_document(self, session: Session, document_id: uuid.UUID) -> Optional[Document]:
        pass
    
    @abstractmethod
    def get_documents_by_user(self, session: Session, user_id: uuid.UUID) -> List[Document]:
        pass
    
    @abstractmethod
    def get_document_by_filename(self, session: Session, filename: str) -> Optional[Document]:
        pass
    
    @abstractmethod
    def update_document(self, session: Session, document_id: uuid.UUID, document_update: DocumentUpdate) -> Optional[Document]:
        pass
    
    @abstractmethod
    def delete_document(self, session: Session, document_id: uuid.UUID) -> bool:
        pass


class ICategoryRepository(ABC):
    """Category repository interface"""
    
    @abstractmethod
    def create_category(self, session: Session, category_create: CategoryCreate) -> Category:
        pass
    
    @abstractmethod
    def get_category(self, session: Session, category_id: uuid.UUID) -> Optional[Category]:
        pass
    
    @abstractmethod
    def get_category_by_name(self, session: Session, name: str) -> Optional[Category]:
        pass
    
    @abstractmethod
    def get_all_categories(self, session: Session) -> List[Category]:
        pass
    
    @abstractmethod
    def get_categories_by_parent(self, session: Session, parent_id: Optional[uuid.UUID]) -> List[Category]:
        pass
    
    @abstractmethod
    def update_category(self, session: Session, category_id: uuid.UUID, category_update: CategoryUpdate) -> Optional[Category]:
        pass
    
    @abstractmethod
    def delete_category(self, session: Session, category_id: uuid.UUID) -> bool:
        pass


class ITransactionRepository(ABC):
    """Transaction repository interface"""
    
    @abstractmethod
    def create_transaction(self, session: Session, transaction_create: TransactionCreate) -> Transaction:
        pass
    
    @abstractmethod
    def create_transactions_bulk(self, session: Session, transactions_create: List[TransactionCreate]) -> List[Transaction]:
        pass
    
    @abstractmethod
    def get_transaction(self, session: Session, transaction_id: uuid.UUID) -> Optional[Transaction]:
        pass
    
    @abstractmethod
    def get_transactions_by_user(self, session: Session, user_id: uuid.UUID) -> List[Transaction]:
        pass
    
    @abstractmethod
    def get_transactions_by_document(self, session: Session, document_id: uuid.UUID) -> List[Transaction]:
        pass
    
    @abstractmethod
    def update_transaction(self, session: Session, transaction_id: uuid.UUID, transaction_update: TransactionUpdate) -> Optional[Transaction]:
        pass
    
    @abstractmethod
    def delete_transaction(self, session: Session, transaction_id: uuid.UUID) -> bool:
        pass