---
name: query-optimization
description: |
  N+1 문제 방지, 인덱싱, EXPLAIN 분석을 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Query Optimization Skill

N+1 문제 방지, 인덱싱, EXPLAIN 분석을 구현합니다.

## Triggers

- "쿼리 최적화", "N+1", "인덱스", "성능 튜닝"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |

---

## Output

### N+1 Problem Prevention

```python
# BAD: N+1 Problem
# This executes 1 query for posts + N queries for each author
async def get_posts_bad():
    posts = await session.execute(select(PostModel))
    for post in posts.scalars():
        # This triggers a separate query for each post!
        print(post.author.name)


# GOOD: Eager Loading with joinedload
async def get_posts_with_author():
    result = await session.execute(
        select(PostModel).options(joinedload(PostModel.author))
    )
    posts = result.scalars().unique().all()
    for post in posts:
        # No additional query - author already loaded
        print(post.author.name)


# GOOD: Eager Loading with selectinload (for collections)
async def get_posts_with_comments():
    result = await session.execute(
        select(PostModel).options(selectinload(PostModel.comments))
    )
    # Executes 2 queries: one for posts, one for all comments
    return result.scalars().all()
```

### Index Definition

```python
# app/infrastructure/database/models/user.py
from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.session import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Composite index for common queries
    __table_args__ = (
        Index("idx_users_status_created", "status", "created_at"),
        Index("idx_users_name_lower", func.lower(name)),  # Functional index
    )
```

```python
# app/infrastructure/database/models/post.py
class PostModel(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        # Composite index for listing published posts by category
        Index("idx_posts_category_published", "category_id", "published_at"),
        # Partial index for only published posts
        Index(
            "idx_posts_published",
            "published_at",
            postgresql_where=text("status = 'published'"),
        ),
    )
```

### Query Analysis

```python
# app/infrastructure/database/query_analyzer.py
import structlog
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger()


async def explain_query(session: AsyncSession, query) -> list[dict]:
    """Run EXPLAIN ANALYZE on a query."""
    # Get the compiled query
    compiled = query.compile(compile_kwargs={"literal_binds": True})
    sql = str(compiled)

    # Run EXPLAIN ANALYZE
    result = await session.execute(text(f"EXPLAIN ANALYZE {sql}"))
    return [{"plan": row[0]} for row in result.fetchall()]


async def analyze_slow_queries(session: AsyncSession, query, threshold_ms: float = 100):
    """Analyze and log slow queries."""
    import time

    start = time.perf_counter()
    result = await session.execute(query)
    duration_ms = (time.perf_counter() - start) * 1000

    if duration_ms > threshold_ms:
        await logger.awarning(
            "Slow query detected",
            duration_ms=duration_ms,
            query=str(query.compile(compile_kwargs={"literal_binds": True})),
        )

        # Get execution plan
        plan = await explain_query(session, query)
        await logger.ainfo("Query plan", plan=plan)

    return result
```

### Batch Loading

```python
# app/infrastructure/repositories/batch.py
from typing import TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BatchLoader:
    """Batch load related entities to avoid N+1."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def load_users_for_posts(
        self,
        posts: list[PostModel],
    ) -> dict[int, UserModel]:
        """Batch load users for posts."""
        if not posts:
            return {}

        user_ids = {post.author_id for post in posts}
        result = await self._session.execute(
            select(UserModel).where(UserModel.id.in_(user_ids))
        )
        users = result.scalars().all()
        return {user.id: user for user in users}

    async def load_tags_for_posts(
        self,
        posts: list[PostModel],
    ) -> dict[int, list[TagModel]]:
        """Batch load tags for posts."""
        if not posts:
            return {}

        post_ids = [post.id for post in posts]

        # Get post-tag associations
        result = await self._session.execute(
            select(post_tags.c.post_id, TagModel)
            .join(TagModel)
            .where(post_tags.c.post_id.in_(post_ids))
        )

        tags_by_post: dict[int, list[TagModel]] = {pid: [] for pid in post_ids}
        for post_id, tag in result:
            tags_by_post[post_id].append(tag)

        return tags_by_post
```

### Pagination Optimization

```python
# app/infrastructure/repositories/optimized.py
from sqlalchemy import select, func


class OptimizedRepository:
    """Repository with optimized pagination."""

    async def list_with_cursor(
        self,
        cursor: int | None = None,
        limit: int = 20,
    ) -> tuple[list[T], int | None]:
        """
        Cursor-based pagination (faster than OFFSET for large datasets).

        Returns: (items, next_cursor)
        """
        query = select(self._model).order_by(self._model.id.desc()).limit(limit + 1)

        if cursor:
            query = query.where(self._model.id < cursor)

        result = await self._session.execute(query)
        items = result.scalars().all()

        # Check if there are more items
        if len(items) > limit:
            next_cursor = items[-1].id
            items = items[:limit]
        else:
            next_cursor = None

        return [self._to_entity(m) for m in items], next_cursor

    async def count_estimated(self) -> int:
        """
        Get estimated count (faster than exact count for large tables).
        PostgreSQL only.
        """
        result = await self._session.execute(
            text(
                "SELECT reltuples::bigint FROM pg_class WHERE relname = :table_name"
            ).bindparams(table_name=self._model.__tablename__)
        )
        return result.scalar() or 0

    async def list_with_deferred_count(
        self,
        offset: int = 0,
        limit: int = 20,
        count_threshold: int = 10000,
    ) -> tuple[list[T], int | None]:
        """
        Return items with count only if below threshold.
        For large datasets, return None for count.
        """
        # Get items
        query = (
            select(self._model)
            .order_by(self._model.id.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(query)
        items = [self._to_entity(m) for m in result.scalars().all()]

        # Only count if we're near the beginning
        if offset < count_threshold:
            count = await self.count()
            return items, count

        return items, None
```

### Query Optimization Tips

```python
# app/infrastructure/repositories/tips.py

# 1. Select only needed columns
async def get_user_names():
    # BAD: Loads all columns
    result = await session.execute(select(UserModel))

    # GOOD: Only select needed columns
    result = await session.execute(
        select(UserModel.id, UserModel.name)
    )
    return result.all()


# 2. Use exists() instead of count() for existence check
async def user_exists(email: str) -> bool:
    # BAD: Counts all matching rows
    count = await session.execute(
        select(func.count()).where(UserModel.email == email)
    )

    # GOOD: Stops at first match
    result = await session.execute(
        select(exists().where(UserModel.email == email))
    )
    return result.scalar()


# 3. Bulk operations instead of loops
async def deactivate_users(user_ids: list[int]):
    # BAD: N update queries
    for uid in user_ids:
        user = await session.get(UserModel, uid)
        user.is_active = False

    # GOOD: Single update query
    await session.execute(
        update(UserModel)
        .where(UserModel.id.in_(user_ids))
        .values(is_active=False)
    )


# 4. Use window functions for rankings
async def get_top_posts_per_category():
    from sqlalchemy import func, over

    subquery = (
        select(
            PostModel,
            func.row_number()
            .over(
                partition_by=PostModel.category_id,
                order_by=PostModel.view_count.desc(),
            )
            .label("rank"),
        )
    ).subquery()

    result = await session.execute(
        select(subquery).where(subquery.c.rank <= 3)
    )
    return result.all()
```

### Monitoring Query Performance

```python
# app/core/query_monitoring.py
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger()


@asynccontextmanager
async def monitor_query(
    session: AsyncSession,
    operation: str,
    threshold_ms: float = 100,
) -> AsyncGenerator[None, None]:
    """Context manager to monitor query execution time."""
    start = time.perf_counter()
    try:
        yield
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        if duration_ms > threshold_ms:
            await logger.awarning(
                "Slow database operation",
                operation=operation,
                duration_ms=round(duration_ms, 2),
            )


# Usage
async def get_user_posts(user_id: int):
    async with monitor_query(session, f"get_posts_for_user_{user_id}"):
        return await repository.get_posts_by_user(user_id)
```

## References

- `_references/REPOSITORY-PATTERN.md`
