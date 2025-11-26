import fitz  # PyMuPDF
from typing import BinaryIO
import logging
import os
from dotenv import load_dotenv
from ..Denterprise.entities import ExtractionResult
from ..Denterprise.repositories import PDFExtractorRepository
from ..Denterprise.bcp_parser import BCPStatementParser

logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()


class AdvancedPDFExtractor(PDFExtractorRepository):
    """Extractor avanzado usando PyMuPDF para PDFs problemáticos
    
    Esta clase solo maneja la infraestructura de extracción de texto del PDF.
    La lógica de negocio de parsing está en BCPStatementParser (Domain layer).
    """
    
    def __init__(self):
        self.parser = BCPStatementParser()
    
    def extract_transactions(self, pdf_file: BinaryIO, filename: str) -> ExtractionResult:
        """Extrae transacciones del PDF usando PyMuPDF y delega parsing al domain layer"""
        try:
            # Obtener contraseña de variable de entorno
            password = os.getenv('PDF_PASSWORD')
            
            # Extraer texto completo (SOLO infraestructura)
            full_text = self._extract_text_with_pymupdf(pdf_file, filename, password)
            
            # Delegar toda la lógica de negocio al parser del dominio
            account_code = self.parser.extract_account_code(full_text)
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
                account_code=None
            )
    
    def _extract_text_with_pymupdf(self, pdf_file: BinaryIO, filename: str, password: str = None) -> str:
        """Extrae texto usando PyMuPDF"""
        logger.info(f"Extrayendo texto con PyMuPDF: {filename}")
        if password:
            logger.info("Usando contraseña para abrir PDF protegido")
        
        try:
            text = ""
            # Resetear puntero del archivo
            pdf_file.seek(0)
            pdf_bytes = pdf_file.read()
            
            # Abrir PDF desde bytes
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            # Si el PDF está encriptado, intentar desencriptar
            if pdf_document.is_encrypted:
                if password:
                    if pdf_document.authenticate(password):
                        logger.info("PDF desencriptado exitosamente con PyMuPDF")
                    else:
                        raise Exception("Contraseña incorrecta para PDF")
                else:
                    raise Exception("PDF está encriptado pero no se proporcionó contraseña")
            
            logger.info(f"PDF tiene {pdf_document.page_count} páginas")
            
            for page_num in range(pdf_document.page_count):
                logger.info(f"Procesando página {page_num + 1}")
                page = pdf_document[page_num]
                page_text = page.get_text()
                if page_text:
                    text += f"\n\n--- PÁGINA {page_num + 1} ---\n\n"
                    text += page_text + "\n"
            
            pdf_document.close()
            return text
        except Exception as e:
            logger.error(f"Error con PyMuPDF: {str(e)}")
            raise
