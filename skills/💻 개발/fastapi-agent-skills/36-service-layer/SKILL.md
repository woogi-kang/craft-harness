---
name: service-layer
description: |
  Clean Architecture의 Application Service 레이어 패턴을 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Service Layer Skill

Clean Architecture의 Application Service 레이어 패턴을 구현합니다.

## Triggers

- "서비스 레이어", "service layer", "use case", "application service", "비즈니스 로직"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |
| `featureName` | ✅ | 피처 이름 |

---

## Output

### Service Layer Architecture

```
app/
├── domain/                      # Domain Layer (innermost)
│   ├── entities/                # Domain entities
│   ├── repositories/            # Repository interfaces
│   └── services/                # Domain services
├── application/                 # Application Layer
│   ├── services/                # Application services (Use Cases)
│   ├── dto/                     # Data Transfer Objects
│   └── interfaces/              # External service interfaces
├── infrastructure/              # Infrastructure Layer
│   ├── repositories/            # Repository implementations
│   └── services/                # External service implementations
└── api/                         # Presentation Layer (outermost)
    └── v1/routes/               # API routes
```

### Base Application Service

```python
# app/application/services/base.py
from abc import ABC
from typing import Generic, TypeVar

import structlog

from app.domain.repositories.base import BaseRepository

T = TypeVar("T")
ID = TypeVar("ID")

logger = structlog.get_logger()


class ApplicationService(ABC, Generic[T, ID]):
    """Base application service with common CRUD operations.

    Responsibilities:
    - Orchestrate domain entities and repositories
    - Handle transaction boundaries
    - Coordinate cross-cutting concerns (logging, events)
    - Transform between DTOs and domain entities
    """

    def __init__(self, repository: BaseRepository[T, ID]) -> None:
        self._repository = repository

    async def get_by_id(self, id: ID) -> T | None:
        """Get entity by ID."""
        return await self._repository.get_by_id(id)

    async def get_by_id_or_raise(self, id: ID) -> T:
        """Get entity by ID or raise NotFoundError."""
        from app.core.exceptions import NotFoundError

        entity = await self._repository.get_by_id(id)
        if not entity:
            raise NotFoundError(resource=self._get_entity_name(), identifier=id)
        return entity

    async def list(
        self,
        offset: int = 0,
        limit: int = 20,
        **filters,
    ) -> tuple[list[T], int]:
        """List entities with pagination."""
        items = await self._repository.get_many(
            offset=offset,
            limit=limit,
            **filters,
        )
        total = await self._repository.count(**filters)
        return items, total

    async def create(self, data: dict) -> T:
        """Create a new entity."""
        entity = await self._repository.create(data)
        await self._on_created(entity)
        return entity

    async def update(self, id: ID, data: dict) -> T:
        """Update an existing entity."""
        entity = await self.get_by_id_or_raise(id)
        updated = await self._repository.update(id, data)
        await self._on_updated(entity, updated)
        return updated

    async def delete(self, id: ID) -> bool:
        """Delete an entity."""
        entity = await self.get_by_id_or_raise(id)
        result = await self._repository.delete(id)
        if result:
            await self._on_deleted(entity)
        return result

    def _get_entity_name(self) -> str:
        """Get entity name for error messages."""
        return "Entity"

    async def _on_created(self, entity: T) -> None:
        """Hook called after entity creation."""
        await logger.ainfo(
            f"{self._get_entity_name()} created",
            entity_id=getattr(entity, "id", None),
        )

    async def _on_updated(self, old: T, new: T) -> None:
        """Hook called after entity update."""
        await logger.ainfo(
            f"{self._get_entity_name()} updated",
            entity_id=getattr(new, "id", None),
        )

    async def _on_deleted(self, entity: T) -> None:
        """Hook called after entity deletion."""
        await logger.ainfo(
            f"{self._get_entity_name()} deleted",
            entity_id=getattr(entity, "id", None),
        )
```

### Use Case Pattern

```python
# app/application/use_cases/base.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

InputDTO = TypeVar("InputDTO")
OutputDTO = TypeVar("OutputDTO")


class UseCase(ABC, Generic[InputDTO, OutputDTO]):
    """Base use case (command/query handler).

    Use cases represent a single business operation.
    They are more specific than application services.
    """

    @abstractmethod
    async def execute(self, input_dto: InputDTO) -> OutputDTO:
        """Execute the use case."""
        ...
```

### Example: User Service

```python
# app/application/services/user.py
from typing import Sequence

from app.application.services.base import ApplicationService
from app.core.exceptions import AlreadyExistsError, ValidationError
from app.core.security import get_password_hash, verify_password
from app.domain.entities.user import UserEntity
from app.domain.repositories.user import UserRepository
from app.application.dto.user import UserCreateDTO, UserUpdateDTO

import structlog

logger = structlog.get_logger()


class UserService(ApplicationService[UserEntity, int]):
    """User application service."""

    def __init__(self, user_repository: UserRepository) -> None:
        super().__init__(user_repository)
        self._user_repository = user_repository

    def _get_entity_name(self) -> str:
        return "User"

    async def create_user(self, dto: UserCreateDTO) -> UserEntity:
        """Create a new user with validation."""
        # Check if email already exists
        existing = await self._user_repository.get_by_email(dto.email)
        if existing:
            raise AlreadyExistsError(resource="User", identifier=dto.email)

        # Hash password
        hashed_password = get_password_hash(dto.password)

        # Create user
        user = await self._user_repository.create({
            "email": dto.email,
            "name": dto.name,
            "hashed_password": hashed_password,
            "is_active": True,
        })

        await logger.ainfo("User created", user_id=user.id, email=user.email)

        return user

    async def update_user(self, user_id: int, dto: UserUpdateDTO) -> UserEntity:
        """Update user with validation."""
        user = await self.get_by_id_or_raise(user_id)

        # Check email uniqueness if changing
        if dto.email and dto.email != user.email:
            existing = await self._user_repository.get_by_email(dto.email)
            if existing:
                raise AlreadyExistsError(resource="User", identifier=dto.email)

        # Build update data
        update_data = dto.model_dump(exclude_unset=True)

        return await self._user_repository.update(user_id, update_data)

    async def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str,
    ) -> None:
        """Change user password with verification."""
        user = await self.get_by_id_or_raise(user_id)

        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise ValidationError("Current password is incorrect")

        # Hash and update new password
        hashed_password = get_password_hash(new_password)
        await self._user_repository.update(
            user_id,
            {"hashed_password": hashed_password},
        )

        await logger.ainfo("Password changed", user_id=user_id)

    async def deactivate_user(self, user_id: int) -> UserEntity:
        """Deactivate a user account."""
        user = await self.get_by_id_or_raise(user_id)

        if not user.is_active:
            raise ValidationError("User is already deactivated")

        updated = await self._user_repository.update(
            user_id,
            {"is_active": False},
        )

        await logger.ainfo("User deactivated", user_id=user_id)

        return updated

    async def get_by_email(self, email: str) -> UserEntity | None:
        """Get user by email."""
        return await self._user_repository.get_by_email(email)

    async def search_users(
        self,
        query: str,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[UserEntity], int]:
        """Search users by name or email."""
        return await self._user_repository.search(
            query=query,
            offset=offset,
            limit=limit,
        )
```

### DTOs (Data Transfer Objects)

```python
# app/application/dto/user.py
from pydantic import BaseModel, EmailStr, Field


class UserCreateDTO(BaseModel):
    """DTO for creating a user."""

    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8)


class UserUpdateDTO(BaseModel):
    """DTO for updating a user."""

    email: EmailStr | None = None
    name: str | None = Field(default=None, min_length=1, max_length=100)


class UserResponseDTO(BaseModel):
    """DTO for user response."""

    id: int
    email: str
    name: str
    is_active: bool

    class Config:
        from_attributes = True
```

### Service with Unit of Work

```python
# app/application/services/order.py
from app.application.services.base import ApplicationService
from app.domain.entities.order import OrderEntity
from app.domain.repositories.order import OrderRepository
from app.domain.repositories.product import ProductRepository
from app.domain.repositories.inventory import InventoryRepository
from app.infrastructure.database.unit_of_work import UnitOfWork
from app.core.exceptions import ValidationError

import structlog

logger = structlog.get_logger()


class OrderService(ApplicationService[OrderEntity, int]):
    """Order service with transaction coordination."""

    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        inventory_repository: InventoryRepository,
        uow: UnitOfWork,
    ) -> None:
        super().__init__(order_repository)
        self._order_repository = order_repository
        self._product_repository = product_repository
        self._inventory_repository = inventory_repository
        self._uow = uow

    def _get_entity_name(self) -> str:
        return "Order"

    async def create_order(
        self,
        user_id: int,
        items: list[dict],
    ) -> OrderEntity:
        """Create order with inventory reservation.

        Uses Unit of Work pattern for transaction management.
        """
        async with self._uow.transaction():
            # Validate products and calculate total
            total = 0
            order_items = []

            for item in items:
                product = await self._product_repository.get_by_id(item["product_id"])
                if not product:
                    raise ValidationError(f"Product not found: {item['product_id']}")

                # Check inventory
                inventory = await self._inventory_repository.get_by_product_id(
                    item["product_id"]
                )
                if not inventory or inventory.quantity < item["quantity"]:
                    raise ValidationError(f"Insufficient inventory for: {product.name}")

                # Reserve inventory
                await self._inventory_repository.decrease_quantity(
                    item["product_id"],
                    item["quantity"],
                )

                order_items.append({
                    "product_id": item["product_id"],
                    "quantity": item["quantity"],
                    "price": product.price,
                })
                total += product.price * item["quantity"]

            # Create order
            order = await self._order_repository.create({
                "user_id": user_id,
                "items": order_items,
                "total": total,
                "status": "pending",
            })

            await logger.ainfo(
                "Order created",
                order_id=order.id,
                user_id=user_id,
                total=total,
            )

            return order

    async def cancel_order(self, order_id: int) -> OrderEntity:
        """Cancel order and restore inventory."""
        async with self._uow.transaction():
            order = await self.get_by_id_or_raise(order_id)

            if order.status not in ("pending", "confirmed"):
                raise ValidationError(f"Cannot cancel order in {order.status} status")

            # Restore inventory
            for item in order.items:
                await self._inventory_repository.increase_quantity(
                    item["product_id"],
                    item["quantity"],
                )

            # Update order status
            updated = await self._order_repository.update(
                order_id,
                {"status": "cancelled"},
            )

            await logger.ainfo("Order cancelled", order_id=order_id)

            return updated
```

### Unit of Work Pattern

The Unit of Work pattern is essential for coordinating **multi-repository transactions**.
Use it when a business operation needs to update multiple aggregates atomically.

**When to use UnitOfWork:**
- Multi-repository operations (OrderService: orders + inventory + products)
- Operations requiring atomic commit/rollback across entities
- Complex domain operations with multiple side effects

**When NOT to use UnitOfWork:**
- Single-repository operations (UserService: users only)
- Read-only operations
- Simple CRUD without cross-entity dependencies

```python
# app/infrastructure/database/unit_of_work.py
from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import async_session_factory


class UnitOfWork:
    """Unit of Work for transaction management.

    Provides atomic transaction boundaries for multi-repository operations.
    All repository operations within a transaction context share the same
    database session and will be committed or rolled back together.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @property
    def session(self) -> AsyncSession:
        """Access to underlying session for repository injection."""
        return self._session

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[None]:
        """Execute within a transaction.

        Commits on success, rolls back on exception.

        Example:
            async with uow.transaction():
                await repo1.create(...)
                await repo2.update(...)
                # Both operations commit together or rollback together
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
```

### Enhanced UoW with Repository Factory

For complex services with many repositories, use a repository factory pattern:

```python
# app/infrastructure/database/unit_of_work.py
from contextlib import asynccontextmanager
from typing import AsyncIterator, Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.repositories.user import UserRepositoryInterface
from app.domain.repositories.order import OrderRepositoryInterface
from app.domain.repositories.product import ProductRepositoryInterface
from app.domain.repositories.inventory import InventoryRepositoryInterface
from app.infrastructure.repositories.user import SQLAlchemyUserRepository
from app.infrastructure.repositories.order import SQLAlchemyOrderRepository
from app.infrastructure.repositories.product import SQLAlchemyProductRepository
from app.infrastructure.repositories.inventory import SQLAlchemyInventoryRepository


class UnitOfWorkWithRepositories:
    """Unit of Work with repository factory.

    Provides lazy-loaded repositories that all share the same session.
    Useful for services that need multiple repositories.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    # Lazy-loaded repositories (created on first access)
    @property
    def users(self) -> UserRepositoryInterface:
        return SQLAlchemyUserRepository(self._session)

    @property
    def orders(self) -> OrderRepositoryInterface:
        return SQLAlchemyOrderRepository(self._session)

    @property
    def products(self) -> ProductRepositoryInterface:
        return SQLAlchemyProductRepository(self._session)

    @property
    def inventory(self) -> InventoryRepositoryInterface:
        return SQLAlchemyInventoryRepository(self._session)

    async def __aenter__(self) -> Self:
        """Start a new unit of work."""
        self._session = self._session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """End the unit of work."""
        if exc_type:
            await self.rollback()
        await self._session.close()

    async def commit(self) -> None:
        """Commit all changes."""
        await self._session.commit()

    async def rollback(self) -> None:
        """Rollback all changes."""
        await self._session.rollback()


# Usage example in service
class OrderServiceWithUoW:
    """Order service using repository factory UoW."""

    def __init__(self, uow_factory: async_sessionmaker[AsyncSession]) -> None:
        self._uow_factory = uow_factory

    async def create_order(self, user_id: int, items: list[dict]) -> OrderEntity:
        """Create order with full atomic transaction."""
        async with UnitOfWorkWithRepositories(self._uow_factory) as uow:
            # All repositories share the same session
            user = await uow.users.get_by_id(user_id)
            if not user:
                raise NotFoundError("User", user_id)

            order_items = []
            total = 0

            for item in items:
                product = await uow.products.get_by_id(item["product_id"])
                inventory = await uow.inventory.get_by_product_id(item["product_id"])

                if inventory.quantity < item["quantity"]:
                    raise ValidationError(f"Insufficient inventory: {product.name}")

                await uow.inventory.decrease_quantity(
                    item["product_id"],
                    item["quantity"],
                )

                order_items.append({...})
                total += product.price * item["quantity"]

            order = await uow.orders.create({
                "user_id": user_id,
                "items": order_items,
                "total": total,
                "status": "pending",
            })

            # Commit all changes atomically
            await uow.commit()

            return order
```

### Service Dependencies

```python
# app/api/v1/dependencies/services.py
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.database import get_async_session
from app.application.services.user import UserService
from app.application.services.order import OrderService
from app.infrastructure.database.unit_of_work import UnitOfWork
from app.infrastructure.repositories.user import SQLAlchemyUserRepository
from app.infrastructure.repositories.order import SQLAlchemyOrderRepository
from app.infrastructure.repositories.product import SQLAlchemyProductRepository
from app.infrastructure.repositories.inventory import SQLAlchemyInventoryRepository


async def get_user_service(
    session: AsyncSession = Depends(get_async_session),
) -> UserService:
    """Get user service with injected dependencies."""
    repository = SQLAlchemyUserRepository(session)
    return UserService(repository)


async def get_order_service(
    session: AsyncSession = Depends(get_async_session),
) -> OrderService:
    """Get order service with injected dependencies."""
    return OrderService(
        order_repository=SQLAlchemyOrderRepository(session),
        product_repository=SQLAlchemyProductRepository(session),
        inventory_repository=SQLAlchemyInventoryRepository(session),
        uow=UnitOfWork(session),
    )


# Type aliases for cleaner route signatures
UserSvc = Annotated[UserService, Depends(get_user_service)]
OrderSvc = Annotated[OrderService, Depends(get_order_service)]
```

### Using Services in Routes

```python
# app/api/v1/routes/users.py
from fastapi import APIRouter, status

from app.api.v1.dependencies import CurrentUser, UserSvc
from app.application.dto.user import UserCreateDTO, UserUpdateDTO, UserResponseDTO
from app.application.schemas.response import APIResponse
from app.application.schemas.pagination import PaginatedResponse, PaginationParams

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=APIResponse[UserResponseDTO],
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_in: UserCreateDTO,
    service: UserSvc,
):
    """Create a new user."""
    user = await service.create_user(user_in)
    return APIResponse(data=UserResponseDTO.model_validate(user))


@router.get("/{user_id}", response_model=APIResponse[UserResponseDTO])
async def get_user(
    user_id: int,
    service: UserSvc,
    _: CurrentUser,
):
    """Get user by ID."""
    user = await service.get_by_id_or_raise(user_id)
    return APIResponse(data=UserResponseDTO.model_validate(user))


@router.patch("/{user_id}", response_model=APIResponse[UserResponseDTO])
async def update_user(
    user_id: int,
    user_in: UserUpdateDTO,
    service: UserSvc,
    current_user: CurrentUser,
):
    """Update user."""
    user = await service.update_user(user_id, user_in)
    return APIResponse(data=UserResponseDTO.model_validate(user))
```

## Domain Events Pattern

Domain Events enable decoupled communication between aggregates and support eventual consistency.

### Event Infrastructure

```python
# app/domain/events/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Coroutine
from uuid import UUID, uuid4

import structlog

logger = structlog.get_logger()


@dataclass(frozen=True)
class DomainEvent(ABC):
    """Base class for domain events.

    Events are immutable records of something that happened.
    """

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    @abstractmethod
    def event_type(self) -> str:
        """Unique event type identifier."""
        ...


# Type alias for event handlers
EventHandler = Callable[[DomainEvent], Coroutine[Any, Any, None]]


class EventPublisher:
    """In-memory event publisher with handler registration.

    For production, consider using:
    - Redis Pub/Sub for multi-instance apps
    - RabbitMQ/Kafka for reliable messaging
    - AWS SNS/SQS for cloud-native apps
    """

    _handlers: dict[str, list[EventHandler]] = {}

    @classmethod
    def subscribe(cls, event_type: str, handler: EventHandler) -> None:
        """Register a handler for an event type."""
        if event_type not in cls._handlers:
            cls._handlers[event_type] = []
        cls._handlers[event_type].append(handler)

    @classmethod
    async def publish(cls, event: DomainEvent) -> None:
        """Publish an event to all registered handlers."""
        handlers = cls._handlers.get(event.event_type, [])

        await logger.ainfo(
            "Publishing domain event",
            event_type=event.event_type,
            event_id=str(event.event_id),
            handler_count=len(handlers),
        )

        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                await logger.aexception(
                    "Event handler failed",
                    event_type=event.event_type,
                    handler=handler.__name__,
                    error=str(e),
                )
                # Continue with other handlers

    @classmethod
    def clear(cls) -> None:
        """Clear all handlers (useful for testing)."""
        cls._handlers.clear()
```

### Domain Event Definitions

```python
# app/domain/events/user.py
from dataclasses import dataclass

from app.domain.events.base import DomainEvent


@dataclass(frozen=True)
class UserCreatedEvent(DomainEvent):
    """Fired when a new user is created."""

    user_id: int
    email: str
    name: str

    @property
    def event_type(self) -> str:
        return "user.created"


@dataclass(frozen=True)
class UserActivatedEvent(DomainEvent):
    """Fired when a user account is activated."""

    user_id: int

    @property
    def event_type(self) -> str:
        return "user.activated"


@dataclass(frozen=True)
class UserDeactivatedEvent(DomainEvent):
    """Fired when a user account is deactivated."""

    user_id: int
    reason: str | None = None

    @property
    def event_type(self) -> str:
        return "user.deactivated"


@dataclass(frozen=True)
class PasswordChangedEvent(DomainEvent):
    """Fired when a user changes their password."""

    user_id: int

    @property
    def event_type(self) -> str:
        return "user.password_changed"


# app/domain/events/order.py
@dataclass(frozen=True)
class OrderCreatedEvent(DomainEvent):
    """Fired when a new order is created."""

    order_id: int
    user_id: int
    total: float
    item_count: int

    @property
    def event_type(self) -> str:
        return "order.created"


@dataclass(frozen=True)
class OrderCancelledEvent(DomainEvent):
    """Fired when an order is cancelled."""

    order_id: int
    user_id: int
    reason: str | None = None

    @property
    def event_type(self) -> str:
        return "order.cancelled"
```

### Service with Event Publishing

```python
# app/application/services/user.py
from app.domain.events.base import EventPublisher
from app.domain.events.user import (
    UserCreatedEvent,
    UserDeactivatedEvent,
    PasswordChangedEvent,
)


class UserService(ApplicationService[UserEntity, int]):
    """User service with domain event publishing."""

    async def create_user(self, dto: UserCreateDTO) -> UserEntity:
        """Create a new user and publish event."""
        # ... validation and creation logic ...

        user = await self._user_repository.create({...})

        # Publish domain event
        await EventPublisher.publish(
            UserCreatedEvent(
                user_id=user.id,
                email=user.email,
                name=user.name,
            )
        )

        return user

    async def deactivate_user(self, user_id: int, reason: str | None = None) -> UserEntity:
        """Deactivate user and publish event."""
        user = await self.get_by_id_or_raise(user_id)

        updated = await self._user_repository.update(
            user_id,
            {"is_active": False},
        )

        # Publish domain event
        await EventPublisher.publish(
            UserDeactivatedEvent(user_id=user_id, reason=reason)
        )

        return updated

    async def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str,
    ) -> None:
        """Change password and publish event."""
        # ... password change logic ...

        await EventPublisher.publish(
            PasswordChangedEvent(user_id=user_id)
        )
```

### Event Handlers

```python
# app/application/handlers/user_handlers.py
import structlog

from app.domain.events.base import EventPublisher
from app.domain.events.user import UserCreatedEvent, UserDeactivatedEvent

logger = structlog.get_logger()


async def send_welcome_email(event: UserCreatedEvent) -> None:
    """Send welcome email when user is created."""
    await logger.ainfo(
        "Sending welcome email",
        user_id=event.user_id,
        email=event.email,
    )
    # await email_service.send_welcome(event.email, event.name)


async def update_analytics(event: UserCreatedEvent) -> None:
    """Update analytics when user is created."""
    await logger.ainfo(
        "Updating analytics for new user",
        user_id=event.user_id,
    )
    # await analytics_service.track_signup(event.user_id)


async def notify_admin_on_deactivation(event: UserDeactivatedEvent) -> None:
    """Notify admin when user is deactivated."""
    await logger.ainfo(
        "Notifying admin of user deactivation",
        user_id=event.user_id,
        reason=event.reason,
    )
    # await notification_service.notify_admin(...)


# Register handlers
def register_user_handlers() -> None:
    """Register all user event handlers."""
    EventPublisher.subscribe("user.created", send_welcome_email)
    EventPublisher.subscribe("user.created", update_analytics)
    EventPublisher.subscribe("user.deactivated", notify_admin_on_deactivation)
```

### Handler Registration in App Startup

```python
# app/main.py
from contextlib import asynccontextmanager

from app.application.handlers.user_handlers import register_user_handlers
from app.application.handlers.order_handlers import register_order_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Register event handlers
    register_user_handlers()
    register_order_handlers()

    yield

    # Shutdown: Clean up
    EventPublisher.clear()
```

### Testing Events

```python
# tests/unit/test_user_service.py
import pytest
from unittest.mock import AsyncMock

from app.domain.events.base import EventPublisher
from app.domain.events.user import UserCreatedEvent


@pytest.fixture(autouse=True)
def clear_event_handlers():
    """Clear handlers before each test."""
    EventPublisher.clear()
    yield
    EventPublisher.clear()


async def test_user_creation_publishes_event(user_service, mock_repository):
    """Test that creating a user publishes UserCreatedEvent."""
    # Arrange
    handler = AsyncMock()
    EventPublisher.subscribe("user.created", handler)

    # Act
    user = await user_service.create_user(UserCreateDTO(...))

    # Assert
    handler.assert_called_once()
    event = handler.call_args[0][0]
    assert isinstance(event, UserCreatedEvent)
    assert event.user_id == user.id
    assert event.email == user.email
```

## Service Layer Best Practices

| Practice | Description |
|----------|-------------|
| Single Responsibility | Each service handles one domain aggregate |
| Transaction Boundaries | Services define transaction scope |
| DTO Conversion | Convert between DTOs and domain entities |
| Validation | Validate business rules before operations |
| Event Publishing | Publish domain events after state changes |
| Error Handling | Throw domain-specific exceptions |

## References

- `_references/ARCHITECTURE-PATTERN.md`
- `_references/REPOSITORY-PATTERN.md`
