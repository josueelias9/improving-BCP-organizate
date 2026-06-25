"""
Category Routes - HTTP Interface
Delegates to application layer use cases
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
import logging
from api.deps import get_db_session
from src.Aframework.gateway.db.category import CategoryDbGateway
from src.Capplication.use_cases.category.get_all_categories import GetAllCategoriesUseCase
from src.Capplication.DTO.category_dto import DTOGetAllCategoriesResponse

router = APIRouter(prefix="/categories", tags=["categories"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=DTOGetAllCategoriesResponse)
def get_all_categories(
    session: Session = Depends(get_db_session),
) -> DTOGetAllCategoriesResponse:
    """
    Get all categories

    Returns:
        List of all categories with their details
    """
    try:

        category_gateway = CategoryDbGateway(session)

        # Inject gateway into use case
        use_case = GetAllCategoriesUseCase(category_gateway)

        return use_case.execute()

    except Exception as e:
        logger.error(f"Error retrieving categories: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving categories: {str(e)}"
        )
