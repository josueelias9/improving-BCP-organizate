"""
Transaction DTOs - Data Transfer Objects
Used for transferring transaction data between layers
"""
import uuid
from datetime import date
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class DTOTransactionData:
    """Data structure for transaction information"""
    order: int
    description: str
    history: Optional[str]
    amount: float
    transaction_type: str  # 'income' or 'expense'
    transaction_date: Optional[date]  # fecha_consumo
    unique_identifier: Optional[str] = None


@dataclass
class DTOLoadTransactionsResult:
    """Result of loading transactions operation"""
    success: bool
    loaded_count: int
    skipped_count: int
    errors: List[str]
    total_records: int


@dataclass
class DTOBatchUpdateItem:
    """Single transaction update item"""
    transaction_id: uuid.UUID
    history: str
    category_name: str = None


@dataclass
class DTOBatchUpdateResult:
    """Result of batch update operation"""
    total: int
    updated: int
    failed: int
    errors: List[Dict[str, Any]]


@dataclass
class DTOExportFilter:
    """Filter criteria for transaction export"""
    month: Optional[str] = None  # Format: YYYY-MM
    document_id: Optional[uuid.UUID] = None


@dataclass
class DTOExportTransactionsResult:
    """Result of export transactions operation"""
    success: bool
    csv_content: str
    filename: str
    transaction_count: int
    error_message: Optional[str] = None


@dataclass
class DTOImportTransactionsResult:
    """Result of import transactions operation"""
    success: bool
    updated_count: int
    skipped_count: int
    errors: List[str]
    total_rows: int
    message: str
