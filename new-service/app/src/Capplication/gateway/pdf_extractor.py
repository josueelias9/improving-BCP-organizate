"""Gateway Interfaces - Application Layer
Defines contracts for data access without implementation details
"""

from abc import ABC, abstractmethod
from typing import BinaryIO, Optional
from src.Denterprise.entities import DocumentEntity


class IPDFExtractorGateway(ABC):
    """Abstract gateway for PDF extraction operations"""

    @abstractmethod
    def extract_document(
        self,
        pdf_file: BinaryIO,
        filename: str = "",
        document_type_id: Optional[str] = None,
    ) -> DocumentEntity:
        """Extract transactions from PDF file and return entity with extracted data"""
        pass
