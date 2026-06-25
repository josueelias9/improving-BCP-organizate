import uuid
from typing import List
from pydantic import BaseModel

"""
Document DTOs - Data Transfer Objects
Used ONLY for transferring data between controllers and use cases (boundary layer)

These DTOs serve as request/response objects at the interface adapter layer.
Internal domain logic uses entities from Denterprise layer.
"""


class DTOPdfProcessingRequest(BaseModel):
    pdf_filepath: str
    user_email: str
    document_type: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "pdf_filepath": "files/EECC102025_09745280.PDF",
                "document_type": "debit",
                "user_email": "admin@bcpextractor.com",
            }
        }
    }


class DTOPdfProcessingResponse(BaseModel):
    """Result DTO for PDF processing - returned from use case to controller"""

    success: bool
    document_id: str
    unique_identifier: str
    already_exists: bool
    transactions_count: int
    message: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "unique_identifier": "09745280-2025-10",
                "already_exists": False,
                "transactions_count": 42,
                "message": "PDF processed successfully",
            }
        }
    }


# ===========================================================


class DTOLoadTransactionsFromDocumentRequest(BaseModel):
    document_id: uuid.UUID

    model_config = {
        "json_schema_extra": {
            "example": {
                "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            }
        }
    }


class DTOLoadTransactionsFromDocumentResponse(BaseModel):
    """Result DTO for loading transactions operation - returned from use case to controller"""

    success: bool
    loaded_count: int
    skipped_count: int
    errors: List[str]
    total_records: int
    document_id: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "loaded_count": 40,
                "skipped_count": 2,
                "errors": [],
                "total_records": 42,
                "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            }
        }
    }


# ===========================================================


class DTOGetAllDocumentsRequest(BaseModel):
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


class DTOGetAllDocumentsResponse(BaseModel):
    """Response DTO for get all documents operation - returned from use case to controller"""

    documents: List[dict]
    total_returned: int
    skip: int
    limit: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "documents": [
                    {
                        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                        "unique_identifier": "09745280-2025-10",
                        "processed": True,
                        "document_type": "debit",
                        "transactions_count": 42,
                    }
                ],
                "total_returned": 1,
                "skip": 0,
                "limit": 100,
            }
        }
    }
