---
name: api-versioning
description: |
  URL Path, Header 기반 API 버저닝 전략을 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# API Versioning Skill

URL Path, Header 기반 API 버저닝 전략을 구현합니다.

## Triggers

- "API 버저닝", "versioning", "버전 관리", "v1/v2"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |
| `strategy` | ❌ | url/header (기본: url) |

---

## Output

### 1. URL Path Versioning (Recommended)

```python
# app/api/router.py
from fastapi import APIRouter

from app.api.v1.router import router as v1_router
from app.api.v2.router import router as v2_router

api_router = APIRouter()

# Mount versioned routers
api_router.include_router(v1_router, prefix="/v1")
api_router.include_router(v2_router, prefix="/v2")
```

### V1 Router

```python
# app/api/v1/router.py
from fastapi import APIRouter

from app.api.v1.routes import auth, users, items

router = APIRouter()

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(items.router)
```

### V2 Router

```python
# app/api/v2/router.py
from fastapi import APIRouter

from app.api.v2.routes import auth, users, items

router = APIRouter()

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(items.router)
```

### Directory Structure

```
app/
├── api/
│   ├── router.py           # Main router
│   ├── v1/
│   │   ├── router.py       # V1 router
│   │   ├── dependencies.py # V1 dependencies
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── users.py
│   │       └── items.py
│   └── v2/
│       ├── router.py       # V2 router
│       ├── dependencies.py # V2 dependencies
│       └── routes/
│           ├── auth.py
│           ├── users.py
│           └── items.py
├── application/
│   └── schemas/
│       ├── v1/
│       │   ├── user.py
│       │   └── item.py
│       └── v2/
│           ├── user.py
│           └── item.py
└── domain/
    └── entities/           # Shared domain entities
```

### Version-Specific Schemas

```python
# app/application/schemas/v1/user.py
from pydantic import BaseModel, EmailStr


class UserResponseV1(BaseModel):
    """V1 User response - legacy format."""

    id: int
    email: EmailStr
    name: str
    is_active: bool


# app/application/schemas/v2/user.py
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserResponseV2(BaseModel):
    """V2 User response - new format with additional fields."""

    id: int
    email: EmailStr
    full_name: str = Field(alias="name")  # Renamed field
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # New fields in V2
    profile_image_url: str | None = None
    preferences: dict | None = None

    class Config:
        populate_by_name = True
```

### Version-Specific Routes

```python
# app/api/v1/routes/users.py
from fastapi import APIRouter

from app.api.v1.dependencies import CurrentUser, Session
from app.application.schemas.v1.user import UserResponseV1

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=UserResponseV1)
async def get_user_v1(
    user_id: int,
    session: Session,
    current_user: CurrentUser,
):
    """V1: Get user by ID."""
    # V1 implementation
    pass


# app/api/v2/routes/users.py
from fastapi import APIRouter

from app.api.v2.dependencies import CurrentUser, Session
from app.application.schemas.v2.user import UserResponseV2

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=UserResponseV2)
async def get_user_v2(
    user_id: int,
    session: Session,
    current_user: CurrentUser,
):
    """V2: Get user by ID with extended information."""
    # V2 implementation with new fields
    pass
```

### 2. Header-Based Versioning

```python
# app/api/versioning.py
from enum import Enum
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status


class APIVersion(str, Enum):
    """Supported API versions."""

    V1 = "1"
    V2 = "2"
    LATEST = "2"  # Alias for latest


def get_api_version(
    accept_version: Annotated[
        str | None,
        Header(
            alias="Accept-Version",
            description="API version (1 or 2)",
        ),
    ] = None,
    x_api_version: Annotated[
        str | None,
        Header(
            alias="X-API-Version",
            description="API version (alternative header)",
        ),
    ] = None,
) -> APIVersion:
    """Extract API version from headers."""
    version_str = accept_version or x_api_version or APIVersion.LATEST

    try:
        return APIVersion(version_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid API version: {version_str}. Supported: 1, 2",
        )


APIVersionDep = Annotated[APIVersion, Depends(get_api_version)]
```

### Header-Based Route Handler

```python
# app/api/routes/users.py
from fastapi import APIRouter

from app.api.versioning import APIVersion, APIVersionDep
from app.application.schemas.v1.user import UserResponseV1
from app.application.schemas.v2.user import UserResponseV2

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    version: APIVersionDep,
):
    """Get user by ID (version-aware)."""
    if version == APIVersion.V1:
        # Return V1 format
        return UserResponseV1(
            id=user_id,
            email="user@example.com",
            name="John Doe",
            is_active=True,
        )
    else:
        # Return V2 format
        return UserResponseV2(
            id=user_id,
            email="user@example.com",
            full_name="John Doe",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            profile_image_url="https://example.com/avatar.jpg",
            preferences={"theme": "dark"},
        )
```

### 3. Deprecation Handling

```python
# app/api/deprecation.py
from datetime import datetime
from functools import wraps
from typing import Callable

from fastapi import Response
from starlette.middleware.base import BaseHTTPMiddleware


class DeprecationMiddleware(BaseHTTPMiddleware):
    """Add deprecation headers to responses."""

    DEPRECATED_PATHS = {
        "/api/v1/": {
            "sunset": "2025-12-31",
            "link": "https://docs.example.com/migration-guide",
        },
    }

    async def dispatch(self, request, call_next):
        response = await call_next(request)

        # Check if path is deprecated
        for path_prefix, info in self.DEPRECATED_PATHS.items():
            if request.url.path.startswith(path_prefix):
                response.headers["Deprecation"] = "true"
                response.headers["Sunset"] = info["sunset"]
                response.headers["Link"] = f'<{info["link"]}>; rel="deprecation"'
                break

        return response


def deprecated(
    message: str = "This endpoint is deprecated",
    sunset_date: str | None = None,
    alternative: str | None = None,
):
    """Decorator to mark endpoints as deprecated.

    Usage:
        @router.get("/old-endpoint", deprecated=True)
        @deprecated(message="Use /new-endpoint", sunset_date="2025-12-31")
        async def old_endpoint(response: Response):
            # Note: Response must be a parameter in the route function
            pass
    """
    import inspect

    def decorator(func: Callable):
        # Update OpenAPI schema
        func.__doc__ = f"**DEPRECATED**: {message}\n\n" + (func.__doc__ or "")

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get response from kwargs if available
            response: Response | None = kwargs.get("response")

            # If not in kwargs, check if it's a positional arg by inspecting signature
            if response is None:
                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                if "response" in params:
                    idx = params.index("response")
                    if idx < len(args):
                        response = args[idx]

            # Set deprecation headers if response is available
            if response is not None:
                response.headers["Deprecation"] = "true"
                response.headers["X-Deprecation-Message"] = message

                if sunset_date:
                    response.headers["Sunset"] = sunset_date

                if alternative:
                    response.headers["X-Alternative-Endpoint"] = alternative

            return await func(*args, **kwargs)

        return wrapper

    return decorator
```

### Using Deprecation Decorator

```python
# app/api/v1/routes/users.py
from fastapi import APIRouter, Response

from app.api.deprecation import deprecated

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/{user_id}",
    deprecated=True,  # Mark as deprecated in OpenAPI
)
@deprecated(
    message="Use GET /api/v2/users/{user_id} instead",
    sunset_date="2025-12-31",
    alternative="/api/v2/users/{user_id}",
)
async def get_user_v1(
    user_id: int,
    response: Response,
):
    """Get user by ID (deprecated, use V2)."""
    pass
```

### 4. Version Negotiation with Accept Header

```python
# app/api/content_negotiation.py
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status


SUPPORTED_VERSIONS = {
    "application/vnd.api.v1+json": "v1",
    "application/vnd.api.v2+json": "v2",
    "application/json": "v2",  # Default to latest
}


def negotiate_version(
    accept: Annotated[
        str,
        Header(
            description="Content-Type with version",
        ),
    ] = "application/json",
) -> str:
    """Negotiate API version from Accept header."""
    # Parse Accept header (simplified)
    for content_type in accept.split(","):
        content_type = content_type.strip().split(";")[0]
        if content_type in SUPPORTED_VERSIONS:
            return SUPPORTED_VERSIONS[content_type]

    raise HTTPException(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        detail=f"Unsupported Accept header. Supported: {list(SUPPORTED_VERSIONS.keys())}",
    )


ContentVersion = Annotated[str, Depends(negotiate_version)]
```

### 5. Version Router Factory

```python
# app/api/version_router.py
from typing import Callable, Type

from fastapi import APIRouter
from pydantic import BaseModel


class VersionedRouter:
    """Factory for creating versioned routers."""

    def __init__(self, prefix: str, tags: list[str] | None = None):
        self.prefix = prefix
        self.tags = tags or []
        self.versions: dict[str, APIRouter] = {}

    def version(self, version: str) -> APIRouter:
        """Get or create router for a specific version."""
        if version not in self.versions:
            self.versions[version] = APIRouter(
                prefix=self.prefix,
                tags=[f"{tag}-{version}" for tag in self.tags],
            )
        return self.versions[version]

    def get_all_routers(self) -> list[tuple[str, APIRouter]]:
        """Get all versioned routers."""
        return list(self.versions.items())


# Usage
users_router = VersionedRouter(prefix="/users", tags=["users"])


# V1 routes
v1 = users_router.version("v1")


@v1.get("/{user_id}")
async def get_user_v1(user_id: int):
    return {"version": "v1", "user_id": user_id}


# V2 routes
v2 = users_router.version("v2")


@v2.get("/{user_id}")
async def get_user_v2(user_id: int):
    return {"version": "v2", "user_id": user_id, "extended": True}


# Mount all versions
def setup_versioned_routes(app):
    for version, router in users_router.get_all_routers():
        app.include_router(router, prefix=f"/api/{version}")
```

### 6. Schema Evolution

```python
# app/application/schemas/evolve.py
from typing import TypeVar

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class SchemaEvolution:
    """Handle schema evolution between versions."""

    @staticmethod
    def v1_to_v2_user(v1_data: dict) -> dict:
        """Transform V1 user data to V2 format."""
        return {
            "id": v1_data["id"],
            "email": v1_data["email"],
            "full_name": v1_data.get("name", ""),  # Renamed field
            "is_active": v1_data.get("is_active", True),
            "created_at": v1_data.get("created_at"),
            "updated_at": v1_data.get("updated_at"),
            # New fields with defaults
            "profile_image_url": None,
            "preferences": {},
        }

    @staticmethod
    def v2_to_v1_user(v2_data: dict) -> dict:
        """Transform V2 user data to V1 format (backward compatibility)."""
        return {
            "id": v2_data["id"],
            "email": v2_data["email"],
            "name": v2_data.get("full_name", ""),  # Original field name
            "is_active": v2_data.get("is_active", True),
        }
```

## Versioning Strategy Comparison

| Strategy | Pros | Cons |
|----------|------|------|
| **URL Path** | Clear, cacheable, easy to route | URL changes between versions |
| **Header** | Clean URLs, content negotiation | Harder to test, not cacheable |
| **Query Param** | Easy to use | Pollutes query params |
| **Accept Header** | RESTful, media type versioning | Complex parsing |

## Best Practices

| Practice | Description |
|----------|-------------|
| Semantic Versioning | Use MAJOR.MINOR.PATCH for API versions |
| Deprecation Period | Give 6-12 months notice before removing |
| Documentation | Document changes between versions |
| Sunset Header | Include RFC 8594 Sunset header |
| Breaking Changes | Only in major versions |
| Backward Compatibility | Support N-1 version minimum |

## References

- `_references/API-PATTERN.md`
