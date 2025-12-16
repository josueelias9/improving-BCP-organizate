"""
Transaction Routes - HTTP Interface
Delegates to application layer use cases
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import Dict, Any, Optional

import logging

from api.deps import get_db_session
from src.Capplication.use_cases.transaction.import_transactions_from_csv import (
    ImportTransactionsFromCsvUseCase,
)
from src.Aframework.gateway.db.transaction import TransactionDbGateway
from src.Aframework.gateway.db.category import CategoryDbGateway

from src.Capplication.DTO.transaction_dto import DTOImportTransactionsFromCsvRequest,DTOImportTransactionsFromCsvResponse

router = APIRouter()
logger = logging.getLogger(__name__)


def presenter(result: DTOImportTransactionsFromCsvResponse):
    return {
        "success": result.success,
        "message": result.message,
        "updated_count": result.updated_count,
        "skipped_count": result.skipped_count,
        "total_rows": result.total_rows,
        "errors": (
            result.errors[:10] if result.errors else []
        ),  # Limit errors to first 10
    }


def controller(csv_filename: Optional[str], session: Session):
    # Instantiate gateways and inject into use case
    transaction_gateway = TransactionDbGateway(session)
    category_gateway = CategoryDbGateway(session)
    use_case = ImportTransactionsFromCsvUseCase(transaction_gateway, category_gateway)

    dto_request = DTOImportTransactionsFromCsvRequest(csv_filename=csv_filename)
    # Execute use case
    dto_response = use_case.execute(dto_request)
    return presenter(dto_response)


@router.post("/import/csv")
def import_transactions_from_csv(
    csv_filename: Optional[str] = Query(
        None,
        description="Specific CSV filename to import (optional, uses latest if not provided)",
    ),
    session: Session = Depends(get_db_session),
) -> Dict[str, Any]:
    """
    Import and update transactions from CSV file

    Reads a CSV file from the output/ directory and updates transactions based on unique_identifier.
    Updates the 'history' and 'category_name' fields for matching transactions.

    Args:
        csv_filename: Optional specific CSV filename. If not provided, uses the most recent CSV file.

    Returns:
        JSON with import summary including updated count, errors, etc.

    Examples:
        - POST /transactions/import/csv - Import from latest CSV file
        - POST /transactions/import/csv?csv_filename=transactions_226records_20251205_221111.csv - Import from specific file
    """
    try:

        return controller(csv_filename, session)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing transactions from CSV: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error importing transactions: {str(e)}"
        )
