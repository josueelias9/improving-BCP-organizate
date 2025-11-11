from fastapi import FastAPI
from api.routes import health, pdf_processing, pdf_upload, output_files, database
import logging
import os
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
    description="Servicio para extraer transacciones de PDFs del BCP usando Clean Architecture con persistencia en PostgreSQL"
)

# Incluir las rutas desde los diferentes módulos
app.include_router(health.router)
app.include_router(pdf_processing.router)
app.include_router(pdf_upload.router)
app.include_router(output_files.router)
app.include_router(database.router)