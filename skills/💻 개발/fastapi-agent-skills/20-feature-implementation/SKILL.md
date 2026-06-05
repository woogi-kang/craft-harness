---
name: feature-implementation
description: |
  Clean Architecture 기반 피처 구현 패턴을 제공합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Feature Implementation Skill

Clean Architecture 기반 피처 구현 패턴을 제공합니다.

## Triggers

- "피처 구현", "feature", "기능 구현", "도메인 구현"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |
| `featureName` | ✅ | 피처 이름 (예: product, order) |

---

## Output

### Feature 디렉토리 구조

```
app/
├── domain/
│   ├── entities/
│   │   └── {feature}.py          # Domain Entity
│   └── repositories/
│       └── {feature}.py          # Repository Interface
├── application/
│   └── services/
│       └── {feature}.py          # Business Logic
├── infrastructure/
│   ├── database/
│   │   └── models/
│   │       └── {feature}.py      # ORM Model
│   └── repositories/
│       └── {feature}.py          # Repository Implementation
├── api/
│   └── v1/
│       ├── routes/
│       │   └── {feature}.py      # API Routes
│       └── dependencies/
│           └── {feature}.py      # Feature Dependencies
└── schemas/
    └── {feature}.py              # Pydantic Schemas
```

### 1. Domain Entity

```python
# app/domain/entities/product.py
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, computed_field


class ProductStatus(str, Enum):
    """Product status enum."""

    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"


class ProductEntity(BaseModel):
    """Product domain entity.

    Uses Pydantic BaseModel for:
    - Built-in validation
    - Easy serialization/deserialization
    - ORM integration via from_attributes
    - Immutable pattern with model_copy()
    """

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    name: str = ""
    description: str = ""
    sku: str = ""
    price: Decimal = Decimal("0.00")
    quantity: int = 0
    status: ProductStatus = ProductStatus.DRAFT
    category_id: int | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @computed_field
    @property
    def is_available(self) -> bool:
        """Check if product is available for purchase."""
        return self.status == ProductStatus.ACTIVE and self.quantity > 0

    @computed_field
    @property
    def is_low_stock(self) -> bool:
        """Check if product has low stock (less than 10 items)."""
        return self.quantity < 10

    def reduce_quantity(self, amount: int) -> Self:
        """Reduce product quantity (immutable).

        Returns:
            New ProductEntity with reduced quantity.

        Raises:
            ValueError: If amount exceeds available quantity.
        """
        if amount > self.quantity:
            raise ValueError(f"Cannot reduce by {amount}, only {self.quantity} available")
        return self.model_copy(
            update={
                "quantity": self.quantity - amount,
                "updated_at": datetime.now(timezone.utc),
            }
        )

    def activate(self) -> Self:
        """Activate the product (immutable).

        Returns:
            New ProductEntity with ACTIVE status.

        Raises:
            ValueError: If quantity is zero.
        """
        if self.quantity <= 0:
            raise ValueError("Cannot activate product with zero quantity")
        return self.model_copy(
            update={
                "status": ProductStatus.ACTIVE,
                "updated_at": datetime.now(timezone.utc),
            }
        )

    def deactivate(self) -> Self:
        """Deactivate the product (immutable).

        Returns:
            New ProductEntity with INACTIVE status.
        """
        return self.model_copy(
            update={
                "status": ProductStatus.INACTIVE,
                "updated_at": datetime.now(timezone.utc),
            }
        )
```

### 2. Repository Interface

```python
# app/domain/repositories/product.py
from abc import ABC, abstractmethod
from decimal import Decimal

from app.domain.entities.product import ProductEntity, ProductStatus
from app.domain.repositories.base import BaseRepository


class ProductRepository(BaseRepository[ProductEntity, int], ABC):
    """Product repository interface."""

    @abstractmethod
    async def get_by_sku(self, sku: str) -> ProductEntity | None:
        """Get product by SKU."""
        ...

    @abstractmethod
    async def list_by_category(
        self,
        category_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> list[ProductEntity]:
        """List products by category."""
        ...

    @abstractmethod
    async def list_by_status(
        self,
        status: ProductStatus,
        offset: int = 0,
        limit: int = 100,
    ) -> list[ProductEntity]:
        """List products by status."""
        ...

    @abstractmethod
    async def search(
        self,
        query: str,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[list[ProductEntity], int]:
        """Search products with filters."""
        ...

    @abstractmethod
    async def update_quantity(
        self,
        product_id: int,
        quantity_delta: int,
    ) -> ProductEntity | None:
        """Update product quantity atomically."""
        ...
```

### 3. ORM Model

```python
# app/infrastructure/database/models/product.py
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities.product import ProductStatus
from app.infrastructure.database.models.base import BaseModel


class ProductModel(BaseModel):
    """Product database model."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    sku: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(
        String(20),
        default=ProductStatus.DRAFT.value,
        index=True,
    )
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships
    category: Mapped["CategoryModel"] = relationship(
        "CategoryModel",
        back_populates="products",
        lazy="selectin",
    )

    # Indexes for common queries
    __table_args__ = (
        Index("idx_products_status_category", "status", "category_id"),
        Index("idx_products_price", "price"),
    )
```

### 4. Repository Implementation

```python
# app/infrastructure/repositories/product.py
from decimal import Decimal

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.product import ProductEntity, ProductStatus
from app.domain.repositories.product import ProductRepository
from app.infrastructure.database.models.product import ProductModel
from app.infrastructure.repositories.base import SQLAlchemyRepository


class ProductRepositoryImpl(
    SQLAlchemyRepository[ProductEntity, ProductModel],
    ProductRepository,
):
    """Product repository implementation."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ProductModel, ProductEntity)

    def _to_entity(self, model: ProductModel) -> ProductEntity:
        """Convert ORM model to domain entity."""
        return ProductEntity(
            id=model.id,
            name=model.name,
            description=model.description,
            sku=model.sku,
            price=model.price,
            quantity=model.quantity,
            status=ProductStatus(model.status),
            category_id=model.category_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_sku(self, sku: str) -> ProductEntity | None:
        """Get product by SKU."""
        result = await self._session.execute(
            select(ProductModel).where(ProductModel.sku == sku)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_category(
        self,
        category_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> list[ProductEntity]:
        """List products by category."""
        result = await self._session.execute(
            select(ProductModel)
            .where(ProductModel.category_id == category_id)
            .offset(offset)
            .limit(limit)
            .order_by(ProductModel.name)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_status(
        self,
        status: ProductStatus,
        offset: int = 0,
        limit: int = 100,
    ) -> list[ProductEntity]:
        """List products by status."""
        result = await self._session.execute(
            select(ProductModel)
            .where(ProductModel.status == status.value)
            .offset(offset)
            .limit(limit)
            .order_by(ProductModel.created_at.desc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def search(
        self,
        query: str,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[list[ProductEntity], int]:
        """Search products with filters."""
        # Build base query
        base_query = select(ProductModel)

        # Apply search filter
        if query:
            search_filter = or_(
                ProductModel.name.ilike(f"%{query}%"),
                ProductModel.description.ilike(f"%{query}%"),
                ProductModel.sku.ilike(f"%{query}%"),
            )
            base_query = base_query.where(search_filter)

        # Apply price filters
        if min_price is not None:
            base_query = base_query.where(ProductModel.price >= min_price)
        if max_price is not None:
            base_query = base_query.where(ProductModel.price <= max_price)

        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self._session.execute(count_query)
        total = count_result.scalar() or 0

        # Get paginated results
        result = await self._session.execute(
            base_query.offset(offset).limit(limit).order_by(ProductModel.name)
        )
        products = [self._to_entity(m) for m in result.scalars().all()]

        return products, total

    async def update_quantity(
        self,
        product_id: int,
        quantity_delta: int,
    ) -> ProductEntity | None:
        """Update product quantity atomically."""
        # Use UPDATE with RETURNING for atomic operation
        result = await self._session.execute(
            update(ProductModel)
            .where(ProductModel.id == product_id)
            .where(ProductModel.quantity + quantity_delta >= 0)  # Prevent negative
            .values(quantity=ProductModel.quantity + quantity_delta)
            .returning(ProductModel)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.flush()
            return self._to_entity(model)
        return None
```

### 5. Service (Business Logic)

```python
# app/application/services/product.py
from datetime import datetime, timezone
from decimal import Decimal

import structlog

from app.core.exceptions import AlreadyExistsError, NotFoundError, ValidationError
from app.domain.entities.product import ProductEntity, ProductStatus
from app.domain.repositories.product import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate

logger = structlog.get_logger()


class ProductService:
    """Product service with business logic."""

    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    async def create(self, data: ProductCreate) -> ProductEntity:
        """Create a new product."""
        # Check SKU uniqueness
        existing = await self._repository.get_by_sku(data.sku)
        if existing:
            raise AlreadyExistsError(resource="Product", identifier=data.sku)

        entity = ProductEntity(
            name=data.name,
            description=data.description or "",
            sku=data.sku,
            price=data.price,
            quantity=data.quantity,
            status=ProductStatus.DRAFT,
            category_id=data.category_id,
        )

        created = await self._repository.create(entity)
        await logger.ainfo("Product created", product_id=created.id, sku=data.sku)
        return created

    async def get_by_id(self, product_id: int) -> ProductEntity:
        """Get product by ID or raise NotFoundError."""
        product = await self._repository.get_by_id(product_id)
        if not product:
            raise NotFoundError(resource="Product", identifier=product_id)
        return product

    async def update(self, product_id: int, data: ProductUpdate) -> ProductEntity:
        """Update product using immutable pattern."""
        product = await self.get_by_id(product_id)

        # Check SKU uniqueness if changing
        if data.sku and data.sku != product.sku:
            existing = await self._repository.get_by_sku(data.sku)
            if existing:
                raise AlreadyExistsError(resource="Product", identifier=data.sku)

        # Build update dict for immutable update
        update_data: dict = {"updated_at": datetime.now(timezone.utc)}
        if data.name is not None:
            update_data["name"] = data.name
        if data.description is not None:
            update_data["description"] = data.description
        if data.sku is not None:
            update_data["sku"] = data.sku
        if data.price is not None:
            update_data["price"] = data.price
        if data.category_id is not None:
            update_data["category_id"] = data.category_id

        # Create new immutable entity
        updated_entity = product.model_copy(update=update_data)

        result = await self._repository.update(product_id, updated_entity)
        if not result:
            raise NotFoundError(resource="Product", identifier=product_id)

        await logger.ainfo("Product updated", product_id=product_id)
        return result

    async def activate(self, product_id: int) -> ProductEntity:
        """Activate a product using immutable pattern."""
        product = await self.get_by_id(product_id)

        try:
            # activate() returns new immutable entity
            activated_product = product.activate()
        except ValueError as e:
            raise ValidationError(str(e)) from e

        updated = await self._repository.update(product_id, activated_product)
        await logger.ainfo("Product activated", product_id=product_id)
        return updated

    async def deactivate(self, product_id: int) -> ProductEntity:
        """Deactivate a product using immutable pattern."""
        product = await self.get_by_id(product_id)
        # deactivate() returns new immutable entity
        deactivated_product = product.deactivate()

        updated = await self._repository.update(product_id, deactivated_product)
        await logger.ainfo("Product deactivated", product_id=product_id)
        return updated

    async def adjust_quantity(
        self,
        product_id: int,
        quantity_delta: int,
    ) -> ProductEntity:
        """Adjust product quantity atomically."""
        product = await self._repository.update_quantity(product_id, quantity_delta)
        if not product:
            raise ValidationError(
                f"Cannot adjust quantity by {quantity_delta}: "
                "product not found or would result in negative quantity"
            )

        await logger.ainfo(
            "Product quantity adjusted",
            product_id=product_id,
            delta=quantity_delta,
            new_quantity=product.quantity,
        )
        return product

    async def search(
        self,
        query: str = "",
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[list[ProductEntity], int]:
        """Search products."""
        return await self._repository.search(
            query=query,
            min_price=min_price,
            max_price=max_price,
            offset=offset,
            limit=limit,
        )
```

### 6. Schemas

```python
# app/schemas/product.py
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.product import ProductStatus


class ProductCreate(BaseModel):
    """Product creation schema."""

    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    sku: str = Field(min_length=1, max_length=50)
    price: Decimal = Field(ge=0, decimal_places=2)
    quantity: int = Field(ge=0, default=0)
    category_id: int | None = None


class ProductUpdate(BaseModel):
    """Product update schema."""

    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    sku: str | None = Field(default=None, min_length=1, max_length=50)
    price: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    category_id: int | None = None


class ProductResponse(BaseModel):
    """Product response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    sku: str
    price: Decimal
    quantity: int
    status: ProductStatus
    category_id: int | None
    is_available: bool
    is_low_stock: bool
    created_at: datetime
    updated_at: datetime


class ProductQuantityAdjust(BaseModel):
    """Product quantity adjustment schema."""

    quantity_delta: int = Field(description="Amount to add (positive) or remove (negative)")
```

### 7. API Routes

```python
# app/api/v1/routes/products.py
from decimal import Decimal

from fastapi import APIRouter, Query, status

from app.api.v1.dependencies import ActiveUser
from app.api.v1.dependencies.product import ProductSvc
from app.schemas.common import PaginatedResponse
from app.schemas.product import (
    ProductCreate,
    ProductQuantityAdjust,
    ProductResponse,
    ProductUpdate,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    service: ProductSvc,
    _: ActiveUser,
):
    """Create a new product."""
    return await service.create(product_in)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    service: ProductSvc,
):
    """Get product by ID."""
    return await service.get_by_id(product_id)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    service: ProductSvc,
    _: ActiveUser,
):
    """Update product."""
    return await service.update(product_id, product_in)


@router.post("/{product_id}/activate", response_model=ProductResponse)
async def activate_product(
    product_id: int,
    service: ProductSvc,
    _: ActiveUser,
):
    """Activate a product."""
    return await service.activate(product_id)


@router.post("/{product_id}/deactivate", response_model=ProductResponse)
async def deactivate_product(
    product_id: int,
    service: ProductSvc,
    _: ActiveUser,
):
    """Deactivate a product."""
    return await service.deactivate(product_id)


@router.post("/{product_id}/adjust-quantity", response_model=ProductResponse)
async def adjust_quantity(
    product_id: int,
    data: ProductQuantityAdjust,
    service: ProductSvc,
    _: ActiveUser,
):
    """Adjust product quantity."""
    return await service.adjust_quantity(product_id, data.quantity_delta)


@router.get("", response_model=PaginatedResponse[ProductResponse])
async def search_products(
    service: ProductSvc,
    query: str = Query(default="", description="Search query"),
    min_price: Decimal | None = Query(default=None, ge=0),
    max_price: Decimal | None = Query(default=None, ge=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    """Search products with filters."""
    offset = (page - 1) * page_size
    products, total = await service.search(
        query=query,
        min_price=min_price,
        max_price=max_price,
        offset=offset,
        limit=page_size,
    )

    return PaginatedResponse.create(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=page,
        page_size=page_size,
    )
```

### 8. Feature Dependencies

```python
# app/api/v1/dependencies/product.py
from typing import Annotated

from fastapi import Depends

from app.api.v1.dependencies.database import get_db_session
from app.application.services.product import ProductService
from app.domain.repositories.product import ProductRepository
from app.infrastructure.repositories.product import ProductRepositoryImpl
from sqlalchemy.ext.asyncio import AsyncSession


def get_product_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ProductRepository:
    """Get product repository dependency."""
    return ProductRepositoryImpl(session)


def get_product_service(
    repository: ProductRepository = Depends(get_product_repository),
) -> ProductService:
    """Get product service dependency."""
    return ProductService(repository)


# Type alias
ProductSvc = Annotated[ProductService, Depends(get_product_service)]
```

## References

- `_references/ARCHITECTURE-PATTERN.md`
- `_references/REPOSITORY-PATTERN.md`
