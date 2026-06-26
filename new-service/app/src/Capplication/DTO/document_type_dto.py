"""
DocumentType DTOs - Data Transfer Objects
Used ONLY for transferring data between controllers and use cases (boundary layer)

These DTOs serve as request/response objects at the interface adapter layer.
Internal domain logic uses entities from Denterprise layer.
"""

from typing import List, Dict, Any
from pydantic import BaseModel


class DTOGetAllDocumentTypesResponse(BaseModel):
    """Response DTO for get all document types operation - returned from use case to controller"""

    document_types: List[Dict[str, Any]]
    total_count: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "document_types": [
                    {"id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890", "name": "debit"},
                    {"id": "b2c3d4e5-f6a7-8901-bcde-f12345678901", "name": "credit"},
                ],
                "total_count": 2,
            }
        }
    }
