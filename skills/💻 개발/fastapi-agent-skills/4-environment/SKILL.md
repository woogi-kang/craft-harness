---
name: environment
description: |
  Pydantic Settings를 사용한 환경 변수 및 다중 환경 설정을 구성합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Environment Skill

Pydantic Settings를 사용한 환경 변수 및 다중 환경 설정을 구성합니다.

## Triggers

- "환경 설정", "env 설정", "settings", "config"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |
| `environments` | ❌ | 환경 목록 (기본: development, staging, production) |

---

## Output

### Settings 클래스

```python
# app/core/config.py
from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    PROJECT_NAME: str = "FastAPI App"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    API_V1_PREFIX: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # Database
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/app"
    )
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: RedisDsn = Field(default="redis://localhost:6379/0")
    REDIS_TTL: int = 3600  # 1 hour

    # Security
    SECRET_KEY: str = Field(min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = Field(default_factory=lambda: ["*"])
    CORS_ALLOW_HEADERS: list[str] = Field(default_factory=lambda: ["*"])

    # Trusted Hosts (for TrustedHostMiddleware)
    ALLOWED_HOSTS: list[str] = Field(
        default_factory=lambda: ["localhost", "127.0.0.1"]
    )

    # Request Limits
    MAX_REQUEST_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "json"

    # External Services
    SENTRY_DSN: str | None = None
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION: str = "ap-northeast-2"
    S3_BUCKET: str | None = None

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, v: str | list[str]) -> list[str]:
        """Parse allowed hosts from comma-separated string or list."""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",") if host.strip()]
        return v

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
```

### 환경별 .env 파일

```bash
# .env.development
PROJECT_NAME="FastAPI App (Dev)"
DEBUG=true
ENVIRONMENT=development

DATABASE_URL="postgresql+asyncpg://dev_user:dev_pass@localhost:5432/app_dev"
REDIS_URL="redis://localhost:6379/0"

SECRET_KEY="development-secret-key-min-32-characters"
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

CORS_ORIGINS="http://localhost:3000,http://localhost:8080"

LOG_LEVEL="DEBUG"
LOG_FORMAT="console"
```

```bash
# .env.staging
PROJECT_NAME="FastAPI App (Staging)"
DEBUG=false
ENVIRONMENT=staging

DATABASE_URL="postgresql+asyncpg://staging_user:staging_pass@db-staging:5432/app_staging"
REDIS_URL="redis://redis-staging:6379/0"

SECRET_KEY="${STAGING_SECRET_KEY}"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

CORS_ORIGINS="https://staging.example.com"

LOG_LEVEL="INFO"
LOG_FORMAT="json"

SENTRY_DSN="${SENTRY_DSN}"
```

```bash
# .env.production
PROJECT_NAME="FastAPI App"
DEBUG=false
ENVIRONMENT=production

DATABASE_URL="postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:5432/${DB_NAME}"
REDIS_URL="redis://${REDIS_HOST}:6379/0"

SECRET_KEY="${SECRET_KEY}"
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

CORS_ORIGINS="https://example.com,https://www.example.com"

LOG_LEVEL="WARNING"
LOG_FORMAT="json"

SENTRY_DSN="${SENTRY_DSN}"
```

### 환경별 로딩

```python
# app/core/config.py (환경별 로딩 버전)
import os
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


def get_env_file() -> str:
    """Get environment file based on APP_ENV."""
    env = os.getenv("APP_ENV", "development")
    env_file = f".env.{env}"
    return env_file if os.path.exists(env_file) else ".env"


class Settings(BaseSettings):
    """Application settings with environment-based configuration."""

    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ... (settings fields)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
```

### Settings Dependency

```python
# app/api/v1/dependencies/config.py
from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings

# Type alias for dependency injection
AppSettings = Annotated[Settings, Depends(get_settings)]
```

### Settings 사용 예시

```python
# 직접 임포트
from app.core.config import settings

print(settings.PROJECT_NAME)
print(settings.DATABASE_URL)

# Dependency로 주입
from fastapi import Depends
from app.core.config import get_settings, Settings


@router.get("/info")
async def get_info(settings: Settings = Depends(get_settings)):
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }
```

---

## 실행 방법

```bash
# 기본 (.env 사용)
uvicorn app.main:app --reload

# 환경 지정
APP_ENV=staging uvicorn app.main:app

# Docker에서 환경 지정
docker run -e APP_ENV=production my-app
```

## References

- `_references/ARCHITECTURE-PATTERN.md`
