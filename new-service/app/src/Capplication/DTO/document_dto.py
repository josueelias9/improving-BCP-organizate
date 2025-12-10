from src.Capplication.DTO.other_dto import DTODocumentSummary

"""
Document DTOs - Data Transfer Objects
Used ONLY for transferring data between controllers and use cases (boundary layer)

These DTOs serve as request/response objects at the interface adapter layer.
Internal domain logic uses entities from Denterprise layer.
"""
import uuid

from typing import List
from dataclasses import dataclass


@dataclass
class DTOPdfProcessingResponse:
    """Result DTO for PDF processing - returned from use case to controller"""

    success: bool
    document_id: str
    unique_identifier: str
    already_exists: bool
    transactions_count: int
    message: str


@dataclass
class DTOLoadTransactionsFromDocumentResponse:
    """Result DTO for loading transactions operation - returned from use case to controller"""

    success: bool
    loaded_count: int
    skipped_count: int
    errors: List[str]
    total_records: int
    document_id: str




@dataclass
class DTOGetAllDocumentsResponse:
    """Response DTO for get all documents operation - returned from use case to controller"""

    documents: List[DTODocumentSummary]
    total_returned: int
    skip: int
    limit: int


@dataclass
class GetAllDocumentsRequest:
    """Request DTO for getting all documents - input from controller"""

    skip: int = 0
    limit: int = 100



@dataclass
class DTOLoadTransactionsFromDocumentRequest:
    document_id: uuid.UUID