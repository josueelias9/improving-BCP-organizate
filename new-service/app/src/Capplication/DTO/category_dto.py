"""
Category DTOs - Data Transfer Objects
Used ONLY for transferring data between controllers and use cases (boundary layer)

These DTOs serve as request/response objects at the interface adapter layer.
Internal domain logic uses entities from Denterprise layer.
"""

from typing import List
from pydantic import BaseModel


class DTOCategory(BaseModel):
    """DTO for category entity - used for transferring data between controllers and use cases"""

    id: str
    name: str
    description: str
    parent_id: str | None = None


class DTOGetCategoriesResponse(BaseModel):
    """Response DTO for get all categories operation - returned from use case to controller"""

    categories: List[DTOCategory]
    total_count: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "categories": [
                    {
                        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                        "name": "Food & Dining",
                        "description": "Restaurants, groceries and food expenses",
                        "parent_id": None,
                    },
                    {
                        "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
                        "name": "Supermarket",
                        "description": "Grocery store purchases",
                        "parent_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                    },
                ],
                "total_count": 2,
            }
        }
    }
