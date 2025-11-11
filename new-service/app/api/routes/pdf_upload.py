from fastapi import APIRouter, File, UploadFile
from src.presentation.pdf_controller import PDFController
from src.application.extract_pdf_use_case import ExtractPDFUseCase
from src.application.export_to_excel_use_case import ExportToExcelUseCase
from src.infrastructure.bcp_pdf_extractor import BCPPDFExtractor
from src.infrastructure.excel_generator import ExcelGenerator

# Crear router para rutas de upload
router = APIRouter(prefix="/api", tags=["PDF Upload"])

# Configurar dependencias
pdf_extractor = BCPPDFExtractor()
excel_generator = ExcelGenerator()
extract_pdf_use_case = ExtractPDFUseCase(pdf_extractor)
export_to_excel_use_case = ExportToExcelUseCase(pdf_extractor, excel_generator)
pdf_controller = PDFController(extract_pdf_use_case, export_to_excel_use_case)


@router.post("/extract-pdf")
async def extract_pdf_endpoint(file: UploadFile = File(...)):
    """Extrae transacciones de un PDF subido"""
    return await pdf_controller.extract_pdf(file)


@router.post("/extract-pdf/excel")
async def extract_pdf_to_excel_endpoint(file: UploadFile = File(...)):
    """Extrae transacciones de un PDF subido y retorna Excel"""
    return await pdf_controller.extract_pdf_to_excel(file)