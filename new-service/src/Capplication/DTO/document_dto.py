from typing import List, Optional
import uuid
from datetime import date
from pydantic import BaseModel, ConfigDict

"""
Document DTOs - Data Transfer Objects
Used ONLY for transferring data between controllers and use cases (boundary layer)

These DTOs serve as request/response objects at the interface adapter layer.
Internal domain logic uses entities from Denterprise layer.
"""


class DTOCreateDocumentRequest(BaseModel):
    pdf_filepath: str
    user_email: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "pdf_filepath": "/downloads/documents/bcp_debit/EECC102025_07750301.PDF",
                "user_email": "admin@bcpextractor.com",
            }
        }
    }


class DTOCreateDocumentResponse(BaseModel):
    """Result DTO for PDF processing - returned from use case to controller"""

    success: bool
    document_id: str
    already_exists: bool
    transactions_count: int
    document_processed: bool


# ===========================================================


class DTODocumentItem(BaseModel):
    """Document summary DTO — plain_text is excluded."""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = None
    account: Optional[str] = None
    balance: Optional[float] = None
    processed: bool = False
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    document_format_name: Optional[str] = None


class DTOGetDocumentsRequest(BaseModel):
    """Request DTO for getting all documents - input from controller"""

    skip: int = 0
    limit: int = 100

    model_config = {
        "json_schema_extra": {
            "example": {
                "skip": 0,
                "limit": 100,
            }
        }
    }


class DTOGetDocumentsResponse(BaseModel):
    """Response DTO for get all documents operation - returned from use case to controller"""

    documents: List[DTODocumentItem]
    total_returned: int
    skip: int
    limit: int


# ===========================================================


class DTOBulkCreateDocumentsRequest(BaseModel):
    base_directory: str = "/downloads/documents"
    user_email: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "base_directory": "/downloads/documents",
                "user_email": "admin@bcpextractor.com",
            }
        }
    }


class DTOBulkCreateDocumentItemResult(BaseModel):
    pdf_filepath: str
    document_format: str
    success: bool
    document_id: Optional[str] = None
    already_exists: Optional[bool] = None
    transactions_count: Optional[int] = None
    error: Optional[str] = None


class DTOBulkCreateDocumentsResponse(BaseModel):
    total: int
    created: int
    already_existed: int
    failed: int
    results: List[DTOBulkCreateDocumentItemResult]
