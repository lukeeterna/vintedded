"""
Vinted Optimizer API - Main Entry Point
FastAPI + Python 3.12 + Pydantic v2
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings
from src.api.v1 import api_router
from src.db.session import init_db, close_db
from src.core.logging import setup_logging

setup_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager"""
    logger.info("Starting Vinted Optimizer API", version=settings.VERSION)
    
    # Startup
    await init_db()
    logger.info("Database connection established")
    
    yield
    
    # Shutdown
    await close_db()
    logger.info("Application shutdown complete")


app = FastAPI(
    title="Vinted Optimizer API",
    description="Enterprise API for Vinted sales optimization",
    version=settings.VERSION,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/api/health", tags=["Health"])
async def health_check() -> dict:
    """
    Health check endpoint for monitoring and load balancers.
    Returns 200 if all services are healthy.
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENV,
    }


@app.get("/api/ready", tags=["Health"])
async def readiness_check() -> dict:
    """
    Readiness check endpoint.
    Verifies database and redis connections.
    """
    from src.db.session import check_db_connection
    from src.core.redis import check_redis_connection
    
    checks = {
        "database": await check_db_connection(),
        "redis": await check_redis_connection(),
    }
    
    all_healthy = all(checks.values())
    
    if not all_healthy:
        logger.error("Readiness check failed", checks=checks)
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "checks": checks,
            }
        )
    
    return {
        "status": "ready",
        "checks": checks,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
