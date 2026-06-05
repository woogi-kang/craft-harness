---
name: di-container
description: |
  Dependency Injection 패턴을 설정합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# DI Container Skill

Dependency Injection 패턴을 설정합니다.

## Triggers

- "DI 설정", "의존성 주입", "dependency injection", "dependencies"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |

---

## Output

### Dependencies 패턴

FastAPI의 `Depends`를 활용한 DI 패턴입니다.

```python
# app/api/v1/dependencies/__init__.py
"""
Dependency injection module.

All dependencies should be defined here and imported in routes.
"""
from app.api.v1.dependencies.auth import (
    get_current_user,
    get_current_active_user,
    get_current_superuser,
)
from app.api.v1.dependencies.database import get_db_session, DBSession
from app.api.v1.dependencies.services import (
    get_user_service,
    get_auth_service,
)

__all__ = [
    # Auth
    "get_current_user",
    "get_current_active_user",
    "get_current_superuser",
    # Database
    "get_db_session",
    "DBSession",
    # Services
    "get_user_service",
    "get_auth_service",
]
```

### Database Dependency

```python
# app/api/v1/dependencies/database.py
from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import async_session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency.

    Transaction handling:
    - Commits on success
    - Rolls back on exception
    - Session is automatically closed by context manager
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        # Note: No explicit close() needed - context manager handles it


# Type alias for cleaner route signatures
DBSession = Annotated[AsyncSession, Depends(get_db_session)]
```

### Repository Dependencies

```python
# app/api/v1/dependencies/repositories.py
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.database import get_db_session
from app.domain.repositories.user import UserRepository
from app.infrastructure.repositories.user import UserRepositoryImpl


def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> UserRepository:
    """Get user repository dependency."""
    return UserRepositoryImpl(session)


# Type alias
UserRepo = Annotated[UserRepository, Depends(get_user_repository)]
```

### Service Dependencies

```python
# app/api/v1/dependencies/services.py
from typing import Annotated

from fastapi import Depends

from app.api.v1.dependencies.repositories import get_user_repository
from app.application.services.user import UserService
from app.application.services.auth import AuthService
from app.domain.repositories.user import UserRepository


def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    """Get user service dependency."""
    return UserService(repository)


def get_auth_service(
    repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """Get auth service dependency."""
    return AuthService(repository)


# Type aliases
UserSvc = Annotated[UserService, Depends(get_user_service)]
AuthSvc = Annotated[AuthService, Depends(get_auth_service)]
```

### Auth Dependencies

```python
# app/api/v1/dependencies/auth.py
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.api.v1.dependencies.services import get_user_service
from app.application.services.user import UserService
from app.core.security import decode_access_token
from app.domain.entities.user import UserEntity

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: UserService = Depends(get_user_service),
) -> UserEntity:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = await user_service.get_by_id(int(user_id))
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[UserEntity, Depends(get_current_user)],
) -> UserEntity:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


async def get_current_superuser(
    current_user: Annotated[UserEntity, Depends(get_current_active_user)],
) -> UserEntity:
    """Get current superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges",
        )
    return current_user


# Type aliases
CurrentUser = Annotated[UserEntity, Depends(get_current_user)]
ActiveUser = Annotated[UserEntity, Depends(get_current_active_user)]
SuperUser = Annotated[UserEntity, Depends(get_current_superuser)]
```

### 사용 예시

```python
# app/api/v1/routes/users.py
from fastapi import APIRouter, status

from app.api.v1.dependencies import (
    ActiveUser,
    SuperUser,
    UserSvc,
)
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: ActiveUser,
) -> UserResponse:
    """Get current user information."""
    return UserResponse.model_validate(current_user)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    service: UserSvc,
    _: SuperUser,  # Only superusers can create users
) -> UserResponse:
    """Create a new user (admin only)."""
    user = await service.create(user_in)
    return UserResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserSvc,
    _: ActiveUser,  # Any authenticated user
) -> UserResponse:
    """Get user by ID."""
    user = await service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    service: UserSvc,
    current_user: ActiveUser,
) -> UserResponse:
    """Update user (own profile or admin)."""
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges",
        )

    user = await service.update(user_id, user_in)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserResponse.model_validate(user)
```

### 테스트용 Dependency Override

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.api.v1.dependencies.database import get_db_session
from app.api.v1.dependencies.auth import get_current_user


@pytest.fixture
async def async_client():
    """Create async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture
def override_db_session(mock_session):
    """Override database session dependency."""
    async def _get_test_session():
        yield mock_session

    app.dependency_overrides[get_db_session] = _get_test_session
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def override_current_user(test_user):
    """Override current user dependency."""
    async def _get_test_user():
        return test_user

    app.dependency_overrides[get_current_user] = _get_test_user
    yield
    app.dependency_overrides.clear()
```

## References

- `_references/ARCHITECTURE-PATTERN.md`
