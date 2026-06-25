from datetime import date
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass, field
import uuid

# TODO: delete this. There will only be a single type of user
# Enums


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


# ==============================================
# Domain Entities - Enterprise Business Rules
# ==============================================


@dataclass
class DocumentTypeEntity:
    """Document type entity"""

    name: str = ""
    id: Optional[uuid.UUID] = None


@dataclass
class UserEntity:
    """User entity"""

    email: str = ""
    name: str = ""
    is_active: bool = True
    id: Optional[uuid.UUID] = None


@dataclass
class TransactionEntity:
    """Transaction entity - represents a bank transaction"""

    order: int = 0
    description: str = ""
    history: Optional[str] = None
    amount: float = 0.0
    transaction_type: str = ""
    transaction_date: Optional[date] = None
    currency: str = ""
    unique_identifier: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    document_id: Optional[uuid.UUID] = None
    id: Optional[uuid.UUID] = None

    def generate_unique_identifier(self) -> str:
        """Generate unique identifier for the transaction

        Format: {order}__{transaction_date}__{amount}__{transaction_type}__{description}

        Returns:
            Unique identifier string
        """
        date_str = (
            self.transaction_date.strftime("%Y-%m-%d") if self.transaction_date else ""
        )
        return f"{self.order}__{date_str}__{self.amount}__{self.transaction_type}__{self.description}"


@dataclass
class CategoryEntity:
    """Category entity"""

    name: str = ""
    description: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    id: Optional[uuid.UUID] = None


@dataclass
class DocumentEntity:
    """Document entity - represents a financial document"""

    data: List[Dict[str, Any]] = field(default_factory=list)
    unique_identifier: Optional[str] = None
    processed: bool = False
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    user_id: Optional[uuid.UUID] = None
    document_type_id: Optional[uuid.UUID] = None
    id: Optional[uuid.UUID] = None
