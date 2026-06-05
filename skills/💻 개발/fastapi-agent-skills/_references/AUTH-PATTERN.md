# Auth Pattern Reference

FastAPI 프로젝트의 인증/인가 패턴 가이드입니다.

## Authentication Flow

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Client  │────▶│ FastAPI │────▶│  JWT    │────▶│ Database│
│         │     │ Route   │     │ Verify  │     │ User    │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
     │               │               │               │
     │   Login       │               │               │
     │──────────────▶│               │               │
     │               │  Verify Creds │               │
     │               │──────────────────────────────▶│
     │               │               │    User       │
     │               │◀──────────────────────────────│
     │               │ Generate JWT  │               │
     │               │──────────────▶│               │
     │   JWT Token   │               │               │
     │◀──────────────│               │               │
     │               │               │               │
     │  API Request  │               │               │
     │──────────────▶│               │               │
     │               │ Verify Token  │               │
     │               │──────────────▶│               │
     │               │   Valid       │               │
     │               │◀──────────────│               │
     │   Response    │               │               │
     │◀──────────────│               │               │
```

## JWT Token Structure

```python
# Access Token Payload
{
    "sub": "user_id",          # Subject (user ID)
    "email": "user@example.com",
    "exp": 1704067200,          # Expiration time
    "iat": 1704063600,          # Issued at
    "jti": "unique-token-id",   # JWT ID for revocation support
    "type": "access"            # Token type
}

# Refresh Token Payload
{
    "sub": "user_id",
    "exp": 1704672000,          # Longer expiration
    "iat": 1704063600,
    "jti": "unique-token-id",   # JWT ID for revocation support
    "type": "refresh"
}
```

## Security Best Practices

### 1. Password Security

```python
# app/infrastructure/security/password.py
from passlib.context import CryptContext

# Argon2 is preferred, bcrypt as fallback
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
)

def hash_password(password: str) -> str:
    """Hash password with Argon2."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)
```

### 2. JWT Configuration

```python
# app/infrastructure/security/jwt.py
import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings

ALGORITHM = "HS256"

def create_access_token(
    subject: int | str,
    additional_claims: dict | None = None,
) -> str:
    """Create JWT access token with jti for revocation support."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "jti": str(uuid.uuid4()),  # JWT ID for blacklist/revocation
        "type": "access",
    }

    if additional_claims:
        # Note: Don't include sensitive data like is_superuser
        payload.update(additional_claims)

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    """Decode and verify JWT token."""
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[ALGORITHM],
    )

# Token blacklist (requires Redis)
async def is_token_blacklisted(jti: str) -> bool:
    """Check if token JTI is in blacklist."""
    # from app.infrastructure.cache.redis import redis_client
    # return await redis_client.exists(f"blacklist:{jti}")
    return False

async def blacklist_token(jti: str, expires_in: int) -> None:
    """Add token JTI to blacklist until expiration."""
    # from app.infrastructure.cache.redis import redis_client
    # await redis_client.setex(f"blacklist:{jti}", expires_in, "1")
    pass
```

### 3. OAuth2 Dependencies

```python
# app/api/v1/dependencies.py
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

from app.domain.entities.user import User
from app.infrastructure.security.jwt import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise credentials_exception

    # Get user from database
    user = await user_repository.get_by_id(session, int(user_id))
    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated",
        )

    return user

CurrentUser = Annotated[User, Depends(get_current_user)]
```

### 4. Permission Checking

```python
# app/api/v1/dependencies.py
from functools import wraps
from typing import Callable

def require_permission(permission: str):
    """Decorator to check user permissions."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, current_user: User, **kwargs):
            if not has_permission(current_user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

def has_permission(user: User, permission: str) -> bool:
    """Check if user has permission."""
    # Superuser has all permissions
    if user.is_superuser:
        return True

    # Check user roles/permissions
    return permission in user.permissions

# Usage
@router.delete("/{user_id}")
@require_permission("users:delete")
async def delete_user(user_id: int, current_user: CurrentUser):
    ...
```

### 5. API Key Authentication

```python
# app/api/v1/dependencies.py
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key_user(
    api_key: str = Depends(api_key_header),
    session: AsyncSession = Depends(get_async_session),
) -> User | None:
    """Authenticate via API key."""
    if not api_key:
        return None

    # Look up API key
    key_hash = hash_api_key(api_key)
    api_key_record = await api_key_repository.get_by_hash(session, key_hash)

    if not api_key_record or not api_key_record.is_active:
        return None

    return await user_repository.get_by_id(session, api_key_record.user_id)
```

## Token Refresh Flow

```python
# app/api/v1/routes/auth.py
@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    session: Session,
):
    """Refresh access token using refresh token."""
    try:
        payload = decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        user_id = payload.get("sub")
        user = await user_repository.get_by_id(session, int(user_id))

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        # Generate new tokens
        access_token = create_access_token(subject=user.id)
        new_refresh_token = create_refresh_token(subject=user.id)

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
        )
```

## Security Checklist

| Item | Status |
|------|--------|
| Password hashing (Argon2/bcrypt) | ✅ |
| JWT with short expiration | ✅ |
| Refresh token rotation | ✅ |
| No sensitive data in JWT | ✅ |
| Server-side permission check | ✅ |
| HTTPS enforced | ✅ |
| Rate limiting on auth endpoints | ✅ |
| Account lockout after failed attempts | ✅ |

## Related Skills

- `12-authentication`: JWT authentication
- `13-authorization`: RBAC/ABAC
- `14-api-keys`: API key management
- `15-security-hardening`: Security middleware
