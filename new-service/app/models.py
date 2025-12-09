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
class CustomerType(str, Enum):
    INDIVIDUAL = "individual"
    BUSINESS = "business"


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"



# ============================================================================= entities

class DocumentTypeBase(SQLModel):
    name: str = Field(max_length=100, unique=True, index=True)



class UserBase(SQLModel):
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    customer_type: CustomerType = Field(default=CustomerType.INDIVIDUAL)

class CategoryBase(SQLModel):
    name: str = Field(max_length=255, index=True)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))


class DocumentBase(SQLModel):
    data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))  # Contains account_number, previous_balance, initial_day, final_day, and transactions list
    currency: str = Field(default="")
    unique_identifier: Optional[str] = Field(default=None, max_length=500)
    processed: bool = Field(default=False)

class TransactionBase(SQLModel):
    order: int
    description: str = Field(max_length=255)
    history: Optional[str] = Field(default=None)
    amount: float
    transaction_type: TransactionType
    transaction_date: Optional[date] = Field(default=None)  # fecha_consumo
    unique_identifier: Optional[str] = Field(default=None, max_length=500)


# ============================================================================= db


class DocumentType(DocumentTypeBase, table=True):
    __tablename__ = "document_types"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    
    # Relationships
    documents: List["Document"] = Relationship(back_populates="document_type")


class User(UserBase, table=True):
    __tablename__ = "users"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    
    # Relationships
    documents: List["Document"] = Relationship(back_populates="user")




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
    
    # Relationships
    parent: Optional["Category"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Category.id"}
    )
    children: List["Category"] = Relationship(back_populates="parent")
    transactions: List["Transaction"] = Relationship(back_populates="category")


class Document(DocumentBase, table=True):
    __tablename__ = "documents"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
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
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    document_id: uuid.UUID = Field(foreign_key="documents.id")
    category_id: Optional[uuid.UUID] = Field(default=None, foreign_key="categories.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    document: Document = Relationship(back_populates="transactions")
    category: Optional[Category] = Relationship(back_populates="transactions")




# ============================================================================= DTO


class UserCreate(UserBase):
    pass

class DocumentCreate(DocumentBase):
    user_id: uuid.UUID
    document_type_id: uuid.UUID


class UserUpdate(SQLModel):
    email: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None
    customer_type: Optional[CustomerType] = None


class DocumentUpdate(SQLModel):
    data: Optional[Dict[str, Any]] = None
    currency: Optional[str] = None
    document_type_id: Optional[uuid.UUID] = None
    processed: Optional[bool] = None






class TransactionUpdate(SQLModel):
    """Model for updating transaction fields - only history and category are editable"""
    history: Optional[str] = Field(default=None)
    category_name: Optional[str] = Field(default=None, max_length=255)


class TransactionBatchUpdateItem(SQLModel):
    """Model for a single transaction update in a batch"""
    transaction_id: uuid.UUID
    history: Optional[str] = Field(default=None)
    category_name: Optional[str] = Field(default=None, max_length=255)


class TransactionBatchUpdate(SQLModel):
    """Model for batch updating multiple transactions"""
    updates: List[TransactionBatchUpdateItem] = Field(min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "updates": [
                    {
                        "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
                        "history": "Gasto en supermercado - alimentación"
                    },
                    {
                        "transaction_id": "123e4567-e89b-12d3-a456-426614174001",
                        "history": "Pago de servicios - electricidad"
                    }
                ]
            }
        }
