from datetime import date
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid


# Enums
class CustomerType(str, Enum):
    INDIVIDUAL = "individual"
    BUSINESS = "business"


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


# ==============================================
# Domain Entities - Enterprise Business Rules
# ==============================================


class DocumentTypeEntity:
    """Document type entity"""

    def __init__(self, id: Optional[uuid.UUID] = None, name: str = ""):
        self.id = id
        self.name = name


class UserEntity:
    """User entity"""

    def __init__(
        self,
        id: Optional[uuid.UUID] = None,
        email: str = "",
        name: str = "",
        is_active: bool = True,
        customer_type: CustomerType = CustomerType.INDIVIDUAL,
    ):
        self.id = id
        self.email = email
        self.name = name
        self.is_active = is_active
        self.customer_type = customer_type


class TransactionEntity:
    """Transaction entity - represents a bank transaction"""

    def __init__(
        self,
        id: Optional[uuid.UUID] = None,
        order: int = 0,
        description: str = "",
        history: Optional[str] = None,
        amount: float = 0.0,
        transaction_type: str = "",
        transaction_date: Optional[date] = None,
        unique_identifier: Optional[str] = None,
        category_id: Optional[uuid.UUID] = None,
        document_id: Optional[uuid.UUID] = None,
    ):
        self.id = id
        self.order = order
        self.description = description
        self.history = history
        self.amount = amount
        self.transaction_type = transaction_type
        self.transaction_date = transaction_date
        self.unique_identifier = unique_identifier
        self.category_id = category_id
        self.document_id = document_id

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


class CategoryEntity:
    """Category entity"""

    def __init__(
        self,
        id: Optional[uuid.UUID] = None,
        name: str = "",
        description: Optional[str] = None,
        parent_id: Optional[uuid.UUID] = None,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.parent_id = parent_id


class DocumentEntity:
    """Document entity - represents a financial document"""

    def __init__(
        self,
        id: Optional[uuid.UUID] = None,
        data: Optional[List[Dict[str, Any]]] = None,
        currency: str = "",
        unique_identifier: Optional[str] = None,
        processed: bool = False,
        user_id: Optional[uuid.UUID] = None,
        document_type_id: Optional[uuid.UUID] = None,
    ):
        self.id = id
        self.data = data or []
        self.currency = currency
        self.unique_identifier = unique_identifier
        self.processed = processed
        self.user_id = user_id
        self.document_type_id = document_type_id
