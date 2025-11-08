import fitz  # PyMuPDF
import pandas as pd
import re
from datetime import datetime
from typing import BinaryIO, List, Dict, Any
import logging
import os
from dotenv import load_dotenv
from ..domain.entities import Transaction, ExtractionResult
from ..domain.repositories import PDFExtractorRepository

logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()


class AdvancedPDFExtractor(PDFExtractorRepository):
    """Extractor avanzado usando PyMuPDF para PDFs problemáticos"""
    
    def __init__(self):
        self.columns_mapping = {
            "fecha_proceso": ["Fecha de proceso", "Fecha proceso", "F. Proceso"],
            "fecha_consumo": ["Fecha de consumo", "Fecha consumo", "F. Consumo"],
            "descripcion": ["Descripción", "Descripcion", "Concepto"],
            "tipo_operacion": ["Tipo de Operación", "Tipo Operacion", "Tipo"],
            "soles": ["Soles", "S/", "PEN"],
            "dolares": ["Dólares", "Dolares", "US$", "USD"]
        }
    
    def extract_transactions(self, pdf_file: BinaryIO, filename: str) -> ExtractionResult:
        """Extrae transacciones del PDF usando PyMuPDF"""
        try:
            # Obtener contraseña de variable de entorno
            password = os.getenv('PDF_PASSWORD')
            
            # Extraer texto completo
            full_text = self._extract_text_with_pymupdf(pdf_file, filename, password)
            
            # Parsear transacciones del texto
            transactions = self._parse_transactions_from_text(full_text)
            
            return ExtractionResult(
                filename=filename,
                transactions=transactions,
                total_transactions=len(transactions),
                success=True,
                extracted_text=full_text
            )
            
        except Exception as e:
            logger.error(f"Error extracting transactions from PDF {filename}: {str(e)}")
            return ExtractionResult(
                filename=filename,
                transactions=[],
                total_transactions=0,
                success=False,
                error_message=str(e),
                extracted_text=None
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
                    text += f"\n--- PÁGINA {page_num + 1} ---\n"
                    text += page_text + "\n"
            
            pdf_document.close()
            return text
        except Exception as e:
            logger.error(f"Error con PyMuPDF: {str(e)}")
            raise
    
    def _parse_transactions_from_text(self, text: str) -> List[Transaction]:
        """Extrae y parsea las transacciones del texto"""
        logger.info("Parseando transacciones del texto extraído...")
        
        transactions = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Buscar líneas que parezcan transacciones
            # Formato: DDMmm DDMmm DESCRIPCION LUGAR TIPO MONTO_SOLES MONTO_DOLARES
            if re.search(r'\d{2}\w{3}\s+\d{2}\w{3}', line):
                logger.debug(f"Línea {line_num}: {line}")
                
                # Intentar parsear la línea
                parts = line.split()
                if len(parts) >= 6:
                    try:
                        fecha_proceso = parts[0]
                        fecha_consumo = parts[1]
                        
                        # Encontrar donde empieza el tipo de operación
                        tipo_idx = -1
                        for i, part in enumerate(parts):
                            if part in ['CONSUMO', 'PAGO', 'COMISION', 'INTERES']:
                                tipo_idx = i
                                break
                        
                        if tipo_idx > 2:
                            descripcion = ' '.join(parts[2:tipo_idx])
                            tipo_operacion = parts[tipo_idx]
                            
                            # Obtener montos
                            soles = 0.0
                            dolares = 0.0
                            
                            if tipo_idx + 1 < len(parts):
                                try:
                                    monto_str = parts[tipo_idx + 1].replace(',', '')
                                    is_negative = '-' in monto_str
                                    monto_str = monto_str.replace('-', '')
                                    soles = float(monto_str) if monto_str else 0.0
                                    # Si es pago o tiene signo negativo, hacer negativo
                                    if 'PAGO' in tipo_operacion or is_negative:
                                        soles = -abs(soles)
                                except:
                                    soles = 0.0
                            
                            if tipo_idx + 2 < len(parts):
                                try:
                                    monto_str = parts[tipo_idx + 2].replace(',', '')
                                    is_negative = '-' in monto_str
                                    monto_str = monto_str.replace('-', '')
                                    dolares = float(monto_str) if monto_str else 0.0
                                    # Si es pago o tiene signo negativo, hacer negativo
                                    if 'PAGO' in tipo_operacion or is_negative:
                                        dolares = -abs(dolares)
                                except:
                                    dolares = 0.0
                            
                            # Limpiar descripción
                            descripcion = re.sub(r'\s+', ' ', descripcion).strip()
                            
                            transaction = Transaction(
                                fecha_proceso=self._parse_date(fecha_proceso),
                                fecha_consumo=self._parse_date(fecha_consumo),
                                descripcion=descripcion,
                                tipo_operacion=tipo_operacion,
                                soles=soles,
                                dolares=dolares
                            )
                            
                            if transaction.is_valid():
                                transactions.append(transaction)
                                logger.debug(f"Transacción encontrada: {transaction}")
                            
                    except Exception as e:
                        logger.debug(f"Error parseando línea {line_num}: {line} - {str(e)}")
                        continue
        
        logger.info(f"Total de transacciones encontradas: {len(transactions)}")
        return transactions
    
    def _parse_date(self, date_str: str) -> str:
        """Convierte fecha del formato DDMmm a DD/MM/YYYY"""
        if not date_str or len(date_str) < 5:
            return date_str
        
        try:
            # Mapeo de meses en español
            months_map = {
                'Ene': '01', 'Feb': '02', 'Mar': '03', 'Abr': '04',
                'May': '05', 'Jun': '06', 'Jul': '07', 'Ago': '08',
                'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dic': '12',
                'Set': '09'  # Setiembre
            }
            
            # Extraer día y mes
            day = date_str[:2]
            month_abbr = date_str[2:]
            
            if month_abbr in months_map:
                month = months_map[month_abbr]
                # Asumir año 2025 (o detectar del contexto)
                year = "2025"
                return f"{day}/{month}/{year}"
            
        except Exception as e:
            logger.debug(f"Error parseando fecha {date_str}: {str(e)}")
        
        return date_str