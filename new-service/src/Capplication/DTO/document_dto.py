from typing import List
from pydantic import BaseModel


from ...Denterprise.entities import DocumentEntity

"""
Document DTOs - Data Transfer Objects
Used ONLY for transferring data between controllers and use cases (boundary layer)

These DTOs serve as request/response objects at the interface adapter layer.
Internal domain logic uses entities from Denterprise layer.
"""


class DTOCreateDocumentRequest(BaseModel):
    pdf_filepath: str
    user_email: str
    document_type: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "pdf_filepath": "/shared_files/examples/EECC102025_07750301.PDF",
                "document_type": "bcp_debit",
                "user_email": "admin@bcpextractor.com",
            }
        }
    }


class DTOCreateDocumentResponse(BaseModel):
    """Result DTO for PDF processing - returned from use case to controller"""

    success: bool
    document_id: str
    unique_identifier: str
    already_exists: bool
    transactions_count: int
    document_processed: bool


# ===========================================================


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

    documents: List[DocumentEntity]
    total_returned: int
    skip: int
    limit: int
