"""
Document DTOs - Data Transfer Objects
Used for transferring document data between layers
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class DTODocumentData:
    """Data structure for document information"""

    id: str
    data: List[Dict[str, Any]]
    currency: str
    processed: bool


@dataclass
class DTOProcessPDFResult:
    """Result of processing a PDF"""

    success: bool
    document_id: str
    unique_identifier: str
    already_exists: bool
    transactions_count: int
    message: str
