from pydantic import BaseModel


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
    document_id: str | None = None
    already_exists: bool | None = None
    transactions_count: int | None = None
    error: str | None = None


class DTOBulkCreateDocumentsResponse(BaseModel):
    total: int
    created: int
    already_existed: int
    failed: int
    results: list[DTOBulkCreateDocumentItemResult]
    links: list[dict[str, str]] = []
