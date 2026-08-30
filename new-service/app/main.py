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
    title="Accounts Manager Service",
    version="2.0.0",
    description="Extracts transactions from PDF documents and manages document types.",
)

# Include API router
app.include_router(api_router)
