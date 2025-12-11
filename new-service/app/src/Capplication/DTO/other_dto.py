from dataclasses import dataclass


@dataclass
class DTODocumentSummary:
    """Document summary DTO - simplified view of a document for list responses"""

    id: str
    currency: str
    unique_identifier: str
    processed: bool
    user_id: str
    document_type_id: str
    transactions_count: int
