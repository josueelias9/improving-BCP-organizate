import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting BCP PDF Extractor Service...")
    uvicorn.run("app:app", host="127.0.0.1", port=8001, reload=True)