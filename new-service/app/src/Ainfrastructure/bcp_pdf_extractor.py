import pdfplumber
import pandas as pd
import re
from datetime import datetime
from typing import BinaryIO, List, Dict, Any
import logging
from ..Ddomain.entities import Transaction, ExtractionResult
from ..Ddomain.repositories import PDFExtractorRepository

logger = logging.getLogger(__name__)


class BCPPDFExtractor(PDFExtractorRepository):
    """Implementation of PDF extractor for BCP bank statements"""
    
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
        """Extract transactions from BCP PDF statement"""
        try:
            tables = self._extract_tables_from_pdf(pdf_file)
            transactions = []
            
            for table in tables:
                # Identify columns
                column_mapping = self._identify_transaction_columns(table)
                
                if not column_mapping:
                    logger.warning(f"No transaction columns found in table on page {table.get('page_number', 'unknown')}")
                    continue
                
                # Extract and clean data
                for _, row in table.iterrows():
                    transaction_data = self._extract_transaction_data(row, column_mapping)
                    transaction = Transaction(**transaction_data)
                    
                    if transaction.is_valid():
                        transactions.append(transaction)
            
            return ExtractionResult(
                filename=filename,
                transactions=transactions,
                total_transactions=len(transactions),
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error extracting transactions from PDF: {str(e)}")
            return ExtractionResult(
                filename=filename,
                transactions=[],
                total_transactions=0,
                success=False,
                error_message=str(e)
            )
    
    def _extract_tables_from_pdf(self, pdf_file: BinaryIO) -> List[pd.DataFrame]:
        """Extract tables from PDF file"""
        tables = []
        with pdfplumber.open(pdf_file) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_tables = page.extract_tables()
                for table in page_tables:
                    if table and len(table) > 1:  # Ensure table has header and data
                        df = pd.DataFrame(table[1:], columns=table[0])
                        df['page_number'] = page_num + 1
                        tables.append(df)
        return tables
    
    def _identify_transaction_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Identify which columns correspond to our target fields"""
        column_mapping = {}
        df_columns = [str(col).strip() for col in df.columns]
        
        for target_field, possible_names in self.columns_mapping.items():
            for col in df_columns:
                for possible_name in possible_names:
                    if possible_name.lower() in col.lower():
                        column_mapping[target_field] = col
                        break
                if target_field in column_mapping:
                    break
        
        return column_mapping
    
    def _extract_transaction_data(self, row: pd.Series, column_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Extract transaction data from a table row"""
        transaction_data = {}
        
        # Extract fecha_proceso
        if 'fecha_proceso' in column_mapping:
            fecha_proceso = self._clean_date(row.get(column_mapping['fecha_proceso']))
            transaction_data['fecha_proceso'] = fecha_proceso
        
        # Extract fecha_consumo
        if 'fecha_consumo' in column_mapping:
            fecha_consumo = self._clean_date(row.get(column_mapping['fecha_consumo']))
            transaction_data['fecha_consumo'] = fecha_consumo
        
        # Extract descripcion
        if 'descripcion' in column_mapping:
            descripcion = str(row.get(column_mapping['descripcion'], '')).strip()
            transaction_data['descripcion'] = descripcion if descripcion != 'nan' else ''
        
        # Extract tipo_operacion
        if 'tipo_operacion' in column_mapping:
            tipo_operacion = str(row.get(column_mapping['tipo_operacion'], '')).strip()
            transaction_data['tipo_operacion'] = tipo_operacion if tipo_operacion != 'nan' else ''
        
        # Extract soles
        if 'soles' in column_mapping:
            soles = self._clean_amount(row.get(column_mapping['soles']))
            transaction_data['soles'] = soles
        
        # Extract dolares
        if 'dolares' in column_mapping:
            dolares = self._clean_amount(row.get(column_mapping['dolares']))
            transaction_data['dolares'] = dolares
        
        return transaction_data
    
    def _clean_date(self, date_str: str) -> str:
        """Clean and standardize date format"""
        if pd.isna(date_str) or not date_str:
            return None
        
        date_str = str(date_str).strip()
        
        # Common date patterns in BCP statements
        date_patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',
            r'(\d{1,2})-(\d{1,2})-(\d{4})',
            r'(\d{4})/(\d{1,2})/(\d{1,2})',
            r'(\d{4})-(\d{1,2})-(\d{1,2})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    if len(match.group(1)) == 4:  # Year first
                        year, month, day = match.groups()
                    else:  # Day first (common in Peru)
                        day, month, year = match.groups()
                    
                    date_obj = datetime.strptime(f"{year}-{month:0>2}-{day:0>2}", "%Y-%m-%d")
                    return date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    continue
        
        return date_str
    
    def _clean_amount(self, amount_str: str) -> float:
        """Clean and convert amount string to float"""
        if pd.isna(amount_str) or not amount_str:
            return 0.0
        
        amount_str = str(amount_str).strip()
        
        # Remove currency symbols and common formatting
        amount_str = re.sub(r'[S/\$USD,]', '', amount_str)
        amount_str = re.sub(r'\s+', '', amount_str)
        
        # Handle negative amounts in parentheses
        if '(' in amount_str and ')' in amount_str:
            amount_str = '-' + re.sub(r'[()]', '', amount_str)
        
        try:
            return float(amount_str) if amount_str else 0.0
        except ValueError:
            return 0.0