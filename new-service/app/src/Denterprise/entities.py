from datetime import date
from typing import Optional, Dict, Any
from sqlmodel import Field, SQLModel, Column, Text
from sqlalchemy import JSON
from enum import Enum


# Enums
class CustomerType(str, Enum):
    INDIVIDUAL = "individual"
    BUSINESS = "business"


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


# ==============================================


class DocumentTypeBase(SQLModel):
    name: str = Field(max_length=100, unique=True, index=True)

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    customer_type: CustomerType = Field(default=CustomerType.INDIVIDUAL)

class TransactionBase(SQLModel):
    order: int
    description: str = Field(max_length=255)
    history: Optional[str] = Field(default=None)
    amount: float
    transaction_type: TransactionType
    transaction_date: Optional[date] = Field(default=None)  # fecha_consumo
    unique_identifier: Optional[str] = Field(default=None, max_length=500)


class CategoryBase(SQLModel):
    name: str = Field(max_length=255, index=True)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))


class DocumentBase(SQLModel):
    data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))  # Contains account_number, previous_balance, initial_day, final_day, and transactions list
    currency: str = Field(default="")
    unique_identifier: Optional[str] = Field(default=None, max_length=500)
    processed: bool = Field(default=False)

