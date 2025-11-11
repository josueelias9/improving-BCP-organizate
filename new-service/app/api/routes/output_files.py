from fastapi import APIRouter
from src.presentation.pdf_processor_controller import PDFProcessorController
from src.application.process_pdf_by_name_use_case import ProcessPDFByNameUseCase
from src.infrastructure.advanced_pdf_extractor import AdvancedPDFExtractor

# Crear router para rutas de archivos de salida
router = APIRouter(prefix="/api", tags=["Output Files"])

# Configurar dependencias
advanced_pdf_extractor = AdvancedPDFExtractor()
process_pdf_by_name_use_case = ProcessPDFByNameUseCase(advanced_pdf_extractor)
pdf_processor_controller = PDFProcessorController(process_pdf_by_name_use_case)


@router.get("/output/{filename}")
async def download_output_file_endpoint(filename: str):
    """
    Descarga un archivo específico de la carpeta output/
    
    - **filename**: Nombre del archivo a descargar
    """
    return await pdf_processor_controller.download_output_file(filename)


@router.get("/output")
async def list_output_files_endpoint():
    """
    Lista todos los archivos disponibles en la carpeta output/
    """
    return await pdf_processor_controller.list_output_files()