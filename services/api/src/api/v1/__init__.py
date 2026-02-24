"""
API v1 Router
"""
from fastapi import APIRouter

from src.api.v1.endpoints import health

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["Health"])
