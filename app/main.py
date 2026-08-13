from fastapi import FastAPI
from app.api.routes.approvals import router as approval_router
from app.api.routes.health import router as health_router
from app.api.routes.orchestrator import router as orchestrator_router


app = FastAPI(
    title="NexusFlow Orchestrator",
    description="Enterprise Multi-Agent Workflow API",
    version="1.0.0",
)


app.include_router(health_router)
app.include_router(orchestrator_router)
app.include_router(approval_router)