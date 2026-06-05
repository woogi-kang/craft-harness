# Test Pattern Reference

FastAPI 프로젝트의 테스트 전략 및 패턴 가이드입니다.

## Test Pyramid

```
                    ┌─────────────┐
                    │    E2E      │  5-10%
                    │   Tests     │  (Critical flows)
                    ├─────────────┤
                    │ Integration │  20-25%
                    │   Tests     │  (Component interaction)
               ┌────┴─────────────┴────┐
               │      Unit Tests       │  60-70%
               │  (Business logic)     │
               └───────────────────────┘
```

## Test Types

### 1. Unit Tests

**Purpose**: Test isolated business logic without external dependencies

```python
# tests/unit/application/test_services.py
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.user import UserService
from app.core.exceptions import NotFoundError
from tests.factories.user import UserFactory


class TestUserService:
    @pytest.fixture
    def mock_repository(self):
        repo = MagicMock()
        repo.get_by_id = AsyncMock()
        repo.create = AsyncMock()
        return repo

    @pytest.fixture
    def service(self, mock_repository):
        return UserService(repository=mock_repository)

    async def test_get_user_success(self, service, mock_repository):
        # Arrange
        expected_user = UserFactory(id=1)
        mock_repository.get_by_id.return_value = expected_user

        # Act
        result = await service.get_by_id(1)

        # Assert
        assert result == expected_user
        mock_repository.get_by_id.assert_called_once_with(1)

    async def test_get_user_not_found(self, service, mock_repository):
        # Arrange
        mock_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError):
            await service.get_by_id(999)
```

### 2. Integration Tests

**Purpose**: Test component interactions with real dependencies

```python
# tests/integration/api/test_users.py
import pytest
from httpx import AsyncClient


class TestUserAPI:
    async def test_create_user(
        self,
        authenticated_client: AsyncClient,
    ):
        # Arrange
        user_data = {
            "email": "new@example.com",
            "password": "SecurePass123!",
            "name": "New User",
        }

        # Act
        response = await authenticated_client.post(
            "/api/v1/users",
            json=user_data,
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["email"] == user_data["email"]

    async def test_get_user_not_found(
        self,
        authenticated_client: AsyncClient,
    ):
        # Act
        response = await authenticated_client.get("/api/v1/users/99999")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
```

### 3. E2E Tests

**Purpose**: Test complete user flows

```python
# tests/e2e/test_user_flow.py
import pytest
from httpx import AsyncClient


class TestUserRegistrationFlow:
    async def test_complete_registration(self, client: AsyncClient):
        # Step 1: Register
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "e2e@example.com",
                "password": "E2ETestPass123!",
                "name": "E2E User",
            },
        )
        assert register_response.status_code == 201

        # Step 2: Login
        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "e2e@example.com",
                "password": "E2ETestPass123!",
            },
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Step 3: Access protected resource
        client.headers["Authorization"] = f"Bearer {token}"
        profile_response = await client.get("/api/v1/auth/me")
        assert profile_response.status_code == 200
```

## Test Fixtures

```python
# tests/conftest.py
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.main import create_app


@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def session(engine) -> AsyncSession:
    """Create session with rollback after each test."""
    async with async_session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(session) -> AsyncClient:
    """Create test client with DI override."""
    app = create_app()

    async def get_test_session():
        yield session

    app.dependency_overrides[get_async_session] = get_test_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def authenticated_client(client, test_user):
    """Client with authentication."""
    token = create_access_token(subject=test_user.id)
    client.headers["Authorization"] = f"Bearer {token}"
    return client
```

## Test Factories

```python
# tests/factories/user.py
import factory
from faker import Faker

from app.domain.entities.user import User

fake = Faker()


class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: n + 1)
    email = factory.LazyAttribute(lambda _: fake.email())
    name = factory.LazyAttribute(lambda _: fake.name())
    hashed_password = "hashed_password"
    is_active = True
    is_superuser = False
```

## Mock Patterns

```python
# Mocking async functions
from unittest.mock import AsyncMock

mock_service = MagicMock()
mock_service.get_user = AsyncMock(return_value=user)

# Mocking external HTTP calls
import respx
from httpx import Response

@respx.mock
async def test_external_api():
    respx.get("https://api.example.com/data").mock(
        return_value=Response(200, json={"key": "value"})
    )
    # Test code here

# Mocking datetime
from freezegun import freeze_time

@freeze_time("2025-01-11 12:00:00")
def test_with_frozen_time():
    # datetime.now() returns frozen time
    pass
```

## AAA Pattern

```python
async def test_create_user_success(self):
    # Arrange - Setup test data and mocks
    user_data = UserCreate(
        email="test@example.com",
        password="SecurePass123!",
        name="Test User",
    )
    mock_repository.get_by_email.return_value = None
    mock_repository.create.return_value = UserFactory()

    # Act - Execute the code under test
    result = await user_service.create(user_data)

    # Assert - Verify the results
    assert result.email == user_data.email
    mock_repository.create.assert_called_once()
```

## Test Coverage

```toml
# pyproject.toml
[tool.coverage.run]
source = ["app"]
branch = true
omit = ["*/tests/*", "*/migrations/*"]

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
```

## Test Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test type
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v

# Run parallel
pytest -n auto

# Run with specific marker
pytest -m "not slow"
```

## Best Practices

| Practice | Description |
|----------|-------------|
| **Isolation** | Each test is independent |
| **Fast** | Unit tests < 100ms |
| **Deterministic** | Same result every run |
| **Clear naming** | Test name describes behavior |
| **One assertion focus** | Test one thing per test |
| **No I/O in unit tests** | Mock external dependencies |

## Related Skills

- `28-unit-test`: Unit test implementation
- `29-integration-test`: Integration test setup
- `30-e2e-test`: E2E test with testcontainers
