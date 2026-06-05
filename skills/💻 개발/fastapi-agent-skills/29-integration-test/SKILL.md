---
name: integration-test
description: |
  실제 데이터베이스와 연동한 통합 테스트를 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Integration Test Skill

실제 데이터베이스와 연동한 통합 테스트를 구현합니다.

## Triggers

- "통합 테스트", "integration test", "API 테스트", "db 테스트"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |

---

## Output

### Test Database Configuration

```python
# tests/conftest.py
import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import Settings
from app.infrastructure.database.models.base import BaseModel
from app.main import create_app


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for session scope."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Test settings with test database."""
    return Settings(
        DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/test_db",
        SECRET_KEY="test-secret-key-for-testing-only",
        ENVIRONMENT="testing",
        REDIS_URL="redis://localhost:6379/1",
    )


@pytest_asyncio.fixture(scope="session")
async def engine(test_settings: Settings) -> AsyncGenerator[AsyncEngine, None]:
    """Create test database engine."""
    engine = create_async_engine(
        test_settings.DATABASE_URL,
        poolclass=NullPool,  # Disable pooling for tests
        echo=False,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def session(
    engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """Create session with transaction rollback."""
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        # Start a nested transaction
        async with session.begin():
            yield session
            # Rollback after each test
            await session.rollback()


@pytest_asyncio.fixture
async def client(
    engine: AsyncEngine,
    session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with dependency overrides."""
    from app.api.v1.dependencies import get_async_session

    app = create_app()

    # Override session dependency
    async def get_test_session():
        yield session

    app.dependency_overrides[get_async_session] = get_test_session

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()
```

### Test Fixtures for Auth

```python
# tests/fixtures/auth.py
import pytest_asyncio
from httpx import AsyncClient

from app.infrastructure.security.jwt import create_access_token
from tests.factories.user import UserModelFactory


@pytest_asyncio.fixture
async def test_user(session):
    """Create a test user."""
    from app.infrastructure.database.models.user import UserModel
    from app.infrastructure.security.password import hash_password

    user = UserModel(
        email="test@example.com",
        name="Test User",
        hashed_password=hash_password("TestPass123!"),
        is_active=True,
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(session):
    """Create an admin user."""
    from app.infrastructure.database.models.user import UserModel
    from app.infrastructure.security.password import hash_password

    user = UserModel(
        email="admin@example.com",
        name="Admin User",
        hashed_password=hash_password("AdminPass123!"),
        is_active=True,
        is_superuser=True,
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user) -> dict[str, str]:
    """Create auth headers for test user."""
    token = create_access_token(subject=test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(admin_user) -> dict[str, str]:
    """Create auth headers for admin user."""
    token = create_access_token(subject=admin_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def authenticated_client(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> AsyncClient:
    """Client with auth headers."""
    client.headers.update(auth_headers)
    return client
```

### API Integration Tests

```python
# tests/integration/api/test_users.py
import pytest
from httpx import AsyncClient

from tests.factories.user import UserModelFactory


class TestUserAPI:
    """Integration tests for User API."""

    @pytest.fixture(autouse=True)
    async def setup(self, session):
        """Setup test data."""
        UserModelFactory._meta.sqlalchemy_session = session

    async def test_list_users(
        self,
        authenticated_client: AsyncClient,
        session,
    ) -> None:
        """Test listing users."""
        # Create test users
        UserModelFactory.create_batch(3)
        await session.commit()

        response = await authenticated_client.get("/api/v1/users")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 3

    async def test_get_user(
        self,
        authenticated_client: AsyncClient,
        test_user,
    ) -> None:
        """Test getting a user."""
        response = await authenticated_client.get(
            f"/api/v1/users/{test_user.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == test_user.id
        assert data["data"]["email"] == test_user.email

    async def test_get_user_not_found(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test getting non-existent user."""
        response = await authenticated_client.get("/api/v1/users/99999")

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "RES_001"

    async def test_create_user(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test creating a user."""
        user_data = {
            "email": "new@example.com",
            "password": "SecurePass123!",
            "name": "New User",
        }

        response = await authenticated_client.post(
            "/api/v1/users",
            json=user_data,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == user_data["email"]

    async def test_create_user_duplicate_email(
        self,
        authenticated_client: AsyncClient,
        test_user,
    ) -> None:
        """Test creating user with existing email."""
        user_data = {
            "email": test_user.email,
            "password": "SecurePass123!",
            "name": "Duplicate User",
        }

        response = await authenticated_client.post(
            "/api/v1/users",
            json=user_data,
        )

        assert response.status_code == 409
        data = response.json()
        assert data["success"] is False

    async def test_update_user(
        self,
        authenticated_client: AsyncClient,
        test_user,
    ) -> None:
        """Test updating a user."""
        update_data = {"name": "Updated Name"}

        response = await authenticated_client.patch(
            f"/api/v1/users/{test_user.id}",
            json=update_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "Updated Name"

    async def test_delete_user(
        self,
        authenticated_client: AsyncClient,
        session,
    ) -> None:
        """Test deleting a user."""
        user = UserModelFactory.create()
        await session.commit()

        response = await authenticated_client.delete(
            f"/api/v1/users/{user.id}"
        )

        assert response.status_code == 204

    async def test_unauthorized_access(
        self,
        client: AsyncClient,
    ) -> None:
        """Test unauthorized access."""
        response = await client.get("/api/v1/users")

        assert response.status_code == 401

    async def test_pagination(
        self,
        authenticated_client: AsyncClient,
        session,
    ) -> None:
        """Test pagination."""
        UserModelFactory.create_batch(25)
        await session.commit()

        response = await authenticated_client.get(
            "/api/v1/users",
            params={"page": 1, "size": 10},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 10
        assert data["pagination"]["total_items"] >= 25
        assert data["pagination"]["has_next"] is True
```

### Auth Integration Tests

```python
# tests/integration/api/test_auth.py
import pytest
from httpx import AsyncClient

from app.infrastructure.security.password import hash_password


class TestAuthAPI:
    """Integration tests for Auth API."""

    async def test_login_success(
        self,
        client: AsyncClient,
        test_user,
    ) -> None:
        """Test successful login."""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "TestPass123!",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_credentials(
        self,
        client: AsyncClient,
        test_user,
    ) -> None:
        """Test login with invalid credentials."""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == 401

    async def test_login_inactive_user(
        self,
        client: AsyncClient,
        session,
    ) -> None:
        """Test login with inactive user."""
        from app.infrastructure.database.models.user import UserModel

        user = UserModel(
            email="inactive@example.com",
            name="Inactive User",
            hashed_password=hash_password("TestPass123!"),
            is_active=False,
        )
        session.add(user)
        await session.commit()

        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "inactive@example.com",
                "password": "TestPass123!",
            },
        )

        assert response.status_code == 401

    async def test_refresh_token(
        self,
        client: AsyncClient,
        test_user,
    ) -> None:
        """Test token refresh."""
        # First login
        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "TestPass123!",
            },
        )
        refresh_token = login_response.json()["refresh_token"]

        # Refresh token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    async def test_get_current_user(
        self,
        authenticated_client: AsyncClient,
        test_user,
    ) -> None:
        """Test getting current user."""
        response = await authenticated_client.get("/api/v1/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == test_user.id

    async def test_logout(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test logout."""
        response = await authenticated_client.post("/api/v1/auth/logout")

        assert response.status_code == 200
```

### Repository Integration Tests

```python
# tests/integration/repositories/test_user_repository.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.infrastructure.repositories.user import UserRepository


class TestUserRepository:
    """Integration tests for UserRepository."""

    @pytest.fixture
    def repository(self, session: AsyncSession) -> UserRepository:
        """Create repository."""
        return UserRepository(session)

    async def test_create_and_get(
        self,
        repository: UserRepository,
        session: AsyncSession,
    ) -> None:
        """Test creating and retrieving a user."""
        user = User(
            id=None,
            email="test@example.com",
            name="Test User",
            hashed_password="hashed",
        )

        created = await repository.create(user)
        await session.commit()

        retrieved = await repository.get_by_id(created.id)

        assert retrieved is not None
        assert retrieved.email == user.email

    async def test_get_by_email(
        self,
        repository: UserRepository,
        session: AsyncSession,
    ) -> None:
        """Test getting user by email."""
        user = User(
            id=None,
            email="unique@example.com",
            name="Test",
            hashed_password="hashed",
        )

        await repository.create(user)
        await session.commit()

        result = await repository.get_by_email("unique@example.com")

        assert result is not None
        assert result.email == "unique@example.com"

    async def test_update(
        self,
        repository: UserRepository,
        session: AsyncSession,
    ) -> None:
        """Test updating a user."""
        user = User(
            id=None,
            email="update@example.com",
            name="Original Name",
            hashed_password="hashed",
        )

        created = await repository.create(user)
        await session.commit()

        created.name = "Updated Name"
        updated = await repository.update(created)
        await session.commit()

        assert updated.name == "Updated Name"

    async def test_delete(
        self,
        repository: UserRepository,
        session: AsyncSession,
    ) -> None:
        """Test deleting a user."""
        user = User(
            id=None,
            email="delete@example.com",
            name="Delete Me",
            hashed_password="hashed",
        )

        created = await repository.create(user)
        await session.commit()

        await repository.delete(created)
        await session.commit()

        result = await repository.get_by_id(created.id)
        assert result is None

    async def test_list_with_pagination(
        self,
        repository: UserRepository,
        session: AsyncSession,
    ) -> None:
        """Test listing users with pagination."""
        # Create multiple users
        for i in range(15):
            user = User(
                id=None,
                email=f"user{i}@example.com",
                name=f"User {i}",
                hashed_password="hashed",
            )
            await repository.create(user)
        await session.commit()

        # Get first page
        users, total = await repository.list_paginated(offset=0, limit=10)

        assert len(users) == 10
        assert total >= 15

    async def test_exists(
        self,
        repository: UserRepository,
        session: AsyncSession,
    ) -> None:
        """Test exists check."""
        user = User(
            id=None,
            email="exists@example.com",
            name="Test",
            hashed_password="hashed",
        )

        created = await repository.create(user)
        await session.commit()

        exists = await repository.exists(created.id)
        not_exists = await repository.exists(99999)

        assert exists is True
        assert not_exists is False
```

### External Service Integration Tests

```python
# tests/integration/services/test_email_service.py
import pytest
import respx
from httpx import Response

from app.infrastructure.services.email import EmailService


class TestEmailServiceIntegration:
    """Integration tests for EmailService with mock HTTP."""

    @pytest.fixture
    def email_service(self) -> EmailService:
        """Create email service."""
        return EmailService(
            api_key="test-api-key",
            from_email="noreply@example.com",
        )

    @respx.mock
    async def test_send_email_success(
        self,
        email_service: EmailService,
    ) -> None:
        """Test successful email sending."""
        # Mock the email API
        respx.post("https://api.sendgrid.com/v3/mail/send").mock(
            return_value=Response(202)
        )

        result = await email_service.send_email(
            to="user@example.com",
            subject="Test Email",
            body="This is a test email.",
        )

        assert result is True

    @respx.mock
    async def test_send_email_failure(
        self,
        email_service: EmailService,
    ) -> None:
        """Test email sending failure."""
        respx.post("https://api.sendgrid.com/v3/mail/send").mock(
            return_value=Response(500, json={"error": "Server error"})
        )

        result = await email_service.send_email(
            to="user@example.com",
            subject="Test Email",
            body="This is a test email.",
        )

        assert result is False
```

### Database Transaction Tests

```python
# tests/integration/test_transactions.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.unit_of_work import UnitOfWork


class TestTransactions:
    """Test database transaction handling."""

    async def test_commit_success(
        self,
        session: AsyncSession,
    ) -> None:
        """Test successful commit."""
        async with UnitOfWork(session) as uow:
            # Create user
            from app.infrastructure.database.models.user import UserModel

            user = UserModel(
                email="commit@example.com",
                name="Commit Test",
                hashed_password="hashed",
            )
            session.add(user)
            await uow.commit()

        # Verify persisted
        from sqlalchemy import select

        result = await session.execute(
            select(UserModel).where(UserModel.email == "commit@example.com")
        )
        assert result.scalar_one_or_none() is not None

    async def test_rollback_on_error(
        self,
        session: AsyncSession,
    ) -> None:
        """Test rollback on error."""
        from app.infrastructure.database.models.user import UserModel

        try:
            async with UnitOfWork(session) as uow:
                user = UserModel(
                    email="rollback@example.com",
                    name="Rollback Test",
                    hashed_password="hashed",
                )
                session.add(user)
                raise ValueError("Simulated error")
        except ValueError:
            pass

        # Verify not persisted
        from sqlalchemy import select

        result = await session.execute(
            select(UserModel).where(UserModel.email == "rollback@example.com")
        )
        assert result.scalar_one_or_none() is None
```

### Running Integration Tests

```bash
# Run integration tests
pytest tests/integration/ -v -m integration

# Run with test database
DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/test_db" \
    pytest tests/integration/ -v

# Run specific test class
pytest tests/integration/api/test_users.py::TestUserAPI -v

# Run with coverage
pytest tests/integration/ --cov=app --cov-report=html
```

## Docker Compose for Test DB

```yaml
# docker-compose.test.yml
services:
  test-db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: test_db
    ports:
      - "5433:5432"
    tmpfs:
      - /var/lib/postgresql/data

  test-redis:
    image: redis:7-alpine
    ports:
      - "6380:6379"
```

## References

- `_references/TEST-PATTERN.md`
