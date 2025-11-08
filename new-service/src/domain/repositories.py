from abc import ABC, abstractmethod
from typing import BinaryIO, List
from ..domain.entities import Transaction, ExtractionResult


class PDFExtractorRepository(ABC):
    """Abstract repository for PDF extraction operations"""
    
    @abstractmethod
    def extract_transactions(self, pdf_file: BinaryIO, filename: str) -> ExtractionResult:
        """Extract transactions from PDF file"""
        pass


class ExcelGeneratorRepository(ABC):
    """Abstract repository for Excel generation operations"""
    
    @abstractmethod
    def generate_excel(self, transactions: List[Transaction], filename: str) -> BinaryIO:
        """Generate Excel file from transactions"""
        pass