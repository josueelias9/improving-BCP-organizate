from datetime import date
from typing import Optional, Dict, Any
from enum import Enum


# Enums
class CustomerType(str, Enum):
    INDIVIDUAL = "individual"
    BUSINESS = "business"


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


# ==============================================


class DocumentTypeEntity():
    name: str

class UserEntity():
    email: str
    name: str
    is_active: bool
    customer_type: CustomerType

class TransactionEntity():
    order: int
    description: str
    history: Optional[str]
    amount: float
    transaction_type: TransactionType
    transaction_date: Optional[date]
    unique_identifier: Optional[str]


class CategoryEntity():
    name: str
    description: Optional[str]


class DocumentEntity():
    data: Optional[Dict[str, Any]]  # Contains account_number, previous_balance, initial_day, final_day, and transactions list
    currency: str
    unique_identifier: Optional[str]
    processed: bool
