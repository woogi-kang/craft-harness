---
name: http-client
description: |
  httpx async client, retry, timeout 패턴을 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# HTTP Client Skill

httpx async client, retry, timeout 패턴을 구현합니다.

## Triggers

- "HTTP 클라이언트", "외부 API", "httpx", "api client"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |
| `externalApis` | ❌ | 연동할 외부 API 목록 |

---

## Output

### Base HTTP Client

```python
# app/infrastructure/external/http_client.py
from typing import Any

import httpx
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings
from app.core.exceptions import ExternalServiceError

logger = structlog.get_logger()


class HTTPClient:
    """Base HTTP client with retry and timeout handling."""

    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.base_url = base_url
        self.timeout = httpx.Timeout(timeout)
        self.headers = headers or {}

    async def _get_client(self) -> httpx.AsyncClient:
        """Get configured async HTTP client."""
        return httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self.headers,
        )

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=lambda retry_state: logger.warning(
            "Retrying request",
            attempt=retry_state.attempt_number,
            error=str(retry_state.outcome.exception()),
        ),
    )
    async def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make GET request with retry."""
        async with await self._get_client() as client:
            try:
                response = await client.get(
                    path,
                    params=params,
                    headers=headers,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                await logger.aerror(
                    "HTTP error",
                    status_code=e.response.status_code,
                    path=path,
                    response=e.response.text[:500],
                )
                raise ExternalServiceError(
                    service=self.base_url,
                    message=f"HTTP {e.response.status_code}: {e.response.text[:200]}",
                )

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def post(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make POST request with retry."""
        async with await self._get_client() as client:
            try:
                response = await client.post(
                    path,
                    json=json,
                    data=data,
                    headers=headers,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                await logger.aerror(
                    "HTTP error",
                    status_code=e.response.status_code,
                    path=path,
                )
                raise ExternalServiceError(
                    service=self.base_url,
                    message=f"HTTP {e.response.status_code}",
                )

    async def put(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make PUT request."""
        async with await self._get_client() as client:
            response = await client.put(path, json=json, headers=headers)
            response.raise_for_status()
            return response.json()

    async def delete(
        self,
        path: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Make DELETE request."""
        async with await self._get_client() as client:
            response = await client.delete(path, headers=headers)
            response.raise_for_status()
```

### External API Client 예시

```python
# app/infrastructure/external/payment_client.py
from typing import Any

from pydantic import BaseModel

from app.core.config import settings
from app.infrastructure.external.http_client import HTTPClient


class PaymentRequest(BaseModel):
    """Payment request schema."""

    amount: int
    currency: str = "KRW"
    order_id: str
    customer_email: str


class PaymentResponse(BaseModel):
    """Payment response schema."""

    payment_id: str
    status: str
    amount: int
    currency: str


class PaymentClient(HTTPClient):
    """Payment gateway API client."""

    def __init__(self) -> None:
        super().__init__(
            base_url=settings.PAYMENT_API_URL,
            timeout=60.0,  # Longer timeout for payments
            headers={
                "Authorization": f"Bearer {settings.PAYMENT_API_KEY}",
                "Content-Type": "application/json",
            },
        )

    async def create_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Create a new payment."""
        response = await self.post(
            "/v1/payments",
            json=request.model_dump(),
        )
        return PaymentResponse.model_validate(response)

    async def get_payment(self, payment_id: str) -> PaymentResponse:
        """Get payment by ID."""
        response = await self.get(f"/v1/payments/{payment_id}")
        return PaymentResponse.model_validate(response)

    async def cancel_payment(self, payment_id: str, reason: str) -> PaymentResponse:
        """Cancel a payment."""
        response = await self.post(
            f"/v1/payments/{payment_id}/cancel",
            json={"reason": reason},
        )
        return PaymentResponse.model_validate(response)
```

### OAuth2 Client

```python
# app/infrastructure/external/oauth_client.py
from typing import Any

import httpx
from pydantic import BaseModel

from app.core.config import settings


class OAuthTokenResponse(BaseModel):
    """OAuth token response."""

    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str | None = None
    scope: str | None = None


class OAuthUserInfo(BaseModel):
    """OAuth user info."""

    id: str
    email: str
    name: str
    picture: str | None = None


class GoogleOAuthClient:
    """Google OAuth2 client."""

    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    def __init__(self) -> None:
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI

    async def exchange_code(self, code: str) -> OAuthTokenResponse:
        """Exchange authorization code for tokens."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "code": code,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": self.redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            response.raise_for_status()
            return OAuthTokenResponse.model_validate(response.json())

    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """Get user info from access token."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return OAuthUserInfo.model_validate(response.json())

    async def refresh_token(self, refresh_token: str) -> OAuthTokenResponse:
        """Refresh access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "refresh_token": refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "refresh_token",
                },
            )
            response.raise_for_status()
            return OAuthTokenResponse.model_validate(response.json())
```

### Dependency

```python
# app/api/v1/dependencies/external.py
from functools import lru_cache

from app.infrastructure.external.payment_client import PaymentClient
from app.infrastructure.external.oauth_client import GoogleOAuthClient


@lru_cache
def get_payment_client() -> PaymentClient:
    """Get payment client dependency."""
    return PaymentClient()


@lru_cache
def get_google_oauth_client() -> GoogleOAuthClient:
    """Get Google OAuth client dependency."""
    return GoogleOAuthClient()
```

### 사용 예시

```python
# app/api/v1/routes/payments.py
from fastapi import APIRouter, Depends

from app.api.v1.dependencies.external import get_payment_client
from app.infrastructure.external.payment_client import (
    PaymentClient,
    PaymentRequest,
    PaymentResponse,
)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("", response_model=PaymentResponse)
async def create_payment(
    request: PaymentRequest,
    client: PaymentClient = Depends(get_payment_client),
):
    """Create a new payment."""
    return await client.create_payment(request)


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    client: PaymentClient = Depends(get_payment_client),
):
    """Get payment by ID."""
    return await client.get_payment(payment_id)
```

## References

- `_references/API-PATTERN.md`
