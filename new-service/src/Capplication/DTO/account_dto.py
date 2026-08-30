from datetime import date
from typing import List, Optional, Dict
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
