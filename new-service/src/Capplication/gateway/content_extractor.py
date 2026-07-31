"""Gateway Interfaces - Application Layer
Defines contracts for data access without implementation details
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Optional


class IStatementParser(ABC):
    """Abstract interface for parsing document text into structured data."""

    @abstractmethod
    def get_data(self, full_text: str) -> dict[str, Any]:
        """Parse document text and return extracted data.

        Args:
            full_text: Extracted text from the source document

        Returns:
            Dictionary with extracted data
        """
        pass

    @abstractmethod
    def get_unique_identifier(self) -> Optional[str]:
        """Extract unique identifier from the document text.

        Returns:
            Unique identifier as a string, or None if not found
        """
        pass

    @abstractmethod
    def get_initial_day(self, full_text: str) -> Optional[date]:
        pass

    @abstractmethod
    def get_final_day(self, full_text: str) -> Optional[date]:
        pass
