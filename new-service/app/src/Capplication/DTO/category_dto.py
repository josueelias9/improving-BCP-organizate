"""
Category DTOs - Data Transfer Objects
Used ONLY for transferring data between controllers and use cases (boundary layer)

These DTOs serve as request/response objects at the interface adapter layer.
Internal domain logic uses entities from Denterprise layer.
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class DTOGetAllCategoriesResponse:
    """Response DTO for get all categories operation - returned from use case to controller"""

    categories: List[Dict[str, Any]]
    total_count: int
