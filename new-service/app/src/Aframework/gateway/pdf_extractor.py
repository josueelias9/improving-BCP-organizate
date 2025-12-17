"""PDF Extractor Gateway - Interface Adapter Layer
Extracts transactions from BCP PDF bank statements
Implements the PDFExtractorGateway interface
"""

import fitz  # PyMuPDF
from typing import Optional
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
        self.parser_debit = BCPDebitParser()
        self.parser_credit = BCPCreditParser()

    def extract_document(
        self,
        pdf_content: bytes,
        document_type: Optional[str] = None,
    ) -> DocumentEntity:
        """Extract document from PDF content and return DocumentEntity with data

        Args:
            pdf_content: Binary PDF file content as bytes
            document_type: Type of document

        Returns:
            DocumentEntity with extracted transaction data
        """
        try:
            password = os.getenv("PDF_PASSWORD")
            full_text = self._extract_text_from_pdf(pdf_content, password)

            start_date = None
            end_date = None

            if document_type == "bcp_credit":
                # TODO: here is what we discussed about the unique_identifier. The generation of it is being done in the parser.
                # This should be done by the Entity itself.
                data, unique_identifier, start_date, end_date = (
                    self.parser_credit.get_data(full_text)
                )

            else:
                data, unique_identifier, start_date, end_date = (
                    self.parser_debit.get_data(full_text)
                )

            # Return DocumentEntity with the extracted data (currency is now in data)
            return DocumentEntity(
                data=data,
                unique_identifier=unique_identifier or "",
                processed=False,
                start_date=start_date,
                end_date=end_date,
            )

        except Exception as e:
            logger.error(f"Error extracting transactions from PDF: {str(e)}")
            # Return empty DocumentEntity on error
            return DocumentEntity(
                data=[],
                unique_identifier="error_document",
                processed=False,
            )

    def _extract_text_from_pdf(self, pdf_content: bytes, password: str = None) -> str:
        """Extract text from PDF using PyMuPDF"""
        logger.info("Extracting text from PDF")

        try:
            text = ""
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")

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
