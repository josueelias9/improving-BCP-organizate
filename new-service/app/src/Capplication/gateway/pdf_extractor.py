"""Gateway Interfaces - Enterprise Layer
Defines contracts for data access without implementation details
"""

from abc import ABC, abstractmethod
from typing import BinaryIO
from src.Capplication.DTO.entity_dto import DTOExtractionResult


class PDFExtractorGateway(ABC):
    """Abstract gateway for PDF extraction operations"""

    @abstractmethod
    def extract_transactions(
        self, pdf_file: BinaryIO, filename: str
    ) -> DTOExtractionResult:
        """Extract transactions from PDF file and return DTO with extracted data"""
        pass
