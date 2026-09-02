"""
Transaction Routes - HTTP Interface
Delegates to application layer use cases
"""

from fastapi import APIRouter, HTTPException
import uuid
import logging

from api.deps import SessionDep

from src.Aframework.gateway.db.transaction import TransactionDbGateway
from src.Aframework.gateway.db.category import CategoryDbGateway
from src.Capplication.DTO.transaction_dto import (
    DTOReadTransactionsResponse,
    DTOUpdateTransactionRequest,
    DTOUpdateTransactionResponse,
)
from src.Capplication.use_cases.transaction.update_transaction import (
    UpdateTransactionUseCase,
)
from src.Capplication.use_cases.transaction.read_transactions import (
    ReadTransactionsUseCase,
)

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
