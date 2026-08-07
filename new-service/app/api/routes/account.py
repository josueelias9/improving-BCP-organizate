from fastapi import APIRouter, HTTPException
import logging
from api.deps import SessionDep
from src.Aframework.gateway.db.account import AccountDbGateway
from src.Capplication.use_cases.account.get_accounts import GetAccountsUseCase
from src.Capplication.DTO.account_dto import DTOGetAccountsResponse

router = APIRouter(prefix="/accounts", tags=["accounts"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=DTOGetAccountsResponse)
def get_accounts(session: SessionDep):
    try:
        use_case = GetAccountsUseCase(AccountDbGateway(session))
        return use_case.execute()
    except Exception as e:
        logger.error(f"Error retrieving accounts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving accounts: {str(e)}")
