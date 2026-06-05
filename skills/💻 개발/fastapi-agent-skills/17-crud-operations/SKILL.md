---
name: crud-operations
description: |
  Generic CRUD, pagination, filtering, sorting을 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# CRUD Operations Skill

Generic CRUD, pagination, filtering, sorting을 구현합니다.

## Triggers

- "CRUD", "crud 구현", "페이지네이션", "필터링"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |
| `entity` | ✅ | 대상 엔티티 |

---

## Output

### Filter & Sort Types

```python
# app/schemas/common.py
from enum import Enum
from typing import Annotated, Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field

T = TypeVar("T")


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class SortParams(BaseModel):
    """Sort parameters."""

    sort_by: str = Field(default="created_at")
    sort_order: SortOrder = Field(default=SortOrder.DESC)


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response."""

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
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


# Annotated dependencies
Pagination = Annotated[PaginationParams, Query()]
Sorting = Annotated[SortParams, Query()]
```

### Generic CRUD Service

```python
# app/application/services/base.py
from typing import Generic, TypeVar, Type

from app.core.exceptions import NotFoundError
from app.domain.repositories.base import BaseRepository

T = TypeVar("T")  # Entity type
C = TypeVar("C")  # Create schema type
U = TypeVar("U")  # Update schema type


class BaseCRUDService(Generic[T, C, U]):
    """Base CRUD service with common operations."""

    def __init__(
        self,
        repository: BaseRepository[T, int],
        entity_name: str,
    ) -> None:
        self._repository = repository
        self._entity_name = entity_name

    async def get_by_id(self, id: int) -> T:
        """Get entity by ID or raise NotFoundError."""
        entity = await self._repository.get_by_id(id)
        if not entity:
            raise NotFoundError(resource=self._entity_name, identifier=id)
        return entity

    async def get_by_id_optional(self, id: int) -> T | None:
        """Get entity by ID or return None."""
        return await self._repository.get_by_id(id)

    async def list(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> list[T]:
        """List entities with pagination."""
        return await self._repository.list(offset=offset, limit=limit)

    async def create(self, data: C) -> T:
        """Create a new entity."""
        entity = self._create_entity(data)
        return await self._repository.create(entity)

    async def update(self, id: int, data: U) -> T:
        """Update an existing entity."""
        existing = await self.get_by_id(id)
        updated_entity = self._update_entity(existing, data)
        result = await self._repository.update(id, updated_entity)
        if not result:
            raise NotFoundError(resource=self._entity_name, identifier=id)
        return result

    async def delete(self, id: int) -> bool:
        """Delete an entity."""
        if not await self._repository.delete(id):
            raise NotFoundError(resource=self._entity_name, identifier=id)
        return True

    async def count(self) -> int:
        """Count total entities."""
        return await self._repository.count()

    async def exists(self, id: int) -> bool:
        """Check if entity exists."""
        return await self._repository.exists(id)

    def _create_entity(self, data: C) -> T:
        """Convert create schema to entity. Override in subclass."""
        raise NotImplementedError

    def _update_entity(self, existing: T, data: U) -> T:
        """Apply update schema to entity. Override in subclass."""
        raise NotImplementedError
```

### Filter Repository

```python
# app/infrastructure/repositories/filterable.py
from typing import Any, Generic, TypeVar, Type

from sqlalchemy import select, func, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.infrastructure.database.session import Base
from app.schemas.common import SortOrder

T = TypeVar("T")
M = TypeVar("M", bound=Base)


class FilterableRepository(Generic[T, M]):
    """Repository with filtering and sorting capabilities."""

    def __init__(
        self,
        session: AsyncSession,
        model: Type[M],
        entity_class: Type[T],
    ) -> None:
        self._session = session
        self._model = model
        self._entity_class = entity_class

    # Allowed filter fields mapping: filter_name -> model_column
    FILTER_FIELDS: dict[str, str] = {}

    # Allowed sort fields
    SORT_FIELDS: set[str] = {"id", "created_at", "updated_at"}

    def _to_entity(self, model: M) -> T:
        return self._entity_class.model_validate(model)

    def _build_filter_query(
        self,
        query: Select,
        filters: dict[str, Any],
    ) -> Select:
        """Apply filters to query."""
        for key, value in filters.items():
            if value is None:
                continue

            column_name = self.FILTER_FIELDS.get(key, key)
            if not hasattr(self._model, column_name):
                continue

            column = getattr(self._model, column_name)

            # Handle different filter types
            if isinstance(value, str) and key.endswith("_like"):
                query = query.where(column.ilike(f"%{value}%"))
            elif isinstance(value, list):
                query = query.where(column.in_(value))
            elif key.endswith("_gte"):
                query = query.where(column >= value)
            elif key.endswith("_lte"):
                query = query.where(column <= value)
            elif key.endswith("_gt"):
                query = query.where(column > value)
            elif key.endswith("_lt"):
                query = query.where(column < value)
            else:
                query = query.where(column == value)

        return query

    def _build_sort_query(
        self,
        query: Select,
        sort_by: str,
        sort_order: SortOrder,
    ) -> Select:
        """Apply sorting to query."""
        if sort_by not in self.SORT_FIELDS:
            sort_by = "created_at"

        column = getattr(self._model, sort_by)
        order_func = desc if sort_order == SortOrder.DESC else asc
        return query.order_by(order_func(column))

    async def find_with_filters(
        self,
        filters: dict[str, Any],
        offset: int = 0,
        limit: int = 100,
        sort_by: str = "created_at",
        sort_order: SortOrder = SortOrder.DESC,
    ) -> tuple[list[T], int]:
        """Find entities with filters, pagination, and sorting."""
        base_query = select(self._model)

        # Apply filters
        filtered_query = self._build_filter_query(base_query, filters)

        # Get total count
        count_query = select(func.count()).select_from(filtered_query.subquery())
        count_result = await self._session.execute(count_query)
        total = count_result.scalar() or 0

        # Apply sorting and pagination
        sorted_query = self._build_sort_query(filtered_query, sort_by, sort_order)
        paginated_query = sorted_query.offset(offset).limit(limit)

        # Execute
        result = await self._session.execute(paginated_query)
        entities = [self._to_entity(m) for m in result.scalars().all()]

        return entities, total
```

### Product Repository Example

```python
# app/infrastructure/repositories/product.py
from app.domain.entities.product import ProductEntity
from app.infrastructure.database.models.product import ProductModel
from app.infrastructure.repositories.filterable import FilterableRepository


class ProductRepositoryImpl(FilterableRepository[ProductEntity, ProductModel]):
    """Product repository with filtering."""

    FILTER_FIELDS = {
        "name_like": "name",
        "category": "category_id",
        "min_price": "price",
        "max_price": "price",
        "is_active": "is_active",
    }

    SORT_FIELDS = {"id", "name", "price", "created_at", "updated_at"}

    def __init__(self, session) -> None:
        super().__init__(session, ProductModel, ProductEntity)

    def _build_filter_query(self, query, filters):
        """Custom filter handling for products."""
        query = super()._build_filter_query(query, filters)

        # Handle price range
        if filters.get("min_price"):
            query = query.where(ProductModel.price >= filters["min_price"])
        if filters.get("max_price"):
            query = query.where(ProductModel.price <= filters["max_price"])

        return query
```

### CRUD Routes

```python
# app/api/v1/routes/products.py
from fastapi import APIRouter, status

from app.api.v1.dependencies import ActiveUser
from app.schemas.common import Pagination, Sorting, PaginatedResponse
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductFilter,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=PaginatedResponse[ProductResponse])
async def list_products(
    pagination: Pagination,
    sorting: Sorting,
    filters: ProductFilter = Depends(),
    service: ProductSvc,
):
    """List products with pagination, sorting, and filtering."""
    products, total = await service.find_with_filters(
        filters=filters.model_dump(exclude_none=True),
        offset=pagination.offset,
        limit=pagination.limit,
        sort_by=sorting.sort_by,
        sort_order=sorting.sort_order,
    )

    return PaginatedResponse.create(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, service: ProductSvc):
    """Get product by ID."""
    return await service.get_by_id(product_id)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    service: ProductSvc,
    _: ActiveUser,
):
    """Create a new product."""
    return await service.create(product_in)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    service: ProductSvc,
    _: ActiveUser,
):
    """Update a product."""
    return await service.update(product_id, product_in)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    service: ProductSvc,
    _: ActiveUser,
):
    """Delete a product."""
    await service.delete(product_id)
```

### Filter Schema

```python
# app/schemas/product.py
from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, Field


class ProductFilter(BaseModel):
    """Product filter parameters."""

    name_like: str | None = Field(default=None, description="Search by name")
    category: int | None = Field(default=None, description="Filter by category ID")
    min_price: float | None = Field(default=None, ge=0, description="Minimum price")
    max_price: float | None = Field(default=None, ge=0, description="Maximum price")
    is_active: bool | None = Field(default=None, description="Filter by active status")


ProductFilters = Annotated[ProductFilter, Query()]
```

## References

- `_references/REPOSITORY-PATTERN.md`
