"""
Dependency injection configuration - Interface layer
"""
from src.Aframeworks.database.crud.user import UserRepository
from src.Aframeworks.database.crud.document import DocumentRepository
from src.Aframeworks.advanced_pdf_extractor import AdvancedPDFExtractor
from src.Capplication.process_pdf_with_database_use_case import ProcessPDFWithDatabaseUseCase


def get_user_repository() -> UserRepository:
    """Get User repository instance"""
    return UserRepository()


def get_document_repository() -> DocumentRepository:
    """Get Document repository instance"""
    return DocumentRepository()


def get_pdf_extractor() -> AdvancedPDFExtractor:
    """Get PDF extractor instance"""
    return AdvancedPDFExtractor()


def get_process_pdf_use_case() -> ProcessPDFWithDatabaseUseCase:
    """Get Process PDF use case with dependencies injected"""
    return ProcessPDFWithDatabaseUseCase(
        pdf_extractor=get_pdf_extractor(),
        user_repository=get_user_repository(),
        document_repository=get_document_repository()
    )