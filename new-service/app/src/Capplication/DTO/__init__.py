"""
DTO Package - Data Transfer Objects
Centralized location for all DTOs used across application layers
"""
from .transaction_dto import (
    TransactionData,
    LoadTransactionsResult,
    BatchUpdateItem,
    BatchUpdateResult,
    ExportFilter,
    ExportTransactionsResult,
    ImportTransactionsResult
)

from .document_dto import (
    DocumentData,
    ProcessPDFResult
)

from .entity_dto import (
    Transaction,
    ExtractionResult
)

__all__ = [
    # Transaction DTOs
    'TransactionData',
    'LoadTransactionsResult',
    'BatchUpdateItem',
    'BatchUpdateResult',
    'ExportFilter',
    'ExportTransactionsResult',
    'ImportTransactionsResult',
    # Document DTOs
    'DocumentData',
    'ProcessPDFResult',
    # Entity DTOs
    'Transaction',
    'ExtractionResult',
]
