from typing import BinaryIO
import uuid
from typing import List
from dataclasses import dataclass


"""
Document DTOs - Data Transfer Objects
Used ONLY for transferring data between controllers and use cases (boundary layer)

These DTOs serve as request/response objects at the interface adapter layer.
Internal domain logic uses entities from Denterprise layer.
"""


@dataclass
class DTOPdfProcessingRequest:
    pdf_file: BinaryIO
    user_email: str
    document_type: str


@dataclass
class DTOPdfProcessingResponse:
    """Result DTO for PDF processing - returned from use case to controller"""

    success: bool
    document_id: str
    unique_identifier: str
    already_exists: bool
    transactions_count: int
    message: str


# ===========================================================


@dataclass
class DTOLoadTransactionsFromDocumentRequest:
    document_id: uuid.UUID


@dataclass
class DTOLoadTransactionsFromDocumentResponse:
    """Result DTO for loading transactions operation - returned from use case to controller"""

    success: bool
    loaded_count: int
    skipped_count: int
    errors: List[str]
    total_records: int
    document_id: str


# ===========================================================


@dataclass
class DTOGetAllDocumentsRequest:
    """Request DTO for getting all documents - input from controller"""

    skip: int = 0
    limit: int = 100


@dataclass
class DTOGetAllDocumentsResponse:
    """Response DTO for get all documents operation - returned from use case to controller"""

    documents: List[dict]
    total_returned: int
    skip: int
    limit: int
