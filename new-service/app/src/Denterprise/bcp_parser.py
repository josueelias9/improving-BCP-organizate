"""
BCP Bank Statement Parser - Domain Layer
Contains business logic for parsing BCP PDF statements
"""
import re
import logging
from typing import List, Optional, Tuple
from src.Capplication.DTO import Transaction

logger = logging.getLogger(__name__)


class BCPStatementParser:
    """Parser for BCP bank statement business logic"""
    
    # Mapeo de meses en español
    MONTHS_MAP = {
        'ENE': '01', 'FEB': '02', 'MAR': '03', 'ABR': '04',
        'MAY': '05', 'JUN': '06', 'JUL': '07', 'AGO': '08',
        'SEP': '09', 'OCT': '10', 'NOV': '11', 'DIC': '12',
        'SET': '09'  # Setiembre
    }
    
    @staticmethod
    def parse_transactions(text: str) -> List[Transaction]:
        """
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
                description = line[12:30].strip()      # Posición 12-30
                internal_transaction = line[34:35].strip()  # Posición 30-31 (*, opcional)
                egreso_str = line[42:54].strip()       # Posición 31-43
                ingreso_str = line[61:].strip() 

                # Validar que las fechas tengan el formato correcto
                if not (len(fecha_proceso) == 5 and len(fecha_valor) == 5):
                    logger.debug(f"Fechas inválidas en línea {line_num}: {fecha_proceso} | {fecha_valor}")
                    continue
                
                # Convertir fechas
                fecha_proceso_formatted = BCPStatementParser.convert_bcp_date(fecha_proceso)
                fecha_valor_formatted = BCPStatementParser.convert_bcp_date(fecha_valor)
                
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
                    description=description,
                    cargos=egreso,
                    abonos=ingreso,
                    internal_transaction=internal_transaction
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

    @staticmethod
    def convert_bcp_date(date_str: str) -> str:
        """Convierte fecha BCP de DDMMM a DD/MM/YYYY"""
        if not date_str or len(date_str) < 5:
            return date_str
        
        try:
            # Extraer día y mes
            day = date_str[:2]
            month_abbr = date_str[2:5].upper()
            
            if month_abbr in BCPStatementParser.MONTHS_MAP:
                month = BCPStatementParser.MONTHS_MAP[month_abbr]
                # Asumir año actual (2025 basado en el ejemplo)
                year = "2025"
                return f"{day}/{month}/{year}"
            else:
                logger.warning(f"Mes no reconocido: {month_abbr}")
                return date_str
                
        except Exception as e:
            logger.error(f"Error convirtiendo fecha {date_str}: {str(e)}")
            return date_str

    @staticmethod
    def extract_account_code(text: str) -> Optional[tuple[str, str]]:
        """
        # description
        Extrae el código de cuenta y la moneda del texto del PDF
        
        # Format
        _NNN-NNNNNNNN-N-NN__CCCCC
        
        where:
        - _: space
        - N: digit
        - C: letters (SOLES or DOLARES)
    
        # example 
        191-04106279-0-55  SOLES
        
        # Returns:
        Tuple[str, str]: (account_code, currency) where currency is 'PEN' or 'USD'
        None if not found
        """
        try:
            lines = text.split('\n')
            
            # Patrón específico BCP: NNN-NNNNNNNN-N-NN  CURRENCY
            # Ejemplo: 191-04106279-0-55  SOLES
            account_pattern = r'\b(\d{3}-\d{8}-\d{1}-\d{2})\s+(SOLES|DOLARES)'
            
            for line in lines:
                # Buscar el patrón de cuenta BCP con moneda
                match = re.search(account_pattern, line)
                if match:
                    account_code = match.group(1)
                    currency_text = match.group(2)
                    # Convertir SOLES/DOLARES a PEN/USD
                    logger.info(f"Código de cuenta BCP encontrado: {account_code}, Moneda: {currency_text}")
                    return (account_code, currency_text)
            
            logger.warning("No se pudo encontrar el código de cuenta en formato NNN-NNNNNNNN-N-NN con moneda")
            return None
            
        except Exception as e:
            logger.error(f"Error extrayendo código de cuenta: {str(e)}")
            return None
    
    @staticmethod
    def extract_saldo_anterior(text: str) -> Optional[float]:
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
    
    @staticmethod
    def extract_period(text: str) -> Tuple[Optional[str], Optional[str]]:
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
