"""
API Router - Central routing configuration
"""

from fastapi import APIRouter

from api.routes import health, transaction, category, document_type

from api.routes.documents import (
    pdf_processing,
    get_all_documents,
    load_transactions_from_document,
)

from api.routes.transactions import (
    get_all_transactions,
    import_transactions_from_csv,
    export_transactions,
)

api_router = APIRouter()

# Include all route modules
api_router.include_router(pdf_processing.router)
api_router.include_router(get_all_documents.router)
api_router.include_router(load_transactions_from_document.router)
api_router.include_router(
    get_all_transactions.router, prefix="/api/transactions", tags=["transactions"]
)
api_router.include_router(
    import_transactions_from_csv.router,
    prefix="/api/transactions",
    tags=["transactions"],
)
api_router.include_router(
    export_transactions.router,
    prefix="/api/transactions",
    tags=["transactions"],
)


api_router.include_router(health.router)
api_router.include_router(
    transaction.router, prefix="/api/transactions", tags=["transactions"]
)
api_router.include_router(
    category.router, prefix="/api/categories", tags=["categories"]
)
api_router.include_router(
    document_type.router, prefix="/api/document-types", tags=["document-types"]
)
