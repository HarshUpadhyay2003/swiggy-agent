"""
FastAPI Application Main Module

Entry point for the Swiggy AI Agent backend.
"""

from fastapi import FastAPI

from app.routes.context import router as context_router
from app.routes.order import router as order_router
from app.routes.plan import router as planner_router
from app.routes.profile import router


app = FastAPI(
    title="Swiggy AI Copilot",
    description="AI-powered food ordering assistant backend",
    version="1.0.0"
)


app.include_router(router, prefix="/profile", tags=["profile"])
app.include_router(planner_router, prefix="/planner", tags=["planner"])
app.include_router(order_router, prefix="/order", tags=["order"])
app.include_router(context_router, prefix="/context", tags=["context"])


@app.get("/")
async def root() -> dict[str, str]:
    """
    Root endpoint for health check.

    Returns:
        Welcome message
    """
    return {"message": "Swiggy AI Agent API", "status": "running"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return {"status": "healthy"}