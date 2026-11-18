
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.exceptions import register_exception_handlers
from app.core.database import Base, engine
from app.api.v1.router import api_router
from app import models


# Configure application logging
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""

    if settings.AUTO_CREATE_TABLES:
        Base.metadata.create_all(bind=engine)

    logger.info(
        "%s is starting...",
        settings.APP_NAME,
    )

    yield

    logger.info(
        "%s is shutting down...",
        settings.APP_NAME,
    )


# Initialize FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "BrandGuard AI - An intelligent brand governance "
        "and content compliance review platform."
    ),
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)


# Configure CORS
frontend_origins = [
    origin.strip()
    for origin in settings.FRONTEND_ORIGIN.split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=["Authorization", "Content-Type"],
)


# Register global exception handlers
register_exception_handlers(app)


# Register API routes
app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)


# Root endpoint
@app.get("/", tags=["System"])
async def root():
    return {
        "success": True,
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "message": "BrandGuard AI API is running.",
    }


# Health check
@app.get("/health", tags=["System"])
async def health_check():
    return {
        "success": True,
        "status": "healthy",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# API information
@app.get("/api-info", tags=["System"])
async def api_info():
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "api_prefix": settings.API_V1_PREFIX,
        "documentation": (
            "/docs" if settings.DEBUG else "disabled"
        ),
    }
