"""
Health check endpoints.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def health() -> dict:
    """
    Basic health check.
    """
    return {"status": "ok"}
