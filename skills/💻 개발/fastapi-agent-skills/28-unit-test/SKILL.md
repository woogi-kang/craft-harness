---
name: unit-test
description: |
  pytest를 활용한 유닛 테스트를 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Unit Test Skill

Extends: `../../_shared/unit-test/SKILL.md` (공통 테스트 원칙 참조)

pytest를 활용한 유닛 테스트를 구현합니다.

## Triggers

- "유닛 테스트", "unit test", "단위 테스트", "pytest"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |

---

## Output

### Test Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
python_classes = ["Test*"]
addopts = [
    "-v",
    "-ra",
    "--strict-markers",
    "--tb=short",
    "-p", "no:warnings",
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "slow: Slow tests",
]
filterwarnings = [
    "ignore::DeprecationWarning",
]

[tool.coverage.run]
source = ["app"]
branch = true
omit = [
    "*/tests/*",
    "*/__init__.py",
    "*/migrations/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
]
fail_under = 80
show_missing = true
```

### Test Dependencies

```toml
# pyproject.toml
[project.optional-dependencies]
test = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
    "pytest-xdist>=3.6.0",
    "pytest-mock>=3.14.0",
    "pytest-timeout>=2.3.0",
    "httpx>=0.28.0",
    "factory-boy>=3.3.0",
    "faker>=30.0.0",
    "freezegun>=1.4.0",
    "respx>=0.21.0",
]
```

### Directory Structure

```
tests/
├── conftest.py              # Shared fixtures
├── factories/               # Test factories
│   ├── __init__.py
│   └── user.py
├── unit/                    # Unit tests
│   ├── __init__.py
│   ├── domain/
│   │   └── test_entities.py
│   ├── application/
│   │   ├── test_services.py
│   │   └── test_use_cases.py
│   └── infrastructure/
│       └── test_repositories.py
├── integration/             # Integration tests
│   └── ...
└── e2e/                     # End-to-end tests
    └── ...
```

### Base Fixtures

```python
# tests/conftest.py
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings


@pytest.fixture
def settings() -> Settings:
    """Test settings."""
    return Settings(
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        SECRET_KEY="test-secret-key-for-testing-only",
        ENVIRONMENT="testing",
    )


@pytest.fixture
async def engine(settings: Settings) -> AsyncGenerator[AsyncEngine, None]:
    """Create async engine for tests."""
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
    )

    # Create tables
    from app.infrastructure.database.models.base import BaseModel

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    yield engine

    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def session(
    engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """Create async session for tests."""
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session
        await session.rollback()
```

### Mock Fixtures

```python
# tests/conftest.py (continued)

@pytest.fixture
def mock_user_repository() -> MagicMock:
    """Mock user repository."""
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.get_by_email = AsyncMock(return_value=None)
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_email_service() -> MagicMock:
    """Mock email service."""
    service = MagicMock()
    service.send_email = AsyncMock(return_value=True)
    service.send_template = AsyncMock(return_value=True)
    return service


@pytest.fixture
def mock_cache_service() -> MagicMock:
    """Mock cache service."""
    cache: dict[str, Any] = {}

    async def get(key: str) -> Any:
        return cache.get(key)

    async def set(key: str, value: Any, ttl: int = 3600) -> None:
        cache[key] = value

    async def delete(key: str) -> None:
        cache.pop(key, None)

    service = MagicMock()
    service.get = AsyncMock(side_effect=get)
    service.set = AsyncMock(side_effect=set)
    service.delete = AsyncMock(side_effect=delete)

    return service
```

### Test Factories

```python
# tests/factories/user.py
from datetime import datetime, timezone

import factory
from factory import fuzzy

from app.domain.entities.user import User
from app.infrastructure.database.models.user import UserModel


class UserFactory(factory.Factory):
    """User entity factory."""

    class Meta:
        model = User

    id = factory.Sequence(lambda n: n + 1)
    email = factory.Faker("email")
    name = factory.Faker("name")
    hashed_password = factory.LazyAttribute(
        lambda _: "hashed_password_123"
    )
    is_active = True
    is_superuser = False
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class UserModelFactory(factory.alchemy.SQLAlchemyModelFactory):
    """User ORM model factory.

    Note: For thread-safe session handling, use the factory with
    a session context rather than modifying _meta.sqlalchemy_session directly.
    """

    class Meta:
        model = UserModel
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "flush"  # Use flush, commit in test

    id = factory.Sequence(lambda n: n + 1)
    email = factory.Faker("email")
    name = factory.Faker("name")
    hashed_password = "hashed_password_123"
    is_active = True
    is_superuser = False

    @classmethod
    def _create(cls, model_class, *args, session=None, **kwargs):
        """Override create to accept session parameter for thread-safety."""
        if session is not None:
            # Use provided session instead of _meta.sqlalchemy_session
            obj = model_class(*args, **kwargs)
            session.add(obj)
            return obj
        return super()._create(model_class, *args, **kwargs)
```

### Domain Entity Tests

```python
# tests/unit/domain/test_entities.py
import pytest

from app.domain.entities.user import User
from tests.factories.user import UserFactory


class TestUserEntity:
    """Tests for User entity."""

    def test_create_user(self) -> None:
        """Test user creation."""
        user = UserFactory()

        assert user.id is not None
        assert user.email is not None
        assert user.is_active is True

    def test_user_is_active_by_default(self) -> None:
        """Test user is active by default."""
        user = UserFactory(is_active=True)

        assert user.is_active is True

    def test_user_can_be_deactivated(self) -> None:
        """Test user can be deactivated."""
        user = UserFactory(is_active=True)

        user.deactivate()

        assert user.is_active is False

    def test_user_email_validation(self) -> None:
        """Test email validation."""
        with pytest.raises(ValueError):
            User(
                id=1,
                email="invalid-email",
                name="Test",
                hashed_password="hash",
            )

    def test_user_equality(self) -> None:
        """Test user equality based on ID."""
        user1 = UserFactory(id=1)
        user2 = UserFactory(id=1)
        user3 = UserFactory(id=2)

        assert user1 == user2
        assert user1 != user3

    def test_user_representation(self) -> None:
        """Test user string representation."""
        user = UserFactory(id=1, email="test@example.com")

        assert "test@example.com" in str(user)
```

### Service Tests

```python
# tests/unit/application/test_services.py
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.user import UserService
from app.application.schemas.user import UserCreate
from app.core.exceptions import ConflictError, NotFoundError
from tests.factories.user import UserFactory


class TestUserService:
    """Tests for UserService."""

    @pytest.fixture
    def user_service(self, mock_user_repository: MagicMock) -> UserService:
        """Create user service with mock repository."""
        return UserService(repository=mock_user_repository)

    async def test_get_user_by_id_success(
        self,
        user_service: UserService,
        mock_user_repository: MagicMock,
    ) -> None:
        """Test getting user by ID successfully."""
        expected_user = UserFactory(id=1)
        mock_user_repository.get_by_id.return_value = expected_user

        result = await user_service.get_by_id(1)

        assert result == expected_user
        mock_user_repository.get_by_id.assert_called_once_with(1)

    async def test_get_user_by_id_not_found(
        self,
        user_service: UserService,
        mock_user_repository: MagicMock,
    ) -> None:
        """Test getting non-existent user raises NotFoundError."""
        mock_user_repository.get_by_id.return_value = None

        with pytest.raises(NotFoundError):
            await user_service.get_by_id(999)

    async def test_create_user_success(
        self,
        user_service: UserService,
        mock_user_repository: MagicMock,
    ) -> None:
        """Test creating user successfully."""
        user_data = UserCreate(
            email="new@example.com",
            password="SecurePass123!",
            name="New User",
        )
        mock_user_repository.get_by_email.return_value = None
        created_user = UserFactory(email=user_data.email)
        mock_user_repository.create.return_value = created_user

        result = await user_service.create(user_data)

        assert result.email == user_data.email
        mock_user_repository.create.assert_called_once()

    async def test_create_user_duplicate_email(
        self,
        user_service: UserService,
        mock_user_repository: MagicMock,
    ) -> None:
        """Test creating user with existing email raises ConflictError."""
        user_data = UserCreate(
            email="existing@example.com",
            password="SecurePass123!",
            name="Existing User",
        )
        mock_user_repository.get_by_email.return_value = UserFactory(
            email=user_data.email
        )

        with pytest.raises(ConflictError):
            await user_service.create(user_data)

    async def test_update_user_success(
        self,
        user_service: UserService,
        mock_user_repository: MagicMock,
    ) -> None:
        """Test updating user successfully."""
        existing_user = UserFactory(id=1, name="Old Name")
        mock_user_repository.get_by_id.return_value = existing_user

        updated_user = UserFactory(id=1, name="New Name")
        mock_user_repository.update.return_value = updated_user

        result = await user_service.update(1, {"name": "New Name"})

        assert result.name == "New Name"

    async def test_delete_user_success(
        self,
        user_service: UserService,
        mock_user_repository: MagicMock,
    ) -> None:
        """Test deleting user successfully."""
        existing_user = UserFactory(id=1)
        mock_user_repository.get_by_id.return_value = existing_user
        mock_user_repository.delete.return_value = True

        await user_service.delete(1)

        mock_user_repository.delete.assert_called_once_with(existing_user)
```

### Use Case Tests

```python
# tests/unit/application/test_use_cases.py
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.use_cases.register_user import RegisterUserUseCase
from app.application.schemas.user import UserCreate
from app.core.exceptions import ConflictError
from tests.factories.user import UserFactory


class TestRegisterUserUseCase:
    """Tests for RegisterUserUseCase."""

    @pytest.fixture
    def use_case(
        self,
        mock_user_repository: MagicMock,
        mock_email_service: MagicMock,
    ) -> RegisterUserUseCase:
        """Create use case with mocks."""
        return RegisterUserUseCase(
            user_repository=mock_user_repository,
            email_service=mock_email_service,
        )

    async def test_register_user_success(
        self,
        use_case: RegisterUserUseCase,
        mock_user_repository: MagicMock,
        mock_email_service: MagicMock,
    ) -> None:
        """Test successful user registration."""
        user_data = UserCreate(
            email="new@example.com",
            password="SecurePass123!",
            name="New User",
        )
        mock_user_repository.get_by_email.return_value = None
        created_user = UserFactory(email=user_data.email)
        mock_user_repository.create.return_value = created_user

        result = await use_case.execute(user_data)

        assert result.email == user_data.email
        mock_email_service.send_template.assert_called_once()

    async def test_register_user_sends_welcome_email(
        self,
        use_case: RegisterUserUseCase,
        mock_user_repository: MagicMock,
        mock_email_service: MagicMock,
    ) -> None:
        """Test welcome email is sent on registration."""
        user_data = UserCreate(
            email="new@example.com",
            password="SecurePass123!",
            name="New User",
        )
        mock_user_repository.get_by_email.return_value = None
        created_user = UserFactory(email=user_data.email)
        mock_user_repository.create.return_value = created_user

        await use_case.execute(user_data)

        mock_email_service.send_template.assert_called_once_with(
            to=user_data.email,
            template="welcome",
            context={"name": user_data.name},
        )
```

### Repository Tests

```python
# tests/unit/infrastructure/test_repositories.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.user import UserRepository
from tests.factories.user import UserModelFactory


class TestUserRepository:
    """Tests for UserRepository."""

    @pytest.fixture
    def repository(self, session: AsyncSession) -> UserRepository:
        """Create repository with session."""
        return UserRepository(session)

    async def test_get_by_id(
        self,
        repository: UserRepository,
        session: AsyncSession,
    ) -> None:
        """Test getting user by ID."""
        # Thread-safe factory usage with explicit session
        user = UserModelFactory.create(session=session)
        await session.flush()

        result = await repository.get_by_id(user.id)

        assert result is not None
        assert result.id == user.id

    async def test_get_by_email(
        self,
        repository: UserRepository,
        session: AsyncSession,
    ) -> None:
        """Test getting user by email."""
        user = UserModelFactory.create(email="test@example.com", session=session)
        await session.flush()

        result = await repository.get_by_email("test@example.com")

        assert result is not None
        assert result.email == user.email

    async def test_create_user(
        self,
        repository: UserRepository,
    ) -> None:
        """Test creating a user."""
        from app.domain.entities.user import User

        user = User(
            id=None,
            email="new@example.com",
            name="New User",
            hashed_password="hashed",
        )

        result = await repository.create(user)

        assert result.id is not None
        assert result.email == user.email

    async def test_list_active_users(
        self,
        repository: UserRepository,
        session: AsyncSession,
    ) -> None:
        """Test listing active users."""
        UserModelFactory.create(is_active=True, session=session)
        UserModelFactory.create(is_active=True, session=session)
        UserModelFactory.create(is_active=False, session=session)
        await session.flush()

        result = await repository.list_active()

        assert len(result) == 2
```

### Password Hashing Tests

```python
# tests/unit/infrastructure/test_security.py
import pytest

from app.infrastructure.security.password import (
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    """Tests for password hashing."""

    def test_hash_password(self) -> None:
        """Test password hashing."""
        password = "SecurePass123!"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_success(self) -> None:
        """Test correct password verification."""
        password = "SecurePass123!"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_failure(self) -> None:
        """Test incorrect password verification."""
        password = "SecurePass123!"
        wrong_password = "WrongPass456!"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_same_password_different_hashes(self) -> None:
        """Test same password produces different hashes."""
        password = "SecurePass123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
```

### Running Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/application/test_services.py -v

# Run specific test
pytest tests/unit/application/test_services.py::TestUserService::test_create_user_success -v

# Run with parallel execution
pytest tests/unit/ -n auto

# Run marked tests
pytest tests/unit/ -m "not slow" -v
```

## Test Best Practices

| Practice | Description |
|----------|-------------|
| AAA Pattern | Arrange, Act, Assert in each test |
| One Assertion | Focus on one behavior per test |
| Descriptive Names | Test names describe expected behavior |
| Isolation | Each test is independent |
| No I/O | Unit tests don't touch DB/network |
| Fast | Unit tests should be < 100ms |

## References

- `_references/TEST-PATTERN.md`
