"""
Transaction Routes - HTTP Interface
Delegates to application layer use cases
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Dict, Any, List

import logging

from api.deps import get_db_session
from src.Aframework.gateway.db.transaction import TransactionDbGateway
from src.Aframework.gateway.db.category import CategoryDbGateway
from src.Capplication.use_cases.transaction.get_all_transactions import (
    GetAllTransactionsUseCase,
)
from src.Capplication.DTO.transaction_dto import DTOGetAllTransactionsResponse

router = APIRouter()
logger = logging.getLogger(__name__)


def presenter(dto_response: DTOGetAllTransactionsResponse) -> List[Dict[str, Any]]:
    """Convert DTO response to API response format"""
    return dto_response.transactions


def controller(session, skip, limit):
    transaction_gateway = TransactionDbGateway(session)
    category_gateway = CategoryDbGateway(session)
    use_case = GetAllTransactionsUseCase(transaction_gateway, category_gateway)
    dto_response = use_case.execute(skip=skip, limit=limit)
    return presenter(dto_response)


@router.get("/", response_model=List[Dict[str, Any]])
def get_all_transactions(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_db_session)
) -> List[Dict[str, Any]]:
    """
    Get all transactions with pagination

    Includes category_name field with the name of the associated category.

    Args:
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100, max: 1000)
        session: Database session (injected)

    Returns:
        List of transactions with category_name included
    """
    try:
        return controller(session, skip, limit)

    except Exception as e:
        logger.error(f"Error retrieving transactions: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving transactions: {str(e)}"
        )
