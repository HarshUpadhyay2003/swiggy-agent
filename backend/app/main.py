"""
FastAPI Application Main Module

Entry point for the Swiggy AI Agent backend.
"""

import logging
import os
import traceback
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routes.cart import router as cart_router
from app.routes.chat import ChatRequest, chat as chat_handler, router as chat_router
from app.routes.context import router as context_router
from app.routes.order import router as order_router
from app.routes.plan import router as planner_router
from app.routes.profile import router
from app.routes.telemetry import router as telemetry_router

app = FastAPI(
    title="Swiggy AI Copilot",
    description="AI-powered food ordering assistant backend",
    version="1.0.0",
)

# Setup logger for debug logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("swiggy_agent")
logger.setLevel(logging.INFO)

# CORS: allow frontend origins and preflight handling
origins = [
    "http://localhost:5173",
    "http://localhost:4173",
    "https://swiggy-agent.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex="https://.*\\.vercel\\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    if request.method == "OPTIONS":
        logger.info(f"CORS preflight received for {request.url.path}")
    response = await call_next(request)
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"[VALIDATION_ERROR] Path: {request.method} {request.url.path}")
    logger.error(f"[VALIDATION_ERROR] Errors: {exc.errors()}")
    logger.error(f"[VALIDATION_ERROR] Body: {exc.body}")
    return JSONResponse(
        status_code=400,
        content={
            "status": "error",
            "error": "PAYLOAD_VALIDATION_ERROR",
            "reason": "Request payload failed Pydantic schema validation",
            "details": exc.errors(),
            "field": exc.errors()[0]["loc"][-1] if exc.errors() else "body",
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"[UNHANDLED_EXCEPTION] Path: {request.method} {request.url.path} | Error: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": "SERVER_ERROR",
            "reason": str(exc),
            "details": traceback.format_exc(),
        },
    )


app.include_router(router, prefix="/profile", tags=["profile"])
app.include_router(planner_router, prefix="/planner", tags=["planner"])
app.include_router(order_router, prefix="/order", tags=["order"])
app.include_router(context_router, prefix="/context", tags=["context"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(cart_router, prefix="/cart", tags=["cart"])
app.include_router(telemetry_router, prefix="/telemetry", tags=["telemetry"])


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Swiggy AI Agent API", "status": "running"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}