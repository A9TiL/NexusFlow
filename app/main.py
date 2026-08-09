from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.agent.orchestrator import run_orchestrator


app = FastAPI(
    title = "NexusFlow Orchestrator",
    description = "Enterprise Multi-Agent Workflow API",
    version = "1.0.0"
)

class PromptRequest(BaseModel):
    prompt: str

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

@app.post("/api/v1/orchestrate", tags=["Agent Operations"])
def orchestrate_workflow(request: PromptRequest):
    """
    The main ingestion point for the LangChain agent.
    Takes a natural language prompt and dynamically executes backend tools.
    """
    try:
        result = run_orchestrator(request.prompt)
        return {"status": "success", "agent_response": result}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )