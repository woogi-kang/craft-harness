---
name: repository-pattern
description: |
  Repository 추상화 및 Unit of Work 패턴을 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Repository Pattern Skill

Repository 추상화 및 Unit of Work 패턴을 구현합니다.

## Triggers

- "repository", "레포지토리", "unit of work", "데이터 접근"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |
| `entity` | ✅ | 대상 엔티티 |

---

## Output

### Base Repository Interface

```python
# app/domain/repositories/base.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")
ID = TypeVar("ID")


class BaseRepository(ABC, Generic[T, ID]):
    """Base repository interface.

    Provides standard CRUD operations with pagination and filtering support.
    """

    @abstractmethod
    async def get_by_id(self, id: ID) -> T | None:
        """Get entity by ID."""
        ...

    @abstractmethod
    async def list(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> list[T]:
        """List entities with pagination (no filters)."""
        ...

    @abstractmethod
    async def get_many(
        self,
        offset: int = 0,
        limit: int = 100,
        **filters,
    ) -> list[T]:
        """Get multiple entities with optional filtering.

        Args:
            offset: Number of records to skip
            limit: Maximum records to return
            **filters: Field-value pairs for filtering (e.g., is_active=True)

        Returns:
            List of matching entities
        """
        ...

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity."""
        ...

    @abstractmethod
    async def update(self, id: ID, entity: T) -> T | None:
        """Update an existing entity."""
        ...

    @abstractmethod
    async def delete(self, id: ID) -> bool:
        """Delete an entity."""
        ...

    @abstractmethod
    async def count(self, **filters) -> int:
        """Count entities with optional filtering.

        Args:
            **filters: Field-value pairs for filtering

        Returns:
            Count of matching entities
        """
        ...

    @abstractmethod
    async def exists(self, id: ID) -> bool:
        """Check if entity exists."""
        ...

    @abstractmethod
    async def delete_many(self, **filters) -> int:
        """Delete multiple entities matching filters.

        Returns:
            Number of deleted entities
        """
        ...

    @abstractmethod
    async def get_by_filter(
        self,
        filter_spec: "FilterSpec",
        offset: int = 0,
        limit: int = 100,
    ) -> list[T]:
        """Get entities using advanced filter specification.

        Supports range queries, IN clauses, and pattern matching.
        """
        ...
```

### Filter Specification

```python
# app/domain/repositories/filter.py
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FilterOperator(Enum):
    """Supported filter operators."""

    EQ = "eq"           # Equal
    NE = "ne"           # Not equal
    GT = "gt"           # Greater than
    GTE = "gte"         # Greater than or equal
    LT = "lt"           # Less than
    LTE = "lte"         # Less than or equal
    IN = "in"           # In list
    NOT_IN = "not_in"   # Not in list
    LIKE = "like"       # Pattern match (case-sensitive)
    ILIKE = "ilike"     # Pattern match (case-insensitive)
    IS_NULL = "is_null" # Is null
    IS_NOT_NULL = "is_not_null"  # Is not null
    BETWEEN = "between" # Between two values


@dataclass
class FilterCondition:
    """Single filter condition."""

    field: str
    operator: FilterOperator
    value: Any


@dataclass
class FilterSpec:
    """Specification for advanced filtering.

    Usage:
        spec = FilterSpec(
            conditions=[
                FilterCondition("price", FilterOperator.GTE, 100),
                FilterCondition("price", FilterOperator.LTE, 500),
                FilterCondition("status", FilterOperator.IN, ["active", "pending"]),
                FilterCondition("name", FilterOperator.ILIKE, "%search%"),
            ],
            order_by=[("created_at", "desc"), ("id", "asc")],
        )
    """

    conditions: list[FilterCondition] = field(default_factory=list)
    order_by: list[tuple[str, str]] = field(default_factory=list)  # [(field, "asc"|"desc")]

    def add(
        self,
        field: str,
        operator: FilterOperator,
        value: Any,
    ) -> "FilterSpec":
        """Add a filter condition (fluent API)."""
        self.conditions.append(FilterCondition(field, operator, value))
        return self

    def eq(self, field: str, value: Any) -> "FilterSpec":
        """Shorthand for equality filter."""
        return self.add(field, FilterOperator.EQ, value)

    def gt(self, field: str, value: Any) -> "FilterSpec":
        """Shorthand for greater than filter."""
        return self.add(field, FilterOperator.GT, value)

    def gte(self, field: str, value: Any) -> "FilterSpec":
        """Shorthand for greater than or equal filter."""
        return self.add(field, FilterOperator.GTE, value)

    def lt(self, field: str, value: Any) -> "FilterSpec":
        """Shorthand for less than filter."""
        return self.add(field, FilterOperator.LT, value)

    def lte(self, field: str, value: Any) -> "FilterSpec":
        """Shorthand for less than or equal filter."""
        return self.add(field, FilterOperator.LTE, value)

    def in_(self, field: str, values: list[Any]) -> "FilterSpec":
        """Shorthand for IN filter."""
        return self.add(field, FilterOperator.IN, values)

    def like(self, field: str, pattern: str) -> "FilterSpec":
        """Shorthand for LIKE filter."""
        return self.add(field, FilterOperator.ILIKE, f"%{pattern}%")

    def between(self, field: str, start: Any, end: Any) -> "FilterSpec":
        """Shorthand for BETWEEN filter."""
        return self.add(field, FilterOperator.BETWEEN, (start, end))

    def sort(self, field: str, direction: str = "asc") -> "FilterSpec":
        """Add sort order (fluent API)."""
        self.order_by.append((field, direction))
        return self
```

### User Repository Interface

```python
# app/domain/repositories/user.py
from abc import abstractmethod

from app.domain.entities.user import UserEntity
from app.domain.repositories.base import BaseRepository


class UserRepository(BaseRepository[UserEntity, int]):
    """User repository interface."""

    @abstractmethod
    async def get_by_email(self, email: str) -> UserEntity | None:
        """Get user by email."""
        ...

    @abstractmethod
    async def get_by_username(self, username: str) -> UserEntity | None:
        """Get user by username."""
        ...

    @abstractmethod
    async def list_active(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> list[UserEntity]:
        """List active users."""
        ...

    @abstractmethod
    async def search(
        self,
        query: str,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[list[UserEntity], int]:
        """Search users by name or email."""
        ...
```

### Base Repository Implementation

```python
# app/infrastructure/repositories/base.py
from typing import Generic, TypeVar, Type, Any

from sqlalchemy import select, func, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import Base

T = TypeVar("T")  # Entity type
M = TypeVar("M", bound=Base)  # Model type


class SQLAlchemyRepository(Generic[T, M]):
    """Base SQLAlchemy repository implementation."""

    def __init__(
        self,
        session: AsyncSession,
        model: Type[M],
        entity_class: Type[T],
    ) -> None:
        self._session = session
        self._model = model
        self._entity_class = entity_class

    def _to_entity(self, model: M) -> T:
        """Convert model to entity."""
        return self._entity_class.model_validate(model)

    def _to_model(self, entity: T, exclude_unset: bool = False) -> dict[str, Any]:
        """Convert entity to model dict."""
        return entity.model_dump(
            exclude={"id", "created_at", "updated_at"} if exclude_unset else {"id"},
            exclude_unset=exclude_unset,
        )

    async def get_by_id(self, id: int) -> T | None:
        """Get entity by ID."""
        result = await self._session.execute(
            select(self._model).where(self._model.id == id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> list[T]:
        """List entities with pagination (no filters)."""
        result = await self._session.execute(
            select(self._model)
            .offset(offset)
            .limit(limit)
            .order_by(self._model.id.desc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_many(
        self,
        offset: int = 0,
        limit: int = 100,
        **filters,
    ) -> list[T]:
        """Get multiple entities with optional filtering.

        Supports simple equality filters on model fields.
        """
        stmt = select(self._model)

        # Apply filters
        for field, value in filters.items():
            if hasattr(self._model, field) and value is not None:
                stmt = stmt.where(getattr(self._model, field) == value)

        stmt = stmt.offset(offset).limit(limit).order_by(self._model.id.desc())

        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def create(self, entity: T) -> T:
        """Create a new entity."""
        model = self._model(**self._to_model(entity))
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, id: int, entity: T) -> T | None:
        """Update an existing entity."""
        result = await self._session.execute(
            select(self._model).where(self._model.id == id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None

        for key, value in self._to_model(entity, exclude_unset=True).items():
            if value is not None:
                setattr(model, key, value)

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, id: int) -> bool:
        """Delete an entity."""
        result = await self._session.execute(
            select(self._model).where(self._model.id == id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False

        await self._session.delete(model)
        await self._session.flush()
        return True

    async def count(self, **filters) -> int:
        """Count entities with optional filtering."""
        stmt = select(func.count()).select_from(self._model)

        # Apply filters
        for field, value in filters.items():
            if hasattr(self._model, field) and value is not None:
                stmt = stmt.where(getattr(self._model, field) == value)

        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def exists(self, id: int) -> bool:
        """Check if entity exists."""
        result = await self._session.execute(
            select(func.count()).select_from(self._model).where(self._model.id == id)
        )
        return (result.scalar() or 0) > 0

    async def delete_many(self, **filters) -> int:
        """Bulk delete entities matching filters.

        More efficient than individual deletes - uses single DELETE statement.

        Returns:
            Number of deleted rows
        """
        stmt = sql_delete(self._model)

        # Apply filters
        for field, value in filters.items():
            if hasattr(self._model, field) and value is not None:
                stmt = stmt.where(getattr(self._model, field) == value)

        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount

    async def get_by_filter(
        self,
        filter_spec: "FilterSpec",
        offset: int = 0,
        limit: int = 100,
    ) -> list[T]:
        """Get entities using advanced filter specification.

        Supports: =, !=, >, >=, <, <=, IN, NOT IN, LIKE, ILIKE, IS NULL, BETWEEN
        """
        from app.domain.repositories.filter import FilterOperator

        stmt = select(self._model)

        # Apply filter conditions
        for condition in filter_spec.conditions:
            if not hasattr(self._model, condition.field):
                continue

            column = getattr(self._model, condition.field)
            op = condition.operator
            val = condition.value

            if op == FilterOperator.EQ:
                stmt = stmt.where(column == val)
            elif op == FilterOperator.NE:
                stmt = stmt.where(column != val)
            elif op == FilterOperator.GT:
                stmt = stmt.where(column > val)
            elif op == FilterOperator.GTE:
                stmt = stmt.where(column >= val)
            elif op == FilterOperator.LT:
                stmt = stmt.where(column < val)
            elif op == FilterOperator.LTE:
                stmt = stmt.where(column <= val)
            elif op == FilterOperator.IN:
                stmt = stmt.where(column.in_(val))
            elif op == FilterOperator.NOT_IN:
                stmt = stmt.where(column.not_in(val))
            elif op == FilterOperator.LIKE:
                stmt = stmt.where(column.like(val))
            elif op == FilterOperator.ILIKE:
                stmt = stmt.where(column.ilike(val))
            elif op == FilterOperator.IS_NULL:
                stmt = stmt.where(column.is_(None))
            elif op == FilterOperator.IS_NOT_NULL:
                stmt = stmt.where(column.isnot(None))
            elif op == FilterOperator.BETWEEN:
                stmt = stmt.where(column.between(val[0], val[1]))

        # Apply ordering
        for field, direction in filter_spec.order_by:
            if hasattr(self._model, field):
                column = getattr(self._model, field)
                stmt = stmt.order_by(column.desc() if direction == "desc" else column.asc())

        # Default ordering if not specified
        if not filter_spec.order_by:
            stmt = stmt.order_by(self._model.id.desc())

        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]
```

### Bulk Delete Usage Example

```python
# Delete all inactive users
deleted_count = await user_repo.delete_many(is_active=False)
print(f"Deleted {deleted_count} inactive users")

# Delete with multiple conditions
deleted_count = await product_repo.delete_many(
    status="draft",
    created_by=user_id,
)
```

### Advanced Filter Usage Example

```python
from app.domain.repositories.filter import FilterSpec

# Find products with price between $100-$500, in specific categories
spec = (
    FilterSpec()
    .between("price", 100, 500)
    .in_("category_id", [1, 2, 3])
    .eq("is_active", True)
    .like("name", "premium")
    .sort("price", "asc")
    .sort("created_at", "desc")
)

products = await product_repo.get_by_filter(spec, offset=0, limit=20)
```

### User Repository Implementation

```python
# app/infrastructure/repositories/user.py
from sqlalchemy import select, func, or_

from app.domain.entities.user import UserEntity
from app.domain.repositories.user import UserRepository
from app.infrastructure.database.models.user import UserModel
from app.infrastructure.repositories.base import SQLAlchemyRepository


class UserRepositoryImpl(SQLAlchemyRepository[UserEntity, UserModel], UserRepository):
    """User repository implementation."""

    def __init__(self, session) -> None:
        super().__init__(session, UserModel, UserEntity)

    async def get_by_email(self, email: str) -> UserEntity | None:
        """Get user by email."""
        result = await self._session.execute(
            select(self._model).where(self._model.email == email)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_username(self, username: str) -> UserEntity | None:
        """Get user by username."""
        result = await self._session.execute(
            select(self._model).where(self._model.username == username)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_active(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> list[UserEntity]:
        """List active users."""
        result = await self._session.execute(
            select(self._model)
            .where(self._model.is_active == True)
            .offset(offset)
            .limit(limit)
            .order_by(self._model.created_at.desc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def search(
        self,
        query: str,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[list[UserEntity], int]:
        """Search users by name or email."""
        search_filter = or_(
            self._model.name.ilike(f"%{query}%"),
            self._model.email.ilike(f"%{query}%"),
        )

        # Get total count
        count_result = await self._session.execute(
            select(func.count())
            .select_from(self._model)
            .where(search_filter)
        )
        total = count_result.scalar() or 0

        # Get paginated results
        result = await self._session.execute(
            select(self._model)
            .where(search_filter)
            .offset(offset)
            .limit(limit)
            .order_by(self._model.name)
        )
        users = [self._to_entity(m) for m in result.scalars().all()]

        return users, total
```

### Unit of Work

```python
# app/infrastructure/database/unit_of_work.py
from contextlib import asynccontextmanager
from typing import AsyncIterator, Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.repositories.user import UserRepository
from app.infrastructure.repositories.user import UserRepositoryImpl


class UnitOfWork:
    """Unit of Work for managing transactions.

    Provides atomic transaction boundaries for multi-repository operations.
    All repository operations within a transaction context share the same
    database session and will be committed or rolled back together.

    Usage patterns:
    1. Context manager (recommended for multi-repository ops):
       async with uow.transaction():
           await uow.users.create(...)
           await uow.orders.create(...)

    2. Dependency injection (auto-commit on success):
       async def get_uow() -> AsyncGenerator[UnitOfWork, None]:
           async with UnitOfWork(session) as uow:
               yield uow
               await uow.commit()
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._users: UserRepository | None = None

    @property
    def session(self) -> AsyncSession:
        """Access underlying session for advanced operations."""
        return self._session

    # === Lazy-loaded Repositories ===

    @property
    def users(self) -> UserRepository:
        """Get user repository (lazy-loaded)."""
        if self._users is None:
            self._users = UserRepositoryImpl(self._session)
        return self._users

    # Add more repositories as needed:
    # @property
    # def orders(self) -> OrderRepository:
    #     if self._orders is None:
    #         self._orders = OrderRepositoryImpl(self._session)
    #     return self._orders

    # === Transaction Management ===

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[None]:
        """Execute operations within a transaction.

        Commits on success, rolls back on exception.

        Example:
            async with uow.transaction():
                await uow.users.create(user)
                await uow.orders.create(order)
                # Both commit together or rollback together
        """
        try:
            yield
            await self._session.commit()
        except Exception:
            await self._session.rollback()
            raise

    async def commit(self) -> None:
        """Commit the current transaction."""
        await self._session.commit()

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        await self._session.rollback()

    # === Context Manager Protocol ===

    async def __aenter__(self) -> Self:
        """Enter context (session already provided)."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context with automatic rollback on error."""
        if exc_type:
            await self.rollback()
        await self._session.close()
```

### UoW Dependency

```python
# app/api/v1/dependencies/uow.py
from typing import Annotated, AsyncGenerator

from fastapi import Depends

from app.infrastructure.database.session import async_session_factory
from app.infrastructure.database.unit_of_work import UnitOfWork


async def get_uow() -> AsyncGenerator[UnitOfWork, None]:
    """Get Unit of Work dependency."""
    async with async_session_factory() as session:
        uow = UnitOfWork(session)
        try:
            yield uow
            await uow.commit()
        except Exception:
            await uow.rollback()
            raise


UoW = Annotated[UnitOfWork, Depends(get_uow)]
```

### 사용 예시

```python
# app/application/services/user.py
class UserService:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def transfer_role(
        self,
        from_user_id: int,
        to_user_id: int,
        role: str,
    ) -> None:
        """Transfer role from one user to another (atomic operation)."""
        from_user = await self._uow.users.get_by_id(from_user_id)
        to_user = await self._uow.users.get_by_id(to_user_id)

        if not from_user or not to_user:
            raise NotFoundError(resource="User", identifier=f"{from_user_id} or {to_user_id}")

        # Both updates happen in same transaction
        from_user.role = "user"
        to_user.role = role

        await self._uow.users.update(from_user_id, from_user)
        await self._uow.users.update(to_user_id, to_user)
        # Commit happens automatically via dependency
```

## References

- `_references/REPOSITORY-PATTERN.md`
