"""
Transaction Routes - HTTP Interface
Delegates to application layer use cases
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import Optional
import uuid
import logging

from api.deps import SessionDep

from src.Aframework.gateway.db.transaction import TransactionDbGateway
from src.Aframework.gateway.file_extractor import FileExtractorGateway
from src.Aframework.gateway.db.category import CategoryDbGateway
from src.Aframework.gateway.db.document import DocumentDbGateway
from src.Aframework.gateway.db.document_type import DocumentTypeDbGateway
from src.Capplication.DTO.transaction_dto import (
    DTOBatchUpdateListRequest,
    DTOBatchUpdateResponse,
    DTOExportTransactionsRequest,
    DTOExportTransactionsResponse,
    DTOImportTransactionsFromCsvRequest,
    DTOImportTransactionsFromCsvResponse,
    DTOGetAllTransactionsResponse,
    DTOUpdateTransactionRequest,
    DTOUpdateTransactionResponse,
)
from src.Capplication.use_cases.transaction.update_transaction import (
    UpdateTransactionUseCase,
)
from src.Capplication.use_cases.transaction.batch_update_transactions import (
    BatchUpdateTransactionsUseCase,
)
from src.Capplication.use_cases.transaction.export_transactions import (
    ExportTransactionsUseCase,
)
from src.Capplication.use_cases.transaction.get_all_transactions import (
    GetAllTransactionsUseCase,
)
from src.Capplication.use_cases.transaction.import_transactions_from_csv import (
    ImportTransactionsFromCsvUseCase,
)


from src.Capplication.use_cases.transaction.create_transactions import (
    CreateTransactionsUseCase,
)
from src.Capplication.DTO.transaction_dto import (
    DTOCreateTransactionsRequest,
    DTOCreateTransactionsResponse,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])
logger = logging.getLogger(__name__)

# CRUD


@router.get("/", response_model=DTOGetAllTransactionsResponse)
def get_transactions(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> DTOGetAllTransactionsResponse:
    """
    Get all transactions with pagination

    Includes category_name and document_type_name fields.

    Args:
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100, max: 1000)
        session: Database session (injected)

    Returns:
        List of transactions with category_name included
    """
    try:
        transaction_gateway = TransactionDbGateway(session)
        category_gateway = CategoryDbGateway(session)
        document_gateway = DocumentDbGateway(session)
        document_type_gateway = DocumentTypeDbGateway(session)
        use_case = GetAllTransactionsUseCase(
            transaction_gateway,
            category_gateway,
            document_gateway,
            document_type_gateway,
        )
        dto_response = use_case.execute(skip=skip, limit=limit)

        return dto_response

    except Exception as e:
        logger.error(f"Error retrieving transactions: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving transactions: {str(e)}"
        )


@router.post(
    "/{document_id}",
    response_model=DTOCreateTransactionsResponse,
)
def create_transactions(document_id: uuid.UUID, session: SessionDep):
    """
    Load transactions from a document's data column into the transactions table.

    This endpoint delegates to the application layer use case.

    Args:
        document_id: The UUID of the document to load transactions from
        session: Database session (injected)

    Returns:
        Summary of loaded transactions

    Raises:
        HTTPException: 404 if document not found, 400 for validation errors
    """
    try:

        # Instantiate concrete gateways
        document_gateway = DocumentDbGateway(session)
        transaction_gateway = TransactionDbGateway(session)

        # Inject gateways into use case
        use_case = CreateTransactionsUseCase(document_gateway, transaction_gateway)

        dto_request = DTOCreateTransactionsRequest(document_id=document_id)
        # Execute use case
        dto_response = use_case.execute(dto_request)

        return dto_response

    except ValueError as e:
        # Business validation errors
        error_msg = str(e)

        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)

    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error loading transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{transaction_id}", response_model=DTOUpdateTransactionResponse)
def update_transaction(
    transaction_id: uuid.UUID,
    transaction_update: DTOUpdateTransactionRequest,
    session: SessionDep,
):
    """
    Update a specific transaction by ID.

    This endpoint delegates to the application layer use case.

    Args:
        transaction_id: The UUID of the transaction to update
        transaction_update: The fields to update
        session: Database session (injected)

    Returns:
        Update result with transaction information

    Raises:
        HTTPException: 404 if transaction not found, 400 for validation errors
    """
    try:
        # Instantiate gateways and inject into use case
        transaction_gateway = TransactionDbGateway(session)
        category_gateway = CategoryDbGateway(session)
        use_case = UpdateTransactionUseCase(transaction_gateway, category_gateway)

        # Convert Pydantic model to dict, excluding None values
        # TODO: move this logic inside the use case to keep controller thin
        update_data = transaction_update.model_dump(
            exclude_unset=True, exclude_none=True
        )

        # Validate that at least one field is being updated
        if not update_data:
            raise HTTPException(
                status_code=400, detail="At least one field must be provided for update"
            )

        # Execute use case
        result = use_case.execute(transaction_id, update_data)

        return DTOUpdateTransactionResponse(**result)

    except ValueError as e:
        # Business validation errors
        error_msg = str(e)

        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)

    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error updating transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# other endpoints


@router.patch("/batch", response_model=DTOBatchUpdateResponse)
def batch_update_transactions(
    batch_update: DTOBatchUpdateListRequest, session: SessionDep
):
    """
    Update multiple transactions simultaneously.

    Only 'history' and 'category_name' fields can be updated for each transaction.
    If category_name is provided, it will be validated against existing categories.
    This endpoint processes all updates and returns a summary of the operation.

    Args:
        batch_update: List of transaction updates to apply
        session: Database session (injected)

    Returns:
        Summary of batch update operation with success/failure counts

    Raises:
        HTTPException: 400 for validation errors
    """
    try:
        # Instantiate gateways and inject into use case
        transaction_gateway = TransactionDbGateway(session)
        category_gateway = CategoryDbGateway(session)
        use_case = BatchUpdateTransactionsUseCase(transaction_gateway, category_gateway)

        # Convert Pydantic models to domain objects
        updates = batch_update.updates

        # Execute use case
        result = use_case.execute(updates)
        # TODO: it seems that this message will always be the same, maybe we can move it to the use case
        result.message = (
            f"Successfully updated {result.updated}/{result.total} transactions"
        )
        return result

    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error in batch update: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# TODO: it seams to me that this two endpoints belong to the document prefix. That is because its importing and exporting csv files


@router.get("/export/csv", response_model=DTOExportTransactionsResponse)
def export_transactions(
    session: SessionDep,
    month: Optional[str] = Query(
        None, description="Filter by month in format YYYY-MM (e.g., 2025-01)"
    ),
    document_id: Optional[uuid.UUID] = Query(None, description="Filter by document ID"),
    output_dir: str = Query(
        "./exports", description="Output directory for exported CSV files"
    ),
) -> DTOExportTransactionsResponse:
    """
    Export transactions to CSV format and save to file

    Filters:
        - month: Optional filter by month in format YYYY-MM (e.g., "2025-01")
        - document_id: Optional filter by specific document
        - output_dir: Output directory for CSV file (default: ./exports)

    Returns:
        JSON with file path, transaction count, and status

    Examples:
        - GET /transactions/export/csv - Export all transactions
        - GET /transactions/export/csv?month=2025-01 - Export transactions from January 2025
        - GET /transactions/export/csv?document_id=xxx-xxx-xxx - Export transactions from specific document
        - GET /transactions/export/csv?month=2025-01&document_id=xxx-xxx-xxx - Combined filters
    """
    try:
        # Controller:
        # Instantiate gateways and inject into use case
        transaction_gateway = TransactionDbGateway(session)
        file_extractor_gateway = FileExtractorGateway()
        use_case = ExportTransactionsUseCase(
            transaction_gateway=transaction_gateway,
            file_extractor_gateway=file_extractor_gateway,
        )

        # Create filter object with output_dir
        filters = DTOExportTransactionsRequest(
            month=month, document_id=document_id, output_dir=output_dir
        )

        # Execute use case
        dto_response = use_case.execute(filters)

        if not dto_response.success:
            raise HTTPException(
                status_code=400 if "Invalid" in dto_response.error_message else 404,
                detail=dto_response.error_message,
            )
        # Presenter:
        return dto_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting transactions to CSV: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error exporting transactions: {str(e)}"
        )


@router.post("/import/csv", response_model=DTOImportTransactionsFromCsvResponse)
def import_transactions_from_csv(
    session: SessionDep,
    csv_filename: Optional[str] = Query(
        None,
        description="Specific CSV filename to import (optional, uses latest if not provided)",
    ),
    input_dir: str = Query(
        "/shared_files/output", description="Directory where to read the CSV file from"
    ),
):
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
        return dto_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing transactions from CSV: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error importing transactions: {str(e)}"
        )
