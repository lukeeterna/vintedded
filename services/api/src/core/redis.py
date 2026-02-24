"""
Redis connection management for caching and sessions.
"""
import redis.asyncio as redis
from typing import Optional

from src.config import settings

_redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Get Redis client instance"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def close_redis() -> None:
    """Close Redis connection"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


async def check_redis_connection() -> bool:
    """Check if Redis connection is healthy"""
    try:
        client = await get_redis()
        await client.ping()
        return True
    except Exception:
        return False
