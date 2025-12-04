from fastapi import FastAPI
from api.routes import health, document, transaction, category
import logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="BCP PDF Extractor", 
    version="2.0.0",
    description="Servicio para extraer transacciones de PDFs del BCP usando Clean Architecture"
)

# Incluir las rutas desde los diferentes módulos
app.include_router(health.router)
app.include_router(document.router)
app.include_router(transaction.router, prefix="/api/transactions", tags=["transactions"])
app.include_router(category.router, prefix="/api/categories", tags=["categories"])