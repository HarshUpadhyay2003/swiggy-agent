"""
FastAPI Application Main Module

Entry point for the Swiggy AI Agent backend.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

from app.routes.chat import router as chat_router, chat as chat_handler, ChatRequest
from app.routes.context import router as context_router
from app.routes.order import router as order_router
from app.routes.plan import router as planner_router
from app.routes.profile import router
from app.routes.cart import router as cart_router
from app.routes.telemetry import router as telemetry_router


app = FastAPI(
    title="Swiggy AI Copilot",
    description="AI-powered food ordering assistant backend",
    version="1.0.0"
)

# Setup logger for lightweight request/debug logging
logger = logging.getLogger("swiggy_agent")
logger.setLevel(logging.INFO)

# Load allowed origins from environment variable
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

# CORS: allow frontend origins and preflight handling
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Safe, minimal logging: method and path only
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    if request.method == "OPTIONS":
        logger.info(f"CORS preflight received for {request.url.path}")
    response = await call_next(request)
    return response


app.include_router(router, prefix="/profile", tags=["profile"])
app.include_router(planner_router, prefix="/planner", tags=["planner"])
app.include_router(order_router, prefix="/order", tags=["order"])
app.include_router(context_router, prefix="/context", tags=["context"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(cart_router, prefix="/cart", tags=["cart"])
app.include_router(telemetry_router, prefix="/telemetry", tags=["telemetry"])


# Alias handlers for requests made to /chat (no trailing slash)
# This avoids 307 redirects and ensures preflight OPTIONS requests succeed.
@app.options("/chat")
async def chat_options(request: Request):
    logger.info("OPTIONS /chat - CORS preflight handled")
    return JSONResponse(status_code=200, content={"detail": "CORS preflight OK"})


@app.post("/chat")
async def chat_no_slash(request: Request):
    """Accept POSTs to /chat (no trailing slash) and forward to existing router handler."""
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"status": "error", "detail": "Invalid JSON payload"})

    try:
        chat_request = ChatRequest(**payload)
    except Exception as exc:
        logger.info("Invalid chat payload: %s", exc)
        return JSONResponse(status_code=422, content={"status": "error", "detail": str(exc)})

    # Delegate to existing chat handler (keeps all orchestrator logic intact)
    return await chat_handler(chat_request)


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