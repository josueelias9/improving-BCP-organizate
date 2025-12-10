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


class BCPTransactionEntity:
    """BCP Transaction entity - represents a bank transaction from BCP statement"""

    def __init__(
        self,
        fecha_proceso: Optional[date] = None,
        fecha_valor: Optional[date] = None,
        description: Optional[str] = None,
        cargos: float = 0.0,
        abonos: float = 0.0,
        internal_transaction: Optional[str] = None,
    ):
        self.fecha_proceso = fecha_proceso
        self.fecha_valor = fecha_valor
        self.description = description
        self.cargos = cargos
        self.abonos = abonos
        self.internal_transaction = internal_transaction

    def is_valid(self) -> bool:
        """Check if transaction has meaningful data"""
        return (
            (self.description and self.description.strip())
            or self.cargos != 0.0
            or self.abonos != 0.0
        )

    def to_transaction_type_and_amount(self) -> tuple[str, float]:
        """Convert cargos/abonos to type and amount"""
        if self.cargos == 0.0:
            return ("income", self.abonos)
        else:
            return ("expense", self.cargos)


class ExtractionResultEntity:
    """Entity representing the result of PDF extraction"""

    def __init__(
        self,
        filename: str = "",
        transactions: Optional[List[BCPTransactionEntity]] = None,
        total_transactions: int = 0,
        success: bool = False,
        error_message: Optional[str] = None,
        extracted_text: Optional[str] = None,
        account_code: Optional[str] = None,
        currency: Optional[str] = None,
        saldo_anterior: Optional[float] = None,
        initial_day: Optional[date] = None,
        final_day: Optional[date] = None,
    ):
        self.filename = filename
        self.transactions = transactions or []
        self.total_transactions = total_transactions
        self.success = success
        self.error_message = error_message
        self.extracted_text = extracted_text
        self.account_code = account_code
        self.currency = currency
        self.saldo_anterior = saldo_anterior
        self.initial_day = initial_day
        self.final_day = final_day
