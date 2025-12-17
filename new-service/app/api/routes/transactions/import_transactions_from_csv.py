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

from src.Capplication.DTO.transaction_dto import (
    DTOImportTransactionsFromCsvRequest,
    DTOImportTransactionsFromCsvResponse,
)

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


def controller(csv_filename: Optional[str], input_dir: str, session: Session):
    # Instantiate gateways and inject into use case
    transaction_gateway = TransactionDbGateway(session)
    category_gateway = CategoryDbGateway(session)
    use_case = ImportTransactionsFromCsvUseCase(
        transaction_gateway,
        category_gateway,
    )

    # Create DTO request with input_dir
    dto_request = DTOImportTransactionsFromCsvRequest(
        csv_filename=csv_filename, input_dir=input_dir
    )
    # Execute use case
    dto_response = use_case.execute(dto_request)
    return presenter(dto_response)


@router.post("/import/csv")
def import_transactions_from_csv(
    csv_filename: Optional[str] = Query(
        None,
        description="Specific CSV filename to import (optional, uses latest if not provided)",
    ),
    input_dir: str = Query(
        "/shared_files/output", description="Directory where to read the CSV file from"
    ),
    session: Session = Depends(get_db_session),
) -> Dict[str, Any]:
    """
    Import and update transactions from CSV file

    Reads a CSV file from the specified directory and updates transactions based on unique_identifier.
    Updates the 'history' and 'category_name' fields for matching transactions.

    Args:
        csv_filename: Optional specific CSV filename. If not provided, uses the most recent CSV file.
        input_dir: Directory where to read the CSV file from (default: /shared_files/output)

    Returns:
        JSON with import summary including updated count, errors, etc.

    Examples:
        - POST /transactions/import/csv - Import from latest CSV file in default directory
        - POST /transactions/import/csv?input_dir=/custom/path - Import from custom directory
        - POST /transactions/import/csv?csv_filename=transactions.csv - Import from specific file
        - POST /transactions/import/csv?csv_filename=transactions.csv&input_dir=/custom/path - Custom file and directory
    """
    try:

        return controller(csv_filename, input_dir, session)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing transactions from CSV: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error importing transactions: {str(e)}"
        )
