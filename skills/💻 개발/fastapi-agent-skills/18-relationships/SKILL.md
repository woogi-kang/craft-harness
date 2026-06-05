---
name: relationships
description: |
  1:N, N:M 관계 및 eager/lazy loading을 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Relationships Skill

1:N, N:M 관계 및 eager/lazy loading을 구현합니다.

## Triggers

- "관계", "relationship", "1:N", "N:M", "eager loading"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |

---

## Output

### One-to-Many Relationship

```python
# app/infrastructure/database/models/user.py
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.session import Base


class UserModel(Base):
    """User model with one-to-many relationship to posts."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(100))

    # One-to-Many: User -> Posts
    posts: Mapped[list["PostModel"]] = relationship(
        "PostModel",
        back_populates="author",
        lazy="selectin",  # Eager load by default
        cascade="all, delete-orphan",
    )

    # One-to-Many: User -> Comments
    comments: Mapped[list["CommentModel"]] = relationship(
        "CommentModel",
        back_populates="author",
        lazy="noload",  # Don't load by default
    )
```

```python
# app/infrastructure/database/models/post.py
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.session import Base


class PostModel(Base):
    """Post model with many-to-one relationship to user."""

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Many-to-One: Post -> User
    author: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="posts",
        lazy="joined",  # Always join load
    )

    # One-to-Many: Post -> Comments
    comments: Mapped[list["CommentModel"]] = relationship(
        "CommentModel",
        back_populates="post",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
```

### Many-to-Many Relationship

```python
# app/infrastructure/database/models/associations.py
from sqlalchemy import Column, ForeignKey, Table

from app.infrastructure.database.session import Base

# Association table for Post <-> Tag (Many-to-Many)
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

# Association table for User <-> Role (Many-to-Many)
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)
```

```python
# app/infrastructure/database/models/tag.py
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.associations import post_tags
from app.infrastructure.database.session import Base


class TagModel(Base):
    """Tag model with many-to-many relationship to posts."""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    # Many-to-Many: Tag <-> Posts
    posts: Mapped[list["PostModel"]] = relationship(
        "PostModel",
        secondary=post_tags,
        back_populates="tags",
        lazy="selectin",
    )
```

```python
# app/infrastructure/database/models/post.py (updated)
from app.infrastructure.database.models.associations import post_tags


class PostModel(Base):
    __tablename__ = "posts"

    # ... other fields

    # Many-to-Many: Post <-> Tags
    tags: Mapped[list["TagModel"]] = relationship(
        "TagModel",
        secondary=post_tags,
        back_populates="posts",
        lazy="selectin",
    )
```

### Many-to-Many with Extra Fields

```python
# app/infrastructure/database/models/order.py
from datetime import datetime
from sqlalchemy import ForeignKey, Integer, Numeric, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.session import Base


class OrderItemModel(Base):
    """Order item (association model with extra fields)."""

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2))

    # Relationships
    order: Mapped["OrderModel"] = relationship(back_populates="items")
    product: Mapped["ProductModel"] = relationship()


class OrderModel(Base):
    """Order model."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user: Mapped["UserModel"] = relationship()
    items: Mapped[list["OrderItemModel"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def total_amount(self) -> float:
        return sum(item.quantity * item.unit_price for item in self.items)
```

### Loading Strategies

```python
# app/infrastructure/repositories/post.py
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload, noload

from app.infrastructure.database.models.post import PostModel


class PostRepositoryImpl:
    """Post repository with different loading strategies."""

    async def get_with_author(self, post_id: int) -> PostModel | None:
        """Get post with author (joined load)."""
        result = await self._session.execute(
            select(PostModel)
            .options(joinedload(PostModel.author))
            .where(PostModel.id == post_id)
        )
        return result.scalar_one_or_none()

    async def get_with_comments(self, post_id: int) -> PostModel | None:
        """Get post with comments (selectin load)."""
        result = await self._session.execute(
            select(PostModel)
            .options(selectinload(PostModel.comments))
            .where(PostModel.id == post_id)
        )
        return result.scalar_one_or_none()

    async def get_with_all_relations(self, post_id: int) -> PostModel | None:
        """Get post with all relations."""
        result = await self._session.execute(
            select(PostModel)
            .options(
                joinedload(PostModel.author),
                selectinload(PostModel.comments),
                selectinload(PostModel.tags),
            )
            .where(PostModel.id == post_id)
        )
        return result.scalar_one_or_none()

    async def list_without_relations(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[PostModel]:
        """List posts without loading relations."""
        result = await self._session.execute(
            select(PostModel)
            .options(
                noload(PostModel.author),
                noload(PostModel.comments),
                noload(PostModel.tags),
            )
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def list_by_tag(self, tag_id: int) -> list[PostModel]:
        """List posts by tag (using many-to-many)."""
        result = await self._session.execute(
            select(PostModel)
            .join(PostModel.tags)
            .where(TagModel.id == tag_id)
            .options(selectinload(PostModel.tags))
        )
        return result.scalars().all()
```

### Nested Schema Response

```python
# app/schemas/post.py
from datetime import datetime
from pydantic import BaseModel


class AuthorResponse(BaseModel):
    """Nested author response."""

    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}


class TagResponse(BaseModel):
    """Nested tag response."""

    id: int
    name: str

    model_config = {"from_attributes": True}


class CommentResponse(BaseModel):
    """Nested comment response."""

    id: int
    content: str
    author: AuthorResponse
    created_at: datetime

    model_config = {"from_attributes": True}


class PostResponse(BaseModel):
    """Post response with nested relations."""

    id: int
    title: str
    content: str
    author: AuthorResponse
    tags: list[TagResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PostDetailResponse(PostResponse):
    """Post detail with comments."""

    comments: list[CommentResponse]
```

### Routes with Relations

```python
# app/api/v1/routes/posts.py
from fastapi import APIRouter

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, service: PostSvc):
    """Get post with author and tags."""
    return await service.get_with_relations(post_id)


@router.get("/{post_id}/detail", response_model=PostDetailResponse)
async def get_post_detail(post_id: int, service: PostSvc):
    """Get post with all details including comments."""
    return await service.get_with_all_relations(post_id)


@router.post("/{post_id}/tags/{tag_id}")
async def add_tag_to_post(
    post_id: int,
    tag_id: int,
    service: PostSvc,
    _: ActiveUser,
):
    """Add tag to post (many-to-many)."""
    return await service.add_tag(post_id, tag_id)


@router.delete("/{post_id}/tags/{tag_id}")
async def remove_tag_from_post(
    post_id: int,
    tag_id: int,
    service: PostSvc,
    _: ActiveUser,
):
    """Remove tag from post."""
    return await service.remove_tag(post_id, tag_id)
```

## References

- `_references/REPOSITORY-PATTERN.md`
