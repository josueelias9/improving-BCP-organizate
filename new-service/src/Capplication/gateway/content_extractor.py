"""Gateway Interfaces - Application Layer
Defines contracts for data access without implementation details
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Optional


class IStatementParser(ABC):
    """Abstract interface for parsing document text into structured data."""

    @abstractmethod
    def get_data(
        self,
        full_text: str,
    ) -> tuple[dict[str, Any], str, Optional[date], Optional[date]]:
        """Parse document text and return extracted data.

        Args:
            full_text: Extracted text from the source document

        Returns:
            Tuple with extracted data, unique identifier, start date and end date
        """
        pass

