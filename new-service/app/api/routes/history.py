"""
History routes - HTTP Interface
Handles cross-account balance snapshot generation.
"""

import logging

from fastapi import APIRouter, HTTPException

from api.deps import SessionDep
from src.Aframework.gateway.db.account import AccountDbGateway
from src.Aframework.gateway.db.history import HistoryDbGateway
from src.Aframework.gateway.db.document import DocumentDbGateway
from src.Aframework.gateway.content_extractor.bcp_credit_parser import BCPCreditParser
from src.Aframework.gateway.content_extractor.bcp_debit_parser import BCPDebitParser
from src.Aframework.gateway.content_extractor.yape_parser import YapeParser
from src.Capplication.use_cases.account.create_histories import (
    CreateHistoriesUseCase,
)
from src.Capplication.DTO.account_dto import DTOCreateAllAccountHistoriesResponse

router = APIRouter(prefix="/histories", tags=["histories"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=DTOCreateAllAccountHistoriesResponse)
def create_histories(
    session: SessionDep,
) -> DTOCreateAllAccountHistoriesResponse:
    try:
        parsers = {
            "bcp_credit": BCPCreditParser(),
            "bcp_debit": BCPDebitParser(),
            "yape": YapeParser(),
        }

        use_case = CreateHistoriesUseCase(
            account_gateway=AccountDbGateway(session),
            history_gateway=HistoryDbGateway(session),
            document_gateway=DocumentDbGateway(session),
            parsers=parsers,
        )
        return use_case.execute()
    except Exception as e:
        logger.error(f"Error creating histories for all accounts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating histories for all accounts: {str(e)}",
        )
