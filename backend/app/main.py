"""
Main FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from app.core.config import settings
from app.db.session import init_db, close_db


# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
)

logger.add(
    settings.LOG_FILE_PATH,
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    level=settings.LOG_LEVEL,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Initialize database
    await init_db()

    yield

    # Shutdown
    logger.info("Shutting down application...")
    await close_db()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered Commerce Intelligence Platform API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


# Import and include routers
from app.api.v1 import auth, forecasts, products, subscriptions, admin

app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(forecasts.router, prefix=f"{settings.API_V1_PREFIX}/forecasts", tags=["Forecasts"])
app.include_router(products.router, prefix=f"{settings.API_V1_PREFIX}/products", tags=["Products"])
app.include_router(subscriptions.router, prefix=f"{settings.API_V1_PREFIX}/subscriptions", tags=["Subscriptions"])
app.include_router(admin.router, prefix=f"{settings.API_V1_PREFIX}/admin", tags=["Admin"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
