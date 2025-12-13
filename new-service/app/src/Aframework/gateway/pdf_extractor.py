"""PDF Extractor Gateway - Interface Adapter Layer
Extracts transactions from BCP PDF bank statements
Implements the PDFExtractorGateway interface
"""

import fitz  # PyMuPDF
from typing import BinaryIO, List, Optional, Tuple
from datetime import date
import logging
import os
import uuid
from dotenv import load_dotenv
from src.Aframework.parser.bcp_statement_parser import BCPStatementParser
from src.Capplication.gateway.pdf_extractor import IPDFExtractorGateway
from src.Denterprise.entities import DocumentEntity

logger = logging.getLogger(__name__)
load_dotenv()


class PDFExtractorGateway(IPDFExtractorGateway):
    """Gateway implementation for BCP PDF bank statements extraction"""

    def __init__(self):
        self.parser = BCPStatementParser()

    def extract_document(
        self, pdf_file: BinaryIO, filename: str = "", document_type_id: Optional[str] = None
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

            # Use parser from Denterprise layer for business logic
            account_code, currency = self.parser.extract_account_code(full_text)
            saldo_anterior = self.parser.extract_saldo_anterior(full_text)
            initial_day, final_day = self.parser.extract_period(full_text)
            transactions = self.parser.parse_transactions(full_text)

            # Convert transactions to data list
            data = []
            for transaction in transactions:
                data.append({
                    "fecha_proceso": transaction.fecha_proceso.isoformat() if transaction.fecha_proceso else None,
                    "fecha_valor": transaction.fecha_valor.isoformat() if transaction.fecha_valor else None,
                    "description": transaction.description,
                    "cargos": transaction.cargos,
                    "abonos": transaction.abonos,
                    "internal_transaction": transaction.internal_transaction,
                })

            # Return DocumentEntity with the extracted data
            return DocumentEntity(
                data=data,
                currency=currency or "",
                unique_identifier=f"{account_code}_{initial_day}_{final_day}" if account_code and initial_day and final_day else filename,
                processed=False,
                document_type_id=document_type_id,
            )

        except Exception as e:
            logger.error(f"Error extracting transactions from PDF: {str(e)}")
            # Return empty DocumentEntity on error
            return DocumentEntity(
                data=[],
                currency="",
                unique_identifier=filename or "error_document",
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
