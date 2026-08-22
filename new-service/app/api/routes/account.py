from fastapi import APIRouter, HTTPException
import logging
from api.deps import SessionDep
from src.Aframework.gateway.db.account import AccountDbGateway
from src.Aframework.gateway.db.history import HistoryDbGateway
from src.Aframework.gateway.db.transaction import TransactionDbGateway
from src.Capplication.use_cases.account.read_accounts import ReadAccountsUseCase
from src.Capplication.use_cases.account.read_account_transactions import (
    ReadAccountTransactionsUseCase,
)
from src.Capplication.use_cases.account.read_account_histories import (
    ReadAccountHistoriesUseCase,
)
from src.Capplication.DTO.account_dto import (
    DTOGetAccountHistoriesResponse,
    DTOGetAccountsResponse,
)
from src.Capplication.DTO.transaction_dto import DTOReadTransactionsResponse

router = APIRouter(prefix="/accounts", tags=["accounts"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=DTOGetAccountsResponse)
def read_accounts(session: SessionDep):
    try:
        use_case = ReadAccountsUseCase(AccountDbGateway(session))
        return use_case.execute()
    except Exception as e:
        logger.error(f"Error retrieving accounts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving accounts: {str(e)}")


@router.get("/{account_id}/transactions", response_model=DTOReadTransactionsResponse)
def read_account_transactions(
    account_id: str,
    session: SessionDep,
) -> DTOReadTransactionsResponse:
    try:
        use_case = ReadAccountTransactionsUseCase(TransactionDbGateway(session))
        return use_case.execute(account_id=account_id)
    except Exception as e:
        logger.error(f"Error retrieving transactions for account {account_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving transactions for account {account_id}: {str(e)}",
        )


@router.get("/{account_id}/histories", response_model=DTOGetAccountHistoriesResponse)
def read_account_histories(
    account_id: str,
    session: SessionDep,
) -> DTOGetAccountHistoriesResponse:
    try:
        use_case = ReadAccountHistoriesUseCase(HistoryDbGateway(session))
        return use_case.execute(account_id=account_id)
    except Exception as e:
        logger.error(f"Error retrieving histories for account {account_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving histories for account {account_id}: {str(e)}",
        )
