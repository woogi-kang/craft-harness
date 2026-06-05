---
name: error-handling
description: |
  예외 처리 및 HTTP Exception handlers를 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Error Handling Skill

예외 처리 및 HTTP Exception handlers를 구현합니다.

## Triggers

- "에러 처리", "예외 처리", "error handling", "exception"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |

---

## Output

### Error Codes

```python
# app/core/error_codes.py
from enum import Enum


class ErrorCode(str, Enum):
    """Standardized error codes.

    Categories:
    - AUTH_xxx: Authentication errors (401)
    - AUTHZ_xxx: Authorization errors (403)
    - VAL_xxx: Validation errors (422)
    - RES_xxx: Resource errors (404, 409)
    - RATE_xxx: Rate limiting (429)
    - SRV_xxx: Server errors (500, 503)
    - BIZ_xxx: Business logic errors (400)
    """

    # Authentication errors (1xxx)
    AUTHENTICATION_REQUIRED = "AUTH_001"
    INVALID_CREDENTIALS = "AUTH_002"
    TOKEN_EXPIRED = "AUTH_003"
    TOKEN_INVALID = "AUTH_004"
    REFRESH_TOKEN_EXPIRED = "AUTH_005"

    # Authorization errors (2xxx)
    PERMISSION_DENIED = "AUTHZ_001"
    INSUFFICIENT_PERMISSIONS = "AUTHZ_002"
    RESOURCE_FORBIDDEN = "AUTHZ_003"

    # Validation errors (3xxx)
    VALIDATION_ERROR = "VAL_001"
    INVALID_INPUT = "VAL_002"
    MISSING_FIELD = "VAL_003"
    INVALID_FORMAT = "VAL_004"

    # Resource errors (4xxx)
    NOT_FOUND = "RES_001"
    ALREADY_EXISTS = "RES_002"
    CONFLICT = "RES_003"
    GONE = "RES_004"

    # Rate limiting (5xxx)
    RATE_LIMIT_EXCEEDED = "RATE_001"
    QUOTA_EXCEEDED = "RATE_002"

    # Server errors (6xxx)
    INTERNAL_ERROR = "SRV_001"
    SERVICE_UNAVAILABLE = "SRV_002"
    DATABASE_ERROR = "SRV_003"
    EXTERNAL_SERVICE_ERROR = "SRV_004"

    # Business logic errors (7xxx)
    BUSINESS_RULE_VIOLATION = "BIZ_001"
    INVALID_STATE = "BIZ_002"
    OPERATION_NOT_ALLOWED = "BIZ_003"
```

### Custom Exceptions

```python
# app/core/exceptions.py
from typing import Any

from app.core.error_codes import ErrorCode


class AppException(Exception):
    """Base exception for application errors."""

    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        status_code: int = 400,
        field: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.field = field
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(AppException):
    """Resource not found error."""

    def __init__(
        self,
        resource: str,
        identifier: Any = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        message = f"{resource} not found"
        if identifier is not None:
            message = f"{resource} not found: {identifier}"
        super().__init__(
            message=message,
            code=ErrorCode.NOT_FOUND,
            status_code=404,
            details=details or {"resource": resource, "identifier": str(identifier) if identifier else None},
        )


class AlreadyExistsError(AppException):
    """Resource already exists error."""

    def __init__(
        self,
        resource: str,
        identifier: Any,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=f"{resource} already exists: {identifier}",
            code=ErrorCode.ALREADY_EXISTS,
            status_code=409,
            details=details or {"resource": resource, "identifier": str(identifier)},
        )


class ValidationError(AppException):
    """Validation error."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=ErrorCode.VALIDATION_ERROR,
            status_code=422,
            field=field,
            details=details or {},
        )


class AuthenticationError(AppException):
    """Authentication error."""

    def __init__(
        self,
        message: str = "Authentication failed",
        code: ErrorCode = ErrorCode.AUTHENTICATION_REQUIRED,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=401,
            details=details or {},
        )


class AuthorizationError(AppException):
    """Authorization error."""

    def __init__(
        self,
        message: str = "Permission denied",
        code: ErrorCode = ErrorCode.PERMISSION_DENIED,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=403,
            details=details or {},
        )


class RateLimitError(AppException):
    """Rate limit exceeded error."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=ErrorCode.RATE_LIMIT_EXCEEDED,
            status_code=429,
            details=details or {"retry_after": retry_after} if retry_after else details or {},
        )


class ExternalServiceError(AppException):
    """External service error."""

    def __init__(
        self,
        service: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=f"{service}: {message}",
            code=ErrorCode.EXTERNAL_SERVICE_ERROR,
            status_code=503,
            details=details or {"service": service},
        )
```

### Error Response Schema

```python
# app/schemas/error.py
from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Error detail schema."""

    code: str = Field(description="Error code (e.g., VAL_001)")
    message: str = Field(description="Human-readable error message")
    field: str | None = Field(default=None, description="Field that caused the error")
    details: dict[str, Any] | None = Field(default=None, description="Additional details")


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    success: bool = False
    error: ErrorDetail = Field(description="Primary error information")
    errors: list[ErrorDetail] | None = Field(
        default=None,
        description="Multiple errors (for validation)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": False,
                    "error": {
                        "code": "RES_001",
                        "message": "User not found: 123",
                        "field": None,
                        "details": {"resource": "User", "identifier": "123"},
                    },
                    "errors": None,
                },
                {
                    "success": False,
                    "error": {
                        "code": "VAL_001",
                        "message": "Validation failed",
                        "field": None,
                        "details": None,
                    },
                    "errors": [
                        {"code": "VAL_001", "message": "Invalid email format", "field": "email", "details": None},
                        {"code": "VAL_001", "message": "Password too short", "field": "password", "details": None},
                    ],
                },
            ]
        }
    }
```

### Exception Handlers

```python
# app/api/exception_handlers.py
import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from app.core.error_codes import ErrorCode
from app.core.exceptions import AppException
from app.schemas.error import ErrorResponse, ErrorDetail

logger = structlog.get_logger()


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup exception handlers for the application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request,
        exc: AppException,
    ) -> JSONResponse:
        """Handle application exceptions."""
        await logger.awarning(
            "Application exception",
            error_code=exc.code.value,
            message=exc.message,
            details=exc.details,
            path=str(request.url),
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=ErrorDetail(
                    code=exc.code.value,
                    message=exc.message,
                    field=exc.field,
                    details=exc.details if exc.details else None,
                ),
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Handle request validation errors."""
        errors = [
            ErrorDetail(
                code=ErrorCode.VALIDATION_ERROR.value,
                message=error["msg"],
                field=".".join(str(loc) for loc in error["loc"]),
                details={"type": error["type"]},
            )
            for error in exc.errors()
        ]

        await logger.awarning(
            "Validation error",
            errors=[e.model_dump() for e in errors],
            path=str(request.url),
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.VALIDATION_ERROR.value,
                    message="Request validation failed",
                ),
                errors=errors,
            ).model_dump(),
        )

    @app.exception_handler(PydanticValidationError)
    async def pydantic_validation_exception_handler(
        request: Request,
        exc: PydanticValidationError,
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        errors = [
            ErrorDetail(
                code=ErrorCode.VALIDATION_ERROR.value,
                message=error["msg"],
                field=".".join(str(loc) for loc in error["loc"]),
            )
            for error in exc.errors()
        ]

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.VALIDATION_ERROR.value,
                    message="Data validation failed",
                ),
                errors=errors,
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle unhandled exceptions."""
        await logger.aexception(
            "Unhandled exception",
            exc_info=exc,
            path=str(request.url),
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR.value,
                    message="An unexpected error occurred",
                ),
            ).model_dump(),
        )
```

### main.py에 등록

```python
# app/main.py
from fastapi import FastAPI

from app.api.exception_handlers import setup_exception_handlers


def create_app() -> FastAPI:
    app = FastAPI(...)

    # Setup exception handlers
    setup_exception_handlers(app)

    return app
```

### 사용 예시

```python
# app/application/services/user.py
from app.core.exceptions import NotFoundError, AlreadyExistsError


class UserService:
    async def get_by_id(self, user_id: int) -> UserEntity:
        user = await self._repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(resource="User", identifier=user_id)
        return user

    async def create(self, user_in: UserCreate) -> UserEntity:
        existing = await self._repository.get_by_email(user_in.email)
        if existing:
            raise AlreadyExistsError(resource="User", identifier=user_in.email)
        return await self._repository.create(...)
```

## References

- `_references/API-PATTERN.md`
