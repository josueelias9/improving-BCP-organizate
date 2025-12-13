"""PDF Extractor Gateway - Interface Adapter Layer
Extracts transactions from BCP PDF bank statements
Implements the PDFExtractorGateway interface
"""

import fitz  # PyMuPDF
from typing import BinaryIO, Optional
import logging
import os
from dotenv import load_dotenv
from src.Aframework.parser.bcp_debit_parser import BCPDebitParser
from src.Aframework.parser.bcp_credit_parser import BCPCreditParser
from src.Capplication.gateway.pdf_extractor import IPDFExtractorGateway
from src.Denterprise.entities import DocumentEntity

logger = logging.getLogger(__name__)
load_dotenv()


class PDFExtractorGateway(IPDFExtractorGateway):
    """Gateway implementation for BCP PDF bank statements extraction"""



    def __init__(self):
        self.parser = BCPDebitParser()
        self.parser_credit = BCPCreditParser()

    def extract_document(
        self, pdf_file: BinaryIO, document_type_id: Optional[str] = None,
        document_type: Optional[str] = None
    ) -> DocumentEntity:
        """Extract document from PDF file and return DocumentEntity with data
        
        Args:
            pdf_file: Binary PDF file content
            filename: Filename for unique identifier
            document_type_id: UUID of the document type
            
        Returns:
            DocumentEntity with extracted transaction data
        """
        try:
            password = os.getenv("PDF_PASSWORD")
            full_text = self._extract_text_from_pdf(pdf_file, password)

            if document_type == "bcp_credit":
                data = self.parser_credit.get_data(full_text)

            else:
                data = self.parser.get_data(full_text)

            # Return DocumentEntity with the extracted data
            return DocumentEntity(
                data=data,
                currency=data["currency"] or "",
                unique_identifier=f"{data['account_code']}__{data['initial_day']}__{data['final_day']}",
                processed=False,
                document_type_id=document_type_id,
            )

        except Exception as e:
            logger.error(f"Error extracting transactions from PDF: {str(e)}")
            # Return empty DocumentEntity on error
            return DocumentEntity(
                data=[],
                currency="",
                unique_identifier="error_document",
                processed=False,
            )

    def _extract_text_from_pdf(self, pdf_file: BinaryIO, password: str = None) -> str:
        """Extract text from PDF using PyMuPDF"""
        logger.info("Extracting text from PDF")

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
