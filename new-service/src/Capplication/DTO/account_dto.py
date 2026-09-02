from datetime import date
from typing import Any, List, Optional, Dict
import uuid
from pydantic import BaseModel, ConfigDict

# ============================================================


class DTOCreateAccountTransactionsRequest(BaseModel):
    account_id: str


class DTOCreateAccountTransactionsResponse(BaseModel):
    success: bool
    loaded_count: int
    skipped_count: int
    errors: List[str]
    total_records: int
    documents_processed: int
    account_id: str


# ============================================================


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


class DTOUpdateAccountTransactionsResponse(BaseModel):
    """Result DTO for batch update operation - returned from use case to controller"""

    total: int
    updated: int
    failed: int
    errors: List[Dict[str, Any]]
    message: Optional[str] = None


class DTOUpdateAccountTransactionsRequest(BaseModel):
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


# ============================================================


class DTOCreateAccountHistoryRequest(BaseModel):
    pass


class DTOCreateAccountHistoryResponse(BaseModel):
    id: Optional[uuid.UUID] = None
    account_id: str
    balance: float
    registration_date: Optional[date] = None


class DTOCreateAccountHistoriesResponse(BaseModel):
    histories: List[DTOCreateAccountHistoryResponse]
    total_count: int


# ============================================================


class DTOCreateAllAccountHistoriesItemResult(BaseModel):
    account_id: str
    success: bool
    histories: List[DTOCreateAccountHistoryResponse] = []
    error: Optional[str] = None


class DTOCreateAllAccountHistoriesResponse(BaseModel):
    total_accounts: int
    total_histories: int
    results: List[DTOCreateAllAccountHistoriesItemResult]


# ============================================================


# TODO: maybe we can have a single DTO
class DTOAccount(BaseModel):
    id: str
    links: List[Dict[str, str]] = []


class DTOReadAccountsResponse(BaseModel):
    accounts: List[DTOAccount]
    total_count: int


# ============================================================


class DTOHistory(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[uuid.UUID] = None
    account_id: Optional[str] = None
    balance: float
    registration_date: Optional[date] = None


class DTOReadAccountHistoriesResponse(BaseModel):
    histories: List[DTOHistory]
    total_count: int
