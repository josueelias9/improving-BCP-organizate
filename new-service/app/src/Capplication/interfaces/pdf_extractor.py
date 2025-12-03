"""
Gateway Interfaces - Enterprise Layer
Defines contracts for data access without implementation details
"""
from abc import ABC, abstractmethod
from typing import BinaryIO
from src.Denterprise.entities import ExtractionResult


class PDFExtractorGateway(ABC):
    """Abstract gateway for PDF extraction operations"""
    
    @abstractmethod
    def extract_transactions(self, pdf_file: BinaryIO, filename: str) -> ExtractionResult:
        """Extract transactions from PDF file"""
        pass

