from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.presentation.pdf_processor_controller import PDFProcessorController
from src.application.process_pdf_by_name_use_case import ProcessPDFByNameUseCase
from src.infrastructure.advanced_pdf_extractor import AdvancedPDFExtractor

# Crear router para rutas de procesamiento de PDF
router = APIRouter(prefix="/api", tags=["PDF Processing"])

# Configurar dependencias
advanced_pdf_extractor = AdvancedPDFExtractor()
process_pdf_by_name_use_case = ProcessPDFByNameUseCase(advanced_pdf_extractor)
pdf_processor_controller = PDFProcessorController(process_pdf_by_name_use_case)

# Modelos Pydantic para request body
class PDFProcessRequest(BaseModel):
    pdf_filename: str
    type: str  # "debit" o "credit"
    
    class Config:
        json_schema_extra = {
            "example": {
                "pdf_filename": "files/EECC102025_09745280.PDF",
                "type": "debit"
            }
        }

class PDFInfoRequest(BaseModel):
    pdf_filename: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "pdf_filename": "files/EECC102025_09745280.PDF"
            }
        }


@router.post("/process-pdf")
async def process_pdf_by_name_endpoint(request: PDFProcessRequest):
    """
    Procesa un PDF específico por nombre y devuelve el archivo CSV directamente
    
    - **request**: Objeto JSON con el nombre del archivo PDF y tipo de cuenta
    - **pdf_filename**: Nombre del archivo PDF (ej: "files/documento.pdf")
    - **type**: Tipo de cuenta ("debit" o "credit")
    - Devuelve el archivo CSV para descarga directa
    """
    return await pdf_processor_controller.process_pdf_by_name(request.pdf_filename, request.type)


@router.post("/process-pdf/info")
async def process_pdf_info_endpoint(request: PDFInfoRequest):
    """
    Procesa un PDF específico por nombre y devuelve información JSON
    
    - **request**: Objeto JSON con el nombre del archivo PDF
    - **pdf_filename**: Nombre del archivo PDF (ej: "files/documento.pdf")
    - Devuelve información JSON con estadísticas y transacciones
    """
    return await pdf_processor_controller.process_pdf_info(request.pdf_filename)