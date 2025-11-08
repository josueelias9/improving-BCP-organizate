from fastapi import FastAPI, File, UploadFile
from src.presentation.pdf_controller import PDFController
from src.application.extract_pdf_use_case import ExtractPDFUseCase
from src.application.export_to_excel_use_case import ExportToExcelUseCase
from src.infrastructure.bcp_pdf_extractor import BCPPDFExtractor
from src.infrastructure.excel_generator import ExcelGenerator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="BCP PDF Extractor", version="1.0.0")

# Dependency injection setup
pdf_extractor = BCPPDFExtractor()
excel_generator = ExcelGenerator()

extract_pdf_use_case = ExtractPDFUseCase(pdf_extractor)
export_to_excel_use_case = ExportToExcelUseCase(pdf_extractor, excel_generator)

pdf_controller = PDFController(extract_pdf_use_case, export_to_excel_use_case)

# Routes
@app.get("/")
async def root():
    return {"message": "BCP PDF Extractor Service", "version": "1.0.0"}

@app.post("/extract-pdf")
async def extract_pdf_endpoint(file: UploadFile = File(...)):
    return await pdf_controller.extract_pdf(file)

@app.post("/extract-pdf/excel")
async def extract_pdf_to_excel_endpoint(file: UploadFile = File(...)):
    return await pdf_controller.extract_pdf_to_excel(file)