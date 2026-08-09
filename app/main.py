from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title = "NexusFlow Orchestator",
    description = "Enterprise Multi-Agent Workflow API",
    version = "1.0.0"
)

@app.get("/",tags=["Health"])
async def root_health_check():
    """
    Root endpoint to verify the API is running.
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "online",
            "service": "NexusFlow API",
            "message": "System is operational and ready to orchestrate."
        }
    )
    
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Standard health check endpoint to be used by cloud load balancers 
    to confirm the pod is alive.
    """
    return {"status": "healthy"}