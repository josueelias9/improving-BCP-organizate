from fastapi import APIRouter, HTTPException
import logging
from api.deps import SessionDep
from src.Aframework.gateway.db.account import AccountDbGateway
from src.Aframework.gateway.db.history import HistoryDbGateway
from src.Aframework.gateway.db.transaction import TransactionDbGateway
from src.Aframework.gateway.db.document import DocumentDbGateway
from src.Aframework.gateway.content_extractor.bcp_credit_parser import BCPCreditParser
from src.Aframework.gateway.content_extractor.bcp_debit_parser import BCPDebitParser
from src.Aframework.gateway.content_extractor.yape_parser import YapeParser
from src.Capplication.use_cases.account.read_accounts import ReadAccountsUseCase
from src.Capplication.use_cases.account.read_account_transactions import (
    ReadAccountTransactionsUseCase,
)
from src.Capplication.use_cases.account.read_account_histories import (
    ReadAccountHistoriesUseCase,
)
from src.Capplication.use_cases.account.create_account_transactions import (
    CreateAccountTransactionsUseCase,
)
from src.Capplication.DTO.account_dto import (
    DTOReadAccountHistoriesResponse,
    DTOReadAccountsResponse,
    DTOCreateAccountTransactionsRequest,
    DTOCreateAccountTransactionsResponse,
)
from src.Capplication.DTO.transaction_dto import DTOReadTransactionsResponse
from src.Denterprise.entities import TransactionType

router = APIRouter(prefix="/accounts", tags=["accounts"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=DTOReadAccountsResponse)
def read_accounts(session: SessionDep):
    try:
        use_case = ReadAccountsUseCase(AccountDbGateway(session))
        return use_case.execute()
    except Exception as e:
        logger.error(f"Error retrieving accounts: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving accounts: {str(e)}"
        )


@router.post(
    "/{account_id}/transactions",
    response_model=DTOCreateAccountTransactionsResponse,
)
def create_account_transactions(
    account_id: str,
    session: SessionDep,
) -> DTOCreateAccountTransactionsResponse:
    try:
        parsers = {
            "bcp_credit": BCPCreditParser(),
            "bcp_debit": BCPDebitParser(),
            "yape": YapeParser(),
        }

        document_gateway = DocumentDbGateway(session)
        transaction_gateway = TransactionDbGateway(session)

        use_case = CreateAccountTransactionsUseCase(
            document_gateway, transaction_gateway, parsers
        )

        dto_request = DTOCreateAccountTransactionsRequest(account_id=account_id)
        return use_case.execute(dto_request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{account_id}/transactions", response_model=DTOReadTransactionsResponse)
def read_account_transactions(
    account_id: str,
    transaction_type: TransactionType | None = None,
    session: SessionDep = None,
) -> DTOReadTransactionsResponse:
    try:
        use_case = ReadAccountTransactionsUseCase(TransactionDbGateway(session))
        return use_case.execute(
            account_id=account_id, transaction_type=transaction_type
        )
    except Exception as e:
        logger.error(
            f"Error retrieving transactions for account {account_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving transactions for account {account_id}: {str(e)}",
        )


@router.get("/{account_id}/histories", response_model=DTOReadAccountHistoriesResponse)
def read_account_histories(
    account_id: str,
    session: SessionDep,
) -> DTOReadAccountHistoriesResponse:
    try:
        use_case = ReadAccountHistoriesUseCase(HistoryDbGateway(session))
        return use_case.execute(account_id=account_id)
    except Exception as e:
        logger.error(f"Error retrieving histories for account {account_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving histories for account {account_id}: {str(e)}",
        )
