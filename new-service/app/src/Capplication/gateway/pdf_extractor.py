"""Gateway Interfaces - Application Layer
Defines contracts for data access without implementation details
"""

from abc import ABC, abstractmethod
from typing import Optional
from src.Denterprise.entities import DocumentEntity


class IPDFExtractorGateway(ABC):
    """Abstract gateway for PDF extraction operations"""

    @abstractmethod
    def extract_document(
        self,
        pdf_content: bytes,
        document_type: Optional[str] = None,
    ) -> DocumentEntity:
        """Extract document from PDF content and return DocumentEntity with data

        Args:
            pdf_content: Binary PDF file content as bytes
            document_type: Type of document (e.g., 'bcp_credit', 'bcp_debit')

        Returns:
            DocumentEntity with extracted transaction data

        Raises:
            ValueError: If PDF cannot be processed
        """
        pass
