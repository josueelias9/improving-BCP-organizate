"""
Transaction DTOs - Data Transfer Objects
Used ONLY for transferring data between controllers and use cases (boundary layer)

These DTOs serve as request/response objects at the interface adapter layer.
Internal domain logic uses entities from Denterprise layer.
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class DTOExportTransactionsRequest(BaseModel):
    """Filter criteria DTO for transaction export - request from controller to use case"""

    document_id: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "document_id": "a1b2fb196c146c4c41f3e84946506d76cf5151594050f9d52aece97d4498f80",
            }
        }
    }


class DTOExportTransactionsResponse(BaseModel):
    """Result DTO for export transactions operation - returned from use case to controller"""

    success: bool
    filename: str
    transaction_count: int
    file_path: Optional[str] = None
    document_id: Optional[str] = None
    error_message: Optional[str] = None


# ===========================================================


class DTOImportTransactionsRequest(BaseModel):
    """DTO for import transactions request - from controller to use case"""

    csv_filename: Optional[str] = None  # Specific CSV filename to import

    model_config = {
        "json_schema_extra": {
            "example": {
                "csv_filename": "transactions_2025-01.csv",
                "input_dir": "/shared_files/output",
            }
        }
    }


class DTOImportTransactionsResponse(BaseModel):
    """Result DTO for import transactions operation - returned from use case to controller"""

    success: bool
    updated_count: int
    skipped_count: int
    errors: List[str]
    total_rows: int
    message: str


# ===========================================================


class DTOTransaction(BaseModel):
    """Read model for a single transaction — no FK/PK fields"""

    model_config = ConfigDict(from_attributes=True)

    order: int
    description: str
    category_name: Optional[str] = None
    history: Optional[str]
    amount: float
    transaction_type: str
    transaction_date: Optional[datetime]
    currency: Optional[str]
    document_document_format_name: Optional[str]
    unique_identifier: Optional[str]
    document_unique_identifier: Optional[str]
    id: Optional[uuid.UUID]


class DTOReadTransactionsResponse(BaseModel):
    """DTO for get all transactions response"""

    transactions: List[DTOTransaction]


# ===========================================================


class DTOUpdateTransactionRequest(BaseModel):
    """DTO for updating a single transaction - request from controller to use case"""

    history: Optional[str] = None
    category_name: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "history": "Compra en supermercado - productos de primera necesidad",
                "category_name": "Food & Dining",
            }
        }
    }


class DTOUpdateTransactionResponse(BaseModel):
    """Result DTO for update transaction operation - returned from use case to controller"""

    transaction_id: str
    updated: bool
    message: str


# ===========================================================


class DTOBatchUpdateRequest(BaseModel):
    """Single transaction update item - DTO for batch category update"""

    transaction_id: uuid.UUID
    category_name: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
                "category_name": "Food & Dining",
            }
        }
    }


class DTOUpdateTransactionsResponse(BaseModel):
    """Result DTO for batch update operation - returned from use case to controller"""

    total: int
    updated: int
    failed: int
    errors: List[Dict[str, Any]]
    message: Optional[str] = None


class DTOUpdateTransactionsRequest(BaseModel):
    """Wrapper DTO for batch update list request - input from controller"""

    updates: List[DTOBatchUpdateRequest]

    model_config = {
        "json_schema_extra": {
            "example": {
                "updates": [
                    {
                        "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
                        "category_name": "Food & Dining",
                    },
                    {
                        "transaction_id": "123e4567-e89b-12d3-a456-426614174001",
                        "category_name": "Utilities",
                    },
                ]
            }
        }
    }


# ==========================================================


class DTOCreateTransactionsRequest(BaseModel):
    document_id: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "document_id": "a1b2fb196c146c4c41f3e84946506d76cf5151594050f9d52aece97d4498f80",
            }
        }
    }


class DTOCreateTransactionsResponse(BaseModel):
    """Result DTO for loading transactions operation - returned from use case to controller"""

    success: bool
    loaded_count: int
    skipped_count: int
    errors: List[str]
    total_records: int
    document_id: str
