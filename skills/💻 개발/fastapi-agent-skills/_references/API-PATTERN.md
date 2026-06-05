# API Pattern Reference

FastAPI 프로젝트의 API 설계 패턴 가이드입니다.

## REST API Conventions

### HTTP Methods

| Method | Action | Idempotent | Request Body |
|--------|--------|------------|--------------|
| GET | Read | Yes | No |
| POST | Create | No | Yes |
| PUT | Replace | Yes | Yes |
| PATCH | Update | Yes | Yes |
| DELETE | Delete | Yes | No |

### Status Codes

| Code | Meaning | Use Case |
|------|---------|----------|
| 200 | OK | Successful GET/PATCH/PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Missing/invalid auth |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Duplicate resource |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limited |
| 500 | Internal Server Error | Server error |

## URL Design

```
# Collection endpoints
GET    /api/v1/users              # List users
POST   /api/v1/users              # Create user

# Resource endpoints
GET    /api/v1/users/{id}         # Get user
PATCH  /api/v1/users/{id}         # Update user
DELETE /api/v1/users/{id}         # Delete user

# Nested resources
GET    /api/v1/users/{id}/orders  # User's orders
POST   /api/v1/users/{id}/orders  # Create order for user

# Actions (when REST verbs don't fit)
POST   /api/v1/users/{id}/activate
POST   /api/v1/orders/{id}/cancel
```

## Response Format

### Success Response

```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  },
  "message": "User created successfully",
  "meta": {
    "timestamp": "2025-01-11T12:00:00Z",
    "request_id": "uuid",
    "version": "1.0"
  }
}
```

### Paginated Response

```json
{
  "success": true,
  "data": [
    {"id": 1, "name": "Item 1"},
    {"id": 2, "name": "Item 2"}
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
    "timestamp": "2025-01-11T12:00:00Z"
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
    "field": null
  },
  "errors": [
    {
      "code": "VAL_001",
      "message": "field required",
      "field": "body.email"
    }
  ],
  "meta": {
    "timestamp": "2025-01-11T12:00:00Z",
    "request_id": "uuid"
  }
}
```

## Query Parameters

### Offset Pagination

```python
# GET /api/v1/users?page=1&size=20
@router.get("")
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    offset = (page - 1) * size
    # ...
```

### Cursor Pagination (Recommended for Large Datasets)

Cursor-based pagination is more efficient than offset pagination for large datasets
because it doesn't need to count skipped rows.

```python
# app/schemas/pagination.py
from pydantic import BaseModel, Field


class CursorPaginationParams(BaseModel):
    """Cursor pagination query parameters."""

    cursor: str | None = Field(
        None,
        description="Opaque cursor for next page (from previous response)",
    )
    limit: int = Field(20, ge=1, le=100, description="Items per page")


class CursorPageResponse[T](BaseModel):
    """Cursor-paginated response."""

    items: list[T]
    next_cursor: str | None = Field(
        None,
        description="Cursor for next page, null if no more pages",
    )
    has_more: bool
```

```python
# app/api/v1/routes/items.py
import base64
import json
from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.pagination import CursorPageResponse


@router.get("", response_model=CursorPageResponse[ItemResponse])
async def list_items(
    session: Session,
    cursor: Annotated[str | None, Query(description="Pagination cursor")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """List items with cursor pagination.

    Cursor encodes: {"id": last_id, "created_at": "2025-01-01T00:00:00Z"}
    """
    query = select(ItemModel).order_by(
        ItemModel.created_at.desc(),
        ItemModel.id.desc(),  # Secondary sort for stable ordering
    )

    # Decode cursor and apply WHERE clause
    if cursor:
        try:
            decoded = json.loads(base64.b64decode(cursor).decode())
            last_id = decoded["id"]
            last_created = decoded["created_at"]

            # Use tuple comparison for efficient cursor query
            query = query.where(
                (ItemModel.created_at, ItemModel.id) < (last_created, last_id)
            )
        except (ValueError, KeyError):
            pass  # Invalid cursor, start from beginning

    # Fetch limit + 1 to check if more pages exist
    query = query.limit(limit + 1)
    result = await session.execute(query)
    items = list(result.scalars().all())

    # Check if there are more items
    has_more = len(items) > limit
    items = items[:limit]

    # Generate next cursor from last item
    next_cursor = None
    if has_more and items:
        last_item = items[-1]
        cursor_data = {
            "id": last_item.id,
            "created_at": last_item.created_at.isoformat(),
        }
        next_cursor = base64.b64encode(
            json.dumps(cursor_data).encode()
        ).decode()

    return CursorPageResponse(
        items=[ItemResponse.model_validate(item) for item in items],
        next_cursor=next_cursor,
        has_more=has_more,
    )
```

**Cursor Response Example:**

```json
{
  "items": [
    {"id": 100, "name": "Item 100", "created_at": "2025-01-10T12:00:00Z"},
    {"id": 99, "name": "Item 99", "created_at": "2025-01-10T11:00:00Z"}
  ],
  "next_cursor": "eyJpZCI6IDk5LCAiY3JlYXRlZF9hdCI6ICIyMDI1LTAxLTEwVDExOjAwOjAwWiJ9",
  "has_more": true
}
```

**When to Use Each:**

| Type | Use Case | Pros | Cons |
|------|----------|------|------|
| **Offset** | Small datasets, admin panels | Simple, random access | Slow for large datasets |
| **Cursor** | Large datasets, infinite scroll | Consistent, fast | No random page access |

### Filtering

```python
# GET /api/v1/users?is_active=true&role=admin
@router.get("")
async def list_users(
    is_active: bool | None = Query(None, description="Filter by active status"),
    role: str | None = Query(None, description="Filter by role"),
):
    # ...
```

### Sorting

```python
# GET /api/v1/users?sort=-created_at,name
@router.get("")
async def list_users(
    sort: str | None = Query(
        None,
        description="Sort fields (prefix with - for desc)",
        example="-created_at,name",
    ),
):
    # Parse: -created_at -> (created_at, DESC)
    # ...
```

### Search

```python
# GET /api/v1/users?search=john
@router.get("")
async def list_users(
    search: str | None = Query(
        None,
        min_length=1,
        max_length=100,
        description="Search in name and email",
    ),
):
    # ...
```

## Versioning

### URL Path Versioning (Recommended)

```python
# app/api/router.py
from app.api.v1.router import router as v1_router
from app.api.v2.router import router as v2_router

api_router.include_router(v1_router, prefix="/v1")
api_router.include_router(v2_router, prefix="/v2")
```

### Header Versioning

```python
@router.get("/users")
async def get_users(
    version: str = Header("1", alias="Accept-Version"),
):
    if version == "2":
        return v2_response()
    return v1_response()
```

## OpenAPI Documentation

```python
@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user with email and password.",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Invalid input"},
        409: {"description": "Email already exists"},
    },
)
async def create_user(
    user_in: Annotated[
        UserCreate,
        Body(
            openapi_examples={
                "basic": {
                    "summary": "Basic user",
                    "value": {
                        "email": "user@example.com",
                        "password": "SecurePass123!",
                        "name": "John Doe",
                    },
                },
            },
        ),
    ],
):
    """
    Create a new user.

    - **email**: Valid email address (required)
    - **password**: At least 8 characters (required)
    - **name**: User's full name (required)
    """
    pass
```

## Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, ...):
    ...
```

## Error Handling

```python
# app/core/exceptions.py
class AppException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code

class NotFoundError(AppException):
    def __init__(self, resource: str):
        super().__init__(
            code="RES_001",
            message=f"{resource} not found",
            status_code=404,
        )

# Usage
raise NotFoundError("User")
```

## HATEOAS (Optional)

```json
{
  "id": 1,
  "email": "user@example.com",
  "_links": {
    "self": {"href": "/api/v1/users/1"},
    "orders": {"href": "/api/v1/users/1/orders"},
    "update": {"href": "/api/v1/users/1", "method": "PATCH"},
    "delete": {"href": "/api/v1/users/1", "method": "DELETE"}
  }
}
```

## Best Practices

| Practice | Description |
|----------|-------------|
| **Consistent naming** | Use plural nouns for collections |
| **Use query params** | For filtering, sorting, pagination |
| **Meaningful status codes** | Match HTTP semantics |
| **Error codes** | Machine-readable error codes |
| **Versioning** | Plan for API evolution |
| **Documentation** | Comprehensive OpenAPI docs |

## Related Skills

- `25-openapi-docs`: API documentation
- `26-api-versioning`: Version management
- `27-response-design`: Response format
