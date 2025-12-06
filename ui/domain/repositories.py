"""
Domain Repositories - Interfaces for data access
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities import Transaction, Category


class TransactionRepository(ABC):
    """Interface for transaction data access"""
    
    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 1000) -> List[Transaction]:
        """Get all transactions"""
        pass
    
    @abstractmethod
    def update(self, transaction_id: str, history: Optional[str], category_name: Optional[str]) -> dict:
        """Update a transaction"""
        pass
    
    @abstractmethod
    def batch_update(self, updates: List[dict]) -> dict:
        """Update multiple transactions"""
        pass


class CategoryRepository(ABC):
    """Interface for category data access"""
    
    @abstractmethod
    def get_all(self) -> List[Category]:
        """Get all categories"""
        pass


class FileRepository(ABC):
    """Interface for file storage"""
    
    @abstractmethod
    def save_file(self, file_content: bytes, filename: str) -> str:
        """Save file and return path"""
        pass
    
    @abstractmethod
    def get_single_file_path(self) -> Optional[str]:
        """Get the path of the single file in the directory"""
        pass


class PdfProcessingRepository(ABC):
    """Interface for PDF processing"""
    
    @abstractmethod
    def process_pdf(self, pdf_filename: str, doc_type: str, user_email: str) -> dict:
        """Process PDF file"""
        pass
