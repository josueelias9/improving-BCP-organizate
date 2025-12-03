"""
Gateway Interfaces - Enterprise Layer
Defines contracts for data access without implementation details
"""
import uuid
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict, Any
from src.Denterprise.transaction_service import TransactionData, DocumentData



class IDocumentGateway(ABC):
    """Interface for document persistence operations"""
    
    @abstractmethod
    def get_by_id(self, document_id: uuid.UUID) -> DocumentData:
        """
        Retrieve document by ID
        
        Raises:
            ValueError: If document not found
        """
        pass
    
    @abstractmethod
    def mark_as_processed(self, document_id: uuid.UUID) -> None:
        """Mark document as processed"""
        pass
    
    @abstractmethod
    def get_by_unique_identifier(self, unique_identifier: str):
        """
        Get document by unique identifier
        
        Returns:
            Document if found, None otherwise
        """
        pass
    
    @abstractmethod
    def create(self, document):
        """
        Create a new document
        
        Returns:
            Created document
        """
        pass


class IUserGateway(ABC):
    """Interface for user persistence operations"""
    
    @abstractmethod
    def get_by_email(self, email: str):
        """
        Get user by email
        
        Returns:
            User if found, None otherwise
        """
        pass
    
    @abstractmethod
    def create(self, user_data):
        """
        Create a new user
        
        Returns:
            Created user
        """
        pass


class ICategoryGateway(ABC):
    """Interface for category persistence operations"""
    
    @abstractmethod
    def get_by_name(self, name: str):
        """
        Get category by name
        
        Returns:
            Category if found, None otherwise
        """
        pass


class ITransactionGateway(ABC):
    """Interface for transaction persistence operations"""
    
    @abstractmethod
    def save_batch(
        self, 
        transactions: List[TransactionData],
        document_id: uuid.UUID
    ) -> Tuple[int, int, List[str]]:
        """
        Save multiple transactions
        
        Returns:
            Tuple of (loaded_count, skipped_count, errors)
        """
        pass
    
    @abstractmethod
    def get_by_id(self, transaction_id: uuid.UUID) -> Optional[TransactionData]:
        """
        Get transaction by ID
        
        Returns:
            TransactionData if found, None otherwise
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
