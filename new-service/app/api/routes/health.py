from fastapi import APIRouter

# Create router for main routes
router = APIRouter(prefix="/api", tags=["health check"])


@router.get("")
async def root():
    """Root endpoint for health check and service information."""
    return {
        "message": "BCP PDF Extractor Service",
    }
