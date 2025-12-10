"""Gateway Interfaces - Application Layer
Defines contracts for data access without implementation details
"""

from abc import ABC, abstractmethod
from typing import BinaryIO
from src.Denterprise.entities import ExtractionResultEntity


class PDFExtractorGateway(ABC):
    """Abstract gateway for PDF extraction operations"""

    @abstractmethod
    def extract_transactions(
        self, pdf_file: BinaryIO, filename: str
    ) -> ExtractionResultEntity:
        """Extract transactions from PDF file and return entity with extracted data"""
        pass
