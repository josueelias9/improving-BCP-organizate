"""
Category Routes - HTTP Interface
Delegates to application layer use cases
"""

from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List, Dict, Any
import logging

from api.deps import get_db_session
from src.Aframework.gateway.db.category import CategoryDbGateway

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[Dict[str, Any]])
def get_all_categories(
    session: Session = Depends(get_db_session),
) -> List[Dict[str, Any]]:
    """
    Get all categories

    Returns:
        List of all categories with their details
    """
    try:
        # Create gateway
        category_gateway = CategoryDbGateway(session)

        # Get all categories
        categories = category_gateway.get_all()

        # Transform to response format
        return [
            {
                "id": str(category.id),
                "name": category.name,
                "description": category.description,
                "parent_id": str(category.parent_id) if category.parent_id else None,
            }
            for category in categories
        ]

    except Exception as e:
        logger.error(f"Error retrieving categories: {str(e)}")
        raise
