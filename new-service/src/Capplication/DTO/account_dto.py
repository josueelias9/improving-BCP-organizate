from typing import List
from pydantic import BaseModel


class DTOAccount(BaseModel):
    id: str


class DTOGetAccountsResponse(BaseModel):
    accounts: List[DTOAccount]
    total_count: int
