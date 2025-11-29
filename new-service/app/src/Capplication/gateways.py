"""
Gateway Interfaces - Enterprise Layer
Defines contracts for data access without implementation details
"""
import uuid
from abc import ABC, abstractmethod
from typing import BinaryIO, List, Tuple, Optional
from src.Denterprise.entities import Transaction, ExtractionResult
from src.Denterprise.transaction_service import TransactionData, DocumentData


class PDFExtractorGateway(ABC):
    """Abstract gateway for PDF extraction operations"""
    
    @abstractmethod
    def extract_transactions(self, pdf_file: BinaryIO, filename: str) -> ExtractionResult:
        """Extract transactions from PDF file"""
        pass


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
    def update(self, transaction_id: uuid.UUID, transaction_data: TransactionData) -> bool:
        """
        Update transaction by ID
        
        Returns:
            True if updated successfully, False if not found
        """
        pass
