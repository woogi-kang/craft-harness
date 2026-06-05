---
name: authentication
description: |
  OAuth2 Password flow, JWT access/refresh 토큰을 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Authentication Skill

OAuth2 Password flow, JWT access/refresh 토큰을 구현합니다.

## Triggers

- "인증", "authentication", "jwt", "oauth2", "로그인"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |

---

## Output

### Security 모듈

```python
# app/core/security.py
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing - Argon2 preferred, bcrypt as fallback
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
    additional_claims: dict[str, Any] | None = None,
) -> str:
    """Create JWT access token.

    Includes:
    - sub: Subject (user ID)
    - exp: Expiration time
    - iat: Issued at time
    - jti: JWT ID for token revocation support
    - type: Token type (access/refresh)
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,                    # Issued at - for token freshness
        "jti": str(uuid.uuid4()),      # JWT ID - for blacklist/revocation
        "type": "access",
        **(additional_claims or {}),
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
) -> str:
    """Create JWT refresh token with jti for revocation support."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "jti": str(uuid.uuid4()),
        "type": "refresh",
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and validate JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload.get("type") != "access":
            return None
        return payload
    except InvalidTokenError:
        return None


def decode_refresh_token(token: str) -> dict[str, Any] | None:
    """Decode and validate JWT refresh token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload.get("type") != "refresh":
            return None
        return payload
    except InvalidTokenError:
        return None


# Token blacklist for refresh token rotation (requires Redis)
class TokenBlacklistError(Exception):
    """Raised when token blacklist operation fails."""

    pass


async def is_token_blacklisted(jti: str) -> bool:
    """Check if token is blacklisted.

    Used for:
    - Refresh token rotation (prevent reuse of old tokens)
    - Logout (invalidate all user tokens)
    - Security incidents (revoke compromised tokens)

    Raises:
        TokenBlacklistError: When Redis is unavailable and
            REDIS_BLACKLIST_REQUIRED is True (default).
    """
    import structlog

    from app.core.config import settings

    logger = structlog.get_logger()

    if not settings.REDIS_URL:
        # Security-first: Fail closed when Redis is required
        if getattr(settings, "REDIS_BLACKLIST_REQUIRED", True):
            await logger.aerror(
                "Token blacklist check failed: Redis unavailable",
                jti=jti,
            )
            raise TokenBlacklistError(
                "Token blacklist unavailable. Cannot verify token revocation status."
            )

        # Explicit opt-out: Log warning and allow (less secure)
        await logger.awarning(
            "Token blacklist disabled: Redis not configured",
            jti=jti,
        )
        return False

    import redis.asyncio as redis

    client = redis.from_url(settings.REDIS_URL)
    try:
        exists = await client.exists(f"token:blacklist:{jti}")
        return bool(exists)
    except redis.RedisError as e:
        await logger.aerror(
            "Redis connection failed during blacklist check",
            jti=jti,
            error=str(e),
        )
        if getattr(settings, "REDIS_BLACKLIST_REQUIRED", True):
            raise TokenBlacklistError(f"Redis connection failed: {e}") from e
        return False
    finally:
        await client.aclose()


async def blacklist_token(jti: str, expires_in: int) -> None:
    """Add token to blacklist with TTL.

    Args:
        jti: JWT ID to blacklist
        expires_in: TTL in seconds (should match token expiry)

    Raises:
        TokenBlacklistError: When Redis is unavailable and
            REDIS_BLACKLIST_REQUIRED is True (default).
    """
    import structlog

    from app.core.config import settings

    logger = structlog.get_logger()

    if not settings.REDIS_URL:
        if getattr(settings, "REDIS_BLACKLIST_REQUIRED", True):
            await logger.aerror(
                "Token blacklist failed: Redis unavailable",
                jti=jti,
            )
            raise TokenBlacklistError(
                "Cannot blacklist token. Redis is required for token revocation."
            )

        await logger.awarning(
            "Token not blacklisted: Redis not configured",
            jti=jti,
        )
        return

    import redis.asyncio as redis

    client = redis.from_url(settings.REDIS_URL)
    try:
        await client.setex(f"token:blacklist:{jti}", expires_in, "1")
    except redis.RedisError as e:
        await logger.aerror(
            "Redis connection failed during token blacklist",
            jti=jti,
            error=str(e),
        )
        if getattr(settings, "REDIS_BLACKLIST_REQUIRED", True):
            raise TokenBlacklistError(f"Redis connection failed: {e}") from e
    finally:
        await client.aclose()


async def blacklist_user_tokens(user_id: int) -> None:
    """Blacklist all tokens for a user (logout all sessions).

    This uses a user-specific version number approach:
    - Store token_version per user
    - Tokens issued before version increment are invalid

    Raises:
        TokenBlacklistError: When Redis is unavailable and
            REDIS_BLACKLIST_REQUIRED is True (default).
    """
    import structlog

    from app.core.config import settings

    logger = structlog.get_logger()

    if not settings.REDIS_URL:
        if getattr(settings, "REDIS_BLACKLIST_REQUIRED", True):
            await logger.aerror(
                "User token revocation failed: Redis unavailable",
                user_id=user_id,
            )
            raise TokenBlacklistError(
                "Cannot revoke user tokens. Redis is required for token revocation."
            )

        await logger.awarning(
            "User tokens not revoked: Redis not configured",
            user_id=user_id,
        )
        return

    import redis.asyncio as redis

    client = redis.from_url(settings.REDIS_URL)
    try:
        await client.incr(f"user:{user_id}:token_version")
    except redis.RedisError as e:
        await logger.aerror(
            "Redis connection failed during user token revocation",
            user_id=user_id,
            error=str(e),
        )
        if getattr(settings, "REDIS_BLACKLIST_REQUIRED", True):
            raise TokenBlacklistError(f"Redis connection failed: {e}") from e
    finally:
        await client.aclose()
```

### Auth Schemas

```python
# app/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str


class PasswordChangeRequest(BaseModel):
    """Password change request schema."""

    current_password: str
    new_password: str = Field(min_length=8)


class PasswordResetRequest(BaseModel):
    """Password reset request schema."""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema."""

    token: str
    new_password: str = Field(min_length=8)
```

### Auth Service

```python
# app/application/services/auth.py
from datetime import datetime, timezone

import structlog

from app.core.exceptions import AuthenticationError, NotFoundError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_password_hash,
    verify_password,
)
from app.domain.entities.user import UserEntity
from app.domain.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse

logger = structlog.get_logger()


class AuthService:
    """Authentication service."""

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def login(self, credentials: LoginRequest) -> TokenResponse:
        """Authenticate user and return tokens."""
        # Find user by email
        user = await self._user_repository.get_by_email(credentials.email)
        if not user:
            await logger.awarning("Login failed: user not found", email=credentials.email)
            raise AuthenticationError("Invalid email or password")

        # Verify password
        if not verify_password(credentials.password, user.hashed_password):
            await logger.awarning("Login failed: invalid password", email=credentials.email)
            raise AuthenticationError("Invalid email or password")

        # Check if user is active
        if not user.is_active:
            await logger.awarning("Login failed: user inactive", email=credentials.email)
            raise AuthenticationError("User account is inactive")

        # Generate tokens
        # Note: Avoid including sensitive data like is_superuser in JWT claims
        # Permission checks should be done server-side by fetching user from DB
        access_token = create_access_token(
            subject=user.id,
            additional_claims={
                "email": user.email,
            },
        )
        refresh_token = create_refresh_token(subject=user.id)

        await logger.ainfo("User logged in", user_id=user.id, email=user.email)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token.

        Implements token rotation:
        1. Validate and decode refresh token
        2. Blacklist old refresh token to prevent reuse
        3. Issue new access + refresh token pair
        """
        from app.core.security import blacklist_token, is_token_blacklisted

        payload = decode_refresh_token(refresh_token)
        if not payload:
            raise AuthenticationError("Invalid refresh token")

        user_id = payload.get("sub")
        old_jti = payload.get("jti")
        if not user_id or not old_jti:
            raise AuthenticationError("Invalid refresh token")

        # Check if token is already blacklisted (replay attack prevention)
        if await is_token_blacklisted(old_jti):
            await logger.awarning(
                "Refresh token reuse detected",
                user_id=user_id,
                jti=old_jti,
            )
            raise AuthenticationError("Refresh token has been revoked")

        # Verify user still exists and is active
        user = await self._user_repository.get_by_id(int(user_id))
        if not user:
            raise AuthenticationError("User not found")
        if not user.is_active:
            raise AuthenticationError("User account is inactive")

        # Blacklist old refresh token before issuing new ones
        # Calculate remaining TTL from exp claim
        from datetime import datetime, timezone
        exp_timestamp = payload.get("exp", 0)
        now = datetime.now(timezone.utc).timestamp()
        remaining_ttl = max(int(exp_timestamp - now), 0)

        if remaining_ttl > 0:
            await blacklist_token(old_jti, remaining_ttl)

        # Generate new tokens (token rotation)
        # Note: Avoid including sensitive data like is_superuser in JWT claims
        access_token = create_access_token(
            subject=user.id,
            additional_claims={
                "email": user.email,
            },
        )
        new_refresh_token = create_refresh_token(subject=user.id)

        await logger.ainfo(
            "Token rotation completed",
            user_id=user.id,
            old_jti=old_jti,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
        )

    async def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str,
    ) -> None:
        """Change user password."""
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(resource="User", identifier=user_id)

        if not verify_password(current_password, user.hashed_password):
            raise AuthenticationError("Current password is incorrect")

        hashed_password = get_password_hash(new_password)
        user.hashed_password = hashed_password
        await self._user_repository.update(user_id, user)

        await logger.ainfo("Password changed", user_id=user_id)
```

### Auth Routes

```python
# app/api/v1/routes/auth.py
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.v1.dependencies import ActiveUser, AuthSvc
from app.schemas.auth import (
    LoginRequest,
    PasswordChangeRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.schemas.base import SuccessResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    service: AuthSvc,
):
    """Login with email and password."""
    return await service.login(credentials)


@router.post("/login/form", response_model=TokenResponse)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthSvc = Depends(),
):
    """Login with OAuth2 form (for Swagger UI)."""
    credentials = LoginRequest(
        email=form_data.username,
        password=form_data.password,
    )
    return await service.login(credentials)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    service: AuthSvc,
):
    """Refresh access token."""
    return await service.refresh_tokens(request.refresh_token)


@router.post("/change-password", response_model=SuccessResponse)
async def change_password(
    request: PasswordChangeRequest,
    current_user: ActiveUser,
    service: AuthSvc,
):
    """Change password for current user."""
    await service.change_password(
        user_id=current_user.id,
        current_password=request.current_password,
        new_password=request.new_password,
    )
    return SuccessResponse(message="Password changed successfully")


@router.post("/logout", response_model=SuccessResponse)
async def logout(current_user: ActiveUser):
    """Logout current user (client should discard tokens)."""
    # In a stateless JWT setup, logout is handled client-side
    # For enhanced security, implement token blacklisting with Redis
    return SuccessResponse(message="Logged out successfully")
```

### OAuth2 Password Bearer

```python
# app/api/v1/dependencies/auth.py
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.api.v1.dependencies.services import get_user_service
from app.application.services.user import UserService
from app.core.security import decode_access_token
from app.domain.entities.user import UserEntity

# OAuth2 scheme - points to login endpoint
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login/form",
    auto_error=True,
)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: UserService = Depends(get_user_service),
) -> UserEntity:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = await user_service.get_by_id(int(user_id))
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[UserEntity, Depends(get_current_user)],
) -> UserEntity:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


# Type aliases for cleaner route signatures
CurrentUser = Annotated[UserEntity, Depends(get_current_user)]
ActiveUser = Annotated[UserEntity, Depends(get_current_active_user)]
```

## References

- `_references/AUTH-PATTERN.md`
