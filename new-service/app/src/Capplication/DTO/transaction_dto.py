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

    model_config = {
        "json_schema_extra": {
            "example": {
                "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
                "history": "Gasto en supermercado - alimentación",
                "category_name": "Food & Dining",
            }
        }
    }


class DTOBatchUpdateResponse(BaseModel):
    """Result DTO for batch update operation - returned from use case to controller"""

    total: int
    updated: int
    failed: int
    errors: List[Dict[str, Any]]
    message: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "total": 3,
                "updated": 2,
                "failed": 1,
                "errors": [
                    {
                        "transaction_id": "123e4567-e89b-12d3-a456-426614174002",
                        "error": "Category not found",
                    }
                ],
                "message": "Successfully updated 2/3 transactions",
            }
        }
    }


# ===========================================================


class DTOExportTransactionsRequest(BaseModel):
    """Filter criteria DTO for transaction export - request from controller to use case"""

    month: Optional[str] = None  # Format: YYYY-MM
    document_id: Optional[uuid.UUID] = None
    output_dir: str = (
        "/shared_files/output"  # Directory where to save the exported file
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "month": "2025-01",
                "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "output_dir": "/shared_files/output",
            }
        }
    }


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

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "csv_content": "date,description,amount\n2025-01-15,Supermercado,-150.00",
                "filename": "transactions_2025-01.csv",
                "transaction_count": 35,
                "file_path": "/shared_files/output/transactions_2025-01.csv",
                "month": "2025-01",
                "document_id": None,
                "error_message": None,
            }
        }
    }


# ===========================================================


class DTOImportTransactionsFromCsvRequest(BaseModel):
    """DTO for import transactions request - from controller to use case"""

    csv_filename: Optional[str] = None  # Specific CSV filename to import
    input_dir: str = "/shared_files/output"  # Directory where to read the CSV file from

    model_config = {
        "json_schema_extra": {
            "example": {
                "csv_filename": "transactions_2025-01.csv",
                "input_dir": "/shared_files/output",
            }
        }
    }


class DTOImportTransactionsFromCsvResponse(BaseModel):
    """Result DTO for import transactions operation - returned from use case to controller"""

    success: bool
    updated_count: int
    skipped_count: int
    errors: List[str]
    total_rows: int
    message: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "updated_count": 30,
                "skipped_count": 5,
                "errors": [],
                "total_rows": 35,
                "message": "Import completed successfully",
            }
        }
    }


# ===========================================================


class DTOGetAllTransactionsResponse(BaseModel):
    """DTO for get all transactions response"""

    transactions: List[Dict[str, Any]]

    model_config = {
        "json_schema_extra": {
            "example": {
                "transactions": [
                    {
                        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                        "description": "Supermercado Wong",
                        "amount": -150.00,
                        "transaction_type": "expense",
                        "transaction_date": "2025-01-15",
                        "currency": "PEN",
                        "category_name": "Food & Dining",
                        "document_type_name": "debit",
                    }
                ]
            }
        }
    }


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

    model_config = {
        "json_schema_extra": {
            "example": {
                "transaction_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "updated": True,
                "message": "Transaction updated successfully",
            }
        }
    }


# ===========================================================


class DTOBatchUpdateListRequest(BaseModel):
    """Wrapper DTO for batch update list request - input from controller"""

    updates: List[DTOBatchUpdateRequest]

    model_config = {
        "json_schema_extra": {
            "example": {
                "updates": [
                    {
                        "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
                        "history": "Gasto en supermercado - alimentación",
                        "category_name": "Food & Dining",
                    },
                    {
                        "transaction_id": "123e4567-e89b-12d3-a456-426614174001",
                        "history": "Pago de servicios - electricidad",
                        "category_name": "Utilities",
                    },
                ]
            }
        }
    }
