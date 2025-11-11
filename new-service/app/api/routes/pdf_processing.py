from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session
from src.presentation.pdf_processor_controller import PDFProcessorController
from src.application.process_pdf_by_name_use_case import ProcessPDFByNameUseCase
from src.application.process_pdf_with_database_use_case import ProcessPDFWithDatabaseUseCase
from src.infrastructure.advanced_pdf_extractor import AdvancedPDFExtractor
from src.infrastructure.database.deps import SessionDep

# Crear router para rutas de procesamiento de PDF
router = APIRouter(prefix="/api", tags=["PDF Processing"])

# Configurar dependencias
advanced_pdf_extractor = AdvancedPDFExtractor()
process_pdf_by_name_use_case = ProcessPDFByNameUseCase(advanced_pdf_extractor)
process_pdf_with_db_use_case = ProcessPDFWithDatabaseUseCase(advanced_pdf_extractor)
pdf_processor_controller = PDFProcessorController(process_pdf_by_name_use_case)

# Modelos Pydantic para request body
class PDFProcessRequest(BaseModel):
    pdf_filename: str
    type: str  # "debit" o "credit"
    user_email: str = "admin@sistema.com"  # Usuario por defecto
    
    class Config:
        json_schema_extra = {
            "example": {
                "pdf_filename": "files/EECC102025_09745280.PDF",
                "type": "debit",
                "user_email": "admin@sistema.com"
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


@router.post("/process-pdf/database")
async def process_pdf_with_database_endpoint(request: PDFProcessRequest, session: SessionDep):
    """
    Procesa un PDF específico por nombre y guarda los resultados en la base de datos
    
    - **request**: Objeto JSON con el nombre del archivo PDF, tipo y usuario
    - **pdf_filename**: Nombre del archivo PDF (ej: "files/documento.pdf") 
    - **type**: Tipo de cuenta ("debit" o "credit")
    - **user_email**: Email del usuario (opcional, por defecto admin@sistema.com)
    - Devuelve información JSON con los datos guardados en BD
    """
    try:
        # Verificar tipo de PDF
        if request.type.lower() == "credit":
            raise HTTPException(
                status_code=501,
                detail="Procesamiento de PDFs de cuentas de crédito no implementado aún. Solo se soportan cuentas de débito ('debit')."
            )
        elif request.type.lower() != "debit":
            raise HTTPException(
                status_code=400,
                detail="Tipo de PDF no válido. Use 'debit' o 'credit'."
            )
        
        # Verificar que el archivo existe
        import os
        if not os.path.exists(request.pdf_filename):
            raise HTTPException(
                status_code=404, 
                detail=f"El archivo '{request.pdf_filename}' no fue encontrado"
            )
        
        # Procesar PDF con base de datos
        result = process_pdf_with_db_use_case.execute(
            session=session,
            pdf_filename=request.pdf_filename,
            pdf_type=request.type,
            user_email=request.user_email
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=result["message"]
            )
        
        return {
            "message": result["message"],
            "document_id": result["document_id"],
            "user_id": result["user_id"],
            "transactions_count": result["transactions_count"],
            "transactions": result["transactions"],
            "csv_file": result.get("csv_file"),
            "statistics": result.get("statistics")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando PDF con base de datos: {str(e)}"
        )