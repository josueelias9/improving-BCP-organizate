"""
Enhanced PDF processing use case with database persistence
"""
import uuid
from datetime import datetime
from typing import Dict, Any
from sqlmodel import Session
from src.infrastructure.database.crud import (
    create_document,
    create_transactions_bulk,
    get_user_by_email,
    create_user
)
from models import (
    DocumentCreate, DocumentType,
    TransactionCreate, Currency,
    UserCreate, CustomerType
)


class ProcessPDFWithDatabaseUseCase:
    """
    Use case para procesar PDFs con persistencia en base de datos
    """
    
    def __init__(self, pdf_extractor):
        self._pdf_extractor = pdf_extractor
    
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
            # Obtener o crear usuario
            user = get_user_by_email(session, user_email)
            if not user:
                # Crear usuario por defecto si no existe
                user_create = UserCreate(
                    email=user_email,
                    name="Usuario Admin",
                    customer_type=CustomerType.INDIVIDUAL
                )
                user = create_user(session, user_create)
            
            # Procesar PDF usando el extractor existente
            extractor_result = self._pdf_extractor.extract_data(pdf_filename)
            
            if not extractor_result.get("success", False):
                return {
                    "success": False,
                    "message": "Error procesando PDF",
                    "document_id": None,
                    "transactions_count": 0
                }
            
            # Crear registro del documento en la base de datos
            document_create = DocumentCreate(
                filename=pdf_filename,
                document_type=DocumentType.BCP_STATEMENT,
                user_id=user.id,
                processed_at=datetime.utcnow()
            )
            document = create_document(session, document_create)
            
            # Preparar transacciones para inserción en BD
            transactions_to_create = []
            for transaction_data in extractor_result.get("transactions", []):
                transaction_create = TransactionCreate(
                    name=transaction_data.get("id", f"trans_{uuid.uuid4()}"),
                    date=transaction_data.get("date", datetime.utcnow()),
                    amount=float(transaction_data.get("amount", 0.0)),
                    currency=Currency.PEN,  # Asumimos PEN para BCP
                    description=transaction_data.get("description", ""),
                    account_code=transaction_data.get("account_code"),
                    document_id=document.id,
                    user_id=user.id,
                    # Por ahora no asignamos categoría automáticamente
                    category_id=None
                )
                transactions_to_create.append(transaction_create)
            
            # Insertar transacciones en lote
            created_transactions = []
            if transactions_to_create:
                created_transactions = create_transactions_bulk(session, transactions_to_create)
            
            return {
                "success": True,
                "message": f"PDF procesado exitosamente. {len(created_transactions)} transacciones guardadas.",
                "document_id": str(document.id),
                "transactions_count": len(created_transactions),
                "user_id": str(user.id),
                "csv_file": extractor_result.get("csv_file"),
                "filename": extractor_result.get("filename"),
                "statistics": extractor_result.get("statistics"),
                "transactions": [
                    {
                        "id": str(trans.id),
                        "name": trans.name,
                        "date": trans.date.isoformat() if trans.date else None,
                        "amount": trans.amount,
                        "currency": trans.currency,
                        "description": trans.description,
                        "account_code": trans.account_code
                    }
                    for trans in created_transactions
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error procesando PDF: {str(e)}",
                "document_id": None,
                "transactions_count": 0
            }