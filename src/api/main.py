"""
Main FastAPI Application for the AI-Powered Sales Intelligence Platform.
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from src.api.config import settings
from src.api.v1.api_router import api_router
from src.security.prompt_guard import PromptSecurityError
from src.security.sql_guard import SQLSecurityError

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("sales_intelligence_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown event lifecycle."""
    logger.info("Starting up %s v%s...", settings.PROJECT_NAME, settings.VERSION)
    yield
    logger.info("Shutting down %s...", settings.PROJECT_NAME)


def create_application() -> FastAPI:
    """Factory function creating configured FastAPI instance."""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=(
            "Enterprise-grade, end-to-end **AI-Powered Sales Intelligence Platform API** "
            "integrating Star-Schema Warehousing, Business Analytics Marts, Production ML Pipelines, "
            "and LangGraph Agentic AI into a unified decision-support ecosystem."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # 1. CORS Middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. GZip Compression
    application.add_middleware(GZipMiddleware, minimum_size=1000)

    # 3. Execution Timing Middleware
    @application.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = (time.perf_counter() - start_time) * 1000.0
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        return response

    # 4. Global Exception Handlers
    @application.exception_handler(SQLSecurityError)
    async def sql_security_exception_handler(request: Request, exc: SQLSecurityError):
        logger.warning("SQL Security Violation on %s: %s", request.url, exc)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "error_type": "SQLSecurityError",
                "detail": f"Database Firewall Blocked Query: {exc!s}",
            },
        )

    @application.exception_handler(PromptSecurityError)
    async def prompt_security_exception_handler(request: Request, exc: PromptSecurityError):
        logger.warning("Prompt Injection Violation on %s: %s", request.url, exc)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "error_type": "PromptSecurityError",
                "detail": f"Adversarial Prompt Blocked: {exc!s}",
            },
        )

    # 5. Mount API Router
    application.include_router(api_router, prefix=settings.API_V1_STR)

    # 6. Root Landing Endpoint
    @application.get("/", tags=["Root"])
    def root():
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "online",
            "docs_url": "/docs",
            "api_v1": settings.API_V1_STR,
        }

    return application


app = create_application()
