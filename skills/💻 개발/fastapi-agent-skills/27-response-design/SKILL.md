---
name: response-design
description: |
  일관된 API 응답 형식 및 에러 처리를 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Response Design Skill

일관된 API 응답 형식 및 에러 처리를 구현합니다.

## Triggers

- "응답 설계", "response design", "API 응답", "에러 응답", "pagination"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |

---

## Output

### Standard Response Wrapper

```python
# app/application/schemas/response.py
from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseMeta(BaseModel):
    """Response metadata."""

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Response timestamp in UTC",
    )
    request_id: str | None = Field(
        default=None,
        description="Unique request identifier for tracing",
    )
    version: str = Field(
        default="1.0",
        description="API version",
    )


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""

    success: bool = Field(
        default=True,
        description="Whether the request was successful",
    )
    data: T | None = Field(
        default=None,
        description="Response data",
    )
    message: str | None = Field(
        default=None,
        description="Human-readable message",
    )
    meta: ResponseMeta = Field(
        default_factory=ResponseMeta,
        description="Response metadata",
    )


class ErrorDetail(BaseModel):
    """Error detail information."""

    code: str = Field(
        description="Error code for programmatic handling",
        examples=["VALIDATION_ERROR"],
    )
    message: str = Field(
        description="Human-readable error message",
        examples=["Invalid input data"],
    )
    field: str | None = Field(
        default=None,
        description="Field that caused the error",
        examples=["email"],
    )
    details: dict[str, Any] | None = Field(
        default=None,
        description="Additional error details",
    )


class ErrorResponse(BaseModel):
    """Standard error response."""

    success: bool = Field(
        default=False,
        description="Always false for errors",
    )
    error: ErrorDetail = Field(
        description="Error information",
    )
    errors: list[ErrorDetail] | None = Field(
        default=None,
        description="Multiple errors (for validation)",
    )
    meta: ResponseMeta = Field(
        default_factory=ResponseMeta,
        description="Response metadata",
    )
```

### Pagination Response

```python
# app/application/schemas/pagination.py
from typing import Generic, TypeVar

from pydantic import BaseModel, Field, computed_field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination input parameters."""

    page: int = Field(
        default=1,
        ge=1,
        description="Page number (1-indexed)",
    )
    size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Items per page",
    )

    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.size


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int = Field(description="Current page number")
    size: int = Field(description="Items per page")
    total_items: int = Field(description="Total number of items")
    total_pages: int = Field(description="Total number of pages")

    @computed_field
    @property
    def has_next(self) -> bool:
        """Whether there is a next page."""
        return self.page < self.total_pages

    @computed_field
    @property
    def has_prev(self) -> bool:
        """Whether there is a previous page."""
        return self.page > 1


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    success: bool = Field(default=True)
    data: list[T] = Field(description="List of items")
    pagination: PaginationMeta = Field(description="Pagination info")
    meta: ResponseMeta = Field(default_factory=ResponseMeta)

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        size: int,
    ) -> "PaginatedResponse[T]":
        """Create paginated response."""
        total_pages = (total + size - 1) // size if size > 0 else 0

        return cls(
            data=items,
            pagination=PaginationMeta(
                page=page,
                size=size,
                total_items=total,
                total_pages=total_pages,
            ),
        )


class CursorPaginationMeta(BaseModel):
    """Cursor-based pagination metadata."""

    cursor: str | None = Field(
        description="Current cursor position",
    )
    next_cursor: str | None = Field(
        description="Cursor for next page",
    )
    has_more: bool = Field(
        description="Whether more items exist",
    )
    limit: int = Field(
        description="Items per page",
    )


class CursorPaginatedResponse(BaseModel, Generic[T]):
    """Cursor-based paginated response."""

    success: bool = Field(default=True)
    data: list[T] = Field(description="List of items")
    pagination: CursorPaginationMeta = Field(description="Cursor pagination info")
    meta: ResponseMeta = Field(default_factory=ResponseMeta)
```

### Error Codes

```python
# app/core/error_codes.py
from enum import Enum


class ErrorCode(str, Enum):
    """Standardized error codes."""

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

### Exception Classes

```python
# app/core/exceptions.py
from typing import Any

from app.core.error_codes import ErrorCode


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        status_code: int = 400,
        field: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.field = field
        self.details = details
        super().__init__(message)


class AuthenticationError(AppException):
    """Authentication error."""

    def __init__(
        self,
        message: str = "Authentication required",
        code: ErrorCode = ErrorCode.AUTHENTICATION_REQUIRED,
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=401,
        )


class AuthorizationError(AppException):
    """Authorization error."""

    def __init__(
        self,
        message: str = "Permission denied",
        code: ErrorCode = ErrorCode.PERMISSION_DENIED,
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=403,
        )


class NotFoundError(AppException):
    """Resource not found error."""

    def __init__(
        self,
        resource: str = "Resource",
        message: str | None = None,
    ):
        super().__init__(
            code=ErrorCode.NOT_FOUND,
            message=message or f"{resource} not found",
            status_code=404,
        )


class ConflictError(AppException):
    """Conflict error."""

    def __init__(
        self,
        message: str = "Resource conflict",
        field: str | None = None,
    ):
        super().__init__(
            code=ErrorCode.CONFLICT,
            message=message,
            status_code=409,
            field=field,
        )


class ValidationError(AppException):
    """Validation error."""

    def __init__(
        self,
        message: str = "Validation error",
        field: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            code=ErrorCode.VALIDATION_ERROR,
            message=message,
            status_code=422,
            field=field,
            details=details,
        )


class RateLimitError(AppException):
    """Rate limit exceeded error."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int | None = None,
    ):
        super().__init__(
            code=ErrorCode.RATE_LIMIT_EXCEEDED,
            message=message,
            status_code=429,
            details={"retry_after": retry_after} if retry_after else None,
        )
```

### Exception Handlers

```python
# app/core/exception_handlers.py
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from app.application.schemas.response import ErrorDetail, ErrorResponse, ResponseMeta
from app.core.error_codes import ErrorCode
from app.core.exceptions import AppException

import structlog

logger = structlog.get_logger()


async def app_exception_handler(
    request: Request,
    exc: AppException,
) -> JSONResponse:
    """Handle application exceptions."""
    await logger.awarning(
        "Application error",
        error_code=exc.code,
        message=exc.message,
        path=request.url.path,
    )

    response = ErrorResponse(
        error=ErrorDetail(
            code=exc.code.value,
            message=exc.message,
            field=exc.field,
            details=exc.details,
        ),
        meta=ResponseMeta(
            request_id=request.state.request_id
            if hasattr(request.state, "request_id")
            else None,
        ),
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(mode="json"),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append(
            ErrorDetail(
                code=ErrorCode.VALIDATION_ERROR.value,
                message=error["msg"],
                field=field,
                details={"type": error["type"]},
            )
        )

    response = ErrorResponse(
        error=ErrorDetail(
            code=ErrorCode.VALIDATION_ERROR.value,
            message="Validation failed",
        ),
        errors=errors,
        meta=ResponseMeta(
            request_id=request.state.request_id
            if hasattr(request.state, "request_id")
            else None,
        ),
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response.model_dump(mode="json"),
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle unexpected exceptions."""
    await logger.aexception(
        "Unexpected error",
        path=request.url.path,
    )

    response = ErrorResponse(
        error=ErrorDetail(
            code=ErrorCode.INTERNAL_ERROR.value,
            message="An unexpected error occurred",
        ),
        meta=ResponseMeta(
            request_id=request.state.request_id
            if hasattr(request.state, "request_id")
            else None,
        ),
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response.model_dump(mode="json"),
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers."""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
```

### Response Helpers

```python
# app/api/response_helpers.py
from typing import Any, TypeVar

from fastapi import Response

from app.application.schemas.response import APIResponse, ResponseMeta
from app.application.schemas.pagination import PaginatedResponse, PaginationParams

T = TypeVar("T")


def success_response(
    data: T,
    message: str | None = None,
    request_id: str | None = None,
) -> APIResponse[T]:
    """Create a success response."""
    return APIResponse(
        success=True,
        data=data,
        message=message,
        meta=ResponseMeta(request_id=request_id),
    )


def created_response(
    data: T,
    message: str = "Resource created successfully",
    request_id: str | None = None,
) -> APIResponse[T]:
    """Create a 201 Created response."""
    return APIResponse(
        success=True,
        data=data,
        message=message,
        meta=ResponseMeta(request_id=request_id),
    )


def no_content_response() -> Response:
    """Create a 204 No Content response."""
    return Response(status_code=204)


def paginated_response(
    items: list[T],
    total: int,
    params: PaginationParams,
    request_id: str | None = None,
) -> PaginatedResponse[T]:
    """Create a paginated response."""
    response = PaginatedResponse.create(
        items=items,
        total=total,
        page=params.page,
        size=params.size,
    )
    response.meta.request_id = request_id
    return response
```

### Using Response Wrappers

```python
# app/api/v1/routes/users.py
from fastapi import APIRouter, status

from app.api.response_helpers import (
    success_response,
    created_response,
    no_content_response,
    paginated_response,
)
from app.api.v1.dependencies import CurrentUser, Session, Pagination
from app.application.schemas.response import APIResponse
from app.application.schemas.pagination import PaginatedResponse
from app.application.schemas.v1.user import UserCreate, UserResponse
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    session: Session,
    current_user: CurrentUser,
    pagination: Pagination,
):
    """List users with pagination."""
    users, total = await user_service.get_paginated(
        session,
        offset=pagination.offset,
        limit=pagination.size,
    )

    return paginated_response(
        items=users,
        total=total,
        params=pagination,
    )


@router.get("/{user_id}", response_model=APIResponse[UserResponse])
async def get_user(
    user_id: int,
    session: Session,
    current_user: CurrentUser,
):
    """Get user by ID."""
    user = await user_service.get_by_id(session, user_id)

    if not user:
        raise NotFoundError("User")

    return success_response(
        data=user,
        message="User retrieved successfully",
    )


@router.post(
    "",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_in: UserCreate,
    session: Session,
    current_user: CurrentUser,
):
    """Create a new user."""
    user = await user_service.create(session, user_in)

    return created_response(data=user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    session: Session,
    current_user: CurrentUser,
):
    """Delete a user."""
    await user_service.delete(session, user_id)
    return no_content_response()
```

### Request ID Middleware

```python
# app/middleware/request_id.py
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add request ID to each request."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response
```

### HATEOAS Links

```python
# app/application/schemas/links.py
from pydantic import BaseModel, Field


class Link(BaseModel):
    """HATEOAS link."""

    href: str = Field(description="URL of the link")
    rel: str = Field(description="Relationship type")
    method: str = Field(default="GET", description="HTTP method")


class LinkedResource(BaseModel):
    """Resource with HATEOAS links."""

    _links: dict[str, Link] = Field(
        default_factory=dict,
        description="HATEOAS links",
    )


# Example usage
class UserWithLinks(UserResponse, LinkedResource):
    """User with HATEOAS links."""

    @classmethod
    def from_user(cls, user: UserResponse, base_url: str) -> "UserWithLinks":
        return cls(
            **user.model_dump(),
            _links={
                "self": Link(
                    href=f"{base_url}/users/{user.id}",
                    rel="self",
                ),
                "update": Link(
                    href=f"{base_url}/users/{user.id}",
                    rel="update",
                    method="PATCH",
                ),
                "delete": Link(
                    href=f"{base_url}/users/{user.id}",
                    rel="delete",
                    method="DELETE",
                ),
            },
        )
```

## Response Format Examples

### Success Response

```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  },
  "message": "User retrieved successfully",
  "meta": {
    "timestamp": "2025-01-11T12:00:00Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "version": "1.0"
  }
}
```

### Paginated Response

```json
{
  "success": true,
  "data": [
    {"id": 1, "name": "User 1"},
    {"id": 2, "name": "User 2"}
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total_items": 100,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  },
  "meta": {
    "timestamp": "2025-01-11T12:00:00Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "VAL_001",
    "message": "Validation failed",
    "field": null,
    "details": null
  },
  "errors": [
    {
      "code": "VAL_001",
      "message": "field required",
      "field": "body.email",
      "details": {"type": "missing"}
    }
  ],
  "meta": {
    "timestamp": "2025-01-11T12:00:00Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

## References

- `_references/API-PATTERN.md`
