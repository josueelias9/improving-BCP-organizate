"""
Enhanced PDF processing use case with database persistence - Clean Architecture
"""
from datetime import datetime
from typing import Dict, Any
from sqlmodel import Session
from .repositories import IUserRepository, IDocumentRepository
from models import (
    DocumentCreate, DocumentType,
    UserCreate, CustomerType
)


class ProcessPDFWithDatabaseUseCase:
    """
    Use case para procesar PDFs con persistencia en base de datos
    Depends on abstractions (repositories), not concrete implementations
    """
    
    def __init__(self, 
                 pdf_extractor, 
                 user_repository: IUserRepository, 
                 document_repository: IDocumentRepository):
        self._pdf_extractor = pdf_extractor
        self._user_repository = user_repository
        self._document_repository = document_repository
    
    def execute(
        self,
        session: Session,
        pdf_filename: str,
        pdf_type: str = "debit",
        user_email: str = "admin@sistema.com"
    ) -> Dict[str, Any]:
        """
        Procesa un PDF y guarda los resultados en la base de datos
        
        Args:
            session: Sesión de base de datos
            pdf_filename: Nombre del archivo PDF a procesar
            pdf_type: Tipo de PDF (debit/credit)
            user_email: Email del usuario que procesa el PDF
            
        Returns:
            Diccionario con el resultado del procesamiento
        """
        try:
            # Obtener o crear usuario usando repository abstraction
            user = self._user_repository.get_user_by_email(session, user_email)
            if not user:
                # Crear usuario por defecto si no existe
                user_create = UserCreate(
                    email=user_email,
                    name="Usuario Admin",
                    customer_type=CustomerType.INDIVIDUAL
                )
                user = self._user_repository.create_user(session, user_create)
            
            # Procesar PDF usando el nuevo método extract_transactions
            # Abrir el archivo PDF y pasarlo al extractor
            with open(pdf_filename, 'rb') as pdf_file:
                extraction_result = self._pdf_extractor.extract_transactions(pdf_file, pdf_filename)
            
            if not extraction_result.success:
                return {
                    "success": False,
                    "message": f"Error procesando PDF: {extraction_result.error_message or 'Error desconocido'}",
                    "document_id": None,
                    "transactions_count": 0
                }
            
            # Preparar datos JSON para la columna 'data'
            # Cada fila extraída será un elemento de una lista, cada elemento será un objeto con atributos
            transactions_list = []
            for transaction in extraction_result.transactions:
                transaction_dict = {
                    "fecha_proceso": transaction.fecha_proceso,
                    "fecha_valor": transaction.fecha_valor,
                    "descripcion": transaction.descripcion,
                    "cargos": transaction.cargos,
                    "abonos": transaction.abonos,
                    "transaccion_interna": transaction.transaccion_interna
                }
                transactions_list.append(transaction_dict)
            
            # Preparar los datos como diccionario (no lista)
            json_data = {
                "filename": pdf_filename,
                "account_code": extraction_result.account_code,
                "transactions": transactions_list,
                "extracted_at": datetime.utcnow().isoformat(),
                "total_transactions": extraction_result.total_transactions,
                "extracted_text_preview": extraction_result.extracted_text[:500] if extraction_result.extracted_text else "No text extracted",
                "debug_info": f"Success: {extraction_result.success}, Total found: {len(extraction_result.transactions)}"
            }
            
            # Crear registro del documento en la base de datos con los datos JSON usando repository
            document_create = DocumentCreate(
                account_number=extraction_result.account_code or "UNKNOWN",
                type=DocumentType.BCP_STATEMENT,
                user_id=user.id,
                previous_balance=extraction_result.saldo_anterior,
                initial_day=extraction_result.initial_day,
                final_day=extraction_result.final_day,
                data=json_data  # Guardar los datos extraídos como JSON
            )
            document = self._document_repository.create_document(session, document_create)
            
            return {
                "success": True,
                "message": f"PDF procesado exitosamente. {len(transactions_list)} transacciones guardadas como JSON en la tabla Documents.",
                "document_id": str(document.id),
                "transactions_count": len(transactions_list),
                "user_id": str(user.id),
                "account_code": extraction_result.account_code,
                "filename": extraction_result.filename,
                "data": json_data  # Devolver los datos JSON guardados
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error procesando PDF: {str(e)}",
                "document_id": None,
                "transactions_count": 0
            }