from typing import List, Optional
from pydantic import BaseModel

from src.Capplication.DTO.account_dto import DTOCreateAccountHistoryResponse

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
