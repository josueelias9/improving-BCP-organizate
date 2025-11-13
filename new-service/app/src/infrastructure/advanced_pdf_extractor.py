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
            "fecha_proceso": ["FECHA PROC.", "Fecha Proc.", "F. Proceso", "Fecha de proceso"],
            "fecha_valor": ["FECHA VALOR", "Fecha Valor", "F. Valor", "Fecha valor"],
            "descripcion": ["DESCRIPCION", "Descripción", "DESCRIPCIÓN", "Descripcion", "Concepto"],
            "cargos": ["CARGOS / DEBE", "Cargos / Debe", "CARGOS", "Debe", "Cargo"],
            "abonos": ["ABONOS / HABER", "Abonos / Haber", "ABONOS", "Haber", "Abono"]
        }
    
    def extract_transactions(self, pdf_file: BinaryIO, filename: str) -> ExtractionResult:
        """Extrae transacciones del PDF usando PyMuPDF"""
        try:
            # Obtener contraseña de variable de entorno
            password = os.getenv('PDF_PASSWORD')
            
            # Extraer texto completo
            full_text = self._extract_text_with_pymupdf(pdf_file, filename, password)
            
            # Extraer código de cuenta
            account_code = self._extract_account_code(full_text)
            
            # Parsear transacciones del texto
            transactions = self._parse_transactions_from_text(full_text)
            
            return ExtractionResult(
                filename=filename,
                transactions=transactions,
                total_transactions=len(transactions),
                success=True,
                extracted_text=full_text,
                account_code=account_code
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
                    text += f"\n--- PÁGINA {page_num + 1} ---\n"
                    text += page_text + "\n"
            
            pdf_document.close()
            return text
        except Exception as e:
            logger.error(f"Error con PyMuPDF: {str(e)}")
            raise
    
    def _parse_transactions_from_text(self, text: str) -> List[Transaction]:
        """Extrae y parsea las transacciones del texto del PDF BCP"""
        logger.info("Parseando transacciones del texto extraído...")
        logger.info(f"Texto extraído (primeros 1000 caracteres): {text[:1000]}")
        
        transactions = []
        lines = text.split('\n')
        
        # Patrón específico para transacciones BCP: DDMMM DDMMM DESCRIPCION [MONTO] [MONTO]
        # Ejemplos: 15OCT 15OCT, 01OCT 01OCT
        transaction_pattern = r'^(\d{2}[A-Z]{3})\s+(\d{2}[A-Z]{3})\s+(.+)$'
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Buscar líneas que coincidan con el patrón de transacción
            match = re.match(transaction_pattern, line)
            if match:
                logger.debug(f"Línea de transacción encontrada {line_num}: {line}")
                
                try:
                    fecha_proceso = match.group(1)  # ej: 15OCT
                    fecha_valor = match.group(2)    # ej: 15OCT
                    resto = match.group(3).strip()   # Descripción + montos
                    
                    # Parsear el resto de la línea
                    transaction = self._parse_bcp_transaction_line(fecha_proceso, fecha_valor, resto)
                    if transaction and transaction.is_valid():
                        transactions.append(transaction)
                        logger.debug(f"Transacción válida encontrada: {transaction}")
                    
                except Exception as e:
                    logger.debug(f"Error parseando línea {line_num}: {line} - {str(e)}")
                    continue
        
        logger.info(f"Total de transacciones encontradas: {len(transactions)}")
        return transactions

    def _parse_bcp_transaction_line(self, fecha_proceso: str, fecha_valor: str, resto: str) -> Transaction:
        """Parsea una línea de transacción BCP específicamente"""
        logger.debug(f"Parseando: {fecha_proceso} {fecha_valor} {resto}")
        
        # Convertir fechas de DDMMM a formato estándar
        fecha_proceso_formatted = self._convert_bcp_date(fecha_proceso)
        fecha_valor_formatted = self._convert_bcp_date(fecha_valor)
        
        # Analizar el resto de la línea para extraer descripción y montos
        # Los montos están alineados por columnas, típicamente al final
        
        # Buscar montos decimales con formato ##.## o ###.##
        money_pattern = r'\b\d{1,6}\.\d{2}\b'
        montos = re.findall(money_pattern, resto)
        
        # Si no hay montos decimales, buscar números enteros
        if not montos:
            int_money_pattern = r'\b\d{1,6}\b'
            potential_montos = re.findall(int_money_pattern, resto)
            # Filtrar números que probablemente son montos (mayor a 0.50)
            montos = [m for m in potential_montos if float(m) >= 1]
        
        # Remover montos del texto para obtener descripción limpia
        descripcion = resto
        for monto in montos:
            # Remover el monto y espacios alrededor
            descripcion = re.sub(rf'\s*{re.escape(monto)}\s*', ' ', descripcion, count=1)
        
        # Limpiar descripción
        descripcion = re.sub(r'\s+', ' ', descripcion).strip()
        # Remover asteriscos que aparecen en algunas transacciones
        descripcion = descripcion.replace('*', '').strip()
        
        # Determinar cargos y abonos basado en la posición de los montos
        cargos = 0.0
        abonos = 0.0
        
        if montos:
            # Analizar la posición del monto en la línea original
            # Si aparece cerca del final, es más probable que sea un cargo
            # Si aparece muy al final (después de muchos espacios), podría ser abono
            
            last_monto = float(montos[-1])
            
            # Buscar la posición del monto en la línea original
            monto_pos = resto.rfind(montos[-1])
            total_length = len(resto)
            
            # Si el monto está muy al final (después del 80% de la línea)
            # y hay muchos espacios antes, probablemente es abono
            if monto_pos > total_length * 0.8:
                spaces_before_amount = len(resto[monto_pos-20:monto_pos].strip()) == 0 if monto_pos >= 20 else False
                if spaces_before_amount:
                    abonos = last_monto
                else:
                    cargos = last_monto
            else:
                # Si está más hacia la izquierda, probablemente es cargo
                cargos = last_monto
            
            # Casos especiales basados en la descripción
            if any(keyword in descripcion.upper() for keyword in [
                'ABON', 'ABONO', 'DEPOSITO', 'PAGO YAPE DE', 'TRAN.CTAS.PROP.BM'
            ]):
                # Es un abono
                abonos = last_monto
                cargos = 0.0
            elif any(keyword in descripcion.upper() for keyword in [
                'PAGO YAPE A', 'RETIRO', 'COMISION', 'ITF'
            ]):
                # Es un cargo
                cargos = last_monto
                abonos = 0.0
        
        transaction = Transaction(
            fecha_proceso=fecha_proceso_formatted,
            fecha_valor=fecha_valor_formatted,
            descripcion=descripcion,
            cargos=cargos,
            abonos=abonos
        )
        
        logger.debug(f"Transacción parseada: {transaction}")
        return transaction

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
    
    def _extract_account_code(self, text: str) -> str:
        """Extrae el código de cuenta del texto del PDF"""
        try:
            lines = text.split('\n')
            
            # Buscar líneas que contengan "CODIGO DE CUENTA" o variaciones
            patterns = [
                r'CODIGO\s*DE\s*CUENTA\s*:?\s*(\d+)',
                r'CÓDIGO\s*DE\s*CUENTA\s*:?\s*(\d+)',
                r'COD\.\s*CUENTA\s*:?\s*(\d+)',
                r'CUENTA\s*N[°º]?\s*:?\s*(\d+)',
                r'N[°º]\s*CUENTA\s*:?\s*(\d+)'
            ]
            
            for line in lines:
                line = line.strip().upper()
                if not line:
                    continue
                
                # Probar cada patrón
                for pattern in patterns:
                    match = re.search(pattern, line)
                    if match:
                        account_code = match.group(1)
                        logger.info(f"Código de cuenta encontrado: {account_code}")
                        return account_code
            
            # Si no se encuentra con los patrones, buscar números de tarjeta (para tarjetas de crédito)
            card_patterns = [
                r'(\d{4})-?(\d{2}[X0-9]{2})-?([X0-9]{4})-?(\d{4})',  # 4280-82XX-XXXX-2148
                r'(\d{6}[X0-9]{6}\d{4})',  # 428082XXXXXX2148
                r'NUMERO\s*DE\s*TARJETA\s*:?\s*(\d{4}[X0-9\-]{8,})',
                r'TARJETA\s*N[°º]?\s*:?\s*(\d{4}[X0-9\-]{8,})'
            ]
            
            for line in lines:
                line_upper = line.strip().upper()
                if not line_upper:
                    continue
                
                # Buscar patrones de número de tarjeta
                for pattern in card_patterns:
                    match = re.search(pattern, line_upper)
                    if match:
                        if len(match.groups()) > 1:
                            # Formato con grupos separados (ej: 4280-82XX-XXXX-2148)
                            card_number = ''.join(match.groups()).replace('X', '0')
                        else:
                            # Formato en un solo grupo
                            card_number = match.group(1).replace('X', '0').replace('-', '')
                        
                        # Solo tomar números de tarjeta válidos (16 dígitos aproximadamente)
                        if len(card_number) >= 12:
                            logger.info(f"Número de tarjeta encontrado: {card_number}")
                            return card_number
            
            # Si no se encuentra con los patrones, buscar números largos cerca de "CUENTA" o "TARJETA"
            for line in lines:
                line = line.strip().upper()
                if 'CUENTA' in line or 'TARJETA' in line:
                    # Buscar secuencias de dígitos de al menos 8 caracteres
                    numbers = re.findall(r'\d{8,}', line)
                    if numbers:
                        account_code = numbers[0]
                        logger.info(f"Código de cuenta encontrado (método alternativo): {account_code}")
                        return account_code
            
            logger.warning("No se pudo encontrar el código de cuenta o número de tarjeta en el PDF")
            return None
            
        except Exception as e:
            logger.error(f"Error extrayendo código de cuenta: {str(e)}")
            return None