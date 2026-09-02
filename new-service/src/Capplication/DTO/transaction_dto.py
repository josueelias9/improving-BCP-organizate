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
    account_id: Optional[str]
    unique_identifier: Optional[str]
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
