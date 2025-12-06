"""
API Implementation of PDF Processing Repository
"""
import requests
import logging
from typing import Optional
from domain.repositories import PdfProcessingRepository

logger = logging.getLogger(__name__)


class ApiPdfProcessingRepository(PdfProcessingRepository):
    """PDF processing repository using API"""
    
    def __init__(self, base_url: str = "http://new-service:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def process_pdf(self, pdf_filename: str, doc_type: str = "debit", user_email: str = "admin@bcpextractor.com") -> dict:
        """Process PDF file via API"""
        try:
            url = f"{self.base_url}/api/pdf-processing"
            
            payload = {
                "pdf_filename": pdf_filename,
                "type": doc_type,
                "user_email": user_email
            }
            
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"PDF processed successfully: {pdf_filename}")
            return result
            
        except requests.RequestException as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise
