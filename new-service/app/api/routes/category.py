"""
Category Routes - HTTP Interface
Delegates to application layer use cases
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List, Dict, Any
import logging

from api.deps import get_db_session
from src.Aframework.gateway.db.category import CategoryDbGateway
from src.Capplication.use_cases.category.get_all_categories import (
    GetAllCategoriesUseCase,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=Dict[str, Any])
def get_all_categories(
    session: Session = Depends(get_db_session),
) -> Dict[str, Any]:
    """
    Get all categories

    Returns:
        List of all categories with their details
    """
    try:
        # Instantiate gateway
        category_gateway = CategoryDbGateway(session)

        # Inject gateway into use case
        use_case = GetAllCategoriesUseCase(category_gateway)

        # Execute use case
        result = use_case.execute()

        # Map domain result to HTTP response
        return {
            "categories": [
                {
                    "id": cat.id,
                    "name": cat.name,
                    "description": cat.description,
                    "parent_id": cat.parent_id,
                }
                for cat in result.categories
            ],
            "total_count": result.total_count,
        }

    except Exception as e:
        logger.error(f"Error retrieving categories: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving categories: {str(e)}"
        )
