
"""
Transaction Routes - HTTP Interface
Delegates to application layer use cases
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import Optional

import uuid
import logging

from api.deps import get_db_session
from src.Capplication.DTO.transaction_dto import (
    DTOExportTransactionsRequest, DTOExportTransactionsResponse
)
from src.Capplication.use_cases.transaction.export_transactions import (
    ExportTransactionsUseCase,
)
from src.Aframework.gateway.db.transaction import TransactionDbGateway
from src.Aframework.gateway.file_system import FileSystemGateway


router = APIRouter()
logger = logging.getLogger(__name__)


def presenter(response: DTOExportTransactionsResponse):
    return {
        "success": response.success,
        "message": f"Successfully exported {response.transaction_count} transactions",
        "file_path": response.file_path,
        "filename": response.filename,
        "transaction_count": response.transaction_count,
        "filters": {
            "month": response.month,
            "document_id": str(response.document_id) if response.document_id else None,
        },
    }


def controller(session: Session, month: Optional[str], document_id: Optional[uuid.UUID]):
    # Instantiate gateways and inject into use case
    transaction_gateway = TransactionDbGateway(session)
    file_system_gateway = FileSystemGateway()
    use_case = ExportTransactionsUseCase(
        transaction_gateway=transaction_gateway,
        file_system_gateway=file_system_gateway
    )

    # Create filter object
    filters = DTOExportTransactionsRequest(month=month, document_id=document_id)

    # Execute use case
    dto_response = use_case.execute(filters)

    if not dto_response.success:
        raise HTTPException(
            status_code=400 if "Invalid" in dto_response.error_message else 404,
            detail=dto_response.error_message,
        )

    return presenter(dto_response)

@router.get("/export/csv")
def export_transactions(
    month: Optional[str] = Query(
        None, description="Filter by month in format YYYY-MM (e.g., 2025-01)"
    ),
    document_id: Optional[uuid.UUID] = Query(None, description="Filter by document ID"),
    session: Session = Depends(get_db_session),
):
    """
    Export transactions to CSV format and save to file

    Filters:
        - month: Optional filter by month in format YYYY-MM (e.g., "2025-01")
        - document_id: Optional filter by specific document

    Returns:
        JSON with file path, transaction count, and status

    Examples:
        - GET /transactions/export/csv - Export all transactions
        - GET /transactions/export/csv?month=2025-01 - Export transactions from January 2025
        - GET /transactions/export/csv?document_id=xxx-xxx-xxx - Export transactions from specific document
        - GET /transactions/export/csv?month=2025-01&document_id=xxx-xxx-xxx - Combined filters
    """
    try:
        return controller(month=month, document_id=document_id, session=session)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting transactions to CSV: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error exporting transactions: {str(e)}"
        )
