from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.agent.orchestrator import run_orchestrator


router = APIRouter()


class PromptRequest(BaseModel):
    prompt: str


@router.post("/api/v1/orchestrate", tags=["Agent Operations"])
def orchestrate_workflow(request: PromptRequest):
    """
    The main ingestion point for the LangChain agent.
    Takes a natural language prompt and dynamically executes backend tools.
    """
    try:
        result = run_orchestrator(request.prompt)

        return {
            "status": "success",
            "agent_response": result,
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
            },
        )