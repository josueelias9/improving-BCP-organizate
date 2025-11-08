#!/usr/bin/env python3
"""
Script para extraer contenido del PDF BCP y generar CSV de transacciones
"""
import pdfplumber
import PyPDF2
import fitz  # PyMuPDF
import pandas as pd
import re
from datetime import datetime
import json
import logging
import io
import os
import csv
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFExtractor:
    def __init__(self):
        self.columns_mapping = {
            "fecha_proceso": ["Fecha de proceso", "Fecha proceso", "F. Proceso"],
            "fecha_consumo": ["Fecha de consumo", "Fecha consumo", "F. Consumo"],
            "descripcion": ["Descripción", "Descripcion", "Concepto"],
            "tipo_operacion": ["Tipo de Operación", "Tipo Operacion", "Tipo"],
            "soles": ["Soles", "S/", "PEN"],
            "dolares": ["Dólares", "Dolares", "US$", "USD"]
        }
    
    def extract_text_with_pymupdf(self, pdf_path: str, password: str = None) -> str:
        """Extrae texto usando PyMuPDF (fitz) como alternativa más robusta"""
        logger.info(f"Intentando extraer texto con PyMuPDF: {pdf_path}")
        if password:
            logger.info("Usando contraseña para abrir PDF protegido")
        
        try:
            text = ""
            pdf_document = fitz.open(pdf_path)
            
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
        """Extrae texto usando PyPDF2 como alternativa"""
        logger.info(f"Intentando extraer texto con PyPDF2: {pdf_path}")
        if password:
            logger.info("Usando contraseña para abrir PDF protegido")
        
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Si el PDF está encriptado, intentar desencriptar
                if pdf_reader.is_encrypted:
                    if password:
                        pdf_reader.decrypt(password)
                        logger.info("PDF desencriptado exitosamente")
                    else:
                        raise Exception("PDF está encriptado pero no se proporcionó contraseña")
                
                logger.info(f"PDF tiene {len(pdf_reader.pages)} páginas")
                
                for i, page in enumerate(pdf_reader.pages):
                    logger.info(f"Procesando página {i+1}")
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- PÁGINA {i+1} ---\n"
                        text += page_text + "\n"
                
            return text
        except Exception as e:
            logger.error(f"Error con PyPDF2: {str(e)}")
            raise
    
    def extract_text_from_pdf(self, pdf_path: str, password: str = None) -> str:
        """Extrae todo el texto del PDF"""
        logger.info(f"Extrayendo texto de: {pdf_path}")
        if password:
            logger.info("Usando contraseña para abrir PDF protegido")
        try:
            text = ""
            with pdfplumber.open(pdf_path, password=password) as pdf:
                logger.info(f"PDF tiene {len(pdf.pages)} páginas")
                for i, page in enumerate(pdf.pages):
                    logger.info(f"Procesando página {i+1}")
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- PÁGINA {i+1} ---\n"
                        text += page_text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extrayendo texto del PDF: {str(e)}")
            raise
    
    def extract_tables_from_pdf(self, pdf_path: str, password: str = None) -> list:
        """Extrae todas las tablas del PDF"""
        logger.info(f"Extrayendo tablas de: {pdf_path}")
        if password:
            logger.info("Usando contraseña para abrir PDF protegido")
        try:
            all_tables = []
            with pdfplumber.open(pdf_path, password=password) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    logger.info(f"Buscando tablas en página {page_num + 1}")
                    page_tables = page.extract_tables()
                    if page_tables:
                        logger.info(f"Encontradas {len(page_tables)} tablas en página {page_num + 1}")
                        for table_num, table in enumerate(page_tables):
                            if table and len(table) > 1:
                                df = pd.DataFrame(table[1:], columns=table[0])
                                table_info = {
                                    'page': page_num + 1,
                                    'table_number': table_num + 1,
                                    'rows': len(df),
                                    'columns': len(df.columns),
                                    'column_names': list(df.columns),
                                    'data': df.to_dict('records')
                                }
                                all_tables.append(table_info)
                    else:
                        logger.info(f"No se encontraron tablas en página {page_num + 1}")
            return all_tables
        except Exception as e:
            logger.error(f"Error extrayendo tablas del PDF: {str(e)}")
            raise
    
    def clean_date(self, date_str: str) -> str:
        """Limpia y estandariza formato de fecha"""
        if pd.isna(date_str) or not date_str:
            return None
        
        date_str = str(date_str).strip()
        
        # Patrones de fecha comunes en estados BCP
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
                    if len(match.group(1)) == 4:  # Año primero
                        year, month, day = match.groups()
                    else:  # Día primero (común en Perú)
                        day, month, year = match.groups()
                    
                    date_obj = datetime.strptime(f"{year}-{month:0>2}-{day:0>2}", "%Y-%m-%d")
                    return date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    continue
        
        return date_str
    
    def clean_amount(self, amount_str: str) -> float:
        """Limpia y convierte string de monto a float"""
        if pd.isna(amount_str) or not amount_str:
            return 0.0
        
        amount_str = str(amount_str).strip()
        
        # Remover símbolos de moneda y formato común
        amount_str = re.sub(r'[S/\$USD,]', '', amount_str)
        amount_str = re.sub(r'\s+', '', amount_str)
        
        # Manejar montos negativos en paréntesis
        if '(' in amount_str and ')' in amount_str:
            amount_str = '-' + re.sub(r'[()]', '', amount_str)
        
        try:
            return float(amount_str) if amount_str else 0.0
        except ValueError:
            return 0.0

    def parse_transactions_from_text(self, text: str) -> list:
        """Extrae y parsea las transacciones del texto"""
        logger.info("Parseando transacciones del texto extraído...")
        
        transactions = []
        lines = text.split('\n')
        
        # Buscar líneas que contengan transacciones
        # Patrón típico: fecha fecha descripción lugar tipo monto
        transaction_pattern = re.compile(
            r'(\d{2}\w{3})\s+(\d{2}\w{3})\s+([^A-Z]*[A-Z][^A-Z]*)\s+([A-Z][A-Z\s]*)\s+(CONSUMO|PAGO|COMISION|INTERES)\s+([0-9,.]+(?:-)?)\s*([0-9,.]*(?:-)?)?'
        )
        
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
                                    monto_str = parts[tipo_idx + 1].replace(',', '').replace('-', '')
                                    soles = float(monto_str) if monto_str else 0.0
                                    # Si es pago, hacer negativo
                                    if 'PAGO' in tipo_operacion and '-' in parts[tipo_idx + 1]:
                                        soles = -soles
                                except:
                                    soles = 0.0
                            
                            if tipo_idx + 2 < len(parts):
                                try:
                                    monto_str = parts[tipo_idx + 2].replace(',', '').replace('-', '')
                                    dolares = float(monto_str) if monto_str else 0.0
                                    # Si es pago, hacer negativo
                                    if 'PAGO' in tipo_operacion and '-' in parts[tipo_idx + 2]:
                                        dolares = -dolares
                                except:
                                    dolares = 0.0
                            
                            # Limpiar descripción
                            descripcion = re.sub(r'\s+', ' ', descripcion).strip()
                            
                            transaction = {
                                'fecha_proceso': self.parse_date(fecha_proceso),
                                'fecha_consumo': self.parse_date(fecha_consumo),
                                'descripcion': descripcion,
                                'tipo_operacion': tipo_operacion,
                                'soles': soles,
                                'dolares': dolares
                            }
                            
                            transactions.append(transaction)
                            logger.info(f"Transacción encontrada: {transaction}")
                            
                    except Exception as e:
                        logger.debug(f"Error parseando línea {line_num}: {line} - {str(e)}")
                        continue
        
        logger.info(f"Total de transacciones encontradas: {len(transactions)}")
        return transactions
    
    def parse_date(self, date_str: str) -> str:
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

def main():
    pdf_path = "EECC102025_09745280.PDF"
    logger.info(f"Iniciando extracción de: {pdf_path}")
    
    # Obtener contraseña de variable de entorno
    password = os.getenv('PDF_PASSWORD')
    if not password:
        logger.warning("Variable de entorno PDF_PASSWORD no encontrada, intentando sin contraseña")
    else:
        logger.info("Usando contraseña desde variable de entorno PDF_PASSWORD")
    
    extractor = PDFExtractor()
    
    try:
        # Probar con PyMuPDF primero (más robusto)
        logger.info("=== INTENTANDO EXTRACCIÓN CON PYMUPDF ===")
        try:
            full_text = extractor.extract_text_with_pymupdf(pdf_path, password)
            
            # Guardar texto en archivo
            with open("extracted_text.txt", "w", encoding="utf-8") as f:
                f.write(full_text)
            logger.info("Texto guardado en: extracted_text.txt")
            
            # Parsear transacciones del texto
            logger.info("=== PARSEANDO TRANSACCIONES ===")
            transactions = extractor.parse_transactions_from_text(full_text)
            
            if transactions:
                # Crear CSV con las transacciones
                csv_filename = "transactions.csv"
                with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['fecha_proceso', 'fecha_consumo', 'descripcion', 'tipo_operacion', 'soles', 'dolares']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    # Escribir header
                    writer.writeheader()
                    
                    # Escribir transacciones
                    for transaction in transactions:
                        writer.writerow(transaction)
                
                logger.info(f"CSV generado: {csv_filename}")
                
                # Mostrar resumen de transacciones
                print(f"\n=== TRANSACCIONES ENCONTRADAS ===")
                print(f"Total de transacciones: {len(transactions)}")
                print("\nPrimeras transacciones:")
                for i, transaction in enumerate(transactions[:5]):
                    print(f"{i+1}. {transaction['fecha_proceso']} | {transaction['descripcion']} | S/{transaction['soles']} | US${transaction['dolares']}")
                
                # Mostrar estadísticas
                total_soles = sum(t['soles'] for t in transactions)
                total_dolares = sum(t['dolares'] for t in transactions)
                consumos = [t for t in transactions if t['tipo_operacion'] == 'CONSUMO']
                pagos = [t for t in transactions if t['tipo_operacion'] == 'PAGO']
                
                print(f"\n=== ESTADÍSTICAS ===")
                print(f"Total en soles: S/ {total_soles:.2f}")
                print(f"Total en dólares: US$ {total_dolares:.2f}")
                print(f"Consumos: {len(consumos)}")
                print(f"Pagos: {len(pagos)}")
                
            else:
                logger.warning("No se encontraron transacciones en el texto")
            
            # Mostrar primeras líneas del texto
            lines = full_text.split('\n')[:20]
            print("\n=== PRIMERAS 20 LÍNEAS DEL TEXTO ===")
            for i, line in enumerate(lines, 1):
                if line.strip():  # Solo mostrar líneas no vacías
                    print(f"{i:2d}: {line}")
            
            print(f"\n=== RESUMEN ===")
            print(f"Total de caracteres extraídos: {len(full_text)}")
            total_lines = len(full_text.split('\n'))
            print(f"Total de líneas: {total_lines}")
            
            logger.info("Extracción con PyMuPDF completada exitosamente")
            return
            
        except Exception as e:
            logger.error(f"PyMuPDF falló: {str(e)}")
            raise  # Si PyMuPDF falla, no intentar otros métodos ya que es el más robusto
        
        logger.info("Extracción completada exitosamente")
        
    except Exception as e:
        logger.error(f"Error en la extracción: {str(e)}")
        logger.info("Intentando verificar el archivo PDF...")
        
        # Verificar si es realmente un PDF
        try:
            with open(pdf_path, 'rb') as f:
                first_bytes = f.read(10)
                print(f"Primeros bytes del archivo: {first_bytes}")
                if b'%PDF' not in first_bytes:
                    logger.error("El archivo no parece ser un PDF válido")
                else:
                    logger.info("El archivo parece ser un PDF válido")
        except Exception as verify_error:
            logger.error(f"Error verificando archivo: {str(verify_error)}")
        
        raise

if __name__ == "__main__":
    main()