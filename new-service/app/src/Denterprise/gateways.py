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
