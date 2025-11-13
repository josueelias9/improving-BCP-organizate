from fastapi import HTTPException
from fastapi.responses import JSONResponse, FileResponse
import logging
import os
from ..Capplication.process_pdf_by_name_use_case import ProcessPDFByNameUseCase

logger = logging.getLogger(__name__)


class PDFProcessorController:
    """Controller para procesamiento de PDFs por nombre"""
    
    def __init__(self, process_pdf_use_case: ProcessPDFByNameUseCase):
        self._process_pdf_use_case = process_pdf_use_case
    
    async def process_pdf_by_name(self, pdf_filename: str, pdf_type: str = "debit"):
        """
        Procesa un PDF específico por su nombre y devuelve el archivo CSV
        """
        try:
            logger.info(f"Procesando PDF: {pdf_filename}, tipo: {pdf_type}")
            
            # Verificar tipo de PDF
            if pdf_type.lower() == "credit":
                raise HTTPException(
                    status_code=501,
                    detail="Procesamiento de PDFs de cuentas de crédito no implementado aún. Solo se soportan cuentas de débito ('debit')."
                )
            elif pdf_type.lower() != "debit":
                raise HTTPException(
                    status_code=400,
                    detail="Tipo de PDF no válido. Use 'debit' o 'credit'."
                )
            
            # Verificar que el archivo existe
            if not os.path.exists(pdf_filename):
                raise HTTPException(
                    status_code=404, 
                    detail=f"El archivo '{pdf_filename}' no fue encontrado"
                )
            
            # Procesar PDF
            result = self._process_pdf_use_case.execute(pdf_filename, pdf_type)
            
            if not result["success"]:
                raise HTTPException(
                    status_code=500,
                    detail="Error procesando el PDF"
                )
            
            logger.info(f"PDF procesado exitosamente: {len(result['transactions'])} transacciones encontradas")
            
            # Siempre devolver el archivo CSV (aunque esté vacío)
            if result["csv_file"] and os.path.exists(result["csv_file"]):
                return FileResponse(
                    path=result["csv_file"],
                    filename=os.path.basename(result["csv_file"]),
                    media_type='text/csv'
                )
            else:
                # Si por alguna razón no se pudo crear el CSV, devolver error
                raise HTTPException(
                    status_code=500,
                    detail="Error: No se pudo generar el archivo CSV"
                )
            
        except HTTPException:
            raise
        except FileNotFoundError as e:
            logger.error(f"Archivo no encontrado: {str(e)}")
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(f"Error procesando PDF {pdf_filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error procesando PDF: {str(e)}")
    
    async def process_pdf_info(self, pdf_filename: str):
        """
        Procesa un PDF específico por su nombre y devuelve información JSON
        """
        try:
            logger.info(f"Procesando PDF para info: {pdf_filename}")
            
            # Verificar que el archivo existe
            if not os.path.exists(pdf_filename):
                raise HTTPException(
                    status_code=404, 
                    detail=f"El archivo '{pdf_filename}' no fue encontrado"
                )
            
            # Procesar PDF
            result = self._process_pdf_use_case.execute(pdf_filename)
            
            if not result["success"]:
                raise HTTPException(
                    status_code=500,
                    detail="Error procesando el PDF"
                )
            
            logger.info(f"PDF procesado exitosamente: {len(result['transactions'])} transacciones encontradas")
            
            return JSONResponse(
                status_code=200,
                content={
                    "message": f"PDF '{pdf_filename}' procesado exitosamente",
                    "filename": result["filename"],
                    "csv_file": result["csv_file"],
                    "statistics": result["statistics"],
                    "transactions": result["transactions"]
                }
            )
            
        except HTTPException:
            raise
        except FileNotFoundError as e:
            logger.error(f"Archivo no encontrado: {str(e)}")
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(f"Error procesando PDF {pdf_filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error procesando PDF: {str(e)}")
    
    async def download_output_file(self, filename: str):
        """
        Descarga un archivo de la carpeta output/
        """
        try:
            file_path = os.path.join("output", filename)
            
            if not os.path.exists(file_path):
                raise HTTPException(
                    status_code=404,
                    detail=f"El archivo '{filename}' no fue encontrado en output/"
                )
            
            return FileResponse(
                path=file_path,
                filename=filename,
                media_type='application/octet-stream'
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error descargando archivo {filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error descargando archivo: {str(e)}")
    
    async def list_output_files(self):
        """
        Lista todos los archivos en la carpeta output/
        """
        try:
            output_dir = "output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Carpeta output creada",
                        "files": []
                    }
                )
            
            files = []
            for filename in os.listdir(output_dir):
                file_path = os.path.join(output_dir, filename)
                if os.path.isfile(file_path):
                    file_stats = os.stat(file_path)
                    files.append({
                        "filename": filename,
                        "size": file_stats.st_size,
                        "modified": file_stats.st_mtime
                    })
            
            return JSONResponse(
                status_code=200,
                content={
                    "message": f"Se encontraron {len(files)} archivos en output/",
                    "files": files
                }
            )
            
        except Exception as e:
            logger.error(f"Error listando archivos de output: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error listando archivos: {str(e)}")