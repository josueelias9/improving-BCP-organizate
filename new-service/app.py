from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Query
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from src.presentation.pdf_controller import PDFController
from src.presentation.pdf_processor_controller import PDFProcessorController
from src.application.extract_pdf_use_case import ExtractPDFUseCase
from src.application.export_to_excel_use_case import ExportToExcelUseCase
from src.application.process_pdf_by_name_use_case import ProcessPDFByNameUseCase
from src.infrastructure.bcp_pdf_extractor import BCPPDFExtractor
from src.infrastructure.advanced_pdf_extractor import AdvancedPDFExtractor
from src.infrastructure.excel_generator import ExcelGenerator
import logging
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Modelos Pydantic para request body
class PDFProcessRequest(BaseModel):
    pdf_filename: str
    type: str  # "debit" o "credit"
    
    class Config:
        schema_extra = {
            "example": {
                "pdf_filename": "files/EECC102025_09745280.PDF",
                "type": "debit"
            }
        }

class PDFInfoRequest(BaseModel):
    pdf_filename: str
    
    class Config:
        schema_extra = {
            "example": {
                "pdf_filename": "files/EECC102025_09745280.PDF"
            }
        }

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="BCP PDF Extractor", 
    version="2.0.0",
    description="Servicio para extraer transacciones de PDFs del BCP usando Clean Architecture"
)

# Dependency injection setup
pdf_extractor = BCPPDFExtractor()  # Para uploads
advanced_pdf_extractor = AdvancedPDFExtractor()  # Para archivos por nombre
excel_generator = ExcelGenerator()

# Use cases
extract_pdf_use_case = ExtractPDFUseCase(pdf_extractor)
export_to_excel_use_case = ExportToExcelUseCase(pdf_extractor, excel_generator)
process_pdf_by_name_use_case = ProcessPDFByNameUseCase(advanced_pdf_extractor)

# Controllers
pdf_controller = PDFController(extract_pdf_use_case, export_to_excel_use_case)
pdf_processor_controller = PDFProcessorController(process_pdf_by_name_use_case)

# Routes
@app.get("/")
async def root():
    return {
        "message": "BCP PDF Extractor Service", 
        "version": "2.0.0",
        "endpoints": {
            "upload_and_extract": "/extract-pdf",
            "upload_and_excel": "/extract-pdf/excel", 
            "process_by_name": "/process-pdf (POST with JSON body including 'type')",
            "process_by_name_info": "/process-pdf/info (POST with JSON body, no 'type' required)",
            "download_output": "/output/{filename}",
            "list_output": "/output"
        },
        "example_requests": {
            "process_pdf": {
                "pdf_filename": "files/EECC102025_09745280.PDF",
                "type": "debit"
            },
            "process_pdf_info": {
                "pdf_filename": "files/EECC102025_09745280.PDF"
            }
        }
    }

# Endpoints originales para upload
@app.post("/extract-pdf")
async def extract_pdf_endpoint(file: UploadFile = File(...)):
    """Extrae transacciones de un PDF subido"""
    return await pdf_controller.extract_pdf(file)

@app.post("/extract-pdf/excel")
async def extract_pdf_to_excel_endpoint(file: UploadFile = File(...)):
    """Extrae transacciones de un PDF subido y retorna Excel"""
    return await pdf_controller.extract_pdf_to_excel(file)

# Nuevos endpoints para procesamiento por nombre
@app.post("/process-pdf")
async def process_pdf_by_name_endpoint(request: PDFProcessRequest):
    """
    Procesa un PDF específico por nombre y devuelve el archivo CSV directamente
    
    - **request**: Objeto JSON con el nombre del archivo PDF y tipo de cuenta
    - **pdf_filename**: Nombre del archivo PDF (ej: "files/documento.pdf")
    - **type**: Tipo de cuenta ("debit" o "credit")
    - Devuelve el archivo CSV para descarga directa
    """
    return await pdf_processor_controller.process_pdf_by_name(request.pdf_filename, request.type)

@app.post("/process-pdf/info")
async def process_pdf_info_endpoint(request: PDFInfoRequest):
    """
    Procesa un PDF específico por nombre y devuelve información JSON
    
    - **request**: Objeto JSON con el nombre del archivo PDF
    - **pdf_filename**: Nombre del archivo PDF (ej: "files/documento.pdf")
    - Devuelve información JSON con estadísticas y transacciones
    """
    return await pdf_processor_controller.process_pdf_info(request.pdf_filename)

@app.get("/output/{filename}")
async def download_output_file_endpoint(filename: str):
    """
    Descarga un archivo específico de la carpeta output/
    
    - **filename**: Nombre del archivo a descargar
    """
    return await pdf_processor_controller.download_output_file(filename)

@app.get("/output")
async def list_output_files_endpoint():
    """
    Lista todos los archivos disponibles en la carpeta output/
    """
    return await pdf_processor_controller.list_output_files()