---
name: openapi-docs
description: |
  Swagger UI, ReDoc을 활용한 API 문서화를 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# OpenAPI Documentation Skill

Swagger UI, ReDoc을 활용한 API 문서화를 구현합니다.

## Triggers

- "API 문서", "openapi", "swagger", "redoc", "문서화"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |

---

## Output

### OpenAPI Configuration

```python
# app/core/openapi.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.core.config import settings


def custom_openapi(app: FastAPI) -> dict:
    """Generate custom OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        routes=app.routes,
        servers=[
            {"url": "/", "description": "Current server"},
            {"url": "https://api.example.com", "description": "Production"},
            {"url": "https://staging-api.example.com", "description": "Staging"},
        ],
    )

    # Custom logo
    openapi_schema["info"]["x-logo"] = {
        "url": "https://example.com/logo.png",
        "altText": settings.PROJECT_NAME,
    }

    # Security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT Bearer token authentication",
        },
        "apiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API Key authentication",
        },
        "oauth2": {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": "/api/v1/auth/authorize",
                    "tokenUrl": "/api/v1/auth/token",
                    "scopes": {
                        "read": "Read access",
                        "write": "Write access",
                        "admin": "Admin access",
                    },
                },
            },
        },
    }

    # Tags with descriptions
    openapi_schema["tags"] = [
        {
            "name": "auth",
            "description": "Authentication endpoints",
            "externalDocs": {
                "description": "Auth documentation",
                "url": "https://docs.example.com/auth",
            },
        },
        {
            "name": "users",
            "description": "User management endpoints",
        },
        {
            "name": "health",
            "description": "Health check endpoints",
        },
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


def setup_openapi(app: FastAPI) -> None:
    """Setup custom OpenAPI schema."""
    app.openapi = lambda: custom_openapi(app)
```

### FastAPI App Configuration

```python
# app/main.py
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.openapi import setup_openapi


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        # Disable default docs to customize
        docs_url=None if settings.ENVIRONMENT == "production" else "/docs",
        redoc_url=None if settings.ENVIRONMENT == "production" else "/redoc",
        openapi_url=None if settings.ENVIRONMENT == "production" else "/openapi.json",
        # Contact and license info
        contact={
            "name": "API Support",
            "url": "https://support.example.com",
            "email": "api@example.com",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        # Terms of service
        terms_of_service="https://example.com/terms",
    )

    # Setup custom OpenAPI
    setup_openapi(app)

    return app
```

### Custom Swagger UI

```python
# app/api/docs.py
from fastapi import APIRouter, Request
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
    get_redoc_html,
)
from fastapi.responses import HTMLResponse

from app.core.config import settings

router = APIRouter(tags=["documentation"])


@router.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(request: Request) -> HTMLResponse:
    """Custom Swagger UI with additional configuration."""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{settings.PROJECT_NAME} - Swagger UI",
        oauth2_redirect_url="/docs/oauth2-redirect",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="https://example.com/favicon.ico",
        swagger_ui_parameters={
            "deepLinking": True,
            "persistAuthorization": True,
            "displayRequestDuration": True,
            "filter": True,
            "showExtensions": True,
            "showCommonExtensions": True,
            "syntaxHighlight.theme": "monokai",
            "docExpansion": "list",
            "defaultModelsExpandDepth": 3,
            "defaultModelExpandDepth": 3,
            "tryItOutEnabled": True,
        },
    )


@router.get("/docs/oauth2-redirect", include_in_schema=False)
async def swagger_ui_redirect() -> HTMLResponse:
    """OAuth2 redirect for Swagger UI."""
    return get_swagger_ui_oauth2_redirect_html()


@router.get("/redoc", include_in_schema=False)
async def redoc_html(request: Request) -> HTMLResponse:
    """ReDoc documentation."""
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=f"{settings.PROJECT_NAME} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js",
        redoc_favicon_url="https://example.com/favicon.ico",
        with_google_fonts=True,
    )
```

### Route Documentation Examples

```python
# app/api/v1/routes/users.py
from typing import Annotated

from fastapi import APIRouter, Path, Query, Body, status

from app.application.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserListResponse,
)
from app.api.v1.dependencies import CurrentUser, Session, Pagination

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "",
    response_model=UserListResponse,
    summary="List all users",
    description="""
    Retrieve a paginated list of users.

    **Permissions required:** `users:read`

    **Rate limit:** 100 requests per minute
    """,
    responses={
        200: {
            "description": "Successfully retrieved users",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "id": 1,
                                "email": "user@example.com",
                                "name": "John Doe",
                                "is_active": True,
                            }
                        ],
                        "total": 100,
                        "page": 1,
                        "size": 20,
                    }
                }
            },
        },
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
    },
)
async def list_users(
    session: Session,
    current_user: CurrentUser,
    pagination: Pagination,
    is_active: Annotated[
        bool | None,
        Query(
            description="Filter by active status",
            example=True,
        ),
    ] = None,
    search: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=100,
            description="Search in name and email",
            example="john",
        ),
    ] = None,
):
    """
    List users with pagination and optional filters.

    - **is_active**: Filter by user active status
    - **search**: Search in name and email fields
    """
    pass


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user account with the provided information.",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Invalid input data"},
        409: {"description": "Email already exists"},
    },
)
async def create_user(
    session: Session,
    current_user: CurrentUser,
    user_in: Annotated[
        UserCreate,
        Body(
            openapi_examples={
                "basic": {
                    "summary": "Basic user",
                    "description": "A basic user with minimal info",
                    "value": {
                        "email": "user@example.com",
                        "password": "SecurePass123!",
                        "name": "John Doe",
                    },
                },
                "full": {
                    "summary": "Full user",
                    "description": "A user with all optional fields",
                    "value": {
                        "email": "user@example.com",
                        "password": "SecurePass123!",
                        "name": "John Doe",
                        "phone": "+1-555-123-4567",
                        "is_active": True,
                    },
                },
            },
        ),
    ],
):
    """
    Create a new user.

    The password must meet the following requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    """
    pass


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    responses={
        200: {"description": "User found"},
        404: {"description": "User not found"},
    },
)
async def get_user(
    session: Session,
    current_user: CurrentUser,
    user_id: Annotated[
        int,
        Path(
            title="User ID",
            description="The unique identifier of the user",
            ge=1,
            example=1,
        ),
    ],
):
    """Get a specific user by their ID."""
    pass


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Partially update a user's information.",
    responses={
        200: {"description": "User updated successfully"},
        404: {"description": "User not found"},
        409: {"description": "Email already exists"},
    },
)
async def update_user(
    session: Session,
    current_user: CurrentUser,
    user_id: Annotated[int, Path(ge=1)],
    user_in: UserUpdate,
):
    """
    Update user information.

    Only the fields provided will be updated.
    """
    pass


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    responses={
        204: {"description": "User deleted successfully"},
        404: {"description": "User not found"},
    },
)
async def delete_user(
    session: Session,
    current_user: CurrentUser,
    user_id: Annotated[int, Path(ge=1)],
):
    """Delete a user by their ID."""
    pass
```

### Schema Documentation

```python
# app/application/schemas/user.py
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr = Field(
        description="User's email address",
        examples=["user@example.com"],
    )
    name: str = Field(
        min_length=1,
        max_length=100,
        description="User's full name",
        examples=["John Doe"],
    )


class UserCreate(UserBase):
    """Schema for creating a new user."""

    model_config = ConfigDict(
        json_schema_extra={
            "title": "Create User",
            "description": "Schema for creating a new user account",
        }
    )

    password: str = Field(
        min_length=8,
        max_length=128,
        description="User's password (min 8 chars, must include upper, lower, number, special)",
        examples=["SecurePass123!"],
    )
    phone: str | None = Field(
        default=None,
        pattern=r"^\+?[1-9]\d{1,14}$",
        description="Phone number in E.164 format",
        examples=["+1-555-123-4567"],
    )
    is_active: bool = Field(
        default=True,
        description="Whether the user account is active",
    )


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    model_config = ConfigDict(
        json_schema_extra={
            "title": "Update User",
            "description": "Schema for partially updating a user account",
        }
    )

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="User's full name",
    )
    phone: str | None = Field(
        default=None,
        pattern=r"^\+?[1-9]\d{1,14}$",
        description="Phone number in E.164 format",
    )
    is_active: bool | None = Field(
        default=None,
        description="Whether the user account is active",
    )


class UserResponse(UserBase):
    """Schema for user response."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "title": "User",
            "description": "User account information",
        },
    )

    id: int = Field(
        description="Unique user identifier",
        examples=[1],
    )
    is_active: bool = Field(
        description="Whether the user account is active",
    )
    created_at: datetime = Field(
        description="When the user was created",
    )
    updated_at: datetime = Field(
        description="When the user was last updated",
    )


class UserListResponse(BaseModel):
    """Paginated list of users."""

    items: list[UserResponse] = Field(
        description="List of users",
    )
    total: int = Field(
        description="Total number of users",
        examples=[100],
    )
    page: int = Field(
        description="Current page number",
        examples=[1],
    )
    size: int = Field(
        description="Number of items per page",
        examples=[20],
    )
```

### Error Response Documentation

```python
# app/application/schemas/errors.py
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Error detail for validation errors."""

    loc: list[str | int] = Field(
        description="Location of the error in the request",
        examples=[["body", "email"]],
    )
    msg: str = Field(
        description="Error message",
        examples=["field required"],
    )
    type: str = Field(
        description="Error type",
        examples=["value_error.missing"],
    )


class ValidationErrorResponse(BaseModel):
    """Validation error response."""

    detail: list[ErrorDetail] = Field(
        description="List of validation errors",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "detail": [
                    {
                        "loc": ["body", "email"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    }
                ]
            }
        }
    }


class HTTPErrorResponse(BaseModel):
    """HTTP error response."""

    detail: str = Field(
        description="Error message",
        examples=["Not found"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {"detail": "Not found"}
        }
    }
```

### OpenAPI Extensions

```python
# app/core/openapi_extensions.py
from typing import Any


def add_webhooks(openapi_schema: dict) -> dict:
    """Add webhook definitions to OpenAPI schema."""
    openapi_schema["webhooks"] = {
        "userCreated": {
            "post": {
                "summary": "User Created",
                "description": "Triggered when a new user is created",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "event": {"type": "string", "example": "user.created"},
                                    "data": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "email": {"type": "string"},
                                            "created_at": {"type": "string", "format": "date-time"},
                                        },
                                    },
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Webhook processed"},
                },
            }
        },
        "orderCompleted": {
            "post": {
                "summary": "Order Completed",
                "description": "Triggered when an order is completed",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "event": {"type": "string", "example": "order.completed"},
                                    "data": {
                                        "type": "object",
                                        "properties": {
                                            "order_id": {"type": "integer"},
                                            "total": {"type": "number"},
                                            "completed_at": {"type": "string", "format": "date-time"},
                                        },
                                    },
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Webhook processed"},
                },
            }
        },
    }
    return openapi_schema


def add_x_code_samples(openapi_schema: dict) -> dict:
    """Add code samples to operations."""
    # Example: Add code samples to a specific endpoint
    if "paths" in openapi_schema:
        for path, methods in openapi_schema["paths"].items():
            for method, operation in methods.items():
                if isinstance(operation, dict):
                    operation["x-codeSamples"] = [
                        {
                            "lang": "cURL",
                            "source": f'curl -X {method.upper()} "https://api.example.com{path}" \\\n  -H "Authorization: Bearer $TOKEN"',
                        },
                        {
                            "lang": "Python",
                            "source": f"""import httpx

response = httpx.{method}(
    "https://api.example.com{path}",
    headers={{"Authorization": f"Bearer {{token}}"}}
)
print(response.json())""",
                        },
                    ]
    return openapi_schema
```

### Environment Settings

```python
# Add to app/core/config.py

class Settings(BaseSettings):
    # ... existing settings ...

    # OpenAPI
    PROJECT_NAME: str = "FastAPI Application"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A modern FastAPI application"

    # Docs visibility
    DOCS_ENABLED: bool = True  # Set to False in production if needed
```

## Documentation Best Practices

| Practice | Description |
|----------|-------------|
| Summary | Short, concise operation summary (displayed in list) |
| Description | Detailed markdown description with examples |
| Examples | Multiple examples for different scenarios |
| Error Responses | Document all possible error codes |
| Tags | Group related endpoints |
| Deprecation | Mark deprecated endpoints with `deprecated=True` |

## References

- `_references/API-PATTERN.md`
