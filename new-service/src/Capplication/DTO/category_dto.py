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


class DTOReadCategoriesResponse(BaseModel):
    """Response DTO for read all categories operation - returned from use case to controller"""

    categories: List[DTOCategory]
    total_count: int
