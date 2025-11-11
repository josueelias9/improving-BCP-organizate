"""
Database management routes
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from src.infrastructure.database.deps import get_db_session
from src.infrastructure.database.db import init_db, create_db_and_tables
from models import User, Category, Document, Transaction
import logging

logger = logging.getLogger(__name__)

# Crear router para rutas de base de datos
router = APIRouter(prefix="/api/database", tags=["Database Management"])


@router.post("/initialize")
async def initialize_database(session: Session = Depends(get_db_session)):
    """
    Inicializa la base de datos con datos por defecto
    
    - Crea las tablas si no existen
    - Crea las categorías por defecto
    - Crea el usuario administrador por defecto
    """
    try:
        logger.info("Starting database initialization...")
        
        # Create tables first
        create_db_and_tables()
        
        # Initialize with default data
        init_db(session)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Base de datos inicializada exitosamente",
                "details": "Se crearon tablas, categorías y usuarios por defecto",
                "status": "success"
            }
        )
    except Exception as e:
        logger.error(f"Error inicializando base de datos: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error inicializando base de datos: {str(e)}"
        )


@router.get("/status")
async def database_status(session: Session = Depends(get_db_session)):
    """
    Obtiene el estado actual de la base de datos
    
    - Cuenta de usuarios registrados
    - Cuenta de categorías disponibles
    - Cuenta de documentos procesados
    - Cuenta de transacciones
    """
    try:
        users = session.exec(select(User)).all()
        categories = session.exec(select(Category)).all()
        documents = session.exec(select(Document)).all()
        transactions = session.exec(select(Transaction)).all()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Estado de la base de datos",
                "status": "connected",
                "counts": {
                    "users": len(users),
                    "categories": len(categories), 
                    "documents": len(documents),
                    "transactions": len(transactions)
                },
                "users_sample": [
                    {
                        "id": str(user.id),
                        "email": user.email,
                        "name": user.name,
                        "customer_type": user.customer_type,
                        "is_active": user.is_active
                    }
                    for user in users[:5]  # Mostrar solo los primeros 5
                ],
                "categories_sample": [
                    {
                        "id": str(cat.id),
                        "name": cat.name,
                        "description": cat.description,
                        "parent_id": str(cat.parent_id) if cat.parent_id else None
                    }
                    for cat in categories[:10]  # Mostrar solo las primeras 10
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error obteniendo estado de base de datos: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estado de base de datos: {str(e)}"
        )


@router.post("/reset")
async def reset_database(session: Session = Depends(get_db_session)):
    """
    Resetea la base de datos (PELIGRO: Elimina todos los datos)
    
    - Elimina todas las transacciones
    - Elimina todos los documentos
    - Elimina todas las categorías
    - Elimina todos los usuarios
    - Reinicializa con datos por defecto
    """
    try:
        logger.warning("⚠️ DANGER: Resetting database - this will delete all data!")
        
        # Delete in correct order due to foreign key constraints
        session.exec(select(Transaction).where(Transaction.id.isnot(None))).all()
        for transaction in session.exec(select(Transaction)).all():
            session.delete(transaction)
            
        for document in session.exec(select(Document)).all():
            session.delete(document)
            
        for category in session.exec(select(Category)).all():
            session.delete(category)
            
        for user in session.exec(select(User)).all():
            session.delete(user)
        
        session.commit()
        
        # Re-initialize with default data
        init_db(session)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Base de datos reseteada y re-inicializada exitosamente",
                "status": "success",
                "warning": "TODOS LOS DATOS FUERON ELIMINADOS"
            }
        )
        
    except Exception as e:
        logger.error(f"Error reseteando base de datos: {e}")
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error reseteando base de datos: {str(e)}"
        )