---
name: rate-limiting
description: |
  SlowAPI, Token Bucket, 분산 Rate Limiting을 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Rate Limiting Skill

SlowAPI, Token Bucket, 분산 Rate Limiting을 구현합니다.

## Triggers

- "속도 제한", "rate limit", "throttling", "api 제한"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |

---

## Output

### SlowAPI 설정

```python
# app/api/rate_limiter.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from fastapi import FastAPI, Request

from app.core.config import settings


def get_user_identifier(request: Request) -> str:
    """Get rate limit identifier (user ID or IP)."""
    # Try to get user ID from JWT token
    if hasattr(request.state, "user_id"):
        return f"user:{request.state.user_id}"

    # Fall back to IP address
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return f"ip:{forwarded.split(',')[0].strip()}"

    return f"ip:{get_remote_address(request)}"


# Create limiter with Redis backend for distributed rate limiting
limiter = Limiter(
    key_func=get_user_identifier,
    default_limits=["100/minute"],  # Default: 100 requests per minute
    storage_uri=str(settings.REDIS_URL),
    strategy="fixed-window",  # or "moving-window"
)


def setup_rate_limiter(app: FastAPI) -> None:
    """Setup rate limiter for the application."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
```

### Route별 Rate Limit

```python
# app/api/v1/routes/auth.py
from fastapi import APIRouter, Request
from slowapi import Limiter

from app.api.rate_limiter import limiter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
@limiter.limit("5/minute")  # Strict limit for login
async def login(request: Request, credentials: LoginRequest):
    """Login endpoint with strict rate limiting."""
    return await auth_service.login(credentials)


@router.post("/register")
@limiter.limit("3/hour")  # Very strict for registration
async def register(request: Request, user_in: UserCreate):
    """Register endpoint with very strict rate limiting."""
    return await auth_service.register(user_in)


@router.post("/forgot-password")
@limiter.limit("3/hour")
async def forgot_password(request: Request, email: str):
    """Password reset with strict limiting."""
    return await auth_service.send_password_reset(email)
```

### Custom Rate Limiter (Redis)

```python
# app/infrastructure/cache/rate_limiter.py
import time
from typing import Tuple

import redis.asyncio as redis
import structlog

from app.core.config import settings
from app.core.exceptions import RateLimitError
from app.infrastructure.cache.redis import get_redis_client

logger = structlog.get_logger()


class TokenBucketRateLimiter:
    """Token bucket rate limiter with Redis backend."""

    def __init__(
        self,
        key_prefix: str = "rate_limit",
        max_tokens: int = 100,
        refill_rate: float = 10.0,  # tokens per second
    ) -> None:
        self.key_prefix = key_prefix
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate

    def _get_keys(self, identifier: str) -> Tuple[str, str]:
        """Get Redis keys for tokens and last refill time."""
        base = f"{self.key_prefix}:{identifier}"
        return f"{base}:tokens", f"{base}:last_refill"

    async def is_allowed(self, identifier: str, tokens_needed: int = 1) -> bool:
        """Check if request is allowed and consume tokens."""
        client = await get_redis_client()
        tokens_key, refill_key = self._get_keys(identifier)

        # Get current state
        pipe = client.pipeline()
        pipe.get(tokens_key)
        pipe.get(refill_key)
        current_tokens, last_refill = await pipe.execute()

        now = time.time()

        if current_tokens is None:
            # Initialize bucket
            current_tokens = self.max_tokens
            last_refill = now
        else:
            current_tokens = float(current_tokens)
            last_refill = float(last_refill)

            # Calculate tokens to add based on time elapsed
            time_elapsed = now - last_refill
            tokens_to_add = time_elapsed * self.refill_rate
            current_tokens = min(self.max_tokens, current_tokens + tokens_to_add)

        # Check if enough tokens
        if current_tokens < tokens_needed:
            await logger.awarning(
                "Rate limit exceeded",
                identifier=identifier,
                tokens_available=current_tokens,
                tokens_needed=tokens_needed,
            )
            return False

        # Consume tokens
        new_tokens = current_tokens - tokens_needed

        # Update Redis
        pipe = client.pipeline()
        pipe.set(tokens_key, new_tokens, ex=3600)  # Expire in 1 hour
        pipe.set(refill_key, now, ex=3600)
        await pipe.execute()

        return True

    async def get_remaining(self, identifier: str) -> int:
        """Get remaining tokens for identifier."""
        client = await get_redis_client()
        tokens_key, _ = self._get_keys(identifier)
        tokens = await client.get(tokens_key)
        return int(float(tokens)) if tokens else self.max_tokens


class SlidingWindowRateLimiter:
    """Sliding window rate limiter with Redis backend."""

    def __init__(
        self,
        key_prefix: str = "sliding_rate_limit",
        max_requests: int = 100,
        window_seconds: int = 60,
    ) -> None:
        self.key_prefix = key_prefix
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def _get_key(self, identifier: str) -> str:
        return f"{self.key_prefix}:{identifier}"

    async def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed using sliding window."""
        client = await get_redis_client()
        key = self._get_key(identifier)
        now = time.time()
        window_start = now - self.window_seconds

        pipe = client.pipeline()
        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)
        # Count current entries
        pipe.zcard(key)
        # Add new entry
        pipe.zadd(key, {str(now): now})
        # Set expiration
        pipe.expire(key, self.window_seconds)

        results = await pipe.execute()
        current_count = results[1]

        if current_count >= self.max_requests:
            await logger.awarning(
                "Rate limit exceeded (sliding window)",
                identifier=identifier,
                current_count=current_count,
                max_requests=self.max_requests,
            )
            return False

        return True

    async def get_remaining(self, identifier: str) -> int:
        """Get remaining requests in current window."""
        client = await get_redis_client()
        key = self._get_key(identifier)
        now = time.time()
        window_start = now - self.window_seconds

        # Remove old and count
        pipe = client.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        results = await pipe.execute()

        current_count = results[1]
        return max(0, self.max_requests - current_count)
```

### Rate Limit Dependency

```python
# app/api/v1/dependencies/rate_limit.py
from fastapi import Depends, Request, HTTPException, status

from app.infrastructure.cache.rate_limiter import (
    TokenBucketRateLimiter,
    SlidingWindowRateLimiter,
)


# Create limiters with different configurations
auth_limiter = TokenBucketRateLimiter(
    key_prefix="auth",
    max_tokens=5,
    refill_rate=0.1,  # 1 token per 10 seconds
)

api_limiter = SlidingWindowRateLimiter(
    key_prefix="api",
    max_requests=100,
    window_seconds=60,
)


async def check_auth_rate_limit(request: Request) -> None:
    """Dependency to check auth rate limit."""
    identifier = request.client.host if request.client else "unknown"

    if not await auth_limiter.is_allowed(identifier):
        remaining = await auth_limiter.get_remaining(identifier)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many authentication attempts",
            headers={
                "X-RateLimit-Remaining": str(remaining),
                "Retry-After": "60",
            },
        )


async def check_api_rate_limit(request: Request) -> None:
    """Dependency to check API rate limit."""
    # Use user ID if authenticated, otherwise IP
    if hasattr(request.state, "user_id"):
        identifier = f"user:{request.state.user_id}"
    else:
        identifier = f"ip:{request.client.host if request.client else 'unknown'}"

    if not await api_limiter.is_allowed(identifier):
        remaining = await api_limiter.get_remaining(identifier)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Limit": str(api_limiter.max_requests),
                "Retry-After": "60",
            },
        )
```

### 사용 예시

```python
# app/api/v1/routes/auth.py
from fastapi import APIRouter, Depends

from app.api.v1.dependencies.rate_limit import check_auth_rate_limit

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", dependencies=[Depends(check_auth_rate_limit)])
async def login(credentials: LoginRequest):
    """Login with rate limiting."""
    return await auth_service.login(credentials)


# Or apply to entire router
router = APIRouter(
    prefix="/api",
    dependencies=[Depends(check_api_rate_limit)],
)
```

### main.py에 등록

```python
# app/main.py
from app.api.rate_limiter import setup_rate_limiter


def create_app() -> FastAPI:
    app = FastAPI(...)

    # Setup rate limiter
    setup_rate_limiter(app)

    return app
```

## References

- `_references/API-PATTERN.md`
