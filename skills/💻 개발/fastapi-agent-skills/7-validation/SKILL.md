---
name: validation
description: |
  Pydantic V2 validators 및 커스텀 검증 패턴을 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Validation Skill

Pydantic V2 validators 및 커스텀 검증 패턴을 구현합니다.

## Triggers

- "검증", "validation", "pydantic", "schema"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |

---

## Output

### Base Schema

```python
# app/schemas/base.py
from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields."""

    created_at: datetime | None = None
    updated_at: datetime | None = None


class PaginatedResponse(BaseSchema, Generic[T]):
    """Paginated response schema."""

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse[T]":
        """Create paginated response."""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


class SuccessResponse(BaseSchema, Generic[T]):
    """Standard success response."""

    success: bool = True
    data: T | None = None
    message: str | None = None
```

### User Schema 예시

```python
# app/schemas/user.py
import re
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from app.schemas.base import BaseSchema, TimestampSchema


# Custom types with validation
Username = Annotated[
    str,
    Field(
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Username (alphanumeric, underscore, hyphen)",
    ),
]

Password = Annotated[
    str,
    Field(
        min_length=8,
        max_length=100,
        description="Password (min 8 characters)",
    ),
]


class UserBase(BaseSchema):
    """Base user schema."""

    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    username: Username | None = None


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: Password
    password_confirm: str

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

    @model_validator(mode="after")
    def validate_passwords_match(self) -> "UserCreate":
        """Validate that passwords match."""
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self


class UserUpdate(BaseSchema):
    """Schema for updating a user."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    username: Username | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"name": "John Doe", "username": "johndoe"},
                {"name": "Jane Doe"},
            ]
        }
    )


class UserResponse(TimestampSchema):
    """Schema for user response."""

    id: int
    email: EmailStr
    name: str
    username: str | None = None
    is_active: bool
    is_superuser: bool


class UserListResponse(BaseSchema):
    """Schema for user list response."""

    users: list[UserResponse]
    total: int
```

### Custom Validators

```python
# app/schemas/validators.py
import re
from typing import Any


def validate_phone_number(v: str) -> str:
    """Validate Korean phone number format."""
    # Remove all non-digit characters
    digits = re.sub(r"\D", "", v)

    # Check valid Korean phone number patterns
    patterns = [
        r"^010\d{8}$",      # Mobile: 01012345678
        r"^02\d{7,8}$",     # Seoul: 0212345678
        r"^0[3-6]\d{7,8}$", # Regional
    ]

    if not any(re.match(p, digits) for p in patterns):
        raise ValueError("Invalid phone number format")

    return digits


def validate_business_number(v: str) -> str:
    """Validate Korean business registration number."""
    digits = re.sub(r"\D", "", v)

    if len(digits) != 10:
        raise ValueError("Business number must be 10 digits")

    # Validate checksum
    weights = [1, 3, 7, 1, 3, 7, 1, 3, 5]
    total = sum(int(d) * w for d, w in zip(digits[:9], weights))
    total += int(digits[8]) * 5 // 10
    check_digit = (10 - total % 10) % 10

    if int(digits[9]) != check_digit:
        raise ValueError("Invalid business number checksum")

    return digits


def validate_slug(v: str) -> str:
    """Validate URL-safe slug."""
    if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", v):
        raise ValueError("Slug must be lowercase alphanumeric with hyphens")
    return v
```

### Schema with Custom Validators

```python
# app/schemas/company.py
from pydantic import Field, field_validator

from app.schemas.base import BaseSchema
from app.schemas.validators import validate_business_number, validate_phone_number


class CompanyCreate(BaseSchema):
    """Schema for creating a company."""

    name: str = Field(min_length=1, max_length=200)
    business_number: str = Field(description="Business registration number")
    phone: str = Field(description="Contact phone number")
    address: str | None = None

    @field_validator("business_number")
    @classmethod
    def validate_business_number(cls, v: str) -> str:
        return validate_business_number(v)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return validate_phone_number(v)
```

### Query Parameters Schema

```python
# app/schemas/common.py
from enum import Enum
from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, Field


class SortOrder(str, Enum):
    """Sort order enum."""

    ASC = "asc"
    DESC = "desc"


class PaginationParams(BaseModel):
    """Pagination query parameters."""

    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class SortParams(BaseModel):
    """Sorting query parameters."""

    sort_by: str = Field(default="created_at", description="Field to sort by")
    sort_order: SortOrder = Field(default=SortOrder.DESC, description="Sort order")


# Annotated dependencies for routes
PageParams = Annotated[
    PaginationParams,
    Query(description="Pagination parameters"),
]

SortingParams = Annotated[
    SortParams,
    Query(description="Sorting parameters"),
]
```

### Filter Schema

```python
# app/schemas/filters.py
from datetime import datetime
from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, Field


class UserFilter(BaseModel):
    """User filter parameters."""

    search: str | None = Field(default=None, description="Search by name or email")
    is_active: bool | None = Field(default=None, description="Filter by active status")
    created_after: datetime | None = Field(default=None, description="Created after date")
    created_before: datetime | None = Field(default=None, description="Created before date")


UserFilterParams = Annotated[UserFilter, Query()]
```

### 사용 예시

```python
# app/api/v1/routes/users.py
from fastapi import APIRouter

from app.schemas.common import PageParams, SortingParams
from app.schemas.filters import UserFilterParams
from app.schemas.user import UserCreate, UserResponse, UserListResponse
from app.schemas.base import PaginatedResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    pagination: PageParams,
    sorting: SortingParams,
    filters: UserFilterParams,
    service: UserSvc,
):
    """List users with pagination, sorting, and filtering."""
    users, total = await service.list(
        offset=pagination.offset,
        limit=pagination.limit,
        sort_by=sorting.sort_by,
        sort_order=sorting.sort_order,
        filters=filters,
    )

    return PaginatedResponse.create(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(user_in: UserCreate, service: UserSvc):
    """Create a new user."""
    return await service.create(user_in)
```

## References

- `_references/API-PATTERN.md`
