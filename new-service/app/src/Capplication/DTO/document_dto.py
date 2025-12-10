"""
Document DTOs - Data Transfer Objects
Used ONLY for transferring data between controllers and use cases (boundary layer)

These DTOs serve as request/response objects at the interface adapter layer.
Internal domain logic uses entities from Denterprise layer.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class DTOProcessPDFResult:
    """Result DTO for PDF processing - returned from use case to controller"""

    success: bool
    document_id: str
    unique_identifier: str
    already_exists: bool
    transactions_count: int
    message: str
