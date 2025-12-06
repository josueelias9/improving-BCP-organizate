"""
API Router - Central routing configuration
"""
from fastapi import APIRouter

from api.routes import health, document, transaction, category

api_router = APIRouter()

# Include all route modules
api_router.include_router(health.router)
api_router.include_router(document.router)
api_router.include_router(transaction.router, prefix="/api/transactions", tags=["transactions"])
api_router.include_router(category.router, prefix="/api/categories", tags=["categories"])
