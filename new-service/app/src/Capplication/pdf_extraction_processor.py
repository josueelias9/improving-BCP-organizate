"""
PDF Extraction Processor - Application Layer
Processes and validates PDF extraction results
"""
import logging
from typing import Dict, List, Any, Tuple

from src.Denterprise.entities import ExtractionResult

logger = logging.getLogger(__name__)


class PDFExtractionProcessor:
    """Service for processing PDF extraction results"""
    
    @staticmethod
    def process_extraction_result(extraction_result: ExtractionResult) -> Tuple[str, List[Dict[str, Any]]]:
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
