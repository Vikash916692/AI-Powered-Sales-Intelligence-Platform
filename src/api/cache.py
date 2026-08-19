"""
High-Performance Redis Caching Layer with In-Memory Fallback.

Provides cache-aside decorator with TTL support, key prefixing,
and transparent fallback to memory when Redis is not running.
"""

import json
import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

import redis

from src.api.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages Redis connection and in-memory fallback cache."""

    def __init__(self, redis_url: str | None = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self._memory_cache: dict[str, tuple[Any, float]] = {}
        self._redis_client: redis.Redis | None = None
        self._is_redis_available = False

        self._connect_redis()

    def _connect_redis(self) -> None:
        """Attempt to connect to Redis server."""
        try:
            client = redis.from_url(
                self.redis_url,
                socket_connect_timeout=1,
                socket_timeout=1,
                decode_responses=True,
            )
            client.ping()
            self._redis_client = client
            self._is_redis_available = True
            logger.info("Connected to Redis cache at %s", self.redis_url)
        except Exception as e:
            self._is_redis_available = False
            self._redis_client = None
            logger.info("Redis not available (%s); using in-memory cache fallback.", e)

    def get(self, key: str) -> Any | None:
        """Retrieve item from cache if unexpired."""
        if self._is_redis_available and self._redis_client:
            try:
                val = self._redis_client.get(key)
                if val is not None:
                    return json.loads(val)
            except Exception:
                pass

        # Fallback in-memory
        if key in self._memory_cache:
            val, exp = self._memory_cache[key]
            if time.time() < exp:
                return val
            del self._memory_cache[key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Store item in cache with TTL."""
        if self._is_redis_available and self._redis_client:
            try:
                self._redis_client.setex(key, ttl_seconds, json.dumps(value, default=str))
                return
            except Exception:
                pass

        # In-memory storage
        self._memory_cache[key] = (value, time.time() + ttl_seconds)

    def delete(self, key: str) -> None:
        """Delete key from cache."""
        if self._is_redis_available and self._redis_client:
            try:
                self._redis_client.delete(key)
            except Exception:
                pass
        self._memory_cache.pop(key, None)

    def clear(self) -> None:
        """Clear all cached keys."""
        if self._is_redis_available and self._redis_client:
            try:
                self._redis_client.flushdb()
            except Exception:
                pass
        self._memory_cache.clear()

    @property
    def is_redis(self) -> bool:
        return self._is_redis_available


cache = CacheManager()


def cached(ttl_seconds: int = 300, key_prefix: str = "cache"):
    """
    Decorator for caching endpoint responses based on function arguments.
    """

    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Compute cache key from arguments
            clean_kwargs = {k: v for k, v in kwargs.items() if not hasattr(v, "__class__") or "Request" not in v.__class__.__name__}
            cache_key = f"{key_prefix}:{func.__name__}:{json.dumps(args, default=str)}:{json.dumps(clean_kwargs, sort_keys=True, default=str)}"

            cached_val = cache.get(cache_key)
            if cached_val is not None:
                return cached_val

            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl_seconds=ttl_seconds)
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            clean_kwargs = {k: v for k, v in kwargs.items() if not hasattr(v, "__class__") or "Request" not in v.__class__.__name__}
            cache_key = f"{key_prefix}:{func.__name__}:{json.dumps(args, default=str)}:{json.dumps(clean_kwargs, sort_keys=True, default=str)}"

            cached_val = cache.get(cache_key)
            if cached_val is not None:
                return cached_val

            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl_seconds=ttl_seconds)
            return result

        return async_wrapper if hasattr(func, "__await__") or func.__code__.co_flags & 0x80 else sync_wrapper

    return decorator
