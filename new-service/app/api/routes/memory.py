"""
Memory Routes - HTTP Interface
Delegates to application layer use cases
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging

from api.deps import SessionDep

from src.Aframework.gateway.file_extractor import FileExtractorGateway
from src.Aframework.gateway.db.transaction import TransactionDbGateway
from src.Aframework.gateway.db.category import CategoryDbGateway
from src.Capplication.DTO.memory_dto import (
    DTOExportTransactionsRequest,
    DTOExportTransactionsResponse,
    DTOImportTransactionsRequest,
    DTOImportTransactionsResponse,
)
from src.Capplication.use_cases.memory.export_transactions import (
    ExportTransactionsUseCase,
)
from src.Capplication.use_cases.memory.import_transactions import (
    ImportTransactionsUseCase,
)

router = APIRouter(prefix="/memories", tags=["memories"])
logger = logging.getLogger(__name__)


@router.get("/export", response_model=DTOExportTransactionsResponse)
def export_transactions(
    session: SessionDep,
    account_id: Optional[str] = Query(None, description="Filter by account ID"),
) -> DTOExportTransactionsResponse:
    try:
        transaction_gateway = TransactionDbGateway(session)
        file_extractor_gateway = FileExtractorGateway()
        use_case = ExportTransactionsUseCase(
            transaction_gateway=transaction_gateway,
            file_extractor_gateway=file_extractor_gateway,
        )
        dto_request = DTOExportTransactionsRequest(
            account_id=account_id,
        )
        dto_response = use_case.execute(dto_request)
        if not dto_response.success:
            raise HTTPException(
                status_code=400 if "Invalid" in dto_response.error_message else 404,
                detail=dto_response.error_message,
            )
        return dto_response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting transactions to CSV: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error exporting transactions: {str(e)}"
        )


@router.post("/import", response_model=DTOImportTransactionsResponse)
def import_transactions(
    session: SessionDep,
    account_id: str = Query(description="Account ID to import transactions for"),
):
    try:
        transaction_gateway = TransactionDbGateway(session)
        category_gateway = CategoryDbGateway(session)
        use_case = ImportTransactionsUseCase(transaction_gateway, category_gateway)
        dto_request = DTOImportTransactionsRequest(account_id=account_id)
        return use_case.execute(dto_request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing transactions from CSV: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error importing transactions: {str(e)}"
        )
