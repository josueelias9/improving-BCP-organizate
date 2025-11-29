"""
Process PDF Use Case - Application Layer
Orchestrates the flow of processing a PDF and creating a document
"""
import logging
import uuid
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass

from src.Denterprise.entities import ExtractionResult
from src.Capplication.gateways import IDocumentGateway

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


class ProcessPDFUseCase:
    """Use case for processing PDF and creating document"""
    
    def __init__(self, document_gateway: IDocumentGateway):
        self.document_gateway = document_gateway
    
    def execute(
        self,
        extraction_result: ExtractionResult,
        user_id: uuid.UUID,
        document_type: str = "BCP_STATEMENT"
    ) -> ProcessPDFResult:
        """
        Process PDF extraction result and create document if it doesn't exist
        
        Args:
            extraction_result: The result from PDF extraction
            user_id: User ID who owns the document
            document_type: Type of document (default: BCP_STATEMENT)
            
        Returns:
            ProcessPDFResult with operation details
            
        Raises:
            ValueError: If validation fails
        """
        try:
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
                user_id=user_id,
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
            raise ValueError(f"Error processing PDF: {str(e)}")
    
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
