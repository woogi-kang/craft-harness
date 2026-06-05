---
name: observability
description: |
  로깅, 메트릭, 트레이싱 기반 관측성을 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Observability Skill

로깅, 메트릭, 트레이싱 기반 관측성을 구현합니다.

## Triggers

- "observability", "모니터링", "로깅", "메트릭", "트레이싱", "prometheus", "grafana"

---

## Observability Pyramid

관측성은 세 가지 핵심 신호(Three Pillars)로 구성됩니다. 각 신호는 서로 다른 목적과 비용을 가집니다.

```
                    ┌─────────────┐
                    │   Traces    │  ← 가장 상세, 가장 비쌈
                    │  (샘플링)    │     디버깅, 성능 분석
                    └─────────────┘
                   ╱               ╲
                  ╱                 ╲
           ┌─────────────┐   ┌─────────────┐
           │   Metrics   │   │    Logs     │
           │  (집계됨)    │   │  (샘플링)    │
           │ 대시보드/알림 │   │   디버깅    │
           └─────────────┘   └─────────────┘
                  ╲                 ╱
                   ╲               ╱
                    ╲             ╱
               ┌─────────────────────┐
               │      Events         │  ← 기반 데이터
               │ (HTTP, DB, Cache)   │     모든 관측성의 원천
               └─────────────────────┘
```

### 신호별 특성

| 신호 | 목적 | 저장 비용 | 샘플링 | 쿼리 속도 |
|------|------|-----------|--------|-----------|
| **Metrics** | 대시보드, 알림, SLO | 낮음 (집계) | 불필요 | 빠름 |
| **Logs** | 디버깅, 감사 | 중간 | 필요 (prod) | 중간 |
| **Traces** | 성능 분석, 의존성 추적 | 높음 | 필수 | 느림 |

### 권장 전략

```
┌─────────────────────────────────────────────────────────────────┐
│ Production 환경 관측성 전략                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 1. Metrics: 100% 수집 (집계됨, 저비용)                            │
│    - 모든 요청의 count, latency, error rate                     │
│    - Prometheus + Grafana                                       │
│                                                                 │
│ 2. Logs: 샘플링 수집                                             │
│    - ERROR/WARN: 100% 수집                                      │
│    - INFO: 10% 샘플링 또는 rate limiting                        │
│    - DEBUG: production에서 비활성화                              │
│    - Loki 또는 Elasticsearch                                    │
│                                                                 │
│ 3. Traces: 샘플링 수집 (1-10%)                                   │
│    - 에러 발생 시: 100% 수집                                     │
│    - 정상 요청: 1-5% 샘플링                                      │
│    - 느린 요청 (>1s): 100% 수집                                  │
│    - Jaeger 또는 Tempo                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |

---

## Output

### Structured Logging

```python
# app/core/logging.py
import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor

from app.core.config import settings


def setup_logging() -> None:
    """Configure structured logging."""

    # Shared processors
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.ENVIRONMENT == "development":
        # Development: colored console output
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    else:
        # Production: JSON output
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )

    # Reduce noise from third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)
```

### Log Sampling Strategy

Production 환경에서 로그 볼륨을 관리하기 위한 샘플링 전략입니다.

```python
# app/core/log_sampling.py
import random
import time
from collections import defaultdict
from functools import wraps
from threading import Lock
from typing import Callable, Any

import structlog

logger = structlog.get_logger()


class LogSampler:
    """로그 샘플링 전략 구현.

    전략:
    - ERROR/CRITICAL: 항상 100% 기록
    - WARNING: 50% 샘플링
    - INFO: 10% 샘플링 + rate limiting (초당 100건)
    - DEBUG: production에서 비활성화
    """

    def __init__(
        self,
        info_sample_rate: float = 0.1,
        warn_sample_rate: float = 0.5,
        max_info_per_second: int = 100,
    ):
        self.info_sample_rate = info_sample_rate
        self.warn_sample_rate = warn_sample_rate
        self.max_info_per_second = max_info_per_second

        self._info_count = 0
        self._last_reset = time.time()
        self._lock = Lock()

        # 중복 로그 억제 (같은 메시지 반복 방지)
        self._seen_messages: dict[str, float] = {}
        self._dedup_window = 60  # 60초 내 중복 억제

    def should_log(self, level: str, message: str) -> bool:
        """로그 기록 여부 결정."""
        # ERROR/CRITICAL은 항상 기록
        if level in ("ERROR", "CRITICAL", "EXCEPTION"):
            return True

        # 중복 메시지 억제
        now = time.time()
        message_key = f"{level}:{message[:100]}"
        if message_key in self._seen_messages:
            if now - self._seen_messages[message_key] < self._dedup_window:
                return False
        self._seen_messages[message_key] = now

        # 오래된 메시지 키 정리 (메모리 관리)
        if len(self._seen_messages) > 10000:
            self._cleanup_old_messages(now)

        # WARNING: 50% 샘플링
        if level == "WARNING":
            return random.random() < self.warn_sample_rate

        # INFO: 샘플링 + rate limiting
        if level == "INFO":
            with self._lock:
                # Rate limit 리셋
                if now - self._last_reset >= 1.0:
                    self._info_count = 0
                    self._last_reset = now

                # Rate limit 초과 확인
                if self._info_count >= self.max_info_per_second:
                    return False

                # 샘플링
                if random.random() >= self.info_sample_rate:
                    return False

                self._info_count += 1
                return True

        # DEBUG는 production에서 기본 비활성화
        return False

    def _cleanup_old_messages(self, now: float) -> None:
        """오래된 메시지 키 정리."""
        self._seen_messages = {
            k: v
            for k, v in self._seen_messages.items()
            if now - v < self._dedup_window
        }


# 전역 샘플러
_log_sampler = LogSampler()


class SampledBoundLogger:
    """샘플링이 적용된 structlog 래퍼."""

    def __init__(self, base_logger: structlog.stdlib.BoundLogger):
        self._logger = base_logger

    def info(self, message: str, **kwargs: Any) -> None:
        if _log_sampler.should_log("INFO", message):
            self._logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        if _log_sampler.should_log("WARNING", message):
            self._logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        # ERROR는 항상 기록
        self._logger.error(message, **kwargs)

    def exception(self, message: str, **kwargs: Any) -> None:
        # EXCEPTION은 항상 기록
        self._logger.exception(message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        if _log_sampler.should_log("DEBUG", message):
            self._logger.debug(message, **kwargs)

    # async 버전
    async def ainfo(self, message: str, **kwargs: Any) -> None:
        if _log_sampler.should_log("INFO", message):
            await self._logger.ainfo(message, **kwargs)

    async def awarning(self, message: str, **kwargs: Any) -> None:
        if _log_sampler.should_log("WARNING", message):
            await self._logger.awarning(message, **kwargs)

    async def aerror(self, message: str, **kwargs: Any) -> None:
        await self._logger.aerror(message, **kwargs)

    async def aexception(self, message: str, **kwargs: Any) -> None:
        await self._logger.aexception(message, **kwargs)


def get_sampled_logger(name: str | None = None) -> SampledBoundLogger:
    """샘플링이 적용된 로거 반환."""
    return SampledBoundLogger(structlog.get_logger(name))
```

### 로그 레벨별 전략 요약

| 레벨 | 샘플링 | Rate Limit | 용도 |
|------|--------|------------|------|
| **ERROR/CRITICAL** | 100% | 없음 | 에러 추적, 알림 |
| **WARNING** | 50% | 없음 | 잠재적 문제 |
| **INFO** | 10% | 100/s | 일반 운영 로그 |
| **DEBUG** | 0% (prod) | - | 개발 시에만 |

### Request Logging Middleware

```python
# app/middleware/logging.py
import time
import uuid
from typing import Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all HTTP requests and responses."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        # Generate request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        # Bind request context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
        )

        # Log request
        await logger.ainfo(
            "Request started",
            query_params=dict(request.query_params),
        )

        # Process request
        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log response
            await logger.ainfo(
                "Request completed",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            # Add request ID to response
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            await logger.aexception(
                "Request failed",
                duration_ms=round(duration_ms, 2),
                error=str(e),
            )
            raise
```

### Prometheus Metrics

```python
# app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.requests import Request
from starlette.responses import Response

# Application info
APP_INFO = Info("app", "Application information")

# Request metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "HTTP requests currently being processed",
    ["method", "endpoint"],
)

# Database metrics
DB_QUERY_COUNT = Counter(
    "db_queries_total",
    "Total database queries",
    ["operation", "table"],
)

DB_QUERY_LATENCY = Histogram(
    "db_query_duration_seconds",
    "Database query latency",
    ["operation", "table"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
)

DB_CONNECTIONS_ACTIVE = Gauge(
    "db_connections_active",
    "Active database connections",
)

# Cache metrics
CACHE_HIT = Counter(
    "cache_hits_total",
    "Total cache hits",
    ["cache_type"],
)

CACHE_MISS = Counter(
    "cache_misses_total",
    "Total cache misses",
    ["cache_type"],
)

# Business metrics
USER_REGISTRATIONS = Counter(
    "user_registrations_total",
    "Total user registrations",
)

ACTIVE_USERS = Gauge(
    "active_users",
    "Currently active users",
)


def set_app_info(version: str, environment: str) -> None:
    """Set application info metrics."""
    APP_INFO.info({
        "version": version,
        "environment": environment,
    })


async def metrics_endpoint(request: Request) -> Response:
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
```

### Metrics Middleware with Cardinality Control

```python
# app/middleware/metrics.py
import time
import re
from typing import Callable
from collections import defaultdict
from threading import Lock

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    REQUESTS_IN_PROGRESS,
)


class CardinalityLimiter:
    """메트릭 카디널리티 폭발 방지.

    Prometheus는 레이블 조합당 별도 시계열을 생성합니다.
    - 10 endpoints × 5 methods × 10 status codes = 500 시계열
    - 1000 user_ids를 레이블로 추가하면 = 500,000 시계열 (위험!)

    이 클래스는 고유 레이블 값의 수를 제한합니다.
    """

    def __init__(self, max_unique_values: int = 100):
        self.max_unique_values = max_unique_values
        self._seen_values: dict[str, set] = defaultdict(set)
        self._lock = Lock()

    def get_safe_label(self, label_name: str, value: str, fallback: str = "other") -> str:
        """카디널리티 제한을 적용한 레이블 값 반환."""
        with self._lock:
            seen = self._seen_values[label_name]

            if value in seen:
                return value

            if len(seen) < self.max_unique_values:
                seen.add(value)
                return value

            # 한도 초과 시 fallback 반환
            return fallback


# 전역 카디널리티 제한기
_cardinality_limiter = CardinalityLimiter(max_unique_values=100)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Collect Prometheus metrics for HTTP requests."""

    # 알려진 API 엔드포인트 (화이트리스트 방식 권장)
    KNOWN_ENDPOINTS = {
        "/api/v1/users",
        "/api/v1/users/{id}",
        "/api/v1/auth/login",
        "/api/v1/auth/logout",
        "/api/v1/items",
        "/api/v1/items/{id}",
        "/health",
        "/health/ready",
        "/health/live",
        "/metrics",
    }

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        method = request.method
        # Normalize path to avoid high cardinality
        path = self._normalize_path(request.url.path)

        # 카디널리티 안전 레이블
        safe_path = _cardinality_limiter.get_safe_label("endpoint", path, "/unknown")

        # Track in-progress requests
        REQUESTS_IN_PROGRESS.labels(method=method, endpoint=safe_path).inc()

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            status_code = 500
            raise
        finally:
            # Record request duration
            duration = time.perf_counter() - start_time
            REQUEST_LATENCY.labels(method=method, endpoint=safe_path).observe(duration)

            # 상태 코드도 그룹화 (2xx, 4xx, 5xx)
            status_group = f"{status_code // 100}xx"

            # Record request count
            REQUEST_COUNT.labels(
                method=method,
                endpoint=safe_path,
                status_code=status_group,  # 개별 코드 대신 그룹 사용
            ).inc()

            # Decrease in-progress counter
            REQUESTS_IN_PROGRESS.labels(method=method, endpoint=safe_path).dec()

        return response

    def _normalize_path(self, path: str) -> str:
        """Normalize path to reduce cardinality.

        카디널리티 관리 핵심:
        - /users/123 → /users/{id}
        - /items/abc-def-123 → /items/{uuid}
        - 알 수 없는 경로 → /unknown
        """
        # Replace numeric IDs
        path = re.sub(r'/\d+', '/{id}', path)
        # Replace UUIDs
        path = re.sub(
            r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            '/{uuid}',
            path,
            flags=re.IGNORECASE,
        )
        # Replace slugs (alphanumeric with hyphens, likely dynamic)
        path = re.sub(r'/[a-z0-9]+-[a-z0-9-]+', '/{slug}', path, flags=re.IGNORECASE)

        # 화이트리스트에 없으면 unknown 처리
        if path not in self.KNOWN_ENDPOINTS:
            # 최소한 첫 번째 세그먼트는 유지
            segments = path.split('/')
            if len(segments) > 2:
                path = '/'.join(segments[:3]) + '/...'

        return path
```

### 카디널리티 관리 Best Practices

| 위험 수준 | 레이블 예시 | 조치 |
|-----------|------------|------|
| 🔴 **높음** | `user_id`, `session_id`, `request_id` | 절대 레이블로 사용 금지 |
| 🟠 **중간** | `endpoint` (동적 경로 포함) | 정규화 필수 (`/{id}`) |
| 🟡 **낮음** | `status_code` (개별 코드) | 그룹화 권장 (`2xx`, `4xx`) |
| 🟢 **안전** | `method`, `service`, `environment` | 그대로 사용 가능 |

```python
# ❌ 나쁜 예: 고카디널리티 레이블
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total requests",
    ["method", "endpoint", "status_code", "user_id"],  # user_id 위험!
)

# ✅ 좋은 예: 저카디널리티 레이블
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total requests",
    ["method", "endpoint", "status_group"],  # status_group: 2xx, 4xx, 5xx
)

# 사용자별 메트릭이 필요하면 별도 Counter 사용
USER_ACTIONS = Counter(
    "user_actions_total",
    "User action counts",
    ["action"],  # login, logout, purchase 등 제한된 값
)
```

### OpenTelemetry Tracing

```python
# app/core/tracing.py
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes

from app.core.config import settings


def setup_tracing() -> None:
    """Configure OpenTelemetry tracing."""
    if not settings.OTEL_ENABLED:
        return

    # Create resource
    resource = Resource.create({
        ResourceAttributes.SERVICE_NAME: settings.PROJECT_NAME,
        ResourceAttributes.SERVICE_VERSION: settings.VERSION,
        ResourceAttributes.DEPLOYMENT_ENVIRONMENT: settings.ENVIRONMENT,
    })

    # Create tracer provider
    provider = TracerProvider(resource=resource)

    # Add OTLP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
    )
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    # Set global tracer provider
    trace.set_tracer_provider(provider)


def instrument_app(app) -> None:
    """Instrument FastAPI application."""
    if not settings.OTEL_ENABLED:
        return

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    # Instrument HTTP client
    HTTPXClientInstrumentor().instrument()

    # Instrument Redis
    RedisInstrumentor().instrument()


def instrument_database(engine) -> None:
    """Instrument SQLAlchemy (sync engine only).

    주의: SQLAlchemyInstrumentor는 sync_engine만 지원합니다.
    AsyncSession 사용 시 별도 처리가 필요합니다.
    """
    if not settings.OTEL_ENABLED:
        return

    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)


def get_tracer(name: str = __name__) -> trace.Tracer:
    """Get a tracer instance."""
    return trace.get_tracer(name)
```

### OpenTelemetry Async Database Instrumentation

SQLAlchemy 2.0 async 엔진은 기본 Instrumentor에서 완전히 지원되지 않습니다.
수동으로 async 쿼리를 추적하는 방법입니다.

```python
# app/core/tracing_async.py
from contextlib import asynccontextmanager
from typing import AsyncIterator, Any

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from sqlalchemy.ext.asyncio import AsyncSession

tracer = trace.get_tracer(__name__)


@asynccontextmanager
async def traced_db_session(
    session: AsyncSession,
    operation: str = "db.query",
) -> AsyncIterator[AsyncSession]:
    """Async DB 세션에 트레이싱 추가.

    사용 예:
        async with traced_db_session(session, "users.list") as sess:
            result = await sess.execute(select(User))
    """
    with tracer.start_as_current_span(
        operation,
        attributes={
            "db.system": "postgresql",
            "db.operation": operation,
        },
    ) as span:
        try:
            yield session
            span.set_status(Status(StatusCode.OK))
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise


class TracedAsyncSession:
    """트레이싱이 적용된 AsyncSession 래퍼.

    Repository에서 사용:
        class UserRepository:
            def __init__(self, session: AsyncSession):
                self._session = TracedAsyncSession(session)

            async def get_by_id(self, user_id: int) -> User | None:
                return await self._session.execute(
                    select(User).where(User.id == user_id),
                    operation="users.get_by_id",
                )
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def execute(
        self,
        statement: Any,
        operation: str = "db.execute",
        **kwargs: Any,
    ):
        """트레이싱이 적용된 execute."""
        with tracer.start_as_current_span(
            operation,
            attributes={
                "db.system": "postgresql",
                "db.statement": str(statement)[:500],  # 쿼리 일부만 기록
            },
        ) as span:
            try:
                result = await self._session.execute(statement, **kwargs)
                span.set_attribute("db.rows_affected", result.rowcount or 0)
                span.set_status(Status(StatusCode.OK))
                return result
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

    async def commit(self) -> None:
        """트레이싱이 적용된 commit."""
        with tracer.start_as_current_span("db.commit") as span:
            try:
                await self._session.commit()
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

    async def rollback(self) -> None:
        """트레이싱이 적용된 rollback."""
        with tracer.start_as_current_span("db.rollback") as span:
            await self._session.rollback()
            span.set_status(Status(StatusCode.OK))


# Repository에서 사용하는 데코레이터
def trace_db_operation(operation: str):
    """DB 작업에 트레이싱 추가하는 데코레이터.

    사용 예:
        @trace_db_operation("users.create")
        async def create_user(session: AsyncSession, user: UserCreate) -> User:
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(
                operation,
                attributes={"db.system": "postgresql"},
            ) as span:
                try:
                    result = await func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        return wrapper
    return decorator
```

### Health Check Endpoints

```python
# app/api/health.py
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_async_session
from app.core.config import settings

router = APIRouter(tags=["health"])


class HealthStatus(BaseModel):
    """Health check response."""

    status: str
    version: str
    environment: str
    timestamp: datetime


class ReadinessStatus(BaseModel):
    """Readiness check response."""

    status: str
    checks: dict[str, bool]


@router.get("/health", response_model=HealthStatus)
async def health_check():
    """Liveness probe - basic health check."""
    return HealthStatus(
        status="healthy",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/health/ready", response_model=ReadinessStatus)
async def readiness_check(
    session: AsyncSession = Depends(get_async_session),
):
    """Readiness probe - check all dependencies."""
    checks = {}

    # Check database
    try:
        await session.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        checks["database"] = False

    # Check Redis
    try:
        from app.infrastructure.cache.redis import redis_client
        await redis_client.ping()
        checks["redis"] = True
    except Exception:
        checks["redis"] = False

    # Overall status
    all_healthy = all(checks.values())

    return ReadinessStatus(
        status="ready" if all_healthy else "not_ready",
        checks=checks,
    )


@router.get("/health/live")
async def liveness_check():
    """Simple liveness check for Kubernetes."""
    return {"status": "alive"}
```

### Sentry Integration

```python
# app/core/sentry.py
import sentry_sdk
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

from app.core.config import settings


def setup_sentry() -> None:
    """Configure Sentry error tracking."""
    if not settings.SENTRY_DSN:
        return

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        release=settings.VERSION,
        traces_sample_rate=0.1 if settings.ENVIRONMENT == "production" else 1.0,
        profiles_sample_rate=0.1,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            AsyncioIntegration(),
            SqlalchemyIntegration(),
            RedisIntegration(),
            CeleryIntegration(),
        ],
        # Don't send PII
        send_default_pii=False,
        # Filter sensitive data
        before_send=filter_sensitive_data,
    )


def filter_sensitive_data(event, hint):
    """Filter sensitive data from Sentry events."""
    # Remove sensitive headers
    if "request" in event and "headers" in event["request"]:
        headers = event["request"]["headers"]
        sensitive_headers = ["authorization", "cookie", "x-api-key"]
        for header in sensitive_headers:
            if header in headers:
                headers[header] = "[FILTERED]"

    # Remove sensitive query params
    if "request" in event and "query_string" in event["request"]:
        query = event["request"]["query_string"]
        if "password" in query or "token" in query:
            event["request"]["query_string"] = "[FILTERED]"

    return event


def capture_exception(exception: Exception, **extra) -> None:
    """Capture exception with additional context."""
    with sentry_sdk.push_scope() as scope:
        for key, value in extra.items():
            scope.set_extra(key, value)
        sentry_sdk.capture_exception(exception)


def set_user_context(user_id: int, email: str) -> None:
    """Set user context for Sentry."""
    sentry_sdk.set_user({
        "id": str(user_id),
        "email": email,
    })
```

### Grafana Dashboard - Complete Configuration

```json
{
  "dashboard": {
    "uid": "fastapi-app",
    "title": "FastAPI Application Dashboard",
    "tags": ["fastapi", "api", "monitoring"],
    "timezone": "browser",
    "refresh": "30s",
    "schemaVersion": 38,
    "panels": [
      {
        "id": 1,
        "title": "Request Rate (RPS)",
        "type": "timeseries",
        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8},
        "targets": [
          {
            "expr": "sum(rate(http_requests_total[5m])) by (method)",
            "legendFormat": "{{method}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "reqps",
            "custom": {"lineWidth": 2, "fillOpacity": 10}
          }
        }
      },
      {
        "id": 2,
        "title": "Request Latency Percentiles",
        "type": "timeseries",
        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8},
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "p50"
          },
          {
            "expr": "histogram_quantile(0.90, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "p90"
          },
          {
            "expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "p99"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "s",
            "custom": {"lineWidth": 2}
          }
        }
      },
      {
        "id": 3,
        "title": "Error Rate (%)",
        "type": "timeseries",
        "gridPos": {"x": 0, "y": 8, "w": 8, "h": 6},
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{status_code=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m])) * 100",
            "legendFormat": "5xx Error Rate"
          },
          {
            "expr": "sum(rate(http_requests_total{status_code=~\"4..\"}[5m])) / sum(rate(http_requests_total[5m])) * 100",
            "legendFormat": "4xx Error Rate"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 1},
                {"color": "red", "value": 5}
              ]
            }
          }
        }
      },
      {
        "id": 4,
        "title": "Active DB Connections",
        "type": "gauge",
        "gridPos": {"x": 8, "y": 8, "w": 4, "h": 6},
        "targets": [
          {"expr": "db_connections_active"}
        ],
        "fieldConfig": {
          "defaults": {
            "min": 0,
            "max": 100,
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 70},
                {"color": "red", "value": 90}
              ]
            }
          }
        }
      },
      {
        "id": 5,
        "title": "Cache Hit Rate (%)",
        "type": "gauge",
        "gridPos": {"x": 12, "y": 8, "w": 4, "h": 6},
        "targets": [
          {
            "expr": "sum(rate(cache_hits_total[5m])) / (sum(rate(cache_hits_total[5m])) + sum(rate(cache_misses_total[5m]))) * 100"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 0,
            "max": 100,
            "thresholds": {
              "steps": [
                {"color": "red", "value": null},
                {"color": "yellow", "value": 70},
                {"color": "green", "value": 90}
              ]
            }
          }
        }
      },
      {
        "id": 6,
        "title": "Requests In Progress",
        "type": "stat",
        "gridPos": {"x": 16, "y": 8, "w": 4, "h": 6},
        "targets": [
          {"expr": "sum(http_requests_in_progress)"}
        ],
        "fieldConfig": {
          "defaults": {"unit": "none"}
        }
      },
      {
        "id": 7,
        "title": "Active Users",
        "type": "stat",
        "gridPos": {"x": 20, "y": 8, "w": 4, "h": 6},
        "targets": [
          {"expr": "active_users"}
        ],
        "fieldConfig": {
          "defaults": {"unit": "none", "color": {"mode": "thresholds"}}
        }
      },
      {
        "id": 8,
        "title": "DB Query Latency by Operation",
        "type": "timeseries",
        "gridPos": {"x": 0, "y": 14, "w": 12, "h": 6},
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(db_query_duration_seconds_bucket[5m])) by (operation)",
            "legendFormat": "{{operation}} p95"
          }
        ],
        "fieldConfig": {
          "defaults": {"unit": "s"}
        }
      },
      {
        "id": 9,
        "title": "Top Endpoints by Latency",
        "type": "table",
        "gridPos": {"x": 12, "y": 14, "w": 12, "h": 6},
        "targets": [
          {
            "expr": "topk(10, histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) by (endpoint))",
            "format": "table",
            "instant": true
          }
        ],
        "transformations": [
          {"id": "organize", "options": {"renameByName": {"Value": "p99 Latency (s)"}}}
        ]
      },
      {
        "id": 10,
        "title": "User Registrations",
        "type": "timeseries",
        "gridPos": {"x": 0, "y": 20, "w": 12, "h": 6},
        "targets": [
          {
            "expr": "increase(user_registrations_total[1h])",
            "legendFormat": "Registrations/hour"
          }
        ]
      },
      {
        "id": 11,
        "title": "Status Code Distribution",
        "type": "piechart",
        "gridPos": {"x": 12, "y": 20, "w": 6, "h": 6},
        "targets": [
          {
            "expr": "sum by (status_code) (increase(http_requests_total[1h]))",
            "legendFormat": "{{status_code}}"
          }
        ]
      },
      {
        "id": 12,
        "title": "Memory Usage",
        "type": "timeseries",
        "gridPos": {"x": 18, "y": 20, "w": 6, "h": 6},
        "targets": [
          {
            "expr": "process_resident_memory_bytes / 1024 / 1024",
            "legendFormat": "RSS (MB)"
          }
        ],
        "fieldConfig": {
          "defaults": {"unit": "decmbytes"}
        }
      }
    ],
    "templating": {
      "list": [
        {
          "name": "environment",
          "type": "custom",
          "options": [
            {"text": "production", "value": "production"},
            {"text": "staging", "value": "staging"}
          ],
          "current": {"text": "production", "value": "production"}
        }
      ]
    },
    "annotations": {
      "list": [
        {
          "name": "Deployments",
          "datasource": "Prometheus",
          "expr": "changes(app_info[5m]) > 0",
          "enable": true,
          "iconColor": "blue"
        }
      ]
    }
  }
}
```

### Key Grafana Queries Reference

| Metric | PromQL Query | Purpose |
|--------|--------------|---------|
| **RPS** | `sum(rate(http_requests_total[5m]))` | Requests per second |
| **p99 Latency** | `histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))` | 99th percentile latency |
| **Error Rate** | `sum(rate(http_requests_total{status_code=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100` | 5xx error percentage |
| **Apdex** | `(sum(rate(http_request_duration_seconds_bucket{le="0.5"}[5m])) + sum(rate(http_request_duration_seconds_bucket{le="2.0"}[5m])) / 2) / sum(rate(http_request_duration_seconds_count[5m]))` | User satisfaction score |
| **Cache Hit Rate** | `sum(rate(cache_hits_total[5m])) / (sum(rate(cache_hits_total[5m])) + sum(rate(cache_misses_total[5m]))) * 100` | Cache effectiveness |
| **Saturation** | `sum(http_requests_in_progress)` | Current load |

### Alert Rules

```yaml
# prometheus/alerts.yml
groups:
  - name: fastapi-alerts
    rules:
      - alert: HighErrorRate
        expr: sum(rate(http_requests_total{status_code=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected (>5%)"
          description: "Error rate is {{ $value | printf \"%.2f\" }}%"

      - alert: HighLatency
        expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High p99 latency (>2s)"

      - alert: DatabaseConnectionsHigh
        expr: db_connections_active > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Database connections above 80%"
```

### Environment Settings

```python
# Add to app/core/config.py

class Settings(BaseSettings):
    # ... existing settings ...

    # Logging
    LOG_LEVEL: str = "INFO"

    # OpenTelemetry
    OTEL_ENABLED: bool = False
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"

    # Sentry
    SENTRY_DSN: str | None = None
```

### Main App Integration

```python
# app/main.py
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.metrics import set_app_info, metrics_endpoint
from app.core.tracing import setup_tracing, instrument_app
from app.core.sentry import setup_sentry
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.metrics import MetricsMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan handler."""
    # Startup
    setup_logging()
    setup_tracing()
    setup_sentry()
    set_app_info(settings.VERSION, settings.ENVIRONMENT)

    yield

    # Shutdown
    pass


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        lifespan=lifespan,
    )

    # Add middleware
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(MetricsMiddleware)

    # Instrument for tracing
    instrument_app(app)

    # Add metrics endpoint
    app.add_route("/metrics", metrics_endpoint)

    # Include routers
    from app.api.health import router as health_router
    app.include_router(health_router)

    return app
```

---

## Grafana Datasource Provisioning

Grafana를 코드로 설정하여 재현 가능한 대시보드 환경을 구축합니다.

### Datasource 프로비저닝

```yaml
# grafana/provisioning/datasources/datasources.yaml
apiVersion: 1

datasources:
  # Prometheus - 메트릭
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
    jsonData:
      httpMethod: POST
      timeInterval: "15s"
      exemplarTraceIdDestinations:
        - name: traceID
          datasourceUid: tempo

  # Loki - 로그
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    editable: false
    jsonData:
      derivedFields:
        - datasourceUid: tempo
          matcherRegex: '"trace_id":"([^"]+)"'
          name: TraceID
          url: '$${__value.raw}'

  # Tempo - 트레이스
  - name: Tempo
    type: tempo
    access: proxy
    url: http://tempo:3200
    uid: tempo
    editable: false
    jsonData:
      tracesToLogs:
        datasourceUid: loki
        filterByTraceID: true
        filterBySpanID: true
      tracesToMetrics:
        datasourceUid: prometheus
        queries:
          - name: Request rate
            query: 'sum(rate(http_requests_total{$$__tags}[5m]))'

  # AlertManager
  - name: Alertmanager
    type: alertmanager
    access: proxy
    url: http://alertmanager:9093
    editable: false
    jsonData:
      implementation: prometheus
```

### Dashboard 프로비저닝

```yaml
# grafana/provisioning/dashboards/dashboards.yaml
apiVersion: 1

providers:
  - name: 'FastAPI Dashboards'
    orgId: 1
    folder: 'FastAPI'
    folderUid: 'fastapi'
    type: file
    disableDeletion: true
    editable: false
    options:
      path: /var/lib/grafana/dashboards/fastapi
```

### Docker Compose Grafana 설정

```yaml
# docker-compose.monitoring.yml
services:
  grafana:
    image: grafana/grafana:11.0.0
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
      - ./grafana/dashboards:/var/lib/grafana/dashboards
    depends_on:
      - prometheus
      - loki
      - tempo
```

---

## AlertManager Configuration

Prometheus 알림을 라우팅하고 그룹화하여 전달합니다.

### AlertManager 설정

```yaml
# alertmanager/alertmanager.yml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alertmanager@example.com'
  smtp_auth_username: 'alertmanager@example.com'
  smtp_auth_password: '${SMTP_PASSWORD}'

  slack_api_url: '${SLACK_WEBHOOK_URL}'

# 라우팅 규칙
route:
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'default-receiver'

  routes:
    # Critical 알림 → PagerDuty + Slack
    - match:
        severity: critical
      receiver: 'critical-receiver'
      group_wait: 10s
      repeat_interval: 1h

    # Warning 알림 → Slack만
    - match:
        severity: warning
      receiver: 'warning-receiver'
      repeat_interval: 4h

    # DB 관련 알림 → DBA팀
    - match_re:
        alertname: 'Database.*'
      receiver: 'dba-team'

# 억제 규칙 (중복 알림 방지)
inhibit_rules:
  # Critical 발생 시 Warning 억제
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'instance']

# 수신자 정의
receivers:
  - name: 'default-receiver'
    slack_configs:
      - channel: '#alerts-default'
        send_resolved: true
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

  - name: 'critical-receiver'
    slack_configs:
      - channel: '#alerts-critical'
        send_resolved: true
        color: '{{ if eq .Status "firing" }}danger{{ else }}good{{ end }}'
        title: '🚨 CRITICAL: {{ .GroupLabels.alertname }}'
        text: |
          {{ range .Alerts }}
          *Summary:* {{ .Annotations.summary }}
          *Description:* {{ .Annotations.description }}
          *Runbook:* {{ .Annotations.runbook_url }}
          {{ end }}
    pagerduty_configs:
      - service_key: '${PAGERDUTY_SERVICE_KEY}'
        severity: critical
        description: '{{ .GroupLabels.alertname }}'

  - name: 'warning-receiver'
    slack_configs:
      - channel: '#alerts-warning'
        send_resolved: true
        color: 'warning'
        title: '⚠️ WARNING: {{ .GroupLabels.alertname }}'

  - name: 'dba-team'
    email_configs:
      - to: 'dba-team@example.com'
        send_resolved: true
    slack_configs:
      - channel: '#dba-alerts'
```

### Prometheus Alert Rules 확장

```yaml
# prometheus/rules/fastapi-alerts.yml
groups:
  - name: fastapi.rules
    rules:
      # SLO: 99.9% 가용성
      - alert: HighErrorRateCritical
        expr: |
          (
            sum(rate(http_requests_total{status_code=~"5.."}[5m]))
            / sum(rate(http_requests_total[5m]))
          ) > 0.001
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "에러율이 SLO(99.9%)를 초과했습니다"
          description: "현재 에러율: {{ $value | humanizePercentage }}"
          runbook_url: "https://runbooks.example.com/high-error-rate"

      # SLO: P99 latency < 500ms
      - alert: HighLatencyCritical
        expr: |
          histogram_quantile(0.99,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
          ) > 0.5
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "P99 레이턴시가 500ms를 초과했습니다"
          description: "현재 P99: {{ $value | humanizeDuration }}"

      # DB 연결 고갈 예방
      - alert: DatabaseConnectionsHigh
        expr: db_connections_active > 0.8 * db_connections_max
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "DB 연결이 80%를 초과했습니다"
          description: "활성 연결: {{ $value }}"

      # Pod 재시작 감지
      - alert: PodRestartingFrequently
        expr: |
          increase(kube_pod_container_status_restarts_total{
            container="api"
          }[1h]) > 3
        labels:
          severity: warning
        annotations:
          summary: "Pod가 1시간 내 3회 이상 재시작됨"
          description: "Pod {{ $labels.pod }}가 빈번하게 재시작되고 있습니다"
```

---

## Loki Log Aggregation

Grafana Loki를 사용한 로그 집계 및 쿼리입니다.

### Loki 설정

```yaml
# loki/loki-config.yaml
auth_enabled: false

server:
  http_listen_port: 3100

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2024-01-01
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h

limits_config:
  # 로그 볼륨 제한
  ingestion_rate_mb: 10
  ingestion_burst_size_mb: 20
  max_streams_per_user: 10000
  max_entries_limit_per_query: 5000

  # 보존 기간
  retention_period: 168h  # 7일

# 압축 설정
compactor:
  working_directory: /loki/compactor
  shared_store: filesystem
  compaction_interval: 10m
  retention_enabled: true
  retention_delete_delay: 2h
```

### Promtail (로그 수집기) 설정

```yaml
# promtail/promtail-config.yaml
server:
  http_listen_port: 9080

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  # Kubernetes Pod 로그
  - job_name: kubernetes-pods
    kubernetes_sd_configs:
      - role: pod
    pipeline_stages:
      # JSON 로그 파싱
      - json:
          expressions:
            level: level
            message: event
            request_id: request_id
            trace_id: trace_id
      # 레이블 추출
      - labels:
          level:
          request_id:
          trace_id:
      # 타임스탬프 파싱
      - timestamp:
          source: timestamp
          format: RFC3339Nano
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        target_label: app
      - source_labels: [__meta_kubernetes_namespace]
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod

  # FastAPI 앱 로그 (Docker 환경)
  - job_name: fastapi-app
    static_configs:
      - targets:
          - localhost
        labels:
          job: fastapi-app
          __path__: /var/log/fastapi/*.log
    pipeline_stages:
      - json:
          expressions:
            level: level
            message: event
            request_id: request_id
            duration_ms: duration_ms
      - labels:
          level:
      - metrics:
          log_lines_total:
            type: Counter
            description: "Total log lines"
            source: level
            config:
              action: inc
```

### LogQL 쿼리 예시

```promql
# 최근 에러 로그
{app="fastapi-app"} |= "error" | json

# 특정 request_id로 추적
{app="fastapi-app"} | json | request_id="abc-123"

# 느린 요청 (>1초)
{app="fastapi-app"} | json | duration_ms > 1000

# 에러율 계산 (분당)
sum(rate({app="fastapi-app"} | json | level="ERROR" [1m]))

# 상위 10개 에러 메시지
topk(10, sum by (message) (count_over_time({app="fastapi-app"} | json | level="ERROR" [1h])))

# Trace ID로 로그-트레이스 연결
{app="fastapi-app"} | json | trace_id="abc123"
```

### Python 로그 → Loki 연동

```python
# app/core/logging.py 에 추가
import logging_loki

def setup_loki_handler() -> None:
    """Loki로 로그 전송 설정."""
    if not settings.LOKI_URL:
        return

    handler = logging_loki.LokiHandler(
        url=f"{settings.LOKI_URL}/loki/api/v1/push",
        tags={"app": settings.PROJECT_NAME, "environment": settings.ENVIRONMENT},
        version="1",
    )

    # structlog와 함께 사용
    logging.getLogger().addHandler(handler)
```

---

## Observability Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| Logging | structlog + Loki | Structured JSON logs + 집계 |
| Metrics | Prometheus | Time-series metrics |
| Tracing | OpenTelemetry + Tempo | Distributed tracing |
| Errors | Sentry | Error tracking |
| Visualization | Grafana | Unified dashboards |
| Alerting | AlertManager | Alert routing & grouping |

### 통합 아키텍처

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Grafana                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │ Dashboards  │  │   Alerts    │  │  Explore    │  │  Unified   │ │
│  │             │  │             │  │  (Logs/     │  │  Alerting  │ │
│  │             │  │             │  │   Traces)   │  │            │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬──────┘ │
└─────────┼────────────────┼────────────────┼───────────────┼────────┘
          │                │                │               │
          ▼                ▼                ▼               ▼
   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐
   │ Prometheus  │  │AlertManager │  │    Loki     │  │   Tempo    │
   │  (Metrics)  │  │  (Routing)  │  │   (Logs)    │  │  (Traces)  │
   └──────┬──────┘  └─────────────┘  └──────┬──────┘  └─────┬──────┘
          │                                  │               │
          └──────────────┬───────────────────┴───────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   FastAPI App       │
              │  ┌───────────────┐  │
              │  │ /metrics      │──┼──▶ Prometheus
              │  │ structlog     │──┼──▶ Loki (via Promtail)
              │  │ OpenTelemetry │──┼──▶ Tempo
              │  │ Sentry SDK    │──┼──▶ Sentry
              │  └───────────────┘  │
              └─────────────────────┘
```

## References

- `_references/DEPLOYMENT-PATTERN.md`
- `33-cicd/SKILL.md` - CI/CD와 Prometheus 연동
