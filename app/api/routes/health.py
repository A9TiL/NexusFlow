from fastapi import APIRouter
from fastapi.responses import JSONResponse


router = APIRouter()


@router.get("/", tags=["Health"])
async def root_health_check():
    """
    Root endpoint to verify the API is running.
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "online",
            "service": "NexusFlow API",
            "message": "System is operational and ready to orchestrate.",
        },
    )


@router.get("/health", tags=["Health"])
async def health_check():
    """
    Standard health check endpoint to be used by cloud load balancers
    to confirm the pod is alive.
    """
    return {"status": "healthy"}