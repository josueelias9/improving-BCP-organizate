"""
PDF Extractor Gateway - Interface Adapter Layer
Extracts transactions from BCP PDF bank statements
Implements the PDFExtractorGateway interface
"""
import fitz  # PyMuPDF
from typing import BinaryIO
import logging
import os
from dotenv import load_dotenv
from src.Denterprise.entities import ExtractionResult
from src.Denterprise.bcp_parser import BCPStatementParser
from src.Capplication.gateways import PDFExtractorGateway

logger = logging.getLogger(__name__)
load_dotenv()


class BCPPDFExtractorGateway(PDFExtractorGateway):
    """Gateway implementation for BCP PDF bank statements extraction"""
    
    def __init__(self):
        self.parser = BCPStatementParser()
    
    def extract_transactions(self, pdf_file: BinaryIO, filename: str) -> ExtractionResult:
        """Extract transactions from PDF file"""
        try:
            password = os.getenv('PDF_PASSWORD')
            full_text = self._extract_text_from_pdf(pdf_file, filename, password)
            
            # Use parser from Denterprise layer for business logic
            account_code, currency = self.parser.extract_account_code(full_text)            
            saldo_anterior = self.parser.extract_saldo_anterior(full_text)
            initial_day, final_day = self.parser.extract_period(full_text)
            transactions = self.parser.parse_transactions(full_text)
            
            return ExtractionResult(
                filename=filename,
                transactions=transactions,
                total_transactions=len(transactions),
                success=True,
                extracted_text=full_text,
                account_code=account_code,
                currency=currency,
                saldo_anterior=saldo_anterior,
                initial_day=initial_day,
                final_day=final_day
            )
            
        except Exception as e:
            logger.error(f"Error extracting transactions from PDF {filename}: {str(e)}")
            return ExtractionResult(
                filename=filename,
                transactions=[],
                total_transactions=0,
                success=False,
                error_message=str(e),
                extracted_text=None,
                account_code=None,
                currency=None
            )
    
    def _extract_text_from_pdf(self, pdf_file: BinaryIO, filename: str, password: str = None) -> str:
        """Extract text from PDF using PyMuPDF"""
        logger.info(f"Extracting text from PDF: {filename}")
        
        try:
            text = ""
            pdf_file.seek(0)
            pdf_bytes = pdf_file.read()
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            if pdf_document.is_encrypted:
                if password:
                    if pdf_document.authenticate(password):
                        logger.info("PDF decrypted successfully")
                    else:
                        raise Exception("Incorrect password for PDF")
                else:
                    raise Exception("PDF is encrypted but no password provided")
            
            logger.info(f"PDF has {pdf_document.page_count} pages")
            
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                page_text = page.get_text()
                if page_text:
                    text += f"\n\n--- PAGE {page_num + 1} ---\n\n{page_text}\n"
            
            pdf_document.close()
            return text
        except Exception as e:
            logger.error(f"Error with PyMuPDF: {str(e)}")
            raise
