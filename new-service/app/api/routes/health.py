from fastapi import APIRouter

# Crear router para rutas principales
router = APIRouter(prefix="/api", tags=["Health Check"])


@router.get("")
async def root():
    """Endpoint raíz de la API con información del servicio"""
    return {
        "message": "BCP PDF Extractor Service", 
        "version": "2.0.0",
        "endpoints": {
            "upload_and_extract": "/api/extract-pdf",
            "upload_and_excel": "/api/extract-pdf/excel", 
            "process_by_name": "/api/process-pdf (POST with JSON body including 'type')",
            "process_by_name_info": "/api/process-pdf/info (POST with JSON body, no 'type' required)",
            "download_output": "/api/output/{filename}",
            "list_output": "/api/output"
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