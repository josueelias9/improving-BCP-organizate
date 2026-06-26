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
    description="Extracts transactions from PDF documents and manages document types.",
    openapi_tags=[
        {
            "name": "health check",
            "description": "Endpoints for health checks and service information",
        },
        {
            "name": "document management",
            "description": "Endpoints for managing documents and transactions",
        },
        {
            "name": "document types",
            "description": "Endpoints for managing document types",
        },
    ],
)

# Include API router
app.include_router(api_router)
