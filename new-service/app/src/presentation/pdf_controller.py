from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import io
import logging
from ..application.extract_pdf_use_case import ExtractPDFUseCase
from ..application.export_to_excel_use_case import ExportToExcelUseCase

logger = logging.getLogger(__name__)


class PDFController:
    """Controller for PDF extraction endpoints"""
    
    def __init__(self, extract_pdf_use_case: ExtractPDFUseCase, export_to_excel_use_case: ExportToExcelUseCase):
        self._extract_pdf_use_case = extract_pdf_use_case
        self._export_to_excel_use_case = export_to_excel_use_case
    
    async def extract_pdf(self, file: UploadFile = File(...)):
        """Extract transaction data from BCP PDF statement"""
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        try:
            # Read file content
            content = await file.read()
            pdf_file = io.BytesIO(content)
            
            # Execute use case
            result = self._extract_pdf_use_case.execute(pdf_file, file.filename)
            
            if not result.success:
                raise HTTPException(status_code=500, detail=result.error_message)
            
            if not result.has_transactions:
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "No transaction data found in PDF",
                        "filename": file.filename,
                        "transactions": []
                    }
                )
            
            # Convert transactions to dictionaries for JSON response
            transactions_data = [
                {
                    'fecha_proceso': t.fecha_proceso,
                    'fecha_consumo': t.fecha_consumo,
                    'descripcion': t.descripcion,
                    'tipo_operacion': t.tipo_operacion,
                    'soles': t.soles,
                    'dolares': t.dolares
                }
                for t in result.transactions
            ]
            
            return JSONResponse(
                status_code=200,
                content={
                    "message": f"Successfully extracted {result.total_transactions} transactions",
                    "filename": file.filename,
                    "transactions": transactions_data
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    
    async def extract_pdf_to_excel(self, file: UploadFile = File(...)):
        """Extract transaction data from BCP PDF and return as Excel file"""
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        try:
            # Read file content
            content = await file.read()
            pdf_file = io.BytesIO(content)
            
            # Execute use case
            excel_file = self._export_to_excel_use_case.execute(pdf_file, file.filename)
            
            return StreamingResponse(
                io.BytesIO(excel_file.read()),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename=transactions_{file.filename.replace('.pdf', '.xlsx')}"}
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            if "No transaction data found" in str(e):
                raise HTTPException(status_code=404, detail=str(e))
            raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")