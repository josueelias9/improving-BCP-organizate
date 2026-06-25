"""
Database models based on UML diagram
"""

import uuid
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlmodel import Field, Relationship, SQLModel, Column, Text
from sqlalchemy import JSON
from enum import Enum


# Enums
class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


# ============================================================================= base models
# 1. it was decided to delete all classes that behave as DTOs and are not used for persistence. They were moved to the src.Capplication.DTO module.
# 2. this block was names as "entities", but it is not correct, because these classes are not domain entities, they are base database models. Base because it helped to avoid code duplication in table models and DTO models
# 3. It seems that the best final approach is to delete all these base models and move the features inside the table models

class DocumentTypeBase(SQLModel):
    name: str = Field(max_length=100, unique=True, index=True)


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)
    is_active: bool = Field(default=True)


class CategoryBase(SQLModel):
    name: str = Field(max_length=255, index=True)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))


class DocumentBase(SQLModel):
    data: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )  # Contains account_number, previous_balance, initial_day, final_day, and transactions list
    unique_identifier: Optional[str] = Field(default=None, max_length=500)
    processed: bool = Field(default=False)
    start_date: Optional[date] = Field(default=None)
    end_date: Optional[date] = Field(default=None)


class TransactionBase(SQLModel):
    order: int
    description: str = Field(max_length=255)
    history: Optional[str] = Field(default=None)
    amount: float
    transaction_type: TransactionType
    transaction_date: Optional[date] = Field(default=None)  # fecha_consumo
    currency: str = Field(default="")
    unique_identifier: Optional[str] = Field(default=None, max_length=500)


# ============================================================================= db


class DocumentType(DocumentTypeBase, table=True):
    __tablename__ = "document_types"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False
    )

    # Relationships
    documents: List["Document"] = Relationship(back_populates="document_type")


class User(UserBase, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False
    )

    # Relationships
    documents: List["Document"] = Relationship(back_populates="user")


class Category(CategoryBase, table=True):
    __tablename__ = "categories"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False
    )
    # Self-referencing for subcategories
    parent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="categories.id")

    # Relationships
    parent: Optional["Category"] = Relationship(
        back_populates="children", sa_relationship_kwargs={"remote_side": "Category.id"}
    )
    children: List["Category"] = Relationship(back_populates="parent")
    transactions: List["Transaction"] = Relationship(back_populates="category")


class Document(DocumentBase, table=True):
    __tablename__ = "documents"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False
    )
    user_id: uuid.UUID = Field(foreign_key="users.id")
    document_type_id: uuid.UUID = Field(foreign_key="document_types.id")

    # Relationships
    user: User = Relationship(back_populates="documents")
    document_type: "DocumentType" = Relationship(back_populates="documents")
    transactions: List["Transaction"] = Relationship(back_populates="document")


class Transaction(TransactionBase, table=True):
    __tablename__ = "transactions"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False
    )
    document_id: uuid.UUID = Field(foreign_key="documents.id")
    category_id: Optional[uuid.UUID] = Field(default=None, foreign_key="categories.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    document: Document = Relationship(back_populates="transactions")
    category: Optional[Category] = Relationship(back_populates="transactions")
