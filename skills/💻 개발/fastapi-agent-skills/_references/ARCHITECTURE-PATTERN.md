# Architecture Pattern Reference

FastAPI 프로젝트의 Clean Architecture 패턴 가이드입니다.

## Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Presentation Layer                      │
│                  (API Routes, Dependencies)                  │
├─────────────────────────────────────────────────────────────┤
│                      Application Layer                       │
│              (Services, Use Cases, DTOs/Schemas)            │
├─────────────────────────────────────────────────────────────┤
│                        Domain Layer                          │
│           (Entities, Repository Interfaces, Value Objects)   │
├─────────────────────────────────────────────────────────────┤
│                     Infrastructure Layer                     │
│        (Repository Impl, Database, External Services)        │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
app/
├── api/                          # Presentation Layer
│   ├── __init__.py
│   ├── router.py                 # Main router
│   └── v1/
│       ├── __init__.py
│       ├── router.py             # V1 router
│       ├── dependencies.py       # DI dependencies
│       └── routes/
│           ├── __init__.py
│           ├── auth.py
│           ├── users.py
│           └── items.py
│
├── application/                  # Application Layer
│   ├── __init__.py
│   ├── services/                 # Application services
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   ├── use_cases/                # Use cases (optional)
│   │   ├── __init__.py
│   │   └── register_user.py
│   └── schemas/                  # Pydantic schemas (DTOs)
│       ├── __init__.py
│       ├── user.py
│       └── item.py
│
├── domain/                       # Domain Layer
│   ├── __init__.py
│   ├── entities/                 # Domain entities
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   ├── repositories/             # Repository interfaces
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── user.py
│   ├── value_objects/            # Value objects
│   │   ├── __init__.py
│   │   └── email.py
│   └── exceptions.py             # Domain exceptions
│
├── infrastructure/               # Infrastructure Layer
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── session.py            # DB session factory
│   │   ├── unit_of_work.py       # Unit of Work
│   │   └── models/               # ORM models
│   │       ├── __init__.py
│   │       ├── base.py
│   │       └── user.py
│   ├── repositories/             # Repository implementations
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── user.py
│   ├── security/                 # Security utilities
│   │   ├── __init__.py
│   │   ├── password.py
│   │   └── jwt.py
│   ├── cache/                    # Caching
│   │   ├── __init__.py
│   │   └── redis.py
│   └── services/                 # External services
│       ├── __init__.py
│       └── email.py
│
├── core/                         # Shared/Core
│   ├── __init__.py
│   ├── config.py                 # Settings
│   ├── exceptions.py             # Application exceptions
│   └── constants.py              # Constants
│
└── main.py                       # Application entry point
```

## Layer Responsibilities

### 1. Presentation Layer (API)

**Purpose**: Handle HTTP requests/responses, authentication, validation

```python
# app/api/v1/routes/users.py
from fastapi import APIRouter, status

from app.api.v1.dependencies import CurrentUser, Session, UserServiceDep
from app.application.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    session: Session,
    user_service: UserServiceDep,
    current_user: CurrentUser,
):
    """Create a new user."""
    return await user_service.create(session, user_in)
```

### 2. Application Layer (Services)

**Purpose**: Orchestrate use cases, coordinate domain objects, handle transactions

```python
# app/application/services/user.py
from app.application.schemas.user import UserCreate, UserUpdate
from app.domain.entities.user import User
from app.domain.repositories.user import UserRepositoryInterface
from app.core.exceptions import ConflictError, NotFoundError


class UserService:
    def __init__(self, repository: UserRepositoryInterface):
        self._repository = repository

    async def create(self, session, user_in: UserCreate) -> User:
        # Check if email exists
        existing = await self._repository.get_by_email(session, user_in.email)
        if existing:
            raise ConflictError("Email already exists")

        # Create domain entity
        user = User(
            email=user_in.email,
            name=user_in.name,
            hashed_password=hash_password(user_in.password),
        )

        # Persist
        return await self._repository.create(session, user)

    async def get_by_id(self, session, user_id: int) -> User:
        user = await self._repository.get_by_id(session, user_id)
        if not user:
            raise NotFoundError("User")
        return user
```

### 3. Domain Layer (Entities)

**Purpose**: Core business logic, domain rules, no external dependencies

**Entity Pattern Choice:**
We use Pydantic `BaseModel` for domain entities to ensure consistency with DTOs
and leverage Pydantic's validation, serialization, and ORM integration features.

```python
# app/domain/entities/user.py
from datetime import datetime, timezone
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserEntity(BaseModel):
    """User domain entity.

    Uses Pydantic for:
    - Built-in validation
    - Easy serialization/deserialization
    - ORM integration via model_config
    - Immutability with frozen=True (optional)
    """

    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode for model conversion
    )

    id: int | None = None
    email: str
    name: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is not empty."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Name cannot be empty")
        return v.strip()

    def deactivate(self) -> Self:
        """Deactivate user account.

        Returns a new instance with updated values (immutable pattern).
        """
        return self.model_copy(
            update={
                "is_active": False,
                "updated_at": datetime.now(timezone.utc),
            }
        )

    def update_name(self, name: str) -> Self:
        """Update user name.

        Returns a new instance with updated values (immutable pattern).
        """
        return self.model_copy(
            update={
                "name": name.strip(),
                "updated_at": datetime.now(timezone.utc),
            }
        )

    def to_dict(self) -> dict:
        """Convert to dictionary (excludes password)."""
        return self.model_dump(exclude={"hashed_password"})
```

**Alternative: Dataclass Pattern**

For simpler cases or when you prefer mutable entities:

```python
# Alternative using dataclass (not recommended for consistency)
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class User:
    """User domain entity using dataclass."""

    id: int | None
    email: str
    name: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)
```

### 4. Infrastructure Layer (Repositories)

**Purpose**: Implement data access, external integrations

```python
# app/infrastructure/repositories/user.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import UserEntity
from app.domain.repositories.user import UserRepositoryInterface
from app.infrastructure.database.models.user import UserModel


class UserRepository(UserRepositoryInterface):
    """SQLAlchemy implementation of UserRepository."""

    async def get_by_id(self, session: AsyncSession, user_id: int) -> UserEntity | None:
        result = await session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, session: AsyncSession, user: UserEntity) -> UserEntity:
        model = self._to_model(user)
        session.add(model)
        await session.flush()
        await session.refresh(model)
        return self._to_entity(model)

    def _to_entity(self, model: UserModel) -> UserEntity:
        """Convert ORM model to domain entity.

        Uses Pydantic's from_attributes for direct conversion.
        """
        return UserEntity.model_validate(model)

    def _to_model(self, entity: UserEntity) -> UserModel:
        """Convert domain entity to ORM model."""
        return UserModel(
            id=entity.id,
            email=entity.email,
            name=entity.name,
            hashed_password=entity.hashed_password,
            is_active=entity.is_active,
            is_superuser=entity.is_superuser,
        )
```

## Dependency Flow

```
API Layer → Application Layer → Domain Layer
                 ↓
         Infrastructure Layer
```

## Key Principles

| Principle | Description |
|-----------|-------------|
| **Dependency Inversion** | High-level modules don't depend on low-level modules |
| **Single Responsibility** | Each layer has one reason to change |
| **Interface Segregation** | Clients depend on interfaces they use |
| **Domain Isolation** | Domain layer has no external dependencies |
| **Testability** | Each layer can be tested in isolation |

## Related Skills

- `5-di-container`: Dependency injection setup
- `6-service-layer`: Application services
- `16-repository-pattern`: Data access pattern
- `17-unit-of-work`: Transaction management
