from datetime import date
from typing import List, Optional, Dict
import uuid
from pydantic import BaseModel

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


class DTOAccount(BaseModel):
    id: str
    links: List[Dict[str, str]] = []


class DTOGetAccountsResponse(BaseModel):
    accounts: List[DTOAccount]
    total_count: int


# ============================================================


class DTOHistory(BaseModel):
    id: Optional[uuid.UUID] = None
    account_id: Optional[str] = None
    balance: float
    registration_date: Optional[date] = None


class DTOReadAccountHistoriesResponse(BaseModel):
    histories: List[DTOHistory]
    total_count: int
