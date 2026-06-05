---
name: security-hardening
description: |
  HTTPS, 입력 검증, SQL Injection 방지 등 보안 강화를 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Security Hardening Skill

HTTPS, 입력 검증, SQL Injection 방지 등 보안 강화를 구현합니다.

## Triggers

- "보안 강화", "security hardening", "보안 설정", "취약점"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |

---

## Output

### Security Headers Middleware

```python
# app/api/middleware/security_headers.py
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses.

    Note: For production, use nonce-based CSP instead of 'unsafe-inline'.
    Generate nonce per request and pass to templates for script/style tags.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        response = await call_next(request)

        # Content Security Policy
        # For API-only backends, strict CSP is recommended
        # For full-stack apps with templates, use nonce-based approach
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "  # No unsafe-inline for XSS protection
            "style-src 'self'; "   # No unsafe-inline for CSS injection protection
            "img-src 'self' data: https:; "
            "font-src 'self' https:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # XSS Protection (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # HSTS (only in production with HTTPS)
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )

        return response
```

### Input Sanitization

```python
# app/core/sanitization.py
import html
import re
from typing import Any


def sanitize_html(value: str) -> str:
    """Escape HTML special characters."""
    return html.escape(value)


def sanitize_sql_like(value: str) -> str:
    """Escape SQL LIKE special characters."""
    return value.replace("%", r"\%").replace("_", r"\_")


def strip_null_bytes(value: str) -> str:
    """Remove null bytes from string."""
    return value.replace("\x00", "")


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal."""
    # Remove path components
    filename = filename.replace("\\", "/")
    filename = filename.split("/")[-1]

    # Remove dangerous characters
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", filename)

    # Prevent hidden files
    filename = filename.lstrip(".")

    return filename or "unnamed"


def sanitize_input(value: Any) -> Any:
    """Recursively sanitize input data."""
    if isinstance(value, str):
        value = strip_null_bytes(value)
        value = sanitize_html(value)
        return value
    elif isinstance(value, dict):
        return {k: sanitize_input(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [sanitize_input(item) for item in value]
    return value
```

### SQL Injection Prevention

```python
# app/infrastructure/repositories/base.py
from typing import Any, TypeVar

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

T = TypeVar("T")


class BaseRepository:
    """Base repository with safe query building."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def execute_safe_query(
        self,
        query: Select,
    ) -> list[Any]:
        """Execute a query built with SQLAlchemy (safe from injection)."""
        result = await self._session.execute(query)
        return result.scalars().all()

    # NEVER do this - vulnerable to SQL injection
    # async def unsafe_search(self, term: str):
    #     query = f"SELECT * FROM users WHERE name LIKE '%{term}%'"
    #     return await self._session.execute(text(query))

    # Instead, use parameterized queries
    async def safe_search(
        self,
        model: type[T],
        column: str,
        term: str,
    ) -> list[T]:
        """Safe search using parameterized query."""
        # Escape LIKE wildcards
        safe_term = term.replace("%", r"\%").replace("_", r"\_")

        # Use SQLAlchemy's safe query building
        query = select(model).where(
            getattr(model, column).ilike(f"%{safe_term}%")
        )

        result = await self._session.execute(query)
        return result.scalars().all()
```

### Password Validation

```python
# app/core/password_policy.py
import re
from dataclasses import dataclass


@dataclass
class PasswordPolicy:
    """Password policy configuration."""

    min_length: int = 8
    max_length: int = 128
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digit: bool = True
    require_special: bool = True
    special_chars: str = "!@#$%^&*(),.?\":{}|<>"


def validate_password(password: str, policy: PasswordPolicy | None = None) -> list[str]:
    """Validate password against policy. Returns list of errors."""
    if policy is None:
        policy = PasswordPolicy()

    errors = []

    if len(password) < policy.min_length:
        errors.append(f"Password must be at least {policy.min_length} characters")

    if len(password) > policy.max_length:
        errors.append(f"Password must be at most {policy.max_length} characters")

    if policy.require_uppercase and not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")

    if policy.require_lowercase and not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")

    if policy.require_digit and not re.search(r"\d", password):
        errors.append("Password must contain at least one digit")

    if policy.require_special:
        escaped_chars = re.escape(policy.special_chars)
        if not re.search(f"[{escaped_chars}]", password):
            errors.append("Password must contain at least one special character")

    return errors


# Check against common passwords (in production, use a proper list)
COMMON_PASSWORDS = {
    "password", "123456", "12345678", "qwerty", "abc123",
    "monkey", "1234567", "letmein", "trustno1", "dragon",
}


def is_common_password(password: str) -> bool:
    """Check if password is in common passwords list."""
    return password.lower() in COMMON_PASSWORDS
```

### Request Size Limiting

```python
# app/api/middleware/request_size.py
from fastapi import FastAPI, Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Limit request body size."""

    def __init__(self, app, max_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")

        if content_length:
            if int(content_length) > self.max_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Request body too large. Max size: {self.max_size} bytes",
                )

        return await call_next(request)


def setup_request_size_limit(app: FastAPI, max_size: int | None = None) -> None:
    """Setup request size limit middleware."""
    size = max_size or settings.MAX_REQUEST_SIZE
    app.add_middleware(RequestSizeLimitMiddleware, max_size=size)
```

### Rate Limit by IP for Login

```python
# app/core/brute_force_protection.py
import time
from dataclasses import dataclass, field

import structlog

from app.infrastructure.cache.redis import CacheService

logger = structlog.get_logger()


@dataclass
class BruteForceConfig:
    """Brute force protection configuration."""

    max_attempts: int = 5
    lockout_duration: int = 900  # 15 minutes
    attempt_window: int = 300  # 5 minutes


class BruteForceProtection:
    """Protection against brute force attacks."""

    def __init__(
        self,
        cache: CacheService,
        config: BruteForceConfig | None = None,
    ) -> None:
        self._cache = cache
        self._config = config or BruteForceConfig()

    def _get_key(self, identifier: str) -> str:
        return f"bruteforce:{identifier}"

    async def record_attempt(self, identifier: str) -> None:
        """Record a failed login attempt."""
        key = self._get_key(identifier)
        await self._cache.incr(key)
        await self._cache.expire(key, self._config.attempt_window)

    async def is_locked(self, identifier: str) -> bool:
        """Check if identifier is locked out."""
        key = self._get_key(identifier)
        attempts = await self._cache.get(key)

        if attempts and int(attempts) >= self._config.max_attempts:
            await logger.awarning(
                "Account locked due to too many failed attempts",
                identifier=identifier,
                attempts=attempts,
            )
            return True

        return False

    async def clear(self, identifier: str) -> None:
        """Clear failed attempts after successful login."""
        key = self._get_key(identifier)
        await self._cache.delete(key)

    async def get_remaining_attempts(self, identifier: str) -> int:
        """Get remaining login attempts."""
        key = self._get_key(identifier)
        attempts = await self._cache.get(key)
        current = int(attempts) if attempts else 0
        return max(0, self._config.max_attempts - current)
```

---

## Global Rate Limiting (All Endpoints)

Implement rate limiting for all API endpoints using SlowAPI (recommended) or custom Redis-based solution.

### SlowAPI Implementation (Recommended)

```python
# app/core/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from fastapi import FastAPI, Request

from app.core.config import settings


def get_identifier(request: Request) -> str:
    """Get rate limit identifier.

    Priority:
    1. Authenticated user ID (for user-specific limits)
    2. API Key (for API key-specific limits)
    3. Client IP (fallback)
    """
    # Check for authenticated user
    if hasattr(request.state, "user") and request.state.user:
        return f"user:{request.state.user.id}"

    # Check for API key
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"apikey:{api_key[:16]}"  # Use prefix only

    # Fallback to IP
    return f"ip:{get_remote_address(request)}"


# Initialize limiter with Redis backend
limiter = Limiter(
    key_func=get_identifier,
    storage_uri=settings.REDIS_URL,
    strategy="fixed-window",  # or "moving-window"
    headers_enabled=True,  # Add X-RateLimit headers
)


def setup_rate_limiting(app: FastAPI) -> None:
    """Configure global rate limiting for FastAPI app."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
```

### Rate Limit Decorators

```python
# app/api/v1/routes/items.py
from fastapi import APIRouter, Request

from app.core.rate_limit import limiter

router = APIRouter()


# Default rate limit for all endpoints
@router.get("/items")
@limiter.limit("100/minute")  # 100 requests per minute
async def list_items(request: Request):
    """List items with standard rate limit."""
    return {"items": []}


# Stricter limit for expensive operations
@router.post("/items/bulk")
@limiter.limit("10/minute")  # Only 10 bulk operations per minute
async def bulk_create(request: Request):
    """Bulk create with stricter limit."""
    return {"created": 0}


# Higher limit for authenticated users
@router.get("/items/premium")
@limiter.limit("1000/minute", key_func=get_identifier)
async def premium_endpoint(request: Request):
    """Premium endpoint with higher limit."""
    return {"premium": True}


# Multiple rate limits (burst + sustained)
@router.post("/items/upload")
@limiter.limit("5/second")    # Burst limit
@limiter.limit("100/hour")    # Sustained limit
async def upload_item(request: Request):
    """Upload with burst and sustained limits."""
    return {"uploaded": True}
```

### Custom Redis Rate Limiter (No Dependencies)

```python
# app/core/rate_limiter.py
import time
from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from redis.asyncio import Redis

import structlog

logger = structlog.get_logger()


class RateLimitStrategy(str, Enum):
    """Rate limiting strategies."""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    requests: int          # Max requests
    window: int           # Time window in seconds
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW


# Predefined rate limit tiers
RATE_LIMITS = {
    "default": RateLimitConfig(requests=100, window=60),      # 100/min
    "auth": RateLimitConfig(requests=20, window=60),          # 20/min (login, register)
    "api_key": RateLimitConfig(requests=1000, window=60),     # 1000/min
    "premium": RateLimitConfig(requests=5000, window=60),     # 5000/min
    "upload": RateLimitConfig(requests=10, window=60),        # 10/min
    "search": RateLimitConfig(requests=30, window=60),        # 30/min
    "webhook": RateLimitConfig(requests=100, window=1),       # 100/sec burst
}


class RateLimiter:
    """Redis-based rate limiter with multiple strategies."""

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def is_allowed(
        self,
        key: str,
        config: RateLimitConfig,
    ) -> tuple[bool, int, int]:
        """Check if request is allowed.

        Returns:
            Tuple of (allowed, remaining, reset_time)
        """
        if config.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return await self._sliding_window(key, config)
        elif config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return await self._token_bucket(key, config)
        else:
            return await self._fixed_window(key, config)

    async def _fixed_window(
        self,
        key: str,
        config: RateLimitConfig,
    ) -> tuple[bool, int, int]:
        """Fixed window rate limiting."""
        now = int(time.time())
        window_key = f"ratelimit:{key}:{now // config.window}"

        async with self._redis.pipeline() as pipe:
            pipe.incr(window_key)
            pipe.expire(window_key, config.window)
            results = await pipe.execute()

        current = results[0]
        remaining = max(0, config.requests - current)
        reset_time = (now // config.window + 1) * config.window

        return current <= config.requests, remaining, reset_time

    async def _sliding_window(
        self,
        key: str,
        config: RateLimitConfig,
    ) -> tuple[bool, int, int]:
        """Sliding window rate limiting using sorted set."""
        now = time.time()
        window_start = now - config.window
        window_key = f"ratelimit:sliding:{key}"

        async with self._redis.pipeline() as pipe:
            # Remove old entries
            pipe.zremrangebyscore(window_key, 0, window_start)
            # Add current request
            pipe.zadd(window_key, {str(now): now})
            # Count requests in window
            pipe.zcard(window_key)
            # Set expiry
            pipe.expire(window_key, config.window)
            results = await pipe.execute()

        current = results[2]
        remaining = max(0, config.requests - current)
        reset_time = int(now + config.window)

        return current <= config.requests, remaining, reset_time

    async def _token_bucket(
        self,
        key: str,
        config: RateLimitConfig,
    ) -> tuple[bool, int, int]:
        """Token bucket rate limiting.

        Tokens are added at a rate of (requests/window) per second.
        Allows burst up to `requests` tokens.
        """
        bucket_key = f"ratelimit:bucket:{key}"
        now = time.time()
        refill_rate = config.requests / config.window

        # Lua script for atomic token bucket
        lua_script = """
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        local window = tonumber(ARGV[4])

        local bucket = redis.call('HMGET', key, 'tokens', 'last_update')
        local tokens = tonumber(bucket[1]) or capacity
        local last_update = tonumber(bucket[2]) or now

        -- Refill tokens
        local elapsed = now - last_update
        tokens = math.min(capacity, tokens + (elapsed * refill_rate))

        -- Try to consume a token
        local allowed = 0
        if tokens >= 1 then
            tokens = tokens - 1
            allowed = 1
        end

        -- Update bucket
        redis.call('HMSET', key, 'tokens', tokens, 'last_update', now)
        redis.call('EXPIRE', key, window)

        return {allowed, math.floor(tokens)}
        """

        result = await self._redis.eval(
            lua_script,
            1,
            bucket_key,
            config.requests,
            refill_rate,
            now,
            config.window,
        )

        allowed = result[0] == 1
        remaining = result[1]
        reset_time = int(now + (1 / refill_rate))

        return allowed, remaining, reset_time


# Dependency for rate limiting
class RateLimitDependency:
    """FastAPI dependency for rate limiting."""

    def __init__(
        self,
        tier: str = "default",
        key_prefix: str = "",
    ) -> None:
        self.tier = tier
        self.key_prefix = key_prefix

    async def __call__(
        self,
        request: Request,
    ) -> None:
        redis: Redis = request.app.state.redis
        limiter = RateLimiter(redis)
        config = RATE_LIMITS.get(self.tier, RATE_LIMITS["default"])

        # Build rate limit key
        identifier = self._get_identifier(request)
        key = f"{self.key_prefix}:{identifier}" if self.key_prefix else identifier

        allowed, remaining, reset_time = await limiter.is_allowed(key, config)

        # Add rate limit headers
        request.state.ratelimit_remaining = remaining
        request.state.ratelimit_reset = reset_time
        request.state.ratelimit_limit = config.requests

        if not allowed:
            await logger.awarning(
                "Rate limit exceeded",
                key=key,
                tier=self.tier,
                identifier=identifier,
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": f"Rate limit exceeded. Try again in {reset_time - int(time.time())} seconds.",
                    "retry_after": reset_time - int(time.time()),
                },
                headers={
                    "Retry-After": str(reset_time - int(time.time())),
                    "X-RateLimit-Limit": str(config.requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                },
            )

    def _get_identifier(self, request: Request) -> str:
        """Get rate limit identifier from request."""
        # Authenticated user
        if hasattr(request.state, "user") and request.state.user:
            return f"user:{request.state.user.id}"

        # API key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"apikey:{api_key[:16]}"

        # IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"

        return f"ip:{ip}"


# Convenience function for creating rate limit dependencies
def rate_limit(tier: str = "default", key_prefix: str = "") -> RateLimitDependency:
    """Create a rate limit dependency.

    Usage:
        @router.get("/items", dependencies=[Depends(rate_limit("default"))])
        async def list_items(): ...

        @router.post("/login", dependencies=[Depends(rate_limit("auth"))])
        async def login(): ...
    """
    return RateLimitDependency(tier=tier, key_prefix=key_prefix)


# Type aliases for common rate limits
DefaultRateLimit = Annotated[None, Depends(rate_limit("default"))]
AuthRateLimit = Annotated[None, Depends(rate_limit("auth"))]
UploadRateLimit = Annotated[None, Depends(rate_limit("upload"))]
SearchRateLimit = Annotated[None, Depends(rate_limit("search"))]
```

### Rate Limit Middleware (Global)

```python
# app/api/middleware/rate_limit.py
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.rate_limiter import RateLimiter, RATE_LIMITS


class GlobalRateLimitMiddleware(BaseHTTPMiddleware):
    """Apply global rate limiting to all requests.

    This middleware applies a base rate limit to all endpoints.
    Individual endpoints can have stricter limits via dependencies.
    """

    # Paths to exclude from rate limiting
    EXCLUDED_PATHS = {
        "/health",
        "/health/live",
        "/health/ready",
        "/metrics",
        "/openapi.json",
        "/docs",
        "/redoc",
    }

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        # Get Redis from app state
        redis = request.app.state.redis
        limiter = RateLimiter(redis)

        # Determine rate limit tier based on path
        tier = self._get_tier(request.url.path)
        config = RATE_LIMITS.get(tier, RATE_LIMITS["default"])

        # Build identifier
        identifier = self._get_identifier(request)
        key = f"global:{request.method}:{identifier}"

        allowed, remaining, reset_time = await limiter.is_allowed(key, config)

        if not allowed:
            return Response(
                content='{"detail": "Too many requests"}',
                status_code=429,
                media_type="application/json",
                headers={
                    "Retry-After": str(reset_time - int(time.time())),
                    "X-RateLimit-Limit": str(config.requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                },
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(config.requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)

        return response

    def _get_tier(self, path: str) -> str:
        """Determine rate limit tier based on path."""
        if "/auth/" in path or "/login" in path or "/register" in path:
            return "auth"
        elif "/upload" in path or "/import" in path:
            return "upload"
        elif "/search" in path:
            return "search"
        elif "/webhook" in path:
            return "webhook"
        return "default"

    def _get_identifier(self, request: Request) -> str:
        """Get identifier for rate limiting."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


def setup_global_rate_limiting(app: FastAPI) -> None:
    """Setup global rate limiting middleware."""
    app.add_middleware(GlobalRateLimitMiddleware)
```

### Rate Limit Configuration in main.py

```python
# app/main.py
from fastapi import FastAPI

from app.api.middleware.rate_limit import setup_global_rate_limiting
from app.core.rate_limit import setup_rate_limiting  # SlowAPI version


def create_app() -> FastAPI:
    app = FastAPI()

    # Option 1: Use SlowAPI (simpler)
    setup_rate_limiting(app)

    # Option 2: Use custom middleware (more control)
    # setup_global_rate_limiting(app)

    return app
```

### Rate Limiting Summary

| Tier | Limit | Use Case |
|------|-------|----------|
| `default` | 100/min | Standard API endpoints |
| `auth` | 20/min | Login, register, password reset |
| `api_key` | 1000/min | API key authenticated requests |
| `premium` | 5000/min | Premium/paid tier users |
| `upload` | 10/min | File uploads, imports |
| `search` | 30/min | Search endpoints (expensive) |
| `webhook` | 100/sec | Webhook receivers (burst) |

### Rate Limit Headers

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Maximum requests allowed |
| `X-RateLimit-Remaining` | Remaining requests in window |
| `X-RateLimit-Reset` | Unix timestamp when limit resets |
| `Retry-After` | Seconds to wait before retrying |

### Rate Limit Best Practices

1. **Use Redis** for distributed rate limiting across multiple instances
2. **Sliding window** is more accurate but uses more memory
3. **Token bucket** is best for allowing bursts
4. **Exclude health checks** from rate limiting
5. **Log rate limit violations** for monitoring
6. **Return informative error messages** with retry timing
7. **Consider user tier** for differentiated limits
8. **Monitor rate limit metrics** in Prometheus

### Secure File Upload

```python
# app/core/file_upload.py
import hashlib
import magic
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.sanitization import sanitize_filename

# Allowed MIME types
ALLOWED_MIME_TYPES = {
    "image/jpeg": [".jpg", ".jpeg"],
    "image/png": [".png"],
    "image/gif": [".gif"],
    "image/webp": [".webp"],
    "application/pdf": [".pdf"],
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


async def validate_upload(
    file: UploadFile,
    allowed_types: dict[str, list[str]] | None = None,
    max_size: int | None = None,
) -> tuple[str, bytes]:
    """Validate uploaded file.

    Returns:
        Tuple of (sanitized_filename, file_content)
    """
    allowed = allowed_types or ALLOWED_MIME_TYPES
    max_bytes = max_size or MAX_FILE_SIZE

    # Read file content
    content = await file.read()
    await file.seek(0)

    # Check file size
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size: {max_bytes // (1024*1024)}MB",
        )

    # Check MIME type using magic bytes (not extension)
    mime_type = magic.from_buffer(content, mime=True)
    if mime_type not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed: {mime_type}",
        )

    # Validate extension matches MIME type
    filename = sanitize_filename(file.filename or "unnamed")
    ext = Path(filename).suffix.lower()

    if ext not in allowed.get(mime_type, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension doesn't match content type",
        )

    return filename, content


def generate_secure_filename(original: str, content: bytes) -> str:
    """Generate secure filename with hash."""
    # Create hash of content
    content_hash = hashlib.sha256(content).hexdigest()[:12]

    # Get extension
    ext = Path(original).suffix.lower()

    return f"{content_hash}{ext}"
```

### CORS Configuration

```python
# app/core/cors.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


def setup_cors(app: FastAPI) -> None:
    """Configure CORS middleware with security best practices.

    Security Guidelines:
    - NEVER use allow_origins=["*"] in production
    - Always specify exact origins, not wildcards
    - Be restrictive with allowed methods and headers
    - Only enable credentials when absolutely necessary
    """
    # Development: Allow localhost origins
    dev_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
    ]

    # Production: Explicit allowed origins only
    prod_origins = [
        "https://app.example.com",
        "https://admin.example.com",
    ]

    allowed_origins = dev_origins if settings.DEBUG else prod_origins

    # Override with environment variable if set
    if settings.CORS_ORIGINS:
        allowed_origins = [
            origin.strip() for origin in settings.CORS_ORIGINS.split(",")
        ]

    app.add_middleware(
        CORSMiddleware,
        # Explicit origins only - NEVER use ["*"] in production
        allow_origins=allowed_origins,
        # Credentials (cookies, auth headers) - only if needed
        allow_credentials=True,
        # Allowed HTTP methods - be restrictive
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        # Allowed headers - specify explicitly
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Request-ID",
            "X-CSRF-Token",
        ],
        # Expose headers to client
        expose_headers=[
            "X-Request-ID",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
        ],
        # Preflight cache duration (seconds)
        max_age=600,
    )


# Add to config.py
class Settings:
    # CORS
    CORS_ORIGINS: str | None = None  # Comma-separated list of origins
```

### CORS Security Checklist

| Setting | Development | Production | Notes |
|---------|-------------|------------|-------|
| `allow_origins` | localhost URLs | Exact domains only | **NEVER use `["*"]`** |
| `allow_credentials` | `True` | `True` only if needed | Required for cookies |
| `allow_methods` | All methods | Only required methods | Be restrictive |
| `allow_headers` | Common headers | Explicit list | Avoid `["*"]` |
| `max_age` | 600 | 3600 | Preflight cache |

### CSRF Protection

For cookie-based authentication (session cookies), CSRF protection is required.

```python
# app/core/csrf.py
import secrets
from typing import Annotated

from fastapi import Cookie, Depends, Header, HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


CSRF_TOKEN_LENGTH = 32
CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}


def generate_csrf_token() -> str:
    """Generate a cryptographically secure CSRF token."""
    return secrets.token_urlsafe(CSRF_TOKEN_LENGTH)


class CSRFMiddleware(BaseHTTPMiddleware):
    """CSRF protection middleware for cookie-based authentication.

    Implements the Double Submit Cookie pattern:
    1. Set CSRF token in cookie (HttpOnly=False so JS can read it)
    2. Require the same token in request header
    3. Compare cookie value with header value

    Note: Only needed for cookie-based auth.
    JWT Bearer tokens in Authorization header are inherently CSRF-safe.
    """

    async def dispatch(self, request: Request, call_next):
        # Skip CSRF check for safe methods
        if request.method in SAFE_METHODS:
            response = await call_next(request)
            # Set CSRF token cookie if not present
            if CSRF_COOKIE_NAME not in request.cookies:
                csrf_token = generate_csrf_token()
                response.set_cookie(
                    key=CSRF_COOKIE_NAME,
                    value=csrf_token,
                    httponly=False,  # JS needs to read this
                    secure=not settings.DEBUG,
                    samesite="lax",
                    max_age=3600,
                )
            return response

        # For state-changing methods, validate CSRF token
        cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
        header_token = request.headers.get(CSRF_HEADER_NAME)

        if not cookie_token or not header_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing",
            )

        # Constant-time comparison to prevent timing attacks
        if not secrets.compare_digest(cookie_token, header_token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token mismatch",
            )

        return await call_next(request)


# Dependency for routes that need CSRF validation
async def validate_csrf_token(
    csrf_cookie: Annotated[str | None, Cookie(alias=CSRF_COOKIE_NAME)] = None,
    csrf_header: Annotated[str | None, Header(alias=CSRF_HEADER_NAME)] = None,
) -> None:
    """Validate CSRF token in route dependency.

    Use this for routes that handle form submissions with cookies.
    """
    if not csrf_cookie or not csrf_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing",
        )

    if not secrets.compare_digest(csrf_cookie, csrf_header):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token mismatch",
        )


# Type alias for dependency injection
CSRFValidation = Annotated[None, Depends(validate_csrf_token)]
```

### CSRF Usage Example

```python
# app/api/v1/routes/forms.py
from fastapi import APIRouter, Response

from app.core.csrf import CSRFValidation, generate_csrf_token, CSRF_COOKIE_NAME

router = APIRouter()


@router.get("/csrf-token")
async def get_csrf_token(response: Response):
    """Get CSRF token for client-side use."""
    token = generate_csrf_token()
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=token,
        httponly=False,
        secure=True,
        samesite="lax",
    )
    return {"csrf_token": token}


@router.post("/submit-form")
async def submit_form(
    data: FormData,
    _: CSRFValidation,  # CSRF validation dependency
):
    """Form submission with CSRF protection."""
    # Process form...
    return {"status": "submitted"}
```

### When to Use CSRF Protection

| Auth Method | CSRF Required | Reason |
|-------------|---------------|--------|
| Cookie/Session | **Yes** | Browser auto-sends cookies |
| JWT in Header | No | Header not auto-sent |
| API Key in Header | No | Header not auto-sent |
| Basic Auth | **Yes** | Browser may cache credentials |

### main.py 보안 설정

```python
# app/main.py
from fastapi import FastAPI

from app.api.middleware.security_headers import SecurityHeadersMiddleware
from app.api.middleware.request_size import setup_request_size_limit
from app.core.cors import setup_cors
from app.core.csrf import CSRFMiddleware


def create_app() -> FastAPI:
    app = FastAPI(
        # Disable docs in production
        docs_url="/api/v1/docs" if settings.DEBUG else None,
        redoc_url="/api/v1/redoc" if settings.DEBUG else None,
        openapi_url="/api/v1/openapi.json" if settings.DEBUG else None,
    )

    # Security middleware (order matters!)
    app.add_middleware(SecurityHeadersMiddleware)
    setup_cors(app)  # CORS configuration
    setup_request_size_limit(app)

    # CSRF protection (only for cookie-based auth)
    # app.add_middleware(CSRFMiddleware)

    return app
```

## Dependency Vulnerability Scanning

### Tools Overview

| Tool | Type | Best For |
|------|------|----------|
| **pip-audit** | CLI | Quick local scans |
| **safety** | CLI/CI | PyUp.io database |
| **Snyk** | SaaS/CI | Comprehensive, auto-fix PRs |
| **Dependabot** | GitHub | Automated security updates |
| **Trivy** | Container | Docker image scanning |

### pip-audit (Recommended for Local Development)

```bash
# Install
pip install pip-audit

# Scan current environment
pip-audit

# Scan requirements file
pip-audit -r requirements.txt

# Output as JSON (for CI)
pip-audit --format json --output audit-results.json

# Ignore specific vulnerabilities
pip-audit --ignore-vuln PYSEC-2023-XXX
```

### Safety Check

```bash
# Install
pip install safety

# Basic scan
safety check

# Scan requirements file
safety check -r requirements.txt

# Output as JSON
safety check --json > safety-results.json

# Use in CI with exit code
safety check --full-report
```

### GitHub Actions CI Integration

```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * *'  # Daily scan

jobs:
  dependency-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install pip-audit safety
          pip install -r requirements.txt

      - name: Run pip-audit
        run: pip-audit --format json --output pip-audit.json
        continue-on-error: true

      - name: Run safety check
        run: safety check --json > safety.json
        continue-on-error: true

      - name: Upload security scan results
        uses: actions/upload-artifact@v4
        with:
          name: security-scan-results
          path: |
            pip-audit.json
            safety.json

      - name: Check for critical vulnerabilities
        run: |
          pip-audit --desc || exit 1

  container-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t app:scan .

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'app:scan'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'
```

### Dependabot Configuration

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    groups:
      security:
        applies-to: security-updates
      development:
        patterns:
          - "pytest*"
          - "black"
          - "ruff"
    reviewers:
      - "security-team"
    labels:
      - "dependencies"
      - "security"

  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
```

### Pre-commit Hook for Security

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pyupio/safety
    rev: 3.2.0
    hooks:
      - id: safety
        args: ['--short-report']

  - repo: https://github.com/trailofbits/pip-audit
    rev: v2.7.3
    hooks:
      - id: pip-audit
        args: ['--strict']
```

### Vulnerability Response Process

1. **Automated Alerts**: Configure notifications for new CVEs
2. **Triage**: Assess severity and exploitability
3. **Patch**: Update dependency or apply workaround
4. **Verify**: Re-run security scan
5. **Document**: Record in security log

## Security Checklist

- [ ] HTTPS only in production
- [ ] Security headers configured
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (output encoding)
- [ ] CSRF protection (for cookie-based auth)
- [ ] Password policy enforced
- [ ] Brute force protection
- [ ] File upload validation
- [ ] Sensitive data not logged
- [ ] Secrets not in code
- [ ] Dependencies scanned for vulnerabilities
- [ ] Container images scanned
- [ ] Dependabot/Renovate enabled

## References

- `_references/AUTH-PATTERN.md`
