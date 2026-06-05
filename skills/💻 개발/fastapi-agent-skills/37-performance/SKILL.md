---
name: performance
description: |
  API 성능 최적화, 프로파일링, 캐싱 전략을 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Performance Skill

Extends: `../../_shared/performance/SKILL.md` (공통 성능 최적화 원칙 참조)

API 성능 최적화, 프로파일링, 캐싱 전략을 구현합니다.

## Triggers

- "성능 최적화", "performance", "프로파일링", "profiling", "속도 개선"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |

---

## Output

### 1. Async Optimization

```python
# app/core/async_utils.py
import asyncio
from typing import Awaitable, Callable, TypeVar
from functools import wraps

T = TypeVar("T")


async def gather_with_concurrency(
    limit: int,
    *tasks: Awaitable[T],
) -> list[T]:
    """Execute coroutines with concurrency limit.

    Prevents overwhelming external services or database.
    """
    semaphore = asyncio.Semaphore(limit)

    async def limited_task(task: Awaitable[T]) -> T:
        async with semaphore:
            return await task

    return await asyncio.gather(*[limited_task(t) for t in tasks])


async def run_in_executor(
    func: Callable[..., T],
    *args,
    **kwargs,
) -> T:
    """Run blocking function in thread pool executor."""
    import functools

    loop = asyncio.get_event_loop()
    partial = functools.partial(func, *args, **kwargs)
    return await loop.run_in_executor(None, partial)


def async_timed(func: Callable) -> Callable:
    """Decorator to measure async function execution time."""
    import time
    import structlog

    logger = structlog.get_logger()

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return await func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start
            await logger.ainfo(
                "Async function completed",
                function=func.__name__,
                elapsed_ms=round(elapsed * 1000, 2),
            )

    return wrapper
```

### 2. Database Query Optimization

```python
# app/infrastructure/repositories/optimized.py
from typing import Sequence, TypeVar

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

T = TypeVar("T")


class OptimizedRepository:
    """Repository with optimized query patterns."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_with_relationships(
        self,
        model,
        id: int,
        *relationships: str,
    ):
        """Get entity with eager-loaded relationships.

        Prevents N+1 queries by loading relationships in single query.
        """
        stmt = select(model).where(model.id == id)

        for rel in relationships:
            stmt = stmt.options(selectinload(getattr(model, rel)))

        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_many_optimized(
        self,
        model,
        *,
        offset: int = 0,
        limit: int = 20,
        relationships: list[str] | None = None,
        order_by: str | None = None,
    ) -> Sequence:
        """Get multiple entities with optimizations."""
        stmt = select(model)

        # Eager load relationships
        if relationships:
            for rel in relationships:
                stmt = stmt.options(selectinload(getattr(model, rel)))

        # Apply ordering
        if order_by:
            if order_by.startswith("-"):
                stmt = stmt.order_by(getattr(model, order_by[1:]).desc())
            else:
                stmt = stmt.order_by(getattr(model, order_by))

        # Apply pagination
        stmt = stmt.offset(offset).limit(limit)

        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def count_efficient(self, model, **filters) -> int:
        """Efficient count query without loading entities."""
        stmt = select(func.count()).select_from(model)

        for key, value in filters.items():
            stmt = stmt.where(getattr(model, key) == value)

        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def exists(self, model, **filters) -> bool:
        """Check existence without loading entity."""
        from sqlalchemy import exists as sql_exists

        stmt = select(sql_exists().where(
            *[getattr(model, k) == v for k, v in filters.items()]
        ))
        result = await self._session.execute(stmt)
        return result.scalar() or False

    async def bulk_insert(self, model, items: list[dict]) -> int:
        """Efficient bulk insert."""
        from sqlalchemy import insert

        stmt = insert(model).values(items)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount

    async def bulk_update(
        self,
        model,
        items: list[dict],
        key_field: str = "id",
    ) -> int:
        """Efficient bulk update using CASE WHEN."""
        from sqlalchemy import case, update

        if not items:
            return 0

        # Group updates by field
        ids = [item[key_field] for item in items]
        update_fields = {}

        for field in items[0].keys():
            if field == key_field:
                continue
            update_fields[field] = case(
                {item[key_field]: item[field] for item in items if field in item},
                value=getattr(model, key_field),
            )

        stmt = (
            update(model)
            .where(getattr(model, key_field).in_(ids))
            .values(**update_fields)
        )

        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount
```

### 3. Response Caching

```python
# app/core/cache.py
import hashlib
import json
from functools import wraps
from typing import Callable, TypeVar

from fastapi import Request

import redis.asyncio as redis

T = TypeVar("T")


class CacheManager:
    """Cache manager with Redis backend."""

    def __init__(self, redis_url: str) -> None:
        self._redis = redis.from_url(redis_url)

    async def get(self, key: str) -> str | None:
        """Get cached value."""
        return await self._redis.get(key)

    async def set(
        self,
        key: str,
        value: str,
        ttl: int = 300,
    ) -> None:
        """Set cached value with TTL."""
        await self._redis.setex(key, ttl, value)

    async def delete(self, key: str) -> None:
        """Delete cached value."""
        await self._redis.delete(key)

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        keys = []
        async for key in self._redis.scan_iter(pattern):
            keys.append(key)

        if keys:
            return await self._redis.delete(*keys)
        return 0

    async def invalidate_prefix(self, prefix: str) -> int:
        """Invalidate all cache entries with prefix."""
        return await self.delete_pattern(f"{prefix}:*")

    # === Tag-based Cache Invalidation ===

    async def set_with_tags(
        self,
        key: str,
        value: str,
        ttl: int = 300,
        tags: list[str] | None = None,
    ) -> None:
        """Set cached value with associated tags for group invalidation.

        Tags allow invalidating related cache entries together.
        Example: tag "user:123" invalidates all cache for user 123.
        """
        # Set the actual value
        await self._redis.setex(key, ttl, value)

        # Associate key with each tag
        if tags:
            pipe = self._redis.pipeline()
            for tag in tags:
                tag_key = f"cache:tag:{tag}"
                pipe.sadd(tag_key, key)
                pipe.expire(tag_key, ttl + 60)  # Tag outlives cache slightly
            await pipe.execute()

    async def invalidate_by_tag(self, tag: str) -> int:
        """Invalidate all cache entries with a specific tag.

        Usage:
            # Cache user data with tag
            await cache.set_with_tags(
                "user:123:profile", data, tags=["user:123"]
            )
            await cache.set_with_tags(
                "user:123:orders", orders, tags=["user:123", "orders"]
            )

            # Invalidate all user:123 cache when user is updated
            await cache.invalidate_by_tag("user:123")
        """
        tag_key = f"cache:tag:{tag}"
        keys = await self._redis.smembers(tag_key)

        if keys:
            deleted = await self._redis.delete(*keys, tag_key)
            return deleted
        return 0

    async def invalidate_by_tags(self, tags: list[str]) -> int:
        """Invalidate cache entries matching any of the given tags."""
        total_deleted = 0
        for tag in tags:
            total_deleted += await self.invalidate_by_tag(tag)
        return total_deleted


# === Event-based Cache Invalidation ===

class CacheInvalidator:
    """Event-based cache invalidation coordinator.

    Subscribes to domain events and invalidates related cache.
    """

    def __init__(self, cache: CacheManager) -> None:
        self._cache = cache
        self._handlers: dict[str, list[callable]] = {}

    def on(self, event_type: str):
        """Decorator to register cache invalidation handler."""
        def decorator(func):
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(func)
            return func
        return decorator

    async def handle(self, event_type: str, payload: dict) -> None:
        """Handle event and trigger cache invalidation."""
        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            await handler(self._cache, payload)


# Example usage with domain events
cache_invalidator = CacheInvalidator(cache=None)  # Initialize with actual cache


@cache_invalidator.on("user.updated")
async def invalidate_user_cache(cache: CacheManager, payload: dict):
    """Invalidate user cache when user is updated."""
    user_id = payload.get("user_id")
    await cache.invalidate_by_tag(f"user:{user_id}")


@cache_invalidator.on("order.created")
async def invalidate_order_cache(cache: CacheManager, payload: dict):
    """Invalidate order-related cache when order is created."""
    user_id = payload.get("user_id")
    await cache.invalidate_by_tags([
        f"user:{user_id}:orders",
        "orders:stats",
    ])


def cached(
    ttl: int = 300,
    key_prefix: str = "",
    key_builder: Callable[..., str] | None = None,
):
    """Decorator for caching endpoint responses.

    Args:
        ttl: Cache TTL in seconds
        key_prefix: Prefix for cache key
        key_builder: Custom function to build cache key
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get cache manager from app state
            request: Request = kwargs.get("request") or args[0]
            cache: CacheManager = request.app.state.cache

            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                key_parts = [key_prefix or func.__name__]
                key_parts.extend(str(v) for v in kwargs.values() if v is not None)
                cache_key = ":".join(key_parts)

            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value:
                return json.loads(cached_value)

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            if result is not None:
                await cache.set(cache_key, json.dumps(result), ttl)

            return result

        return wrapper

    return decorator
```

### 4. Request Profiling Middleware

```python
# app/api/middleware/profiling.py
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

import structlog

logger = structlog.get_logger()


class ProfilingMiddleware(BaseHTTPMiddleware):
    """Middleware for request profiling and performance monitoring."""

    def __init__(
        self,
        app,
        slow_request_threshold_ms: float = 500,
        enable_detailed_profiling: bool = False,
    ) -> None:
        super().__init__(app)
        self._slow_threshold = slow_request_threshold_ms
        self._detailed_profiling = enable_detailed_profiling

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        start_time = time.perf_counter()

        # Profile memory if detailed profiling enabled
        if self._detailed_profiling:
            import tracemalloc
            tracemalloc.start()

        try:
            response = await call_next(request)
        finally:
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            # Log performance metrics
            log_data = {
                "method": request.method,
                "path": request.url.path,
                "elapsed_ms": round(elapsed_ms, 2),
                "status_code": response.status_code if 'response' in dir() else 500,
            }

            # Add memory stats if profiling
            if self._detailed_profiling:
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                log_data["memory_current_mb"] = round(current / 1024 / 1024, 2)
                log_data["memory_peak_mb"] = round(peak / 1024 / 1024, 2)

            # Log slow requests as warnings
            if elapsed_ms > self._slow_threshold:
                await logger.awarning("Slow request detected", **log_data)
            else:
                await logger.ainfo("Request completed", **log_data)

            # Add timing header
            response.headers["X-Response-Time"] = f"{round(elapsed_ms, 2)}ms"

        return response
```

### 5. Connection Pooling

```python
# app/infrastructure/database/pool.py
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool

from app.core.config import settings


def create_optimized_engine():
    """Create database engine with optimized connection pooling."""
    return create_async_engine(
        settings.DATABASE_URL,
        # Pool settings
        poolclass=AsyncAdaptedQueuePool,
        pool_size=20,              # Base number of connections
        max_overflow=30,           # Additional connections when pool is full
        pool_timeout=30,           # Seconds to wait for available connection
        pool_recycle=1800,         # Recycle connections after 30 minutes
        pool_pre_ping=True,        # Verify connection health before use
        # Performance settings
        echo=settings.DEBUG,       # SQL logging (disable in production)
        echo_pool=False,           # Pool event logging
        # Connection settings
        connect_args={
            "command_timeout": 30,           # Query timeout in seconds
            "server_settings": {
                "application_name": settings.PROJECT_NAME,
                "statement_timeout": "30000",  # 30 seconds
            },
        },
    )
```

### 6. HTTP Client Optimization

```python
# app/infrastructure/http/client.py
import httpx
from typing import Any


class OptimizedHTTPClient:
    """HTTP client with connection pooling and retry logic."""

    def __init__(
        self,
        base_url: str = "",
        timeout: float = 30.0,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(
                max_connections=max_connections,
                max_keepalive_connections=max_keepalive_connections,
                keepalive_expiry=30.0,
            ),
            http2=True,  # Enable HTTP/2 for multiplexing
        )

    async def get(
        self,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
    ) -> httpx.Response:
        """GET request with retry."""
        return await self._request("GET", url, params=params, headers=headers)

    async def post(
        self,
        url: str,
        json: dict | None = None,
        headers: dict | None = None,
    ) -> httpx.Response:
        """POST request with retry."""
        return await self._request("POST", url, json=json, headers=headers)

    async def _request(
        self,
        method: str,
        url: str,
        max_retries: int = 3,
        **kwargs,
    ) -> httpx.Response:
        """Make request with exponential backoff retry."""
        import asyncio
        from tenacity import (
            retry,
            stop_after_attempt,
            wait_exponential,
            retry_if_exception_type,
        )

        @retry(
            stop=stop_after_attempt(max_retries),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((httpx.TransportError, httpx.TimeoutException)),
        )
        async def _do_request():
            response = await self._client.request(method, url, **kwargs)
            response.raise_for_status()
            return response

        return await _do_request()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
```

### 7. Response Streaming

```python
# app/api/v1/routes/streaming.py
from typing import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/stream", tags=["streaming"])


async def generate_large_response() -> AsyncIterator[str]:
    """Generate large response in chunks."""
    import asyncio

    for i in range(1000):
        # Simulate data generation
        yield f"data: {i}\n"
        # Allow other coroutines to run
        if i % 100 == 0:
            await asyncio.sleep(0)


@router.get("/large-data")
async def stream_large_data():
    """Stream large dataset without loading all into memory."""
    return StreamingResponse(
        generate_large_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
```

### 8. Lazy Loading and Pagination

```python
# app/application/services/pagination.py
from dataclasses import dataclass
from typing import Generic, TypeVar, Sequence

T = TypeVar("T")


@dataclass
class CursorPage(Generic[T]):
    """Cursor-based pagination result."""

    items: Sequence[T]
    next_cursor: str | None
    has_more: bool


async def paginate_with_cursor(
    query,
    cursor: str | None,
    limit: int = 20,
    order_field: str = "id",
) -> CursorPage:
    """Efficient cursor-based pagination.

    More efficient than offset pagination for large datasets.
    """
    import base64
    from sqlalchemy import select

    # Decode cursor
    if cursor:
        try:
            cursor_value = base64.b64decode(cursor).decode()
            last_value = int(cursor_value)
            query = query.where(getattr(query.column_descriptions[0]["entity"], order_field) > last_value)
        except Exception:
            pass

    # Get one extra to check if there's more
    query = query.limit(limit + 1)

    result = await query.all()

    has_more = len(result) > limit
    items = result[:limit]

    # Generate next cursor
    next_cursor = None
    if has_more and items:
        last_item = items[-1]
        cursor_value = str(getattr(last_item, order_field))
        next_cursor = base64.b64encode(cursor_value.encode()).decode()

    return CursorPage(
        items=items,
        next_cursor=next_cursor,
        has_more=has_more,
    )
```

### 9. Background Task Queue

```python
# app/infrastructure/tasks/queue.py
from typing import Callable, Any
import asyncio

from arq import create_pool
from arq.connections import RedisSettings

from app.core.config import settings


class TaskQueue:
    """Background task queue using ARQ."""

    def __init__(self) -> None:
        self._pool = None

    async def connect(self) -> None:
        """Connect to Redis."""
        self._pool = await create_pool(
            RedisSettings.from_dsn(settings.REDIS_URL)
        )

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._pool:
            await self._pool.close()

    async def enqueue(
        self,
        task_name: str,
        *args,
        delay: int | None = None,
        **kwargs,
    ) -> str:
        """Enqueue a background task.

        Returns job ID.
        """
        if delay:
            job = await self._pool.enqueue_job(
                task_name,
                *args,
                _defer_by=delay,
                **kwargs,
            )
        else:
            job = await self._pool.enqueue_job(task_name, *args, **kwargs)

        return job.job_id


# Task definitions
async def send_email_task(ctx, to: str, subject: str, body: str):
    """Background task for sending email."""
    from app.infrastructure.email.smtp import SMTPEmailService
    from app.domain.services.email import EmailMessage

    service = SMTPEmailService()
    await service.send(EmailMessage(
        to=[to],
        subject=subject,
        body_html=body,
    ))


class WorkerSettings:
    """ARQ worker settings."""

    functions = [send_email_task]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    max_jobs = 10
    job_timeout = 300
```

## Performance Best Practices

| Practice | Description |
|----------|-------------|
| Connection Pooling | Reuse database/HTTP connections |
| Eager Loading | Prevent N+1 queries with selectinload |
| Response Caching | Cache expensive computations |
| Async I/O | Never block the event loop |
| Pagination | Use cursor-based for large datasets |
| Background Tasks | Offload heavy work to queue |
| Profiling | Monitor and log slow requests |
| Streaming | Stream large responses |

## Cache Invalidation Strategies

| Strategy | Use Case | Pros | Cons |
|----------|----------|------|------|
| **TTL-based** | Read-heavy, eventual consistency OK | Simple, automatic | Stale data possible |
| **Tag-based** | Related data groups | Precise invalidation | Additional Redis ops |
| **Event-based** | Real-time consistency | Immediate invalidation | Complex setup |
| **Write-through** | Critical data | Always consistent | Slower writes |
| **Pattern delete** | Bulk invalidation | Simple API | SCAN can be slow |

### Cache Invalidation Decision Tree

```
Data changed?
├── Single entity → invalidate_by_tag("entity:{id}")
├── Related entities → invalidate_by_tags(["entity:{id}", "related:*"])
├── All entities → invalidate_prefix("entities")
└── Complex dependency → Event-based invalidation
```

### Common Invalidation Patterns

```python
# 1. Entity update → invalidate entity cache
async def update_user(user_id: int, data: UserUpdate):
    user = await repo.update(user_id, data)
    await cache.invalidate_by_tag(f"user:{user_id}")
    return user

# 2. List modification → invalidate list + entity
async def delete_item(item_id: int):
    item = await repo.delete(item_id)
    await cache.invalidate_by_tags([
        f"item:{item_id}",
        "items:list",
        f"category:{item.category_id}:items",
    ])

# 3. Aggregate invalidation → invalidate stats
async def create_order(order: OrderCreate):
    result = await repo.create(order)
    await cache.invalidate_by_tags([
        f"user:{order.user_id}:orders",
        "orders:stats",
        "dashboard:metrics",
    ])
```

## Performance Metrics to Monitor

| Metric | Target | Tool |
|--------|--------|------|
| P99 Latency | < 500ms | Prometheus |
| Throughput | > 1000 RPS | Load testing |
| Error Rate | < 0.1% | Sentry |
| Memory Usage | Stable | Grafana |
| DB Query Time | < 100ms | Slow query log |
| Cache Hit Rate | > 90% | Redis stats |

## References

- `_references/ARCHITECTURE-PATTERN.md`
