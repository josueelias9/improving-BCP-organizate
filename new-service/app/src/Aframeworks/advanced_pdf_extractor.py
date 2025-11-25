import fitz  # PyMuPDF
import re
from typing import BinaryIO, List, Optional
import logging
import os
from dotenv import load_dotenv
from ..Denterprise.entities import Transaction, ExtractionResult
from ..Denterprise.repositories import PDFExtractorRepository

logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()


class AdvancedPDFExtractor(PDFExtractorRepository):
    """Extractor avanzado usando PyMuPDF para PDFs problemáticos"""
    
    def __init__(self):
        pass
    
    def extract_transactions(self, pdf_file: BinaryIO, filename: str) -> ExtractionResult:
        """Extrae transacciones del PDF usando PyMuPDF"""
        try:
            # Obtener contraseña de variable de entorno
            password = os.getenv('PDF_PASSWORD')
            
            # Extraer texto completo
            full_text = self._extract_text_with_pymupdf(pdf_file, filename, password)
            
            # Extraer código de cuenta
            account_code = self._extract_account_code(full_text)
            
            # Extraer saldo anterior
            saldo_anterior = self._extract_saldo_anterior(full_text)
            
            # Extraer período (initial_day, final_day)
            initial_day, final_day = self._extract_period(full_text)
            
            # Parsear transacciones del texto
            transactions = self._parse_transactions_from_text(full_text)
            
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
    
    def  _parse_transactions_from_text(self, text: str) -> List[Transaction]:
        """

        # find
        NNMM
        N: number
        M: character

        # extract
        Extrae y parsea las transacciones del texto del PDF BCP usando posiciones fijas
        
        Formato BCP (posicional):

                  111111111122222222223333333333444444444455555555556666666666777
        0123456789012345678901234567890123456789012345678901234567890123456789012
        ----- ----- ------------------    -       ------------       ------------
          a     b            c            d             e                 f 

        
        a (0-5):   Fecha procesamiento (5 chars)
        b (6-11):  Fecha valor (5 chars)  
        c (12-30): Descripción (18 chars)
        d (30-31): Transacción interna (1 char)
        e (31-43): Egreso/Cargo (12 chars)
        f (43-55): Ingreso/Abono (12 chars)
        """
        logger.info("Parseando transacciones del texto extraído...")
        logger.info(f"Texto extraído (primeros 1000 caracteres): {text[:1000]}")
        
        transactions = []
        lines = text.split('\n')
        
        # Patrón para detectar líneas que empiezan con fecha (DDMMM)
        date_pattern = r'^\d{2}[A-Z]{3}\s'
        
        for line_num, line in enumerate(lines):
            # NO hacer strip() para preservar las posiciones
            if not line or len(line) < 12:
                continue
            
            # Verificar si la línea empieza con un patrón de fecha
            if not re.match(date_pattern, line):
                continue
            
            logger.debug(f"Línea de transacción encontrada {line_num}: [{line}]")
            
            try:
                # Extraer por posiciones fijas
                fecha_proceso = line[0:5].strip()      # Posición 0-5
                fecha_valor = line[6:11].strip()       # Posición 6-11
                descripcion = line[12:30].strip()      # Posición 12-30
                transaccion_interna = line[34:35].strip()  # Posición 30-31 (*, opcional)
                egreso_str = line[42:54].strip()       # Posición 31-43
                ingreso_str = line[61:].strip() 

                # Validar que las fechas tengan el formato correcto
                if not (len(fecha_proceso) == 5 and len(fecha_valor) == 5):
                    logger.debug(f"Fechas inválidas en línea {line_num}: {fecha_proceso} | {fecha_valor}")
                    continue
                
                # Convertir fechas
                fecha_proceso_formatted = self._convert_bcp_date(fecha_proceso)
                fecha_valor_formatted = self._convert_bcp_date(fecha_valor)
                
                # Parsear montos
                egreso = 0.0
                ingreso = 0.0
                
                if egreso_str:
                    try:
                        egreso = float(egreso_str.replace(',', ''))
                    except ValueError:
                        pass
                
                if ingreso_str:
                    try:
                        ingreso = float(ingreso_str.replace(',', ''))
                    except ValueError:
                        pass
                
                # Crear transacción
                transaction = Transaction(
                    fecha_proceso=fecha_proceso_formatted,
                    fecha_valor=fecha_valor_formatted,
                    descripcion=descripcion,
                    cargos=egreso,
                    abonos=ingreso,
                    transaccion_interna=transaccion_interna
                )
                
                if transaction.is_valid():
                    transactions.append(transaction)
                    logger.debug(f"Transacción válida: {transaction}")
                else:
                    logger.debug(f"Transacción inválida (sin montos): {transaction}")
                
            except Exception as e:
                logger.debug(f"Error parseando línea {line_num}: {line} - {str(e)}")
                continue
        
        logger.info(f"Total de transacciones encontradas: {len(transactions)}")
        return transactions

    def _convert_bcp_date(self, date_str: str) -> str:
        """Convierte fecha BCP de DDMMM a DD/MM/YYYY"""
        if not date_str or len(date_str) < 5:
            return date_str
        
        try:
            # Mapeo de meses en español
            months_map = {
                'ENE': '01', 'FEB': '02', 'MAR': '03', 'ABR': '04',
                'MAY': '05', 'JUN': '06', 'JUL': '07', 'AGO': '08',
                'SEP': '09', 'OCT': '10', 'NOV': '11', 'DIC': '12',
                'SET': '09'  # Setiembre
            }
            
            # Extraer día y mes
            day = date_str[:2]
            month_abbr = date_str[2:5].upper()
            
            if month_abbr in months_map:
                month = months_map[month_abbr]
                # Asumir año actual (2025 basado en el ejemplo)
                year = "2025"
                return f"{day}/{month}/{year}"
            else:
                logger.warning(f"Mes no reconocido: {month_abbr}")
                return date_str
                
        except Exception as e:
            logger.error(f"Error convirtiendo fecha {date_str}: {str(e)}")
            return date_str

    
    def _extract_account_code(self, text: str) -> str:
        """
        Extrae el código de cuenta del texto del PDF
        
        Formato BCP: NNN-NNNNNNNN-N-NN
        Ejemplo: 191-04106279-0-55
        """
        try:
            lines = text.split('\n')
            
            # Patrón específico BCP: NNN-NNNNNNNN-N-NN
            # Ejemplo: 191-04106279-0-55
            account_pattern = r'\b(\d{3}-\d{8}-\d{1}-\d{2})\b'
            
            for line in lines:
                # Buscar el patrón de cuenta BCP
                match = re.search(account_pattern, line)
                if match:
                    account_code = match.group(1)
                    logger.info(f"Código de cuenta BCP encontrado: {account_code}")
                    return account_code
            
            logger.warning("No se pudo encontrar el código de cuenta en formato NNN-NNNNNNNN-N-NN")
            return None
            
        except Exception as e:
            logger.error(f"Error extrayendo código de cuenta: {str(e)}")
            return None
    
    def _extract_saldo_anterior(self, text: str) -> Optional[float]:
        """
        Extrae el saldo anterior del texto del PDF
        
        Formato: SALDO ANTERIOR seguido del monto en posición fija (columna 58-68)
        Ejemplo: ------------SALDO ANTERIOR---------------------------------    NNNNNNN.NN
        """
        try:
            lines = text.split('\n')
            
            for line in lines:
                # Buscar línea que contenga "SALDO ANTERIOR"
                if 'SALDO ANTERIOR' in line:
                    # Extraer monto desde posición 58 en adelante
                    saldo_str = line[58:].strip()
                    
                    if saldo_str:
                        try:
                            saldo = float(saldo_str.replace(',', ''))
                            logger.info(f"Saldo anterior encontrado: {saldo}")
                            return saldo
                        except ValueError:
                            logger.warning(f"No se pudo convertir saldo anterior a número: {saldo_str}")
            
            logger.warning("No se encontró línea con SALDO ANTERIOR")
            return None
            
        except Exception as e:
            logger.error(f"Error extrayendo saldo anterior: {str(e)}")
            return None
    
    def _extract_period(self, text: str) -> tuple[Optional[str], Optional[str]]:
        """
        Extrae el período del estado de cuenta del PDF
        
        Formato: DEL  NN/NN/NN  AL  NN/NN/NN
        Ejemplo: DEL  01/10/25  AL  31/10/25
        
        Returns:
            tuple: (initial_day, final_day) o (None, None) si no se encuentra
        """
        try:
            lines = text.split('\n')
            
            # Patrón: DEL  NN/NN/NN  AL  NN/NN/NN
            period_pattern = r'DEL\s+(\d{2}/\d{2}/\d{2})\s+AL\s+(\d{2}/\d{2}/\d{2})'
            
            for line in lines:
                match = re.search(period_pattern, line.upper())
                if match:
                    initial_day = match.group(1)
                    final_day = match.group(2)
                    logger.info(f"Período encontrado: DEL {initial_day} AL {final_day}")
                    return (initial_day, final_day)
            
            logger.warning("No se encontró línea con patrón DEL NN/NN/NN AL NN/NN/NN")
            return (None, None)
            
        except Exception as e:
            logger.error(f"Error extrayendo período: {str(e)}")
            return (None, None)