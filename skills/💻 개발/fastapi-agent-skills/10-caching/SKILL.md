---
name: caching
description: |
  Redis 캐싱 및 fastapi-cache2 패턴을 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Caching Skill

Redis 캐싱 및 fastapi-cache2 패턴을 구현합니다.

## Triggers

- "캐싱", "cache", "redis", "캐시"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |

---

## Output

### Redis Client

```python
# app/infrastructure/cache/redis.py
from typing import Any

import redis.asyncio as redis
import structlog
from redis.asyncio import ConnectionPool

from app.core.config import settings

logger = structlog.get_logger()

# Global connection pool
_pool: ConnectionPool | None = None


async def get_redis_pool() -> ConnectionPool:
    """Get or create Redis connection pool."""
    global _pool
    if _pool is None:
        _pool = redis.ConnectionPool.from_url(
            str(settings.REDIS_URL),
            max_connections=20,
            decode_responses=True,
        )
    return _pool


async def get_redis_client() -> redis.Redis:
    """Get Redis client from pool."""
    pool = await get_redis_pool()
    return redis.Redis(connection_pool=pool)


async def close_redis_pool() -> None:
    """Close Redis connection pool."""
    global _pool
    if _pool is not None:
        await _pool.disconnect()
        _pool = None


class CacheService:
    """Redis cache service."""

    def __init__(self, prefix: str = "cache") -> None:
        self.prefix = prefix

    def _make_key(self, key: str) -> str:
        """Create prefixed cache key."""
        return f"{self.prefix}:{key}"

    async def get(self, key: str) -> str | None:
        """Get value from cache."""
        client = await get_redis_client()
        try:
            return await client.get(self._make_key(key))
        except redis.RedisError as e:
            await logger.aerror("Cache get error", key=key, error=str(e))
            return None

    async def set(
        self,
        key: str,
        value: str,
        ttl: int | None = None,
    ) -> bool:
        """Set value in cache."""
        client = await get_redis_client()
        try:
            await client.set(
                self._make_key(key),
                value,
                ex=ttl or settings.REDIS_TTL,
            )
            return True
        except redis.RedisError as e:
            await logger.aerror("Cache set error", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        client = await get_redis_client()
        try:
            await client.delete(self._make_key(key))
            return True
        except redis.RedisError as e:
            await logger.aerror("Cache delete error", key=key, error=str(e))
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        client = await get_redis_client()
        try:
            keys = []
            async for key in client.scan_iter(self._make_key(pattern)):
                keys.append(key)
            if keys:
                return await client.delete(*keys)
            return 0
        except redis.RedisError as e:
            await logger.aerror("Cache delete pattern error", pattern=pattern, error=str(e))
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        client = await get_redis_client()
        try:
            return await client.exists(self._make_key(key)) > 0
        except redis.RedisError as e:
            await logger.aerror("Cache exists error", key=key, error=str(e))
            return False

    async def incr(self, key: str, amount: int = 1) -> int | None:
        """Increment value."""
        client = await get_redis_client()
        try:
            return await client.incrby(self._make_key(key), amount)
        except redis.RedisError as e:
            await logger.aerror("Cache incr error", key=key, error=str(e))
            return None

    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration on key."""
        client = await get_redis_client()
        try:
            return await client.expire(self._make_key(key), ttl)
        except redis.RedisError as e:
            await logger.aerror("Cache expire error", key=key, error=str(e))
            return False
```

### fastapi-cache2 설정

```python
# app/infrastructure/cache/fastapi_cache.py
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from app.infrastructure.cache.redis import get_redis_client


async def setup_cache(app: FastAPI) -> None:
    """Setup FastAPI cache with Redis backend."""
    redis_client = await get_redis_client()
    FastAPICache.init(
        RedisBackend(redis_client),
        prefix="fastapi-cache",
    )


def cache_response(expire: int = 60):
    """Cache decorator for route responses.

    Args:
        expire: Cache expiration time in seconds.
    """
    return cache(expire=expire)
```

### 캐시 사용 예시 (Routes)

```python
# app/api/v1/routes/products.py
from fastapi import APIRouter, Depends

from app.api.v1.dependencies import ActiveUser
from app.infrastructure.cache.fastapi_cache import cache_response
from app.schemas.product import ProductResponse

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/{product_id}", response_model=ProductResponse)
@cache_response(expire=300)  # Cache for 5 minutes
async def get_product(product_id: int):
    """Get product by ID (cached)."""
    # This response will be cached
    return await product_service.get_by_id(product_id)


@router.get("", response_model=list[ProductResponse])
@cache_response(expire=60)  # Cache for 1 minute
async def list_products(category: str | None = None):
    """List products (cached)."""
    return await product_service.list(category=category)
```

### 캐시 무효화

```python
# app/application/services/product.py
import json
from app.infrastructure.cache.redis import CacheService


class ProductService:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository
        self._cache = CacheService(prefix="product")

    async def get_by_id(self, product_id: int) -> ProductEntity | None:
        """Get product with cache."""
        # Try cache first
        cached = await self._cache.get(f"id:{product_id}")
        if cached:
            return ProductEntity.model_validate_json(cached)

        # Fetch from DB
        product = await self._repository.get_by_id(product_id)
        if product:
            # Store in cache
            await self._cache.set(
                f"id:{product_id}",
                product.model_dump_json(),
                ttl=300,
            )

        return product

    async def update(self, product_id: int, data: ProductUpdate) -> ProductEntity | None:
        """Update product and invalidate cache."""
        product = await self._repository.update(product_id, data)
        if product:
            # Invalidate specific cache
            await self._cache.delete(f"id:{product_id}")
            # Invalidate list cache
            await self._cache.delete_pattern("list:*")
        return product

    async def delete(self, product_id: int) -> bool:
        """Delete product and invalidate cache."""
        result = await self._repository.delete(product_id)
        if result:
            await self._cache.delete(f"id:{product_id}")
            await self._cache.delete_pattern("list:*")
        return result
```

### Cache Key Builder

```python
# app/infrastructure/cache/key_builder.py
from typing import Any
import hashlib
import json


def build_cache_key(
    prefix: str,
    *args: Any,
    **kwargs: Any,
) -> str:
    """Build a cache key from arguments.

    Args:
        prefix: Cache key prefix.
        *args: Positional arguments to include in key.
        **kwargs: Keyword arguments to include in key.

    Returns:
        Cache key string.
    """
    parts = [prefix]

    # Add positional args
    for arg in args:
        parts.append(str(arg))

    # Add sorted kwargs
    if kwargs:
        sorted_kwargs = sorted(kwargs.items())
        kwargs_str = json.dumps(sorted_kwargs, sort_keys=True)
        # Hash long kwargs
        if len(kwargs_str) > 50:
            kwargs_hash = hashlib.md5(kwargs_str.encode()).hexdigest()[:8]
            parts.append(kwargs_hash)
        else:
            parts.append(kwargs_str)

    return ":".join(parts)


# Usage
key = build_cache_key("user", user_id, filters={"status": "active"})
# Result: "user:123:{"filters": {"status": "active"}}"
```

### Lifespan에 등록

```python
# app/main.py
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.infrastructure.cache.redis import close_redis_pool
from app.infrastructure.cache.fastapi_cache import setup_cache


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan events."""
    # Startup
    await setup_cache(app)
    yield
    # Shutdown
    await close_redis_pool()
```

## References

- `_references/API-PATTERN.md`
