---
name: middleware
description: |
  CORS, Request logging, Timing 등 미들웨어를 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Middleware Skill

CORS, Request logging, Timing 등 미들웨어를 구현합니다.

## Triggers

- "미들웨어", "middleware", "cors", "logging"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |

---

## Output

### CORS Middleware

```python
# app/api/middleware/cors.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


def setup_cors(app: FastAPI) -> None:
    """Setup CORS middleware."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
        expose_headers=["X-Request-ID", "X-Process-Time"],
        max_age=600,  # Cache preflight requests for 10 minutes
    )
```

### Request ID Middleware

```python
# app/api/middleware/request_id.py
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add unique request ID to each request."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        # Get or generate request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Store in request state
        request.state.request_id = request_id

        # Bind to structlog context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        # Process request
        response = await call_next(request)

        # Add to response headers
        response.headers["X-Request-ID"] = request_id

        return response
```

### Timing Middleware

```python
# app/api/middleware/timing.py
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()


class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware to measure request processing time."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = time.perf_counter() - start_time
        process_time_ms = round(process_time * 1000, 2)

        # Add to response headers
        response.headers["X-Process-Time"] = f"{process_time_ms}ms"

        # Log slow requests
        if process_time_ms > 1000:  # > 1 second
            await logger.awarning(
                "Slow request",
                path=str(request.url.path),
                method=request.method,
                process_time_ms=process_time_ms,
            )

        return response
```

### Logging Middleware

```python
# app/api/middleware/logging.py
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests and responses."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        # Skip health check endpoints
        if request.url.path in ["/health", "/ready", "/metrics"]:
            return await call_next(request)

        start_time = time.perf_counter()

        # Log request
        await logger.ainfo(
            "Request started",
            method=request.method,
            path=str(request.url.path),
            query_params=dict(request.query_params),
            client_ip=self._get_client_ip(request),
            user_agent=request.headers.get("User-Agent"),
        )

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Log response
        log_method = logger.ainfo if response.status_code < 400 else logger.awarning
        await log_method(
            "Request completed",
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP from request headers or connection."""
        # Check common proxy headers
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct connection
        if request.client:
            return request.client.host

        return "unknown"
```

### Error Handling Middleware

```python
# app/api/middleware/error_handler.py
import asyncio
import traceback
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

from app.schemas.error import ErrorResponse

logger = structlog.get_logger()


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware to catch unhandled exceptions."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        try:
            return await call_next(request)
        except asyncio.CancelledError:
            # Don't catch CancelledError - it's used for graceful shutdown
            raise
        except Exception as exc:
            # Log the exception
            await logger.aexception(
                "Unhandled exception in middleware",
                path=str(request.url.path),
                method=request.method,
                error=str(exc),
                traceback=traceback.format_exc(),
            )

            # Return generic error response
            return JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    error="INTERNAL_ERROR",
                    message="An unexpected error occurred",
                    details={},
                ).model_dump(),
            )
```

### GZip Middleware

```python
# app/api/middleware/compression.py
from fastapi import FastAPI
from starlette.middleware.gzip import GZipMiddleware


def setup_compression(app: FastAPI, minimum_size: int = 1000) -> None:
    """Setup GZip compression middleware."""
    app.add_middleware(GZipMiddleware, minimum_size=minimum_size)
```

### Trusted Host Middleware

```python
# app/api/middleware/trusted_host.py
from fastapi import FastAPI
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings


def setup_trusted_hosts(app: FastAPI) -> None:
    """Setup trusted host middleware for production."""
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS,
        )
```

### Middleware Setup

```python
# app/api/middleware/__init__.py
from fastapi import FastAPI

from app.api.middleware.cors import setup_cors
from app.api.middleware.compression import setup_compression
from app.api.middleware.error_handler import ErrorHandlerMiddleware
from app.api.middleware.logging import LoggingMiddleware
from app.api.middleware.request_id import RequestIDMiddleware
from app.api.middleware.timing import TimingMiddleware
from app.api.middleware.trusted_host import setup_trusted_hosts


def setup_middleware(app: FastAPI) -> None:
    """Setup all middleware for the application.

    Note: Middleware is executed in LIFO order (last added = first executed).
    """
    # Error handler (outermost - catches all errors)
    app.add_middleware(ErrorHandlerMiddleware)

    # Compression
    setup_compression(app)

    # Trusted hosts (production only)
    setup_trusted_hosts(app)

    # CORS (must be before other middleware that modify response)
    setup_cors(app)

    # Timing (measure total request time)
    app.add_middleware(TimingMiddleware)

    # Logging (log after timing is measured)
    app.add_middleware(LoggingMiddleware)

    # Request ID (innermost - generates ID first)
    app.add_middleware(RequestIDMiddleware)
```

### main.py에 등록

```python
# app/main.py
from fastapi import FastAPI

from app.api.middleware import setup_middleware


def create_app() -> FastAPI:
    app = FastAPI(...)

    # Setup middleware
    setup_middleware(app)

    return app
```

## References

- `_references/API-PATTERN.md`
