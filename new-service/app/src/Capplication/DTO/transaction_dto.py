"""
Transaction DTOs - Data Transfer Objects
Used ONLY for transferring data between controllers and use cases (boundary layer)

These DTOs serve as request/response objects at the interface adapter layer.
Internal domain logic uses entities from Denterprise layer.
"""

import uuid
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class DTOBatchUpdateRequest:
    """Single transaction update item - DTO for batch update request"""

    transaction_id: uuid.UUID
    history: str
    category_name: str = None


@dataclass
class DTOBatchUpdateResponse:
    """Result DTO for batch update operation - returned from use case to controller"""

    total: int
    updated: int
    failed: int
    errors: List[Dict[str, Any]]


@dataclass
class DTOExportTransactionsRequest:
    """Filter criteria DTO for transaction export - request from controller to use case"""

    month: Optional[str] = None  # Format: YYYY-MM
    document_id: Optional[uuid.UUID] = None


@dataclass
class DTOExportTransactionsResponse:
    """Result DTO for export transactions operation - returned from use case to controller"""

    success: bool
    csv_content: str
    filename: str
    transaction_count: int
    file_path: Optional[str] = None
    month: Optional[str] = None
    document_id: Optional[uuid.UUID] = None
    error_message: Optional[str] = None


@dataclass
class DTOImportTransactionsFromCsvRequest:
    """DTO for import transactions request - from controller to use case"""

    csv_filename: Optional[str] = None  # Specific CSV filename to import


@dataclass
class DTOImportTransactionsFromCsvResponse:
    """Result DTO for import transactions operation - returned from use case to controller"""

    success: bool
    updated_count: int
    skipped_count: int
    errors: List[str]
    total_rows: int
    message: str


@dataclass
class DTOGetAllTransactionsResponse:
    """DTO for get all transactions response"""

    transactions: List[Dict[str, Any]]
