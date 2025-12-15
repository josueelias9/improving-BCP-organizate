from fastapi import FastAPI
from api.main import api_router
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
    description="Servicio para extraer transacciones de PDFs del BCP usando Clean Architecture",
)

# Include API router
app.include_router(api_router)
