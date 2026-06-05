---
name: architecture
description: |
  Clean Architecture 기반 프로젝트 구조를 설계합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Architecture Skill

Extends: `../../_shared/architecture/SKILL.md` (공통 아키텍처 원칙 참조)

Clean Architecture 기반 프로젝트 구조를 설계합니다.

## Triggers

- "아키텍처 설계", "구조 설계", "clean architecture"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | FastAPI 프로젝트 경로 |
| `features` | ❌ | 초기 생성할 Feature 목록 |

---

## 레이어 구조

```
┌─────────────────────────────────────┐
│            API Layer                │
│  Router (Endpoint) ◄──► Dependencies │
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│         Application Layer           │
│  Service (Business Logic)           │
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│           Domain Layer              │
│  Entity → Repository (Interface)    │
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│       Infrastructure Layer          │
│  Repository (Impl) → Database/Cache │
└─────────────────────────────────────┘
```

---

## Feature 구조

```
app/
├── api/v1/routes/{feature}.py           # API 엔드포인트
├── api/v1/dependencies/{feature}.py     # DI Dependencies
├── schemas/{feature}.py                  # Request/Response Pydantic
├── domain/
│   ├── entities/{feature}.py            # Domain Entity
│   └── repositories/{feature}.py        # Repository Interface (ABC)
├── application/services/{feature}.py    # Business Logic
└── infrastructure/
    ├── database/models/{feature}.py     # SQLAlchemy Model
    └── repositories/{feature}.py        # Repository Implementation
```

---

## 레이어별 책임

### API Layer (app/api/)

- HTTP 요청/응답 처리
- 요청 유효성 검사 (Pydantic)
- 인증/인가 처리 (Dependencies)
- 라우팅

```python
# app/api/v1/routes/users.py
from fastapi import APIRouter, Depends, status
from app.api.v1.dependencies.auth import get_current_user
from app.api.v1.dependencies.services import get_user_service
from app.application.services.user import UserService
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Create a new user."""
    return await service.create(user_in)
```

### Application Layer (app/application/)

- 비즈니스 로직 구현
- 트랜잭션 관리
- 여러 Repository 조합

```python
# app/application/services/user.py
from app.domain.entities.user import UserEntity
from app.domain.repositories.user import UserRepository
from app.schemas.user import UserCreate


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def create(self, user_in: UserCreate) -> UserEntity:
        """Create a new user."""
        # 비즈니스 로직 수행
        entity = UserEntity(
            email=user_in.email,
            name=user_in.name,
            hashed_password=hash_password(user_in.password),
        )
        return await self._repository.create(entity)

    async def get_by_id(self, user_id: int) -> UserEntity | None:
        """Get user by ID."""
        return await self._repository.get_by_id(user_id)
```

### Domain Layer (app/domain/)

- 핵심 비즈니스 엔티티
- Repository 인터페이스 정의
- 외부 의존성 없음 (순수 Python)

```python
# app/domain/entities/user.py
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserEntity(BaseModel):
    """User domain entity."""
    id: int | None = None
    email: EmailStr
    name: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
```

```python
# app/domain/repositories/user.py
from abc import ABC, abstractmethod
from app.domain.entities.user import UserEntity


class UserRepository(ABC):
    """User repository interface."""

    @abstractmethod
    async def create(self, entity: UserEntity) -> UserEntity:
        """Create a new user."""
        ...

    @abstractmethod
    async def get_by_id(self, user_id: int) -> UserEntity | None:
        """Get user by ID."""
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> UserEntity | None:
        """Get user by email."""
        ...

    @abstractmethod
    async def update(self, user_id: int, entity: UserEntity) -> UserEntity | None:
        """Update user."""
        ...

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """Delete user."""
        ...
```

### Infrastructure Layer (app/infrastructure/)

- 외부 시스템과의 통신
- Repository 구현
- 데이터베이스 모델

```python
# app/infrastructure/database/models/user.py
from datetime import datetime
from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.database.session import Base


class UserModel(Base):
    """User database model."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
```

```python
# app/infrastructure/repositories/user.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.user import UserEntity
from app.domain.repositories.user import UserRepository
from app.infrastructure.database.models.user import UserModel


class UserRepositoryImpl(UserRepository):
    """User repository implementation."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, entity: UserEntity) -> UserEntity:
        model = UserModel(**entity.model_dump(exclude={"id", "created_at", "updated_at"}))
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return UserEntity.model_validate(model)

    async def get_by_id(self, user_id: int) -> UserEntity | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return UserEntity.model_validate(model) if model else None

    async def get_by_email(self, email: str) -> UserEntity | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        return UserEntity.model_validate(model) if model else None

    async def update(self, user_id: int, entity: UserEntity) -> UserEntity | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None

        for key, value in entity.model_dump(exclude={"id", "created_at"}).items():
            setattr(model, key, value)

        await self._session.commit()
        await self._session.refresh(model)
        return UserEntity.model_validate(model)

    async def delete(self, user_id: int) -> bool:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False

        await self._session.delete(model)
        await self._session.commit()
        return True
```

---

## 의존성 방향

```
API → Application → Domain ← Infrastructure
 │         │           │            │
 │         │           │            │
 ▼         ▼           ▼            ▼
Router   Service    Entity     Repository
  │         │      Repository     (Impl)
  │         │     (Interface)       │
 Deps       │           │        Database
            └───────────┴───────────┘
```

**핵심 원칙:**
- Domain Layer는 외부 의존성 없음 (순수 Python)
- Infrastructure Layer는 Domain Layer에 의존
- Application Layer는 Domain Layer에 의존
- API Layer는 Application Layer에 의존
- Entity ↔ Model 변환은 Infrastructure Layer에서 수행

## References

- `_references/ARCHITECTURE-PATTERN.md`
