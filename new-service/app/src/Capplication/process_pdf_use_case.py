"""
Process PDF Use Case - Application Layer
Orchestrates the flow of processing a PDF and creating a document
"""
import logging
import uuid
from typing import Dict, Any
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
        unique_id: str,
        transactions_list: list,
        user_id: uuid.UUID,
        document_type: str
    ) -> ProcessPDFResult:
        """
        Process PDF extraction result and create document if it doesn't exist
        
        Args:
            extraction_result: The result from PDF extraction
            unique_id: Unique identifier for the document
            transactions_list: List of transactions as dicts
            user_id: User ID who owns the document
            document_type: Type of document
            
        Returns:
            ProcessPDFResult with operation details
            
        Raises:
            ValueError: If validation fails
        """
        try:
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
