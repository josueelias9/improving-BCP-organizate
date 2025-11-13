from abc import ABC, abstractmethod
from typing import BinaryIO, List
from ..Ddomain.entities import Transaction, ExtractionResult


class PDFExtractorRepository(ABC):
    """Abstract repository for PDF extraction operations"""
    
    @abstractmethod
    def extract_transactions(self, pdf_file: BinaryIO, filename: str) -> ExtractionResult:
        """Extract transactions from PDF file"""
        pass
