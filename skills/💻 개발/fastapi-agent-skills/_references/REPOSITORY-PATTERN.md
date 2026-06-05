# Repository Pattern Reference

FastAPI 프로젝트의 Repository Pattern 구현 가이드입니다.

## Pattern Overview

```
┌─────────────────┐     ┌─────────────────────┐     ┌─────────────────┐
│  Application    │────▶│  Repository         │────▶│  Database       │
│  Service        │     │  Interface          │     │  (SQLAlchemy)   │
└─────────────────┘     └─────────────────────┘     └─────────────────┘
                               ▲
                               │
                        ┌──────┴──────┐
                        │ Repository  │
                        │ Impl        │
                        └─────────────┘
```

## Repository Interface (Domain Layer)

```python
# app/domain/repositories/base.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class RepositoryInterface(ABC, Generic[T]):
    """Base repository interface."""

    @abstractmethod
    async def get_by_id(self, session, entity_id: int) -> T | None:
        """Get entity by ID."""
        pass

    @abstractmethod
    async def create(self, session, entity: T) -> T:
        """Create a new entity."""
        pass

    @abstractmethod
    async def update(self, session, entity: T) -> T:
        """Update an existing entity."""
        pass

    @abstractmethod
    async def delete(self, session, entity: T) -> bool:
        """Delete an entity."""
        pass

    @abstractmethod
    async def list_all(self, session) -> list[T]:
        """List all entities."""
        pass
```

```python
# app/domain/repositories/user.py
from abc import abstractmethod

from app.domain.entities.user import User
from app.domain.repositories.base import RepositoryInterface


class UserRepositoryInterface(RepositoryInterface[User]):
    """User repository interface."""

    @abstractmethod
    async def get_by_email(self, session, email: str) -> User | None:
        """Get user by email."""
        pass

    @abstractmethod
    async def get_active_users(self, session) -> list[User]:
        """Get all active users."""
        pass

    @abstractmethod
    async def exists(self, session, user_id: int) -> bool:
        """Check if user exists."""
        pass
```

## Repository Implementation (Infrastructure Layer)

```python
# app/infrastructure/repositories/base.py
from typing import Generic, TypeVar

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")  # Entity type
M = TypeVar("M")  # Model type


class BaseRepository(Generic[T, M]):
    """Base SQLAlchemy repository implementation."""

    model_class: type[M]

    def __init__(self):
        if not hasattr(self, 'model_class'):
            raise NotImplementedError("Subclass must define model_class")

    async def get_by_id(self, session: AsyncSession, entity_id: int) -> T | None:
        result = await session.execute(
            select(self.model_class).where(self.model_class.id == entity_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, session: AsyncSession, entity: T) -> T:
        model = self._to_model(entity)
        session.add(model)
        await session.flush()
        await session.refresh(model)
        return self._to_entity(model)

    async def update(self, session: AsyncSession, entity: T) -> T:
        model = await session.get(self.model_class, entity.id)
        if model:
            self._update_model(model, entity)
            await session.flush()
            await session.refresh(model)
            return self._to_entity(model)
        raise ValueError(f"Entity with id {entity.id} not found")

    async def delete(self, session: AsyncSession, entity: T) -> bool:
        result = await session.execute(
            delete(self.model_class).where(self.model_class.id == entity.id)
        )
        return result.rowcount > 0

    async def list_all(self, session: AsyncSession) -> list[T]:
        result = await session.execute(select(self.model_class))
        return [self._to_entity(m) for m in result.scalars().all()]

    def _to_entity(self, model: M) -> T:
        """Convert ORM model to domain entity."""
        raise NotImplementedError

    def _to_model(self, entity: T) -> M:
        """Convert domain entity to ORM model."""
        raise NotImplementedError

    def _update_model(self, model: M, entity: T) -> None:
        """Update ORM model from entity."""
        raise NotImplementedError
```

```python
# app/infrastructure/repositories/user.py
from sqlalchemy import select, exists as sql_exists
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.repositories.user import UserRepositoryInterface
from app.infrastructure.database.models.user import UserModel
from app.infrastructure.repositories.base import BaseRepository


class UserRepository(BaseRepository[User, UserModel], UserRepositoryInterface):
    """SQLAlchemy implementation of UserRepository."""

    model_class = UserModel

    async def get_by_email(self, session: AsyncSession, email: str) -> User | None:
        result = await session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_active_users(self, session: AsyncSession) -> list[User]:
        result = await session.execute(
            select(UserModel).where(UserModel.is_active == True)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def exists(self, session: AsyncSession, user_id: int) -> bool:
        result = await session.execute(
            select(sql_exists().where(UserModel.id == user_id))
        )
        return result.scalar() or False

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            name=model.name,
            hashed_password=model.hashed_password,
            is_active=model.is_active,
            is_superuser=model.is_superuser,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            email=entity.email,
            name=entity.name,
            hashed_password=entity.hashed_password,
            is_active=entity.is_active,
            is_superuser=entity.is_superuser,
        )

    def _update_model(self, model: UserModel, entity: User) -> None:
        model.email = entity.email
        model.name = entity.name
        model.hashed_password = entity.hashed_password
        model.is_active = entity.is_active
        model.is_superuser = entity.is_superuser
```

## Pagination Support

```python
# app/infrastructure/repositories/base.py (extended)
from typing import Sequence

from sqlalchemy import func


class PaginatedRepository(BaseRepository[T, M]):
    """Repository with pagination support."""

    async def list_paginated(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[T], int]:
        """Get paginated list with total count."""
        # Count total
        count_result = await session.execute(
            select(func.count()).select_from(self.model_class)
        )
        total = count_result.scalar() or 0

        # Get page
        result = await session.execute(
            select(self.model_class)
            .offset(offset)
            .limit(limit)
            .order_by(self.model_class.id)
        )
        items = [self._to_entity(m) for m in result.scalars().all()]

        return items, total
```

## Specification Pattern

```python
# app/domain/specifications/base.py
from abc import ABC, abstractmethod
from typing import Any


class Specification(ABC):
    """Base specification for filtering."""

    @abstractmethod
    def to_expression(self) -> Any:
        """Convert to SQLAlchemy expression."""
        pass

    def __and__(self, other: "Specification") -> "AndSpecification":
        return AndSpecification(self, other)

    def __or__(self, other: "Specification") -> "OrSpecification":
        return OrSpecification(self, other)


class AndSpecification(Specification):
    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right

    def to_expression(self):
        from sqlalchemy import and_
        return and_(self.left.to_expression(), self.right.to_expression())


class OrSpecification(Specification):
    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right

    def to_expression(self):
        from sqlalchemy import or_
        return or_(self.left.to_expression(), self.right.to_expression())
```

```python
# app/domain/specifications/user.py
from app.domain.specifications.base import Specification
from app.infrastructure.database.models.user import UserModel


class IsActiveSpecification(Specification):
    def to_expression(self):
        return UserModel.is_active == True


class EmailContainsSpecification(Specification):
    def __init__(self, search: str):
        self.search = search

    def to_expression(self):
        return UserModel.email.ilike(f"%{self.search}%")


class NameContainsSpecification(Specification):
    def __init__(self, search: str):
        self.search = search

    def to_expression(self):
        return UserModel.name.ilike(f"%{self.search}%")


# Usage
spec = IsActiveSpecification() & EmailContainsSpecification("@example.com")
```

## Unit of Work Integration

```python
# app/infrastructure/database/unit_of_work.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.user import UserRepositoryInterface
from app.infrastructure.repositories.user import UserRepository


class UnitOfWork:
    """Unit of Work for transaction management."""

    def __init__(self, session: AsyncSession):
        self._session = session
        self.users: UserRepositoryInterface = UserRepository()

    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
```

## Transaction Rollback Scenarios

트랜잭션 롤백이 필요한 시나리오와 처리 방법입니다.

### Scenario 1: Business Rule Violation

```python
# app/application/services/order.py
class OrderService:
    """Order service with transaction rollback on business rule violation."""

    async def create_order(
        self,
        user_id: int,
        items: list[OrderItemCreate],
    ) -> Order:
        """Create order with inventory reservation.

        Rollback scenarios:
        - Insufficient inventory
        - Invalid product
        - User credit limit exceeded
        """
        async with self._uow.transaction():
            # 1. Validate user credit
            user = await self._user_repo.get_by_id(user_id)
            if not user:
                raise NotFoundError("User", user_id)

            total = await self._calculate_total(items)
            if user.credit_limit < total:
                # Transaction will rollback - no inventory deducted
                raise ValidationError("Credit limit exceeded")

            # 2. Reserve inventory (updates DB)
            for item in items:
                product = await self._product_repo.get_by_id(item.product_id)
                if not product:
                    raise NotFoundError("Product", item.product_id)

                inventory = await self._inventory_repo.get_by_product_id(item.product_id)
                if inventory.quantity < item.quantity:
                    # Transaction will rollback - previous inventory updates reverted
                    raise ValidationError(f"Insufficient inventory for {product.name}")

                await self._inventory_repo.decrease_quantity(
                    item.product_id,
                    item.quantity,
                )

            # 3. Create order
            order = await self._order_repo.create({
                "user_id": user_id,
                "items": items,
                "total": total,
                "status": "pending",
            })

            return order
```

### Scenario 2: External Service Failure

```python
# app/application/services/payment.py
class PaymentService:
    """Payment service with rollback on external service failure."""

    async def process_payment(
        self,
        order_id: int,
        payment_method: PaymentMethod,
    ) -> PaymentResult:
        """Process payment with compensation on failure.

        Rollback scenarios:
        - Payment gateway timeout
        - Payment declined
        - Network error
        """
        async with self._uow.transaction():
            order = await self._order_repo.get_by_id(order_id)
            if not order:
                raise NotFoundError("Order", order_id)

            # 1. Reserve funds (internal)
            await self._order_repo.update(
                order_id,
                {"status": "payment_processing"},
            )

            try:
                # 2. Call external payment gateway
                payment_result = await self._payment_gateway.charge(
                    amount=order.total,
                    method=payment_method,
                    idempotency_key=f"order-{order_id}",
                )

                if not payment_result.success:
                    # Payment declined - rollback order status
                    raise PaymentDeclinedError(payment_result.error)

                # 3. Confirm payment
                await self._order_repo.update(
                    order_id,
                    {
                        "status": "paid",
                        "payment_id": payment_result.transaction_id,
                    },
                )

                return payment_result

            except PaymentGatewayError as e:
                # External service error - transaction will rollback
                # Order status reverts to previous state
                await logger.aerror(
                    "Payment gateway error",
                    order_id=order_id,
                    error=str(e),
                )
                raise
```

### Scenario 3: Partial Failure with Compensation

```python
# app/application/services/transfer.py
class TransferService:
    """Money transfer with saga pattern for partial failures."""

    async def transfer_funds(
        self,
        from_account_id: int,
        to_account_id: int,
        amount: Decimal,
    ) -> TransferResult:
        """Transfer funds between accounts.

        Uses saga pattern for cross-aggregate transactions.
        """
        # Start saga
        saga_id = await self._saga_repo.create({
            "type": "fund_transfer",
            "status": "started",
            "steps_completed": [],
        })

        try:
            async with self._uow.transaction():
                # Step 1: Debit source account
                source = await self._account_repo.get_by_id(from_account_id)
                if source.balance < amount:
                    raise ValidationError("Insufficient funds")

                await self._account_repo.update(
                    from_account_id,
                    {"balance": source.balance - amount},
                )
                await self._saga_repo.add_step(saga_id, "debit_completed")

                # Step 2: Credit destination account
                dest = await self._account_repo.get_by_id(to_account_id)
                if not dest:
                    # Destination not found - rollback debit
                    raise NotFoundError("Account", to_account_id)

                await self._account_repo.update(
                    to_account_id,
                    {"balance": dest.balance + amount},
                )
                await self._saga_repo.add_step(saga_id, "credit_completed")

                # Complete saga
                await self._saga_repo.update(saga_id, {"status": "completed"})

                return TransferResult(success=True, saga_id=saga_id)

        except Exception as e:
            # Transaction rolled back - update saga status
            await self._saga_repo.update(saga_id, {
                "status": "failed",
                "error": str(e),
            })
            raise
```

### Scenario 4: Deadlock Handling

```python
# app/infrastructure/repositories/base.py
from sqlalchemy.exc import OperationalError

class RetryableRepository:
    """Repository with deadlock retry logic."""

    MAX_RETRIES = 3
    RETRY_DELAY = 0.1  # seconds

    async def with_retry(
        self,
        operation: Callable[[], Awaitable[T]],
    ) -> T:
        """Execute operation with deadlock retry.

        Handles:
        - Deadlock (error code 1213 in MySQL, 40P01 in PostgreSQL)
        - Lock wait timeout
        """
        import asyncio

        for attempt in range(self.MAX_RETRIES):
            try:
                return await operation()

            except OperationalError as e:
                is_deadlock = (
                    "deadlock" in str(e).lower() or
                    "40P01" in str(e) or  # PostgreSQL
                    "1213" in str(e)      # MySQL
                )

                if is_deadlock and attempt < self.MAX_RETRIES - 1:
                    await logger.awarning(
                        "Deadlock detected, retrying",
                        attempt=attempt + 1,
                        max_retries=self.MAX_RETRIES,
                    )
                    await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))
                    continue

                raise

        raise RuntimeError("Max retries exceeded")
```

### Rollback Summary

| Scenario | Trigger | Behavior |
|----------|---------|----------|
| **Business Rule** | ValidationError | Auto-rollback via UoW context |
| **Not Found** | NotFoundError | Auto-rollback, preserve data integrity |
| **External Service** | PaymentGatewayError | Rollback internal changes |
| **Partial Failure** | Any exception | Saga compensation pattern |
| **Deadlock** | OperationalError | Retry with backoff |

### Testing Rollback

```python
# tests/integration/test_order_rollback.py
async def test_order_rollback_on_insufficient_inventory(
    order_service: OrderService,
    session: AsyncSession,
):
    """Test that order creation rolls back on insufficient inventory."""
    # Arrange
    product = await create_product(session, quantity=5)
    initial_quantity = product.quantity

    # Act & Assert
    with pytest.raises(ValidationError, match="Insufficient inventory"):
        await order_service.create_order(
            user_id=1,
            items=[OrderItemCreate(product_id=product.id, quantity=10)],
        )

    # Verify rollback - quantity unchanged
    await session.refresh(product)
    assert product.quantity == initial_quantity
```

## Key Principles

| Principle | Description |
|-----------|-------------|
| **Abstraction** | Domain layer uses interfaces, not implementations |
| **Encapsulation** | Data access logic is hidden from domain |
| **Testability** | Easy to mock repositories in tests |
| **Single Responsibility** | One repository per aggregate root |
| **Entity Mapping** | ORM models ↔ Domain entities conversion |

## Related Skills

- `16-repository-pattern`: Full implementation
- `17-unit-of-work`: Transaction management
- `18-query-optimization`: Performance optimization
