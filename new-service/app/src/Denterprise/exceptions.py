"""
Domain Exceptions - Enterprise Layer
Business rule violations and domain-specific errors
"""


class DomainException(Exception):
    """Base exception for domain/business rule violations"""
    pass


class UnsupportedDocumentTypeException(DomainException):
    """Raised when a document type is not supported by the system"""
    
    def __init__(self, document_type: str, supported_types: list[str] = None):
        self.document_type = document_type
        self.supported_types = supported_types or ["debit"]
        
        message = f"Document type '{document_type}' is not supported."
        if supported_types:
            message += f" Supported types: {', '.join(supported_types)}"
        
        super().__init__(message)
