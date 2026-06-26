"""
Get All Categories Use Case - Application Layer

Business logic for retrieving all categories.
Accepts DTOs at the boundary and works with entities internally.
"""

import logging
from typing import List, Dict, Any

from src.Capplication.gateway.db import ICategoryDbGateway
from src.Capplication.DTO.category_dto import DTOGetCategoriesResponse

logger = logging.getLogger(__name__)


class GetCategoriesUseCase:
    """
    Use Case: Retrieve all categories

    Responsibility: Orchestrate category retrieval and conversion to DTO for presentation
    """

    def __init__(self, category_gateway: ICategoryDbGateway):
        """
        Initialize use case with required gateway

        Args:
            category_gateway: Gateway for category persistence operations
        """
        self.category_gateway = category_gateway

    def execute(self) -> DTOGetCategoriesResponse:
        """
        Execute the use case to get all categories

        Returns:
            DTOGetCategoriesResponse with list of category dicts
        """
        # Get all categories as entities from gateway
        category_entities = self.category_gateway.get_all()

        # Convert entities to simple dicts for presentation
        categories: List[Dict[str, Any]] = []

        for category_entity in category_entities:
            category_dict = {
                "id": str(category_entity.id),
                "name": category_entity.name,
                "description": category_entity.description,
                "parent_id": (
                    str(category_entity.parent_id)
                    if category_entity.parent_id
                    else None
                ),
            }
            categories.append(category_dict)

        logger.info(f"Retrieved {len(categories)} categories")

        # Return DTO response
        return DTOGetCategoriesResponse(
            categories=categories, total_count=len(categories)
        )
