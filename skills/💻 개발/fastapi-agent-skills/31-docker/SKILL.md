---
name: docker
description: |
  멀티스테이지 빌드, Docker Compose 구성을 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Docker Skill

멀티스테이지 빌드, Docker Compose 구성을 구현합니다.

## Triggers

- "docker", "dockerfile", "컨테이너", "docker compose"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |

---

## Output

### Production Dockerfile

```dockerfile
# Dockerfile
# Stage 1: Build
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Stage 2: Runtime
FROM python:3.12-slim as runtime

WORKDIR /app

# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Change ownership to non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Development Dockerfile

```dockerfile
# Dockerfile.dev
FROM python:3.12-slim

WORKDIR /app

# Install development dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install all dependencies including dev
RUN uv sync --frozen

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Run with hot reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### Docker Compose (Development)

```yaml
# docker-compose.yml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app
      - /app/.venv  # Don't override venv
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/app
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=development-secret-key
      - ENVIRONMENT=development
      - DEBUG=true
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - app-network

  db:
    image: postgres:16-alpine
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: app
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  # Background worker (Celery)
  worker:
    build:
      context: .
      dockerfile: Dockerfile.dev
    command: celery -A app.infrastructure.tasks.celery_app worker --loglevel=info
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/app
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
    depends_on:
      - db
      - redis
    networks:
      - app-network

  # Celery Beat (Scheduler)
  beat:
    build:
      context: .
      dockerfile: Dockerfile.dev
    command: celery -A app.infrastructure.tasks.celery_app beat --loglevel=info
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/app
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    networks:
      - app-network

  # Flower (Celery monitoring)
  flower:
    build:
      context: .
      dockerfile: Dockerfile.dev
    command: celery -A app.infrastructure.tasks.celery_app flower --port=5555
    ports:
      - "5555:5555"
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - worker
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  postgres-data:
  redis-data:
```

### Docker Compose (Production)

```yaml
# docker-compose.prod.yml
services:
  api:
    image: ${DOCKER_REGISTRY}/fastapi-app:${VERSION:-latest}
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - app-network
      - traefik-public
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`api.example.com`)"
      - "traefik.http.routers.api.tls=true"
      - "traefik.http.routers.api.tls.certresolver=letsencrypt"
      - "traefik.http.services.api.loadbalancer.server.port=8000"

  worker:
    image: ${DOCKER_REGISTRY}/fastapi-app:${VERSION:-latest}
    command: celery -A app.infrastructure.tasks.celery_app worker --loglevel=info --concurrency=4
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - CELERY_BROKER_URL=${REDIS_URL}
    networks:
      - app-network

  beat:
    image: ${DOCKER_REGISTRY}/fastapi-app:${VERSION:-latest}
    command: celery -A app.infrastructure.tasks.celery_app beat --loglevel=info
    deploy:
      replicas: 1  # Only one beat instance
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - CELERY_BROKER_URL=${REDIS_URL}
    networks:
      - app-network

networks:
  app-network:
    driver: overlay
  traefik-public:
    external: true
```

### Docker Ignore

```text
# .dockerignore
# Git
.git
.gitignore

# Python
__pycache__
*.py[cod]
*$py.class
*.so
.Python
.venv
venv/
ENV/

# IDE
.vscode
.idea
*.swp
*.swo

# Testing
.pytest_cache
.coverage
htmlcov/
.tox
.nox

# Build
*.egg-info/
dist/
build/

# Docker
Dockerfile*
docker-compose*.yml
.docker

# CI/CD
.github
.gitlab-ci.yml

# Documentation
docs/
*.md
!README.md

# Local configs
.env
.env.*
!.env.example

# Logs
*.log
logs/

# Misc
*.DS_Store
Thumbs.db
```

### Makefile for Docker

```makefile
# Makefile
.PHONY: help build up down logs shell db-shell migrate test lint

DOCKER_COMPOSE = docker-compose
DOCKER_COMPOSE_PROD = docker-compose -f docker-compose.prod.yml

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development
build: ## Build development containers
	$(DOCKER_COMPOSE) build

up: ## Start development containers
	$(DOCKER_COMPOSE) up -d

down: ## Stop development containers
	$(DOCKER_COMPOSE) down

logs: ## View container logs
	$(DOCKER_COMPOSE) logs -f

shell: ## Open shell in api container
	$(DOCKER_COMPOSE) exec api bash

db-shell: ## Open PostgreSQL shell
	$(DOCKER_COMPOSE) exec db psql -U postgres -d app

redis-cli: ## Open Redis CLI
	$(DOCKER_COMPOSE) exec redis redis-cli

# Database
migrate: ## Run database migrations
	$(DOCKER_COMPOSE) exec api alembic upgrade head

migrate-create: ## Create new migration
	$(DOCKER_COMPOSE) exec api alembic revision --autogenerate -m "$(name)"

migrate-down: ## Rollback last migration
	$(DOCKER_COMPOSE) exec api alembic downgrade -1

# Testing
test: ## Run tests
	$(DOCKER_COMPOSE) exec api pytest -v

test-cov: ## Run tests with coverage
	$(DOCKER_COMPOSE) exec api pytest --cov=app --cov-report=html

# Linting
lint: ## Run linters
	$(DOCKER_COMPOSE) exec api ruff check app/
	$(DOCKER_COMPOSE) exec api ruff format --check app/

lint-fix: ## Fix linting issues
	$(DOCKER_COMPOSE) exec api ruff check --fix app/
	$(DOCKER_COMPOSE) exec api ruff format app/

# Production
prod-build: ## Build production image
	docker build -t fastapi-app:latest .

prod-up: ## Start production containers
	$(DOCKER_COMPOSE_PROD) up -d

prod-down: ## Stop production containers
	$(DOCKER_COMPOSE_PROD) down

# Cleanup
clean: ## Remove all containers, volumes, and images
	$(DOCKER_COMPOSE) down -v --rmi all
	docker system prune -f
```

### Multi-Architecture Build

```yaml
# .github/workflows/docker-build.yml
name: Docker Build

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: myorg/fastapi-app
          tags: |
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Security Scanning

```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * *'

jobs:
  trivy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build image
        run: docker build -t fastapi-app:scan .

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'fastapi-app:scan'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'
```

## Docker Best Practices

| Practice | Description |
|----------|-------------|
| Multi-stage builds | Minimize image size |
| Non-root user | Security best practice |
| Health checks | Container orchestration support |
| .dockerignore | Reduce build context |
| Layer caching | Optimize build time |
| Pinned versions | Reproducible builds |

## References

- `_references/DEPLOYMENT-PATTERN.md`
