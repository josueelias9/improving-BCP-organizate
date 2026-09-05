from typing import Optional, List
from pydantic import BaseModel


class DTOExportTransactionsRequest(BaseModel):
    """Filter criteria DTO for transaction export - request from controller to use case"""

    account_id: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "account_id": "191-04106279-0-55",
            }
        }
    }


class DTOExportTransactionsResponse(BaseModel):
    """Result DTO for export transactions operation - returned from use case to controller"""

    success: bool
    filename: str
    transaction_count: int
    file_path: Optional[str] = None
    account_id: Optional[str] = None
    error_message: Optional[str] = None


# ===========================================================


class DTOImportTransactionsRequest(BaseModel):
    """DTO for import transactions request - from controller to use case"""

    account_id: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "account_id": "191-04106279-0-55",
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
