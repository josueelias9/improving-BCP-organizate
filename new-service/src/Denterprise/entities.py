import hashlib
from datetime import date, datetime
from typing import Optional, List
from enum import Enum
from dataclasses import dataclass
import uuid

# Enums


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    SOL = "SOL"


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
    transaction_date: Optional[datetime] = None
    # TODO: currency is not being validated. Maybe pyndantic could fix this
    currency: Currency = None
    unique_identifier: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    document_id: Optional[str] = None
    id: Optional[uuid.UUID] = None
    category_name: Optional[str] = None
    document_document_format_name: Optional[str] = None
    document_unique_identifier: Optional[str] = None

    def generate_unique_identifier(self) -> str:
        """Generate unique identifier for the transaction

        Format: {order}__{transaction_date}__{amount}__{transaction_type}__{description}

        Returns:
            Unique identifier string
        """
        self.unique_identifier = f"{self.transaction_type}__{self.transaction_date.strftime('%Y-%m-%dT%H:%M:%S')}__{self.order}__{self.amount}__{self.description}"


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

    account: Optional[str] = None
    balance: Optional[float] = None
    processed: bool = False
    registration_date: Optional[date] = None
    user_id: Optional[uuid.UUID] = None
    document_type_id: Optional[uuid.UUID] = None
    id: Optional[str] = None
    plain_text: Optional[str] = None
    document_format_name: Optional[str] = None

    def generate_id(self):
        self.id = hashlib.sha256(self.plain_text.encode()).hexdigest()


# con respecto al unique identifier
# - es algo que caracteriza al doucmento/transaccion
# - no puede ser sacado en base al id porque es es autogenerado y puede variar para un mismo doucmento/transaccion
# - tiene que contener informacion propia del doucmento/transaccion
