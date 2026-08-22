"""
Transaction Routes - HTTP Interface
Delegates to application layer use cases
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import uuid
import logging

from api.deps import SessionDep

from src.Aframework.gateway.content_extractor.bcp_credit_parser import BCPCreditParser
from src.Aframework.gateway.content_extractor.bcp_debit_parser import BCPDebitParser
from src.Aframework.gateway.content_extractor.yape_parser import YapeParser
from src.Aframework.gateway.db.transaction import TransactionDbGateway
from src.Aframework.gateway.db.category import CategoryDbGateway
from src.Aframework.gateway.db.document import DocumentDbGateway
from src.Aframework.gateway.db.account import AccountDbGateway, HistoryDbGateway
from src.Capplication.DTO.transaction_dto import (
    DTOUpdateTransactionsRequest,
    DTOUpdateTransactionsResponse,
    DTOExportTransactionsRequest,
    DTOExportTransactionsResponse,
    DTOImportTransactionsRequest,
    DTOImportTransactionsResponse,
    DTOReadTransactionsResponse,
    DTOUpdateTransactionRequest,
    DTOUpdateTransactionResponse,
    DTOCreateTransactionsRequest,
    DTOCreateTransactionsResponse,
)
from src.Capplication.use_cases.transaction.update_transaction import (
    UpdateTransactionUseCase,
)
from src.Capplication.use_cases.transaction.update_transactions import (
    UpdateTransactionsUseCase,
)
from src.Capplication.use_cases.transaction.export_transactions import (
    ExportTransactionsUseCase,
)
from src.Capplication.use_cases.transaction.read_transactions import (
    ReadTransactionsUseCase,
)
from src.Capplication.use_cases.transaction.import_transactions import (
    ImportTransactionsUseCase,
)
from src.Capplication.use_cases.transaction.create_transactions import (
    CreateTransactionsUseCase,
)
from src.Aframework.gateway.file_extractor import FileExtractorGateway

router = APIRouter(prefix="/transactions", tags=["transactions"])
logger = logging.getLogger(__name__)

# CRUD


@router.get("/", response_model=DTOReadTransactionsResponse)
def read_transactions(
    session: SessionDep,
) -> DTOReadTransactionsResponse:
    """Get all transactions without pagination or account filtering."""
    try:
        transaction_gateway = TransactionDbGateway(session)
        use_case = ReadTransactionsUseCase(transaction_gateway)
        return use_case.execute()

    except Exception as e:
        logger.error(f"Error retrieving transactions: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving transactions: {str(e)}"
        )


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


@router.put("/batch", response_model=DTOUpdateTransactionsResponse)
def update_transactions(dto_request: DTOUpdateTransactionsRequest, session: SessionDep):
    try:
        transaction_gateway = TransactionDbGateway(session)
        category_gateway = CategoryDbGateway(session)
        use_case = UpdateTransactionsUseCase(transaction_gateway, category_gateway)
        return use_case.execute(dto_request)
    except Exception as e:
        logger.error(f"Unexpected error in batch update: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/bulk",
    response_model=DTOCreateTransactionsResponse,
)
def create_transactions(dto_request: DTOCreateTransactionsRequest, session: SessionDep):
    """
    Given an account ID, find all its unprocessed documents and extract their transactions.
    """
    try:
        parsers = {
            "bcp_credit": BCPCreditParser(),
            "bcp_debit": BCPDebitParser(),
            "yape": YapeParser(),
        }

        document_gateway = DocumentDbGateway(session)
        transaction_gateway = TransactionDbGateway(session)

        use_case = CreateTransactionsUseCase(
            document_gateway, transaction_gateway, parsers
        )

        return use_case.execute(dto_request)

    except HTTPException:
        raise

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

        # TODO: fix this
        return DTOUpdateTransactionResponse(**result)

    except HTTPException:
        raise

    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error updating transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
