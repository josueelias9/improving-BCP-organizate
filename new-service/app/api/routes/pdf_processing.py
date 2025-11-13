from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session
from src.application.process_pdf_with_database_use_case import ProcessPDFWithDatabaseUseCase
from src.infrastructure.advanced_pdf_extractor import AdvancedPDFExtractor
from src.infrastructure.database.deps import SessionDep

# Crear router para rutas de procesamiento de PDF
router = APIRouter(prefix="/api", tags=["PDF Processing"])

# Configurar dependencias
advanced_pdf_extractor = AdvancedPDFExtractor()
process_pdf_with_db_use_case = ProcessPDFWithDatabaseUseCase(advanced_pdf_extractor)

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



@router.post("/process-pdf")
async def process_pdf_endpoint(request: PDFProcessRequest, session: SessionDep):
    """
    Procesa un PDF específico por nombre y guarda los datos extraídos en la tabla Documents
    
    - **request**: Objeto JSON con el nombre del archivo PDF, tipo y usuario
    - **pdf_filename**: Nombre del archivo PDF (ej: "files/documento.pdf") 
    - **type**: Tipo de cuenta ("debit" o "credit")
    - **user_email**: Email del usuario (opcional, por defecto admin@sistema.com)
    - Los datos extraídos se guardan como JSON en la columna 'data' de la tabla Documents
    - Cada fila extraída será un elemento de una lista, cada elemento será un objeto con atributos
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
            "success": True,
            "message": result["message"],
            "document_id": result["document_id"],
            "user_id": result["user_id"],
            "account_number": result.get("account_number"),
            "filename": result.get("filename"),
            "transactions_count": result["transactions_count"],
            "data_saved_to_database": "Datos extraídos guardados como JSON en tabla Documents, columna 'data'"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando PDF: {str(e)}"
        )