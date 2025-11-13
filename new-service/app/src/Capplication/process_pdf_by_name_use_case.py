import os
import csv
from typing import Dict, Any
from ..Ddomain.entities import ExtractionResult
from ..Ddomain.repositories import PDFExtractorRepository


class ProcessPDFByNameUseCase:
    """Caso de uso para procesar PDFs por nombre de archivo"""
    
    def __init__(self, pdf_extractor: PDFExtractorRepository):
        self._pdf_extractor = pdf_extractor
    
    def execute(self, pdf_filename: str, pdf_type: str = "debit", output_dir: str = "output") -> Dict[str, Any]:
        """
        Procesa un PDF específico y guarda los resultados en la carpeta output
        
        Args:
            pdf_filename: Nombre del archivo PDF a procesar
            pdf_type: Tipo de PDF ("debit" o "credit")
            output_dir: Directorio donde guardar los archivos de salida
            
        Returns:
            Dict con información del procesamiento
        """
        # Verificar que el archivo existe
        if not os.path.exists(pdf_filename):
            raise FileNotFoundError(f"El archivo {pdf_filename} no existe")
        
        # Crear directorio de salida si no existe
        os.makedirs(output_dir, exist_ok=True)
        
        # Abrir archivo PDF
        with open(pdf_filename, 'rb') as pdf_file:
            # Extraer transacciones
            result = self._pdf_extractor.extract_transactions(pdf_file, pdf_filename)
        
        if not result.success:
            raise Exception(result.error_message or "Error en la extracción")
        
        # Generar nombres de archivo de salida
        base_name = os.path.splitext(os.path.basename(pdf_filename))[0]
        
        # Si es tipo debit y hay código de cuenta, crear nombre simplificado
        if pdf_type.lower() == "debit" and result.account_code:
            # Extraer solo la parte EECC del nombre original (antes del primer _)
            prefix_part = base_name.split('_')[0]  # EECC102025
            csv_filename = f"{prefix_part}_{result.account_code}"
        else:
            # Formato original para otros casos
            csv_filename = f"{base_name}_transactions"
        
        csv_output = os.path.join(output_dir, f"{csv_filename}.csv")
        
        # Guardar CSV con transacciones (siempre crear el archivo, aunque esté vacío)
        with open(csv_output, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'fecha_proceso', 'fecha_consumo', 'descripcion', 'tipo_operacion', 'soles', 'dolares']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Escribir header
            writer.writeheader()
            
            # Escribir transacciones (si las hay)
            if result.transactions:
                for i, transaction in enumerate(result.transactions, 1):
                    # Usar el nombre del CSV como base para el ID
                    transaction_id = f"{csv_filename}_{i}"
                    writer.writerow({
                        'id': transaction_id,
                        'fecha_proceso': transaction.fecha_proceso,
                        'fecha_consumo': transaction.fecha_consumo,
                        'descripcion': transaction.descripcion,
                        'tipo_operacion': transaction.tipo_operacion,
                        'soles': transaction.soles,
                        'dolares': transaction.dolares
                    })
        
        # Calcular estadísticas
        total_soles = sum(t.soles for t in result.transactions)
        total_dolares = sum(t.dolares for t in result.transactions)
        consumos = [t for t in result.transactions if t.tipo_operacion == 'CONSUMO']
        pagos = [t for t in result.transactions if t.tipo_operacion == 'PAGO']
        
        return {
            "success": True,
            "filename": pdf_filename,
            "csv_file": csv_output,  # Siempre devolver el path del CSV
            "account_code": result.account_code,  # Agregar código de cuenta
            "statistics": {
                "total_transactions": result.total_transactions,
                "total_soles": total_soles,
                "total_dolares": total_dolares,
                "consumos": len(consumos),
                "pagos": len(pagos)
            },
            "transactions": [
                {
                    "id": f"{csv_filename}_{i}",
                    "fecha_proceso": t.fecha_proceso,
                    "fecha_consumo": t.fecha_consumo,
                    "descripcion": t.descripcion,
                    "tipo_operacion": t.tipo_operacion,
                    "soles": t.soles,
                    "dolares": t.dolares
                }
                for i, t in enumerate(result.transactions, 1)
            ]
        }