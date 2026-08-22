from datetime import date
from typing import List, Optional
import uuid
from pydantic import BaseModel


class DTOAccount(BaseModel):
    id: str


class DTOHistory(BaseModel):
    id: Optional[uuid.UUID] = None
    account_id: Optional[str] = None
    balance: float
    registration_date: Optional[date] = None


class DTOGetAccountsResponse(BaseModel):
    accounts: List[DTOAccount]
    total_count: int


class DTOGetAccountHistoriesResponse(BaseModel):
    histories: List[DTOHistory]
    total_count: int
