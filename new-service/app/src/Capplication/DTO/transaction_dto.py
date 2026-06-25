"""
Transaction DTOs - Data Transfer Objects
Used ONLY for transferring data between controllers and use cases (boundary layer)

These DTOs serve as request/response objects at the interface adapter layer.
Internal domain logic uses entities from Denterprise layer.
"""

import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class DTOBatchUpdateRequest(BaseModel):
    """Single transaction update item - DTO for batch update request"""

    transaction_id: uuid.UUID
    history: str
    category_name: str = None


class DTOBatchUpdateResponse(BaseModel):
    """Result DTO for batch update operation - returned from use case to controller"""

    total: int
    updated: int
    failed: int
    errors: List[Dict[str, Any]]


# ===========================================================


class DTOExportTransactionsRequest(BaseModel):
    """Filter criteria DTO for transaction export - request from controller to use case"""

    month: Optional[str] = None  # Format: YYYY-MM
    document_id: Optional[uuid.UUID] = None
    output_dir: str = (
        "/shared_files/output"  # Directory where to save the exported file
    )


class DTOExportTransactionsResponse(BaseModel):
    """Result DTO for export transactions operation - returned from use case to controller"""

    success: bool
    csv_content: str
    filename: str
    transaction_count: int
    file_path: Optional[str] = None
    month: Optional[str] = None
    document_id: Optional[uuid.UUID] = None
    error_message: Optional[str] = None


# ===========================================================


class DTOImportTransactionsFromCsvRequest(BaseModel):
    """DTO for import transactions request - from controller to use case"""

    csv_filename: Optional[str] = None  # Specific CSV filename to import
    input_dir: str = "/shared_files/output"  # Directory where to read the CSV file from


class DTOImportTransactionsFromCsvResponse(BaseModel):
    """Result DTO for import transactions operation - returned from use case to controller"""

    success: bool
    updated_count: int
    skipped_count: int
    errors: List[str]
    total_rows: int
    message: str


# ===========================================================


class DTOGetAllTransactionsResponse(BaseModel):
    """DTO for get all transactions response"""

    transactions: List[Dict[str, Any]]
