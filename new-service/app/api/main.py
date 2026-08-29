"""
API Router - Central routing configuration
"""

from fastapi import APIRouter

from api.routes import (
    health,
    transaction,
    category,
    document_format,
    document,
    account,
    users,
)

api_router = APIRouter()

# Include all route modules
api_router.include_router(health.router)
api_router.include_router(transaction.router)
api_router.include_router(document.router)
api_router.include_router(category.router)
api_router.include_router(document_format.router)
api_router.include_router(account.router)
api_router.include_router(users.router)
