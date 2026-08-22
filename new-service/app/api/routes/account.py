from fastapi import APIRouter, HTTPException
import logging
from api.deps import SessionDep
from src.Aframework.gateway.db.account import AccountDbGateway
from src.Aframework.gateway.db.transaction import TransactionDbGateway
from src.Capplication.use_cases.account.get_accounts import GetAccountsUseCase
from src.Capplication.use_cases.account.get_account_transactions import (
    GetAccountTransactionsUseCase,
)
from src.Capplication.DTO.account_dto import DTOGetAccountsResponse
from src.Capplication.DTO.transaction_dto import DTOReadTransactionsResponse

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


@router.get("/{account_id}/transactions", response_model=DTOReadTransactionsResponse)
def get_account_transactions(
    account_id: str,
    session: SessionDep,
) -> DTOReadTransactionsResponse:
    try:
        use_case = GetAccountTransactionsUseCase(TransactionDbGateway(session))
        return use_case.execute(account_id=account_id)
    except Exception as e:
        logger.error(f"Error retrieving transactions for account {account_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving transactions for account {account_id}: {str(e)}",
        )
