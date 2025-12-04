from fastapi import APIRouter

# Crear router para rutas principales
router = APIRouter(prefix="/api", tags=["Health Check"])


@router.get("")
async def root():
    """Endpoint raíz de la API con información del servicio"""
    return {
        "message": "BCP PDF Extractor Service", 
        "version": "2.0.0",
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