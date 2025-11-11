"""
Database models based on UML diagram
"""
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlmodel import Field, Relationship, SQLModel, Column, Text
from sqlalchemy import JSON
from enum import Enum


# Enums
class CustomerType(str, Enum):
    INDIVIDUAL = "individual"
    BUSINESS = "business"


class DocumentType(str, Enum):
    BCP_STATEMENT = "bcp_statement"
    DEBIT_STATEMENT = "debit_statement"
    CREDIT_STATEMENT = "credit_statement"


class Currency(str, Enum):
    PEN = "PEN"  # Soles
    USD = "USD"  # Dólares


# Shared properties
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    customer_type: CustomerType = Field(default=CustomerType.INDIVIDUAL)


class User(UserBase, table=True):
    __tablename__ = "users"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    documents: List["Document"] = Relationship(back_populates="user")
    transactions: List["Transaction"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class UserUpdate(SQLModel):
    email: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None
    customer_type: Optional[CustomerType] = None


# Category Model
class CategoryBase(SQLModel):
    name: str = Field(max_length=255, index=True)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))


class Category(CategoryBase, table=True):
    __tablename__ = "categories"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    # Self-referencing for subcategories
    parent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="categories.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    parent: Optional["Category"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Category.id"}
    )
    children: List["Category"] = Relationship(back_populates="parent")
    transactions: List["Transaction"] = Relationship(back_populates="category")


class CategoryCreate(CategoryBase):
    parent_id: Optional[uuid.UUID] = None


class CategoryRead(CategoryBase):
    id: uuid.UUID
    parent_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime


class CategoryUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None


# Document Model
class DocumentBase(SQLModel):
    account_number: str = Field(max_length=255, index=True)
    type: DocumentType
    currency: Currency = Field(default=Currency.PEN)
    data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))  # JSON data from PDF


class Document(DocumentBase, table=True):
    __tablename__ = "documents"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    user_id: uuid.UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="documents")
    transactions: List["Transaction"] = Relationship(back_populates="document")


class DocumentCreate(DocumentBase):
    user_id: uuid.UUID


class DocumentRead(DocumentBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class DocumentUpdate(SQLModel):
    account_number: Optional[str] = None
    type: Optional[DocumentType] = None
    currency: Optional[Currency] = None
    data: Optional[str] = None


# Transaction Model
class TransactionBase(SQLModel):
    name: str = Field(max_length=255)  # ID único de transacción (ej: EECC102025_4280820000002148_1)
    amount: float
    currency: Currency = Field(default=Currency.PEN)
    description: str = Field(sa_column=Column(Text))
    fecha_proceso: Optional[str] = Field(default=None, max_length=20)
    fecha_consumo: Optional[str] = Field(default=None, max_length=20)
    tipo_operacion: Optional[str] = Field(default=None, max_length=50)


class Transaction(TransactionBase, table=True):
    __tablename__ = "transactions"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    user_id: uuid.UUID = Field(foreign_key="users.id")
    document_id: uuid.UUID = Field(foreign_key="documents.id")
    category_id: Optional[uuid.UUID] = Field(default=None, foreign_key="categories.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="transactions")
    document: Document = Relationship(back_populates="transactions")
    category: Optional[Category] = Relationship(back_populates="transactions")


class TransactionCreate(TransactionBase):
    user_id: uuid.UUID
    document_id: uuid.UUID
    category_id: Optional[uuid.UUID] = None


class TransactionRead(TransactionBase):
    id: uuid.UUID
    user_id: uuid.UUID
    document_id: uuid.UUID
    category_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime


class TransactionUpdate(SQLModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[Currency] = None
    description: Optional[str] = None
    fecha_proceso: Optional[str] = None
    fecha_consumo: Optional[str] = None
    tipo_operacion: Optional[str] = None
    category_id: Optional[uuid.UUID] = None