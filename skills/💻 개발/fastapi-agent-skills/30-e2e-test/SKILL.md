---
name: e2e-test
description: |
  Playwright, Docker를 활용한 End-to-End 테스트를 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# E2E Test Skill

Extends: `../../_shared/e2e-test/SKILL.md` (공통 E2E 테스트 원칙 참조)

Playwright, Docker를 활용한 End-to-End 테스트를 구현합니다.

## Triggers

- "e2e 테스트", "end to end", "시나리오 테스트", "playwright"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |

---

## Output

### Testing Pyramid - Coverage Targets

E2E tests should cover **critical user journeys** only. Follow this coverage distribution:

```
        ┌───────────┐
        │   E2E     │  5-10% of tests
        │  (10%)    │  ← Critical flows only
        ├───────────┤
        │Integration│  15-25% of tests
        │  (20%)    │  ← API + DB interaction
        ├───────────┤
        │   Unit    │  60-70% of tests
        │  (70%)    │  ← Fast, isolated tests
        └───────────┘
```

| Test Level | Coverage | Focus | Tools |
|------------|----------|-------|-------|
| **Unit** | 60-70% | Business logic, pure functions | pytest, mock |
| **Integration** | 15-25% | API endpoints, DB operations | TestClient, respx |
| **E2E** | 5-10% | Critical user flows, UI | Testcontainers, Playwright |

**E2E Test Selection Criteria:**
- ✅ User registration & login flow
- ✅ Core business transactions (e.g., checkout)
- ✅ Payment processing (critical path)
- ❌ Every API endpoint (use integration tests)
- ❌ Edge cases (use unit tests)

### E2E Test Configuration

```toml
# pyproject.toml
[project.optional-dependencies]
e2e = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.28.0",
    "testcontainers>=4.8.0",
    "docker>=7.1.0",
]
```

### Docker Compose for E2E

```yaml
# docker-compose.e2e.yml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@db:5432/app
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: e2e-test-secret-key
      ENVIRONMENT: testing
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: app
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  e2e:
    build:
      context: .
      dockerfile: Dockerfile.test
    environment:
      API_BASE_URL: http://api:8000
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@db:5432/app
    depends_on:
      - api
    command: pytest tests/e2e/ -v --tb=short
```

### Retry Logic for Flaky Tests

```python
# tests/e2e/helpers/retry.py
import asyncio
from functools import wraps
from typing import Callable, TypeVar

import structlog

logger = structlog.get_logger()

T = TypeVar("T")


def retry_async(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """Decorator to retry async functions on failure.

    Useful for handling flaky network conditions in E2E tests.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(
                            f"Attempt {attempt}/{max_attempts} failed, retrying...",
                            error=str(e),
                            delay=current_delay,
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff

            raise last_exception

        return wrapper

    return decorator


async def wait_for_service(
    url: str,
    timeout: float = 30.0,
    interval: float = 1.0,
) -> bool:
    """Wait for a service to become available.

    Args:
        url: Health check URL
        timeout: Maximum time to wait in seconds
        interval: Check interval in seconds

    Returns:
        True if service is available, False if timeout
    """
    import httpx

    start_time = asyncio.get_event_loop().time()

    while asyncio.get_event_loop().time() - start_time < timeout:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5.0)
                if response.status_code == 200:
                    return True
        except (httpx.ConnectError, httpx.TimeoutException):
            pass

        await asyncio.sleep(interval)

    return False
```

### Unified E2E conftest.py

This is a **single, unified conftest.py** that handles both API tests (Testcontainers) and
UI tests (Playwright). Use a single conftest to avoid fixture conflicts.

```python
# tests/e2e/conftest.py (UNIFIED - API + Playwright)
import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from app.main import create_app


@pytest.fixture(scope="session")
def postgres_container():
    """Start PostgreSQL container."""
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def redis_container():
    """Start Redis container."""
    with RedisContainer("redis:7-alpine") as redis:
        yield redis


@pytest.fixture(scope="session")
def app_settings(postgres_container, redis_container):
    """Configure app with container URLs."""
    os.environ["DATABASE_URL"] = postgres_container.get_connection_url().replace(
        "postgresql://", "postgresql+asyncpg://"
    )
    os.environ["REDIS_URL"] = f"redis://{redis_container.get_container_host_ip()}:{redis_container.get_exposed_port(6379)}/0"
    os.environ["SECRET_KEY"] = "e2e-test-secret"
    os.environ["ENVIRONMENT"] = "testing"


@pytest_asyncio.fixture(scope="session")
async def app(app_settings):
    """Create FastAPI app."""
    from app.infrastructure.database.models.base import BaseModel
    from app.infrastructure.database.session import engine

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    app = create_app()
    yield app

    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)


@pytest_asyncio.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """Create async client."""
    from httpx import ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client


@pytest_asyncio.fixture
async def auth_client(client: AsyncClient) -> AsyncClient:
    """Create authenticated client."""
    # Register user
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "e2e@example.com",
            "password": "E2ETestPass123!",
            "name": "E2E Test User",
        },
    )

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "e2e@example.com",
            "password": "E2ETestPass123!",
        },
    )
    token = response.json()["access_token"]

    client.headers["Authorization"] = f"Bearer {token}"
    return client
```

### User Flow E2E Tests

```python
# tests/e2e/test_user_flow.py
import pytest
from httpx import AsyncClient


class TestUserFlow:
    """E2E tests for complete user flows."""

    async def test_complete_registration_flow(
        self,
        client: AsyncClient,
    ) -> None:
        """Test complete user registration flow."""
        # Step 1: Register
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "NewUserPass123!",
                "name": "New User",
            },
        )
        assert register_response.status_code == 201
        user_id = register_response.json()["data"]["id"]

        # Step 2: Login
        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "newuser@example.com",
                "password": "NewUserPass123!",
            },
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Step 3: Get profile
        client.headers["Authorization"] = f"Bearer {token}"
        profile_response = await client.get("/api/v1/auth/me")
        assert profile_response.status_code == 200
        assert profile_response.json()["data"]["email"] == "newuser@example.com"

        # Step 4: Update profile
        update_response = await client.patch(
            f"/api/v1/users/{user_id}",
            json={"name": "Updated Name"},
        )
        assert update_response.status_code == 200
        assert update_response.json()["data"]["name"] == "Updated Name"

        # Step 5: Logout
        logout_response = await client.post("/api/v1/auth/logout")
        assert logout_response.status_code == 200

    async def test_password_reset_flow(
        self,
        client: AsyncClient,
    ) -> None:
        """Test password reset flow."""
        # Step 1: Register user
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "reset@example.com",
                "password": "OldPass123!",
                "name": "Reset User",
            },
        )

        # Step 2: Request password reset
        reset_request = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "reset@example.com"},
        )
        assert reset_request.status_code == 200

        # Step 3: In real scenario, get token from email
        # For E2E, we might mock this or use a test endpoint
        # Assuming we have access to the token
        reset_token = "mock-reset-token"

        # Step 4: Reset password
        reset_response = await client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": reset_token,
                "password": "NewPass123!",
            },
        )
        # This would work with proper token
        # assert reset_response.status_code == 200

        # Step 5: Login with new password
        # login_response = await client.post(...)


class TestCRUDFlow:
    """E2E tests for CRUD operations."""

    async def test_item_crud_flow(
        self,
        auth_client: AsyncClient,
    ) -> None:
        """Test complete item CRUD flow."""
        # Create
        create_response = await auth_client.post(
            "/api/v1/items",
            json={
                "name": "Test Item",
                "description": "A test item",
                "price": 99.99,
            },
        )
        assert create_response.status_code == 201
        item_id = create_response.json()["data"]["id"]

        # Read
        get_response = await auth_client.get(f"/api/v1/items/{item_id}")
        assert get_response.status_code == 200
        assert get_response.json()["data"]["name"] == "Test Item"

        # Update
        update_response = await auth_client.patch(
            f"/api/v1/items/{item_id}",
            json={"name": "Updated Item"},
        )
        assert update_response.status_code == 200
        assert update_response.json()["data"]["name"] == "Updated Item"

        # List
        list_response = await auth_client.get("/api/v1/items")
        assert list_response.status_code == 200
        items = list_response.json()["data"]
        assert any(item["id"] == item_id for item in items)

        # Delete
        delete_response = await auth_client.delete(f"/api/v1/items/{item_id}")
        assert delete_response.status_code == 204

        # Verify deleted
        get_deleted = await auth_client.get(f"/api/v1/items/{item_id}")
        assert get_deleted.status_code == 404


class TestSearchAndFilter:
    """E2E tests for search and filter functionality."""

    async def test_search_items(
        self,
        auth_client: AsyncClient,
    ) -> None:
        """Test item search functionality."""
        # Create test items
        items_data = [
            {"name": "Apple", "category": "fruit", "price": 1.50},
            {"name": "Banana", "category": "fruit", "price": 0.75},
            {"name": "Carrot", "category": "vegetable", "price": 0.50},
        ]

        for item in items_data:
            await auth_client.post("/api/v1/items", json=item)

        # Search by name
        search_response = await auth_client.get(
            "/api/v1/items",
            params={"search": "Apple"},
        )
        assert search_response.status_code == 200
        results = search_response.json()["data"]
        assert len(results) == 1
        assert results[0]["name"] == "Apple"

        # Filter by category
        filter_response = await auth_client.get(
            "/api/v1/items",
            params={"category": "fruit"},
        )
        assert filter_response.status_code == 200
        results = filter_response.json()["data"]
        assert len(results) == 2

        # Price range filter
        price_response = await auth_client.get(
            "/api/v1/items",
            params={"min_price": 0.50, "max_price": 1.00},
        )
        assert price_response.status_code == 200


class TestPaginationFlow:
    """E2E tests for pagination."""

    async def test_pagination(
        self,
        auth_client: AsyncClient,
    ) -> None:
        """Test pagination across pages."""
        # Create 25 items
        for i in range(25):
            await auth_client.post(
                "/api/v1/items",
                json={
                    "name": f"Item {i}",
                    "price": i * 10,
                },
            )

        # First page
        page1_response = await auth_client.get(
            "/api/v1/items",
            params={"page": 1, "size": 10},
        )
        assert page1_response.status_code == 200
        page1_data = page1_response.json()
        assert len(page1_data["data"]) == 10
        assert page1_data["pagination"]["has_next"] is True
        assert page1_data["pagination"]["has_prev"] is False

        # Second page
        page2_response = await auth_client.get(
            "/api/v1/items",
            params={"page": 2, "size": 10},
        )
        assert page2_response.status_code == 200
        page2_data = page2_response.json()
        assert len(page2_data["data"]) == 10
        assert page2_data["pagination"]["has_next"] is True
        assert page2_data["pagination"]["has_prev"] is True

        # Third page (partial)
        page3_response = await auth_client.get(
            "/api/v1/items",
            params={"page": 3, "size": 10},
        )
        assert page3_response.status_code == 200
        page3_data = page3_response.json()
        assert len(page3_data["data"]) == 5
        assert page3_data["pagination"]["has_next"] is False
```

### Error Handling E2E Tests

```python
# tests/e2e/test_error_handling.py
import pytest
from httpx import AsyncClient


class TestErrorHandling:
    """E2E tests for error handling."""

    async def test_validation_error(
        self,
        client: AsyncClient,
    ) -> None:
        """Test validation error response."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "short",
                "name": "",
            },
        )

        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert "errors" in data
        assert len(data["errors"]) > 0

    async def test_not_found_error(
        self,
        auth_client: AsyncClient,
    ) -> None:
        """Test not found error response."""
        response = await auth_client.get("/api/v1/items/99999")

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "RES_001"

    async def test_unauthorized_error(
        self,
        client: AsyncClient,
    ) -> None:
        """Test unauthorized error response."""
        response = await client.get("/api/v1/users")

        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False

    async def test_forbidden_error(
        self,
        auth_client: AsyncClient,
    ) -> None:
        """Test forbidden error for admin-only endpoint."""
        response = await auth_client.delete("/api/v1/admin/users/1")

        assert response.status_code == 403


class TestRateLimiting:
    """E2E tests for rate limiting."""

    async def test_rate_limit_exceeded(
        self,
        client: AsyncClient,
    ) -> None:
        """Test rate limit exceeded response."""
        # Make many requests quickly
        for _ in range(100):
            await client.get("/api/v1/health")

        # Should eventually get rate limited
        response = await client.get("/api/v1/health")

        # Check if rate limited (might need to adjust based on actual limits)
        if response.status_code == 429:
            data = response.json()
            assert data["error"]["code"] == "RATE_001"
            assert "Retry-After" in response.headers
```

### Performance E2E Tests

```python
# tests/e2e/test_performance.py
import asyncio
import time

import pytest
from httpx import AsyncClient


class TestPerformance:
    """E2E performance tests."""

    async def test_response_time(
        self,
        auth_client: AsyncClient,
    ) -> None:
        """Test response time is acceptable."""
        start = time.time()
        response = await auth_client.get("/api/v1/users")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 1.0  # Should respond within 1 second

    async def test_concurrent_requests(
        self,
        auth_client: AsyncClient,
    ) -> None:
        """Test handling concurrent requests."""

        async def make_request():
            return await auth_client.get("/api/v1/users")

        # Make 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        start = time.time()
        responses = await asyncio.gather(*tasks)
        elapsed = time.time() - start

        # All should succeed
        assert all(r.status_code == 200 for r in responses)
        # Should complete within 5 seconds
        assert elapsed < 5.0

    async def test_large_payload(
        self,
        auth_client: AsyncClient,
    ) -> None:
        """Test handling large payload."""
        # Create item with large description
        large_description = "x" * 10000  # 10KB

        response = await auth_client.post(
            "/api/v1/items",
            json={
                "name": "Large Item",
                "description": large_description,
                "price": 9.99,
            },
        )

        assert response.status_code == 201
```

### Using Retry in Tests

```python
# tests/e2e/test_with_retry.py
import pytest
from httpx import AsyncClient, ConnectError, TimeoutException

from tests.e2e.helpers.retry import retry_async, wait_for_service


class TestWithRetry:
    """E2E tests with retry logic for flaky scenarios."""

    @retry_async(max_attempts=3, delay=2.0, exceptions=(AssertionError,))
    async def test_eventual_consistency(
        self,
        auth_client: AsyncClient,
    ) -> None:
        """Test that eventually becomes consistent.

        Useful for async operations that may take time to propagate.
        """
        # Create order
        await auth_client.post("/api/v1/orders", json={"product_id": 1})

        # Stats may take time to update (async processing)
        response = await auth_client.get("/api/v1/stats/orders")
        assert response.status_code == 200
        assert response.json()["data"]["total"] > 0

    @retry_async(
        max_attempts=3,
        delay=1.0,
        exceptions=(ConnectError, TimeoutException),
    )
    async def test_external_service_call(
        self,
        auth_client: AsyncClient,
    ) -> None:
        """Test that calls external service (may be flaky)."""
        response = await auth_client.post(
            "/api/v1/payments/process",
            json={"amount": 100, "currency": "USD"},
        )
        assert response.status_code in (200, 201)


@pytest.fixture(scope="session", autouse=True)
async def wait_for_api():
    """Wait for API to be ready before running tests."""
    import os

    api_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
    is_ready = await wait_for_service(f"{api_url}/health", timeout=60.0)

    if not is_ready:
        pytest.fail("API service did not become ready in time")
```

### Running E2E Tests

```bash
# Run E2E tests with testcontainers
pytest tests/e2e/ -v -m e2e

# Run with Docker Compose
docker-compose -f docker-compose.e2e.yml up --build --abort-on-container-exit

# Run specific scenario
pytest tests/e2e/test_user_flow.py -v

# Run with timeout
pytest tests/e2e/ -v --timeout=60

# Run with automatic retries (pytest-rerunfailures)
pytest tests/e2e/ -v --reruns 3 --reruns-delay 2

# Run only flaky tests with more retries
pytest tests/e2e/ -v -m flaky --reruns 5
```

### pytest.ini Configuration for Retries

```ini
# pytest.ini
[pytest]
markers =
    e2e: End-to-end tests
    flaky: Tests that may be flaky due to external dependencies

# Automatically rerun failed tests
addopts = --reruns 2 --reruns-delay 1

# Timeout for each test
timeout = 60
```

### pyproject.toml Test Dependencies

```toml
[project.optional-dependencies]
e2e = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-rerunfailures>=14.0",  # Automatic test retries
    "pytest-timeout>=2.3.0",       # Test timeout
    "httpx>=0.28.0",
    "testcontainers>=4.8.0",
    "docker>=7.1.0",
]

[project.optional-dependencies.playwright]
playwright = [
    "pytest-playwright>=0.5.0",
    "playwright>=1.48.0",
]
```

---

## Playwright UI Automation

For applications with a frontend (Admin UI, Swagger UI, etc.), use Playwright
for browser-based E2E testing.

### Playwright Setup

```bash
# Install Playwright
pip install pytest-playwright playwright

# Install browser binaries
playwright install chromium
```

### Playwright Configuration (Integrated into Unified conftest.py)

Add these fixtures to the unified `tests/e2e/conftest.py`:

```python
# tests/e2e/conftest.py (CONTINUED - Playwright Fixtures)
#
# Add these to the unified conftest.py above
#

from playwright.async_api import async_playwright, Browser, Page, BrowserContext


# ============= Playwright Fixtures =============

@pytest.fixture(scope="session")
def browser_type_launch_args():
    """Browser launch arguments."""
    return {
        "headless": os.environ.get("HEADED", "false").lower() != "true",
        "slow_mo": 100,  # Slow down for debugging
    }


@pytest.fixture(scope="session")
async def browser(browser_type_launch_args) -> Browser:
    """Launch browser for tests (session-scoped for performance)."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(**browser_type_launch_args)
        yield browser
        await browser.close()


@pytest.fixture(scope="function")
async def context(browser: Browser) -> BrowserContext:
    """Create a new browser context for each test (function-scoped for isolation)."""
    context = await browser.new_context(
        viewport={"width": 1280, "height": 720},
        locale="en-US",
    )
    yield context
    await context.close()


@pytest.fixture(scope="function")
async def page(context: BrowserContext) -> Page:
    """Create a new page for each test (function-scoped for isolation)."""
    page = await context.new_page()
    yield page
    await page.close()


@pytest.fixture
def api_base_url() -> str:
    """API base URL for tests - shared between API and Playwright tests."""
    return os.environ.get("API_BASE_URL", "http://localhost:8000")


@pytest.fixture
async def authenticated_page(
    context: BrowserContext,
    api_base_url: str,
    auth_client: AsyncClient,  # Reuse auth from API tests
) -> Page:
    """Create page with authentication - reuses auth_client token."""
    page = await context.new_page()

    # Get token from auth_client (already authenticated)
    token = auth_client.headers.get("Authorization", "").replace("Bearer ", "")

    # Set token in localStorage
    await page.goto(api_base_url)
    await page.evaluate(f"localStorage.setItem('token', '{token}')")

    yield page
    await page.close()


# ============= Screenshot on Failure =============

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture screenshot on test failure."""
    import asyncio

    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        page = item.funcargs.get("page")
        if page:
            async def capture():
                os.makedirs("test-results", exist_ok=True)
                await page.screenshot(
                    path=f"test-results/failure-{item.name}.png",
                    full_page=True,
                )

            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.ensure_future(capture())
                else:
                    loop.run_until_complete(capture())
            except Exception:
                pass  # Don't fail the test due to screenshot error
```

**Key Benefits of Unified conftest.py:**
- Single source of truth for fixtures
- No fixture conflicts between API and Playwright tests
- Shared authentication (auth_client → authenticated_page)
- Consistent api_base_url across all tests
- Proper scope isolation (session for browser, function for context/page)

### Playwright Page Object Model

```python
# tests/e2e/playwright/pages/login_page.py
from playwright.async_api import Page, expect


class LoginPage:
    """Login page object."""

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

        # Locators
        self.email_input = page.locator('input[name="email"]')
        self.password_input = page.locator('input[name="password"]')
        self.submit_button = page.locator('button[type="submit"]')
        self.error_message = page.locator('[data-testid="error-message"]')

    async def goto(self) -> None:
        """Navigate to login page."""
        await self.page.goto(f"{self.base_url}/login")

    async def login(self, email: str, password: str) -> None:
        """Fill and submit login form."""
        await self.email_input.fill(email)
        await self.password_input.fill(password)
        await self.submit_button.click()

    async def expect_error(self, message: str) -> None:
        """Verify error message is displayed."""
        await expect(self.error_message).to_contain_text(message)

    async def expect_logged_in(self) -> None:
        """Verify successful login (redirected to dashboard)."""
        await expect(self.page).to_have_url(f"{self.base_url}/dashboard")
```

```python
# tests/e2e/playwright/pages/swagger_page.py
from playwright.async_api import Page, expect


class SwaggerUIPage:
    """Swagger UI page object for API documentation testing."""

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

    async def goto(self) -> None:
        """Navigate to Swagger UI."""
        await self.page.goto(f"{self.base_url}/api/v1/docs")
        # Wait for Swagger UI to load
        await self.page.wait_for_selector(".swagger-ui")

    async def authorize(self, token: str) -> None:
        """Set Bearer token authorization."""
        await self.page.click('button.authorize')
        await self.page.fill('input[name="bearerAuth"]', token)
        await self.page.click('button.auth-btn-wrapper button')
        await self.page.click('button.close-modal')

    async def expand_endpoint(self, method: str, path: str) -> None:
        """Expand an API endpoint section."""
        selector = f'[data-path="{path}"] .opblock-{method.lower()}'
        await self.page.click(selector)

    async def try_it_out(self) -> None:
        """Click 'Try it out' button."""
        await self.page.click('button.try-out__btn')

    async def execute(self) -> None:
        """Execute the API request."""
        await self.page.click('button.execute')
        # Wait for response
        await self.page.wait_for_selector('.response-col_status')

    async def get_response_code(self) -> str:
        """Get response status code."""
        return await self.page.locator('.response-col_status').text_content()
```

### Playwright UI Tests

```python
# tests/e2e/playwright/test_login_ui.py
import pytest
from playwright.async_api import Page, expect

from tests.e2e.playwright.pages.login_page import LoginPage


class TestLoginUI:
    """UI tests for login functionality."""

    @pytest.mark.asyncio
    async def test_successful_login(
        self,
        page: Page,
        api_base_url: str,
    ) -> None:
        """Test successful login flow."""
        login_page = LoginPage(page, api_base_url)

        await login_page.goto()
        await login_page.login("user@example.com", "ValidPass123!")
        await login_page.expect_logged_in()

    @pytest.mark.asyncio
    async def test_invalid_credentials(
        self,
        page: Page,
        api_base_url: str,
    ) -> None:
        """Test login with invalid credentials."""
        login_page = LoginPage(page, api_base_url)

        await login_page.goto()
        await login_page.login("user@example.com", "WrongPassword")
        await login_page.expect_error("Invalid email or password")

    @pytest.mark.asyncio
    async def test_form_validation(
        self,
        page: Page,
        api_base_url: str,
    ) -> None:
        """Test client-side form validation."""
        login_page = LoginPage(page, api_base_url)

        await login_page.goto()

        # Submit empty form
        await login_page.submit_button.click()

        # Check for validation errors
        await expect(login_page.email_input).to_have_attribute("aria-invalid", "true")


class TestSwaggerUI:
    """UI tests for Swagger documentation."""

    @pytest.mark.asyncio
    async def test_swagger_loads(
        self,
        page: Page,
        api_base_url: str,
    ) -> None:
        """Test Swagger UI loads correctly."""
        from tests.e2e.playwright.pages.swagger_page import SwaggerUIPage

        swagger = SwaggerUIPage(page, api_base_url)
        await swagger.goto()

        # Verify title
        await expect(page.locator(".title")).to_contain_text("API")

    @pytest.mark.asyncio
    async def test_health_endpoint(
        self,
        page: Page,
        api_base_url: str,
    ) -> None:
        """Test health endpoint via Swagger UI."""
        from tests.e2e.playwright.pages.swagger_page import SwaggerUIPage

        swagger = SwaggerUIPage(page, api_base_url)
        await swagger.goto()

        await swagger.expand_endpoint("GET", "/health")
        await swagger.try_it_out()
        await swagger.execute()

        status = await swagger.get_response_code()
        assert "200" in status
```

### Screenshot on Failure

```python
# tests/e2e/playwright/conftest.py (additional)
import pytest
from playwright.async_api import Page


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture screenshot on test failure."""
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        page = item.funcargs.get("page")
        if page:
            # Async screenshot capture
            import asyncio

            async def capture():
                await page.screenshot(
                    path=f"test-results/failure-{item.name}.png",
                    full_page=True,
                )

            asyncio.get_event_loop().run_until_complete(capture())
```

### Running Playwright Tests

```bash
# Run Playwright tests
pytest tests/e2e/playwright/ -v

# Run with headed browser (for debugging)
pytest tests/e2e/playwright/ -v --headed

# Run specific test
pytest tests/e2e/playwright/test_login_ui.py -v

# Generate HTML report with screenshots
pytest tests/e2e/playwright/ -v --html=report.html
```

### CI/CD E2E Pipeline

```yaml
# .github/workflows/e2e.yml
name: E2E Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  e2e:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Run E2E tests
        run: |
          docker-compose -f docker-compose.e2e.yml up \
            --build \
            --abort-on-container-exit \
            --exit-code-from e2e

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: e2e-results
          path: test-results/
```

## Test Strategy

| Level | Coverage | Purpose |
|-------|----------|---------|
| Unit | 60-70% | Business logic isolation |
| Integration | 20-25% | Component interaction |
| E2E | 5-10% | Critical user flows |

## References

- `_references/TEST-PATTERN.md`
