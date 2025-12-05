"""
Transaction DTOs - Data Transfer Objects
Used for transferring transaction data between layers
"""
import uuid
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class TransactionData:
    """Data structure for transaction information"""
    description: str
    cargos: float
    abonos: float
    currency: str
    fecha_proceso: Optional[str]
    fecha_consumo: Optional[str]
    internal_transaction: bool
    type: Optional[str]
    order: int
    history: Optional[str] = None


@dataclass
class LoadTransactionsResult:
    """Result of loading transactions operation"""
    success: bool
    loaded_count: int
    skipped_count: int
    errors: List[str]
    total_records: int


@dataclass
class BatchUpdateItem:
    """Single transaction update item"""
    transaction_id: uuid.UUID
    history: str
    category_name: str = None


@dataclass
class BatchUpdateResult:
    """Result of batch update operation"""
    total: int
    updated: int
    failed: int
    errors: List[Dict[str, Any]]


@dataclass
class ExportFilter:
    """Filter criteria for transaction export"""
    month: Optional[str] = None  # Format: YYYY-MM
    document_id: Optional[uuid.UUID] = None


@dataclass
class ExportTransactionsResult:
    """Result of export transactions operation"""
    success: bool
    csv_content: str
    filename: str
    transaction_count: int
    error_message: Optional[str] = None


@dataclass
class ImportTransactionsResult:
    """Result of import transactions operation"""
    success: bool
    updated_count: int
    skipped_count: int
    errors: List[str]
    total_rows: int
    message: str
