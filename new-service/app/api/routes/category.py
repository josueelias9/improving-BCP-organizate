"""
Category Routes - HTTP Interface
Delegates to application layer use cases
"""

from fastapi import APIRouter, HTTPException
import logging
from api.deps import SessionDep
from src.Aframework.gateway.db.category import CategoryDbGateway
from src.Capplication.use_cases.category.read_categories import (
    ReadCategoriesUseCase,
)
from src.Capplication.DTO.category_dto import DTOReadCategoriesResponse

router = APIRouter(prefix="/categories", tags=["categories"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=DTOReadCategoriesResponse)
def read_categories(session: SessionDep):
    """
    Get all categories

    Returns:
        List of all categories with their details
    """
    try:

        category_gateway = CategoryDbGateway(session)

        # Inject gateway into use case
        use_case = ReadCategoriesUseCase(category_gateway)

        return use_case.execute()

    except Exception as e:
        logger.error(f"Error retrieving categories: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving categories: {str(e)}"
        )
