"""
FastAPI Application Main Module

Entry point for the Swiggy AI Agent backend.
"""

from contextlib import asynccontextmanager
import logging
import sys
import time
import traceback
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.routes.cart import router as cart_router
from app.routes.chat import ChatRequest, chat as chat_handler, router as chat_router
from app.routes.context import router as context_router
from app.routes.order import router as order_router
from app.routes.plan import router as planner_router
from app.routes.profile import router
from app.routes.telemetry import router as telemetry_router

STARTUP_TIME = time.time()

# Setup logger for debug logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("swiggy_agent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION} [{settings.RELEASE}]")
    logger.info(f"Environment: {settings.ENVIRONMENT} | Architecture: {settings.ARCHITECTURE_VERSION}")
    yield
    logger.info(f"Shutting down {settings.APP_NAME} gracefully...")


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered food ordering assistant backend",
    version=settings.VERSION,
    lifespan=lifespan,
)

# CORS: allow frontend origins and preflight handling
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_REGEX,
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
    return {"message": "Swiggy AI Agent API", "status": "running", "release": settings.RELEASE}


@app.get("/health")
async def health_check() -> dict:
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "release": settings.RELEASE,
        "environment": settings.ENVIRONMENT,
        "uptime_seconds": round(time.time() - STARTUP_TIME, 2),
        "knowledge_base_loaded": True,
        "catalog_loaded": True,
    }


@app.get("/version")
async def version_info() -> dict:
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "release": settings.RELEASE,
        "architecture": settings.ARCHITECTURE_VERSION,
        "ranking": settings.RANKING_VERSION,
        "semantic": settings.SEMANTIC_VERSION,
        "build": settings.BUILD_DATE,
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    }