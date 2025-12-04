"""
Process PDF Use Case - Application Layer
Orchestrates the flow of processing a PDF and creating a document
"""
import logging
from typing import Dict, Any, List, Tuple, BinaryIO
from dataclasses import dataclass

from src.Denterprise.entities import ExtractionResult
from src.Denterprise.exceptions import UnsupportedDocumentTypeException
from src.Capplication.interfaces.db import IDocumentDbGateway, IUserDbGateway
from src.Capplication.interfaces.pdf_extractor import PDFExtractorGateway

logger = logging.getLogger(__name__)


@dataclass
class ProcessPDFResult:
    """Result of processing a PDF"""
    success: bool
    document_id: str
    unique_identifier: str
    already_exists: bool
    transactions_count: int
    message: str


class PDFProcessingUseCase:
    """Use case for processing PDF and creating document"""
    
    def __init__(
        self, 
        document_gateway: IDocumentDbGateway,
        user_gateway: IUserDbGateway,
        pdf_extractor_gateway: PDFExtractorGateway
    ):
        self.document_gateway = document_gateway
        self.user_gateway = user_gateway
        self.pdf_extractor_gateway = pdf_extractor_gateway
    
    def execute(
        self,
        pdf_file: BinaryIO,
        user_email: str,
        document_type: str = "BCP_STATEMENT",
        pdf_filename: str = ""
    ) -> ProcessPDFResult:
        """
        Process PDF file: get/create user, extract transactions, and create document
        
        Args:
            pdf_file: Binary PDF file content
            user_email: Email of the user
            document_type: Type of document (default: BCP_STATEMENT)
            pdf_filename: Optional filename for logging purposes only
            
        Returns:
            ProcessPDFResult with operation details
            
        Raises:
            ValueError: If validation fails
            UnsupportedDocumentTypeException: If document type is not supported
        """
        try:
            # Validate document type (business rule)
            self._validate_document_type(document_type)
            
            # Get or create user
            user = self._get_or_create_user(user_email)
            
            # Extract transactions from PDF
            extraction_result = self.pdf_extractor_gateway.extract_transactions(
                pdf_file, 
                pdf_filename
            )
            
            # Validate and process extraction result
            unique_id, transactions_list = self._process_extraction_result(extraction_result)
            
            # Check if document already exists with this unique_identifier
            existing_document = self.document_gateway.get_by_unique_identifier(unique_id)
            
            if existing_document:
                logger.info(f"Document already exists with unique_id: {unique_id}")
                return ProcessPDFResult(
                    success=True,
                    document_id=str(existing_document.id),
                    unique_identifier=unique_id,
                    already_exists=True,
                    transactions_count=len(transactions_list),
                    message="Document already exists"
                )
            
            # Create new document
            from models import Document, DocumentType
            
            document = Document(
                account_number=extraction_result.account_code or "UNKNOWN",
                type=DocumentType.BCP_STATEMENT if document_type == "BCP_STATEMENT" else DocumentType.DEBIT_STATEMENT,
                currency=extraction_result.currency or "PEN",
                previous_balance=extraction_result.saldo_anterior,
                initial_day=extraction_result.initial_day,
                final_day=extraction_result.final_day,
                data=transactions_list,
                unique_identifier=unique_id,
                user_id=user.id,
            )
            
            created_document = self.document_gateway.create(document)
            
            logger.info(f"Created new document with ID: {created_document.id}")
            
            return ProcessPDFResult(
                success=True,
                document_id=str(created_document.id),
                unique_identifier=unique_id,
                already_exists=False,
                transactions_count=len(transactions_list),
                message=f"PDF processed successfully. {len(transactions_list)} transactions saved."
            )
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise
    
    def _validate_document_type(self, document_type: str) -> None:
        """
        Validate that the document type is supported (business rule)
        
        Args:
            document_type: Type of document to validate
            
        Raises:
            UnsupportedDocumentTypeException: If document type is not supported
        """
        supported_types = ["BCP_STATEMENT", "DEBIT_STATEMENT"]
        
        # For now, only debit statements are fully implemented
        if document_type not in supported_types:
            raise UnsupportedDocumentTypeException(
                document_type=document_type,
                supported_types=supported_types
            )
        
        # Credit card processing not implemented yet
        if document_type == "CREDIT_STATEMENT":
            raise UnsupportedDocumentTypeException(
                document_type="credit",
                supported_types=["debit"]
            )
    
    def _get_or_create_user(self, user_email: str):
        """
        Get existing user or create new one
        
        Args:
            user_email: Email of the user
            
        Returns:
            User object
        """
        user = self.user_gateway.get_by_email(user_email)
        if not user:
            from models import UserCreate, CustomerType
            
            user_create = UserCreate(
                email=user_email,
                name="Admin User",
                customer_type=CustomerType.INDIVIDUAL
            )
            user = self.user_gateway.create(user_create)
            logger.info(f"Created new user with email: {user_email}")
        
        return user
    
    @staticmethod
    def _process_extraction_result(extraction_result: ExtractionResult) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Process extraction result and generate unique identifier and transactions list
        
        Args:
            extraction_result: The result from PDF extraction
            
        Returns:
            Tuple of (unique_id, transactions_list)
            
        Raises:
            ValueError: If extraction result is invalid
        """
        if not extraction_result.success:
            raise ValueError(f"Extraction failed: {extraction_result.error_message or 'Unknown error'}")
        
        # Validate required fields
        if not extraction_result.initial_day:
            raise ValueError("Missing initial_day in extraction result")
        
        if not extraction_result.final_day:
            raise ValueError("Missing final_day in extraction result")
        
        if not extraction_result.account_code:
            raise ValueError("Missing account_code in extraction result")
        
        if not extraction_result.currency:
            raise ValueError("Missing currency in extraction result")
        
        # Convert transactions to dict list
        transactions_list = [t.__dict__ for t in extraction_result.transactions]
        
        # Generate unique identifier
        unique_id = f"{extraction_result.initial_day}__{extraction_result.final_day}__{extraction_result.account_code}__{extraction_result.currency}"
        
        logger.info(f"Processed extraction result: {len(transactions_list)} transactions, unique_id: {unique_id}")
        
        return unique_id, transactions_list
