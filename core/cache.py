import logging

import redis

from core.config import settings


logger = logging.getLogger(__name__)
_redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)


def get(key: str) -> str | None:
    """Get a cached value, returning None when Redis is unavailable."""
    try:
        return _redis_client.get(key)
    except redis.RedisError:
        logger.warning("Redis cache read failed", exc_info=True)
        return None


def set(key: str, value: str, ttl: int) -> None:
    """Store a cached value for ttl seconds; ignore Redis failures."""
    try:
        _redis_client.set(key, value, ex=ttl)
    except redis.RedisError:
        logger.warning("Redis cache write failed", exc_info=True)


def delete(key: str) -> None:
    """Delete a cached value; ignore Redis failures."""
    try:
        _redis_client.delete(key)
    except redis.RedisError:
        logger.warning("Redis cache delete failed", exc_info=True)
