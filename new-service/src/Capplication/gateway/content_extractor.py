"""Gateway Interfaces - Application Layer
Defines contracts for data access without implementation details
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from src.Denterprise.entities import TransactionEntity


class IStatementParser(ABC):
    """Abstract interface for parsing document text into structured data."""

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """File extension handled by this parser (e.g. '.pdf', '.xlsx')."""
        pass

    @abstractmethod
    def read_file(self, file_content: bytes) -> str:
        """Convert raw file bytes to a plain-text or serialised-text representation.

        Args:
            file_content: Raw bytes of the source file (PDF, XLSX, …)

        Returns:
            Text representation suitable for the other parser methods
        """
        pass

    @abstractmethod
    def get_transactions(self, full_text: str) -> List[TransactionEntity]:
        """Parse document text and return transaction entities.

        Args:
            full_text: Extracted text from the source document

        Returns:
            List of TransactionEntity objects
        """
        pass

    @abstractmethod
    def get_initial_day(self, full_text: str) -> Optional[date]:
        pass

    @abstractmethod
    def get_final_day(self, full_text: str) -> Optional[date]:
        pass

    @abstractmethod
    def get_balance(self, full_text: str) -> Optional[float]:
        pass

    @abstractmethod
    def get_account(self, full_text: str) -> Optional[str]:
        pass