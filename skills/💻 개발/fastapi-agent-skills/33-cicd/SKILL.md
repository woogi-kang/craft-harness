---
name: cicd
description: |
  GitHub Actions, GitLab CI 파이프라인을 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# CI/CD Skill

Extends: `../../_shared/cicd/SKILL.md` (공통 CI/CD 원칙 참조)

GitHub Actions, GitLab CI 파이프라인을 구현합니다.

## Triggers

- "ci cd", "github actions", "gitlab ci", "파이프라인", "배포 자동화"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |
| `platform` | ❌ | github/gitlab (기본: github) |

---

## Output

### GitHub Actions - Main Workflow

```yaml
# .github/workflows/main.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  release:
    types: [published]

env:
  PYTHON_VERSION: "3.12"
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

permissions:
  contents: read
  packages: write
  security-events: write

jobs:
  # Lint and Type Check
  lint:
    name: Lint & Type Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"

      - name: Set up Python
        run: uv python install ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: uv sync --frozen

      - name: Run Ruff linter
        run: uv run ruff check app/ tests/

      - name: Run Ruff formatter
        run: uv run ruff format --check app/ tests/

      - name: Run mypy
        run: uv run mypy app/

  # Unit Tests
  test-unit:
    name: Unit Tests
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Set up Python
        run: uv python install ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: uv sync --frozen --extra test

      - name: Run unit tests
        run: |
          uv run pytest tests/unit/ \
            -v \
            --cov=app \
            --cov-report=xml \
            --cov-report=html \
            --junitxml=test-results.xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          files: ./coverage.xml
          fail_ci_if_error: true

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: |
            test-results.xml
            htmlcov/

  # Integration Tests
  test-integration:
    name: Integration Tests
    runs-on: ubuntu-latest
    needs: test-unit
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Set up Python
        run: uv python install ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: uv sync --frozen --extra test

      - name: Run integration tests
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
          SECRET_KEY: test-secret-key
        run: |
          uv run pytest tests/integration/ \
            -v \
            --junitxml=integration-results.xml

  # Security Scan
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Set up Python
        run: uv python install ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: uv sync --frozen

      - name: Run Bandit security scan
        run: uv run bandit -r app/ -f sarif -o bandit-results.sarif

      - name: Upload SARIF results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: bandit-results.sarif

      - name: Run safety check
        run: uv run safety check

  # Build Docker Image
  build:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: [test-unit, test-integration, security]
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
      image-digest: ${{ steps.build.outputs.digest }}
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha

      - name: Build and push
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          provenance: true
          sbom: true

  # Container Scan
  container-scan:
    name: Container Security Scan
    runs-on: ubuntu-latest
    needs: build
    if: github.event_name != 'pull_request'
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'

  # Deploy to Staging
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: [build, container-scan]
    if: github.ref == 'refs/heads/develop'
    environment:
      name: staging
      url: https://staging-api.example.com
    steps:
      - uses: actions/checkout@v4

      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          kubeconfig: ${{ secrets.KUBE_CONFIG_STAGING }}

      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/fastapi-app \
            api=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
            -n fastapi-app-staging

      - name: Wait for rollout
        run: |
          kubectl rollout status deployment/fastapi-app \
            -n fastapi-app-staging \
            --timeout=5m

      - name: Run smoke tests
        run: |
          curl -f https://staging-api.example.com/health || exit 1

  # Deploy to Production
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: build
    if: github.event_name == 'release'
    environment:
      name: production
      url: https://api.example.com
    steps:
      - uses: actions/checkout@v4

      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          kubeconfig: ${{ secrets.KUBE_CONFIG_PRODUCTION }}

      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/fastapi-app \
            api=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.event.release.tag_name }} \
            -n fastapi-app-prod

      - name: Wait for rollout
        run: |
          kubectl rollout status deployment/fastapi-app \
            -n fastapi-app-prod \
            --timeout=5m

      - name: Verify deployment
        run: |
          curl -f https://api.example.com/health || exit 1

      - name: Create Sentry release
        uses: getsentry/action-release@v1
        env:
          SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
          SENTRY_ORG: ${{ secrets.SENTRY_ORG }}
          SENTRY_PROJECT: ${{ secrets.SENTRY_PROJECT }}
        with:
          environment: production
          version: ${{ github.event.release.tag_name }}
```

### Database Migration Workflow

```yaml
# .github/workflows/migrate.yml
name: Database Migration

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to migrate'
        required: true
        type: choice
        options:
          - staging
          - production
      direction:
        description: 'Migration direction'
        required: true
        type: choice
        options:
          - upgrade
          - downgrade
      revision:
        description: 'Target revision (for downgrade)'
        required: false
        default: '-1'

jobs:
  migrate:
    name: Run Migration
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment }}
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --frozen

      - name: Run migration
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          if [ "${{ github.event.inputs.direction }}" == "upgrade" ]; then
            uv run alembic upgrade head
          else
            uv run alembic downgrade ${{ github.event.inputs.revision }}
          fi

      - name: Verify migration
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: uv run alembic current
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - lint
  - test
  - security
  - build
  - deploy

variables:
  PYTHON_VERSION: "3.12"
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"
  DOCKER_TLS_CERTDIR: "/certs"

.python-base:
  image: python:${PYTHON_VERSION}-slim
  before_script:
    - pip install uv
    - uv sync --frozen

cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - .cache/pip
    - .venv

# Lint Stage
lint:
  extends: .python-base
  stage: lint
  script:
    - uv run ruff check app/ tests/
    - uv run ruff format --check app/ tests/
    - uv run mypy app/

# Test Stage
test-unit:
  extends: .python-base
  stage: test
  script:
    - uv sync --frozen --extra test
    - uv run pytest tests/unit/ --cov=app --cov-report=xml --junitxml=report.xml
  artifacts:
    reports:
      junit: report.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

test-integration:
  extends: .python-base
  stage: test
  services:
    - name: postgres:16-alpine
      alias: db
    - name: redis:7-alpine
      alias: redis
  variables:
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: postgres
    POSTGRES_DB: test_db
    DATABASE_URL: postgresql+asyncpg://postgres:postgres@db:5432/test_db
    REDIS_URL: redis://redis:6379/0
    SECRET_KEY: test-secret-key
  script:
    - uv sync --frozen --extra test
    - uv run pytest tests/integration/ --junitxml=integration-report.xml
  artifacts:
    reports:
      junit: integration-report.xml

# Security Stage
security-scan:
  extends: .python-base
  stage: security
  script:
    - uv run bandit -r app/ -f json -o bandit-report.json
    - uv run safety check --json > safety-report.json
  artifacts:
    paths:
      - bandit-report.json
      - safety-report.json
  allow_failure: true

# Build Stage
build:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - |
      if [ "$CI_COMMIT_TAG" ]; then
        docker tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA $CI_REGISTRY_IMAGE:$CI_COMMIT_TAG
        docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_TAG
      fi
  rules:
    - if: $CI_COMMIT_BRANCH == "main" || $CI_COMMIT_TAG

# Deploy Staging
deploy-staging:
  stage: deploy
  image: bitnami/kubectl:latest
  environment:
    name: staging
    url: https://staging-api.example.com
  script:
    - kubectl config use-context staging
    - kubectl set image deployment/fastapi-app api=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA -n fastapi-app-staging
    - kubectl rollout status deployment/fastapi-app -n fastapi-app-staging --timeout=5m
  rules:
    - if: $CI_COMMIT_BRANCH == "develop"

# Deploy Production
deploy-production:
  stage: deploy
  image: bitnami/kubectl:latest
  environment:
    name: production
    url: https://api.example.com
  script:
    - kubectl config use-context production
    - kubectl set image deployment/fastapi-app api=$CI_REGISTRY_IMAGE:$CI_COMMIT_TAG -n fastapi-app-prod
    - kubectl rollout status deployment/fastapi-app -n fastapi-app-prod --timeout=5m
  rules:
    - if: $CI_COMMIT_TAG
  when: manual
```

### Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: detect-private-key
      - id: check-merge-conflict

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy
        additional_dependencies:
          - pydantic>=2.0
          - types-redis

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.2
    hooks:
      - id: gitleaks
```

## CI/CD Best Practices

| Practice | Description |
|----------|-------------|
| Fast feedback | Lint first, then test |
| Parallel jobs | Run independent jobs concurrently |
| Caching | Cache dependencies between runs |
| Environment protection | Require approval for production |
| Rollback strategy | Automatic rollback on failure |
| Secret management | Use encrypted secrets |

---

## Automatic Rollback Strategy

Implement automatic rollback when deployment fails health checks.

### GitHub Actions with Auto-Rollback

```yaml
# .github/workflows/deploy-with-rollback.yml
name: Deploy with Auto-Rollback

on:
  push:
    branches: [main]
  release:
    types: [published]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  deploy-staging:
    name: Deploy to Staging with Rollback
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment:
      name: staging
      url: https://staging-api.example.com
    outputs:
      previous-revision: ${{ steps.get-revision.outputs.revision }}
      deployed: ${{ steps.deploy.outputs.success }}
    steps:
      - uses: actions/checkout@v4

      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          kubeconfig: ${{ secrets.KUBE_CONFIG_STAGING }}

      - name: Get current revision (for rollback)
        id: get-revision
        run: |
          REVISION=$(kubectl rollout history deployment/fastapi-app \
            -n fastapi-app-staging \
            --output=jsonpath='{.metadata.generation}' 2>/dev/null || echo "0")
          echo "revision=$REVISION" >> $GITHUB_OUTPUT
          echo "Current revision: $REVISION"

      - name: Deploy new version
        id: deploy
        run: |
          kubectl set image deployment/fastapi-app \
            api=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
            -n fastapi-app-staging

          # Wait for rollout with timeout
          if kubectl rollout status deployment/fastapi-app \
              -n fastapi-app-staging \
              --timeout=5m; then
            echo "success=true" >> $GITHUB_OUTPUT
          else
            echo "success=false" >> $GITHUB_OUTPUT
            exit 1
          fi

      - name: Health check
        id: healthcheck
        timeout-minutes: 2
        run: |
          MAX_RETRIES=10
          RETRY_DELAY=6

          for i in $(seq 1 $MAX_RETRIES); do
            echo "Health check attempt $i/$MAX_RETRIES"

            # Check /health endpoint
            HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
              https://staging-api.example.com/health || echo "000")

            if [ "$HTTP_CODE" = "200" ]; then
              echo "Health check passed!"
              exit 0
            fi

            echo "Health check failed (HTTP $HTTP_CODE), retrying in ${RETRY_DELAY}s..."
            sleep $RETRY_DELAY
          done

          echo "Health check failed after $MAX_RETRIES attempts"
          exit 1

      - name: Rollback on failure
        if: failure() && steps.deploy.outputs.success == 'true'
        run: |
          echo "Rolling back to previous revision..."

          # Rollback to previous revision
          kubectl rollout undo deployment/fastapi-app \
            -n fastapi-app-staging

          # Wait for rollback to complete
          kubectl rollout status deployment/fastapi-app \
            -n fastapi-app-staging \
            --timeout=5m

          echo "Rollback completed successfully"

      - name: Notify on rollback
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "⚠️ Deployment failed and rolled back",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Deployment Failed*\n- Environment: staging\n- Commit: ${{ github.sha }}\n- Rolled back to previous version"
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}

  deploy-production:
    name: Deploy to Production with Rollback
    runs-on: ubuntu-latest
    if: github.event_name == 'release'
    environment:
      name: production
      url: https://api.example.com
    steps:
      - uses: actions/checkout@v4

      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          kubeconfig: ${{ secrets.KUBE_CONFIG_PRODUCTION }}

      - name: Create deployment annotation
        run: |
          kubectl annotate deployment/fastapi-app \
            kubernetes.io/change-cause="Release ${{ github.event.release.tag_name }}" \
            -n fastapi-app-prod \
            --overwrite

      - name: Deploy with blue-green strategy
        run: |
          # Deploy to green (new version)
          kubectl set image deployment/fastapi-app \
            api=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.event.release.tag_name }} \
            -n fastapi-app-prod

          # Wait for pods to be ready
          kubectl rollout status deployment/fastapi-app \
            -n fastapi-app-prod \
            --timeout=10m

      - name: Smoke tests
        id: smoke
        timeout-minutes: 5
        run: |
          # Basic health check
          curl -f https://api.example.com/health || exit 1

          # API response check
          RESPONSE=$(curl -s https://api.example.com/api/v1/health)
          if echo "$RESPONSE" | jq -e '.status == "healthy"' > /dev/null; then
            echo "Smoke tests passed"
          else
            echo "Smoke tests failed"
            exit 1
          fi

      - name: Rollback on smoke test failure
        if: failure() && steps.smoke.outcome == 'failure'
        run: |
          echo "Smoke tests failed, initiating rollback..."

          # Get previous revision
          PREV_REVISION=$(kubectl rollout history deployment/fastapi-app \
            -n fastapi-app-prod \
            --output=jsonpath='{.status.observedGeneration}')

          ROLLBACK_TO=$((PREV_REVISION - 1))

          kubectl rollout undo deployment/fastapi-app \
            --to-revision=$ROLLBACK_TO \
            -n fastapi-app-prod

          kubectl rollout status deployment/fastapi-app \
            -n fastapi-app-prod \
            --timeout=5m

          # Create incident
          echo "ROLLBACK_PERFORMED=true" >> $GITHUB_ENV

      - name: Create Sentry release
        if: success()
        uses: getsentry/action-release@v1
        env:
          SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
          SENTRY_ORG: ${{ secrets.SENTRY_ORG }}
          SENTRY_PROJECT: ${{ secrets.SENTRY_PROJECT }}
        with:
          environment: production
          version: ${{ github.event.release.tag_name }}
```

### Kubernetes Rollback Script

```bash
#!/bin/bash
# scripts/rollback.sh - Manual/automated rollback script

set -euo pipefail

NAMESPACE="${NAMESPACE:-fastapi-app-prod}"
DEPLOYMENT="${DEPLOYMENT:-fastapi-app}"
REVISION="${1:-}"

echo "=== Kubernetes Rollback Script ==="
echo "Namespace: $NAMESPACE"
echo "Deployment: $DEPLOYMENT"

# Show rollout history
echo ""
echo "Rollout History:"
kubectl rollout history deployment/$DEPLOYMENT -n $NAMESPACE

# Get current revision
CURRENT=$(kubectl get deployment/$DEPLOYMENT -n $NAMESPACE \
  -o jsonpath='{.status.observedGeneration}')
echo ""
echo "Current revision: $CURRENT"

if [ -n "$REVISION" ]; then
  # Rollback to specific revision
  echo "Rolling back to revision: $REVISION"
  kubectl rollout undo deployment/$DEPLOYMENT \
    --to-revision=$REVISION \
    -n $NAMESPACE
else
  # Rollback to previous revision
  echo "Rolling back to previous revision..."
  kubectl rollout undo deployment/$DEPLOYMENT \
    -n $NAMESPACE
fi

# Wait for rollback
echo ""
echo "Waiting for rollback to complete..."
kubectl rollout status deployment/$DEPLOYMENT \
  -n $NAMESPACE \
  --timeout=5m

# Verify
echo ""
echo "Rollback completed. Current pods:"
kubectl get pods -n $NAMESPACE -l app=$DEPLOYMENT

# Health check
echo ""
echo "Running health check..."
kubectl exec -n $NAMESPACE \
  $(kubectl get pod -n $NAMESPACE -l app=$DEPLOYMENT -o jsonpath='{.items[0].metadata.name}') \
  -- curl -s http://localhost:8000/health || echo "Health check failed"
```

### ArgoCD Auto-Rollback Configuration

```yaml
# argocd/application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: fastapi-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/fastapi-app
    targetRevision: HEAD
    path: kubernetes/overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: fastapi-app-prod
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
    retry:
      limit: 3
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
  # Rollback configuration
  revisionHistoryLimit: 10
---
# ArgoCD Rollback Analysis
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
  namespace: argocd
spec:
  metrics:
    - name: success-rate
      interval: 30s
      count: 5
      successCondition: result[0] >= 0.95
      failureLimit: 3
      provider:
        prometheus:
          address: http://prometheus:9090
          query: |
            sum(rate(http_requests_total{status=~"2..",app="fastapi-app"}[5m])) /
            sum(rate(http_requests_total{app="fastapi-app"}[5m]))
    - name: error-rate
      interval: 30s
      count: 5
      successCondition: result[0] < 0.05
      failureLimit: 2
      provider:
        prometheus:
          address: http://prometheus:9090
          query: |
            sum(rate(http_requests_total{status=~"5..",app="fastapi-app"}[5m])) /
            sum(rate(http_requests_total{app="fastapi-app"}[5m]))
```

### Rollback Decision Matrix

| Condition | Action | Method |
|-----------|--------|--------|
| Pod crash loop | Auto rollback | Kubernetes |
| Health check fail | Auto rollback | CI/CD pipeline |
| Error rate > 5% | Auto rollback | ArgoCD Analysis |
| Latency P99 > 2s | Alert + manual | Prometheus Alert |
| Memory leak | Alert + manual | Prometheus Alert |
| Security vuln found | Immediate rollback | Manual |

### Rollback Checklist

```markdown
## Pre-Rollback Checklist
- [ ] Confirm rollback necessity (not transient issue)
- [ ] Identify target revision
- [ ] Notify team in Slack/incident channel
- [ ] Check database migration compatibility

## Rollback Execution
- [ ] Execute rollback command
- [ ] Monitor rollout status
- [ ] Verify pods are healthy
- [ ] Run health checks

## Post-Rollback
- [ ] Confirm service restored
- [ ] Update incident timeline
- [ ] Schedule post-mortem
- [ ] Document root cause
```

---

## Argo Rollouts - Progressive Delivery

Argo Rollouts provides advanced deployment strategies with **automated, metrics-based rollback**.

### Argo Rollouts Installation

```bash
# Install Argo Rollouts controller
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml

# Install kubectl plugin (optional)
brew install argoproj/tap/kubectl-argo-rollouts
```

### Prometheus ServiceMonitor for Argo Rollouts

Prometheus가 애플리케이션 메트릭을 자동으로 수집하도록 ServiceMonitor를 설정합니다.
AnalysisTemplate에서 참조하는 메트릭은 반드시 Prometheus에 수집되어야 합니다.

```yaml
# kubernetes/servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: fastapi-app
  namespace: fastapi-app-prod
  labels:
    release: prometheus  # Prometheus Operator가 이 레이블로 ServiceMonitor를 선택
spec:
  selector:
    matchLabels:
      app: fastapi-app
  namespaceSelector:
    matchNames:
      - fastapi-app-prod
  endpoints:
    - port: http
      path: /metrics
      interval: 15s
      scrapeTimeout: 10s
      honorLabels: true
      # 메트릭에 추가 레이블 부여
      relabelings:
        - sourceLabels: [__meta_kubernetes_pod_label_role]
          targetLabel: role  # canary 또는 stable
        - sourceLabels: [__meta_kubernetes_namespace]
          targetLabel: namespace
---
# Prometheus가 ServiceMonitor를 선택하도록 ClusterRole 확인
# prometheus-operator 설치 시 자동 설정됨
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: prometheus-servicemonitor
rules:
  - apiGroups: ["monitoring.coreos.com"]
    resources: ["servicemonitors"]
    verbs: ["get", "list", "watch"]
```

> **34-observability 연결**: 위 ServiceMonitor는 `34-observability/SKILL.md`의 `/metrics` 엔드포인트와 연결됩니다.
> FastAPI 앱에서 `prometheus_client`로 노출하는 메트릭이 Prometheus에 수집되어 AnalysisTemplate에서 사용됩니다.

### Canary Traffic Steps 설명

Canary 배포는 단계적으로 트래픽을 새 버전으로 이동하면서 메트릭을 분석합니다.

| Step | Weight | 설명 | 분석 대상 |
|------|--------|------|-----------|
| 1 | 5% | 초기 테스트 - 소수 사용자에게만 노출 | 기본 에러율 확인 |
| 2 | pause 2m | 5% 상태에서 메트릭 수집 대기 | success-rate, latency 분석 |
| 3 | 20% | 점진적 확장 - 문제 없으면 증가 | 에러율 5% 미만 확인 |
| 4 | pause 2m | 20% 상태에서 안정성 확인 | P99 latency < 500ms |
| 5 | 50% | 절반 트래픽 - 주요 전환점 | 전체 성능 영향 분석 |
| 6 | pause 5m | 장시간 관찰 - 메모리 누수 등 | 리소스 사용량 모니터링 |
| 7 | 80% | 거의 전체 - 롤백 결정 마지막 기회 | 최종 안정성 확인 |
| 8 | pause 5m | 최종 검증 | 100% 전환 전 마지막 분석 |
| 9 | 100% | 완전 전환 (자동) | - |

### Canary Deployment with Prometheus Metrics

```yaml
# kubernetes/rollout.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: fastapi-app
  namespace: fastapi-app-prod
spec:
  replicas: 5
  revisionHistoryLimit: 5
  selector:
    matchLabels:
      app: fastapi-app
  template:
    metadata:
      labels:
        app: fastapi-app
    spec:
      containers:
        - name: api
          image: ghcr.io/org/fastapi-app:latest
          ports:
            - containerPort: 8000
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
  strategy:
    canary:
      # Canary traffic weight steps
      # 각 단계별로 트래픽 비율을 조절하며 메트릭 분석 수행
      steps:
        - setWeight: 5      # Step 1: 5% 트래픽을 canary로 전송
        - pause: { duration: 2m }  # 2분간 메트릭 수집 및 분석
        - setWeight: 20     # Step 3: 20%로 증가
        - pause: { duration: 2m }
        - setWeight: 50     # Step 5: 50% - 주요 전환점
        - pause: { duration: 5m }  # 장시간 관찰
        - setWeight: 80     # Step 7: 80% - 거의 완전 전환
        - pause: { duration: 5m }  # 최종 검증

      # Prometheus metrics-based analysis at each step
      analysis:
        templates:
          - templateName: success-rate-analysis
          - templateName: latency-analysis
        startingStep: 1  # Start analysis from step 1 (after 5% traffic)
        args:
          - name: service-name
            value: fastapi-app

      # Anti-affinity for canary pods
      canaryMetadata:
        labels:
          role: canary
      stableMetadata:
        labels:
          role: stable

      # Traffic routing (requires Istio/Nginx/ALB)
      trafficRouting:
        nginx:
          stableIngress: fastapi-app-stable
          additionalIngressAnnotations:
            canary-by-header: X-Canary
---
# Analysis Template: Success Rate (Error Rate < 1%)
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate-analysis
  namespace: fastapi-app-prod
spec:
  args:
    - name: service-name
  metrics:
    - name: success-rate
      # ┌─────────────────────────────────────────────────────────────────┐
      # │ AnalysisTemplate 필드 설명                                        │
      # ├─────────────────────────────────────────────────────────────────┤
      # │ interval: 메트릭 측정 주기 (30s = 30초마다 쿼리 실행)               │
      # │ count: 총 측정 횟수 (10 = 10번 측정 후 분석 완료)                   │
      # │ successCondition: 성공으로 판단하는 조건 (result[0] >= 0.99)       │
      # │ failureCondition: 즉시 실패로 판단하는 조건 (result[0] < 0.95)     │
      # │ failureLimit: 실패 허용 횟수 (3 = 3번 연속 실패 시 롤백)           │
      # │                                                                 │
      # │ 동작 흐름:                                                       │
      # │ 1. 30초마다 Prometheus 쿼리 실행                                  │
      # │ 2. result[0] >= 0.99 → 해당 측정은 "성공"                        │
      # │ 3. result[0] < 0.95 → 해당 측정은 "실패" (failureLimit 카운트)    │
      # │ 4. 0.95 <= result[0] < 0.99 → "불확실" (pass도 fail도 아님)      │
      # │ 5. failureLimit(3) 초과 시 → 분석 실패 → 자동 롤백                │
      # │ 6. count(10)회 완료 + 실패 < failureLimit → 분석 성공             │
      # └─────────────────────────────────────────────────────────────────┘
      interval: 30s
      count: 10
      # Success: 99%+ success rate (이 조건 만족 시 해당 측정은 성공)
      successCondition: result[0] >= 0.99
      # Fail immediately if success rate drops below 95% (즉시 실패 카운트 증가)
      failureCondition: result[0] < 0.95
      # 3번 연속 실패 시 Analysis 전체가 Failed → 자동 롤백 트리거
      failureLimit: 3
      provider:
        prometheus:
          # ServiceMonitor로 수집된 메트릭을 Prometheus에서 조회
          # prometheus.monitoring은 k8s 내부 서비스 DNS
          address: http://prometheus.monitoring:9090
          query: |
            sum(rate(http_requests_total{
              service="{{args.service-name}}",
              status=~"2.."
            }[5m])) /
            sum(rate(http_requests_total{
              service="{{args.service-name}}"
            }[5m]))
---
# Analysis Template: Latency (P99 < 500ms)
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: latency-analysis
  namespace: fastapi-app-prod
spec:
  args:
    - name: service-name
  metrics:
    - name: latency-p99
      interval: 30s
      count: 10
      # Success: P99 latency under 500ms
      successCondition: result[0] < 0.5
      # Fail if P99 exceeds 1 second
      failureCondition: result[0] > 1.0
      failureLimit: 3
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            histogram_quantile(0.99,
              sum(rate(http_request_duration_seconds_bucket{
                service="{{args.service-name}}"
              }[5m])) by (le)
            )
---
# Analysis Template: Error Rate Spike Detection
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: error-rate-analysis
  namespace: fastapi-app-prod
spec:
  args:
    - name: service-name
  metrics:
    - name: error-rate
      interval: 30s
      count: 10
      # Fail if error rate exceeds 5%
      successCondition: result[0] < 0.05
      failureLimit: 2
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            sum(rate(http_requests_total{
              service="{{args.service-name}}",
              status=~"5.."
            }[5m])) /
            sum(rate(http_requests_total{
              service="{{args.service-name}}"
            }[5m]))

    - name: pod-restart-rate
      interval: 1m
      count: 5
      # Fail if any pod restarts
      successCondition: result[0] == 0
      failureLimit: 1
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            sum(increase(kube_pod_container_status_restarts_total{
              pod=~"fastapi-app-.*"
            }[5m]))
```

### Blue-Green Deployment with Metrics Verification

```yaml
# kubernetes/rollout-blue-green.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: fastapi-app-bg
  namespace: fastapi-app-prod
spec:
  replicas: 5
  revisionHistoryLimit: 3
  selector:
    matchLabels:
      app: fastapi-app
  template:
    metadata:
      labels:
        app: fastapi-app
    spec:
      containers:
        - name: api
          image: ghcr.io/org/fastapi-app:latest
          ports:
            - containerPort: 8000
  strategy:
    blueGreen:
      # Reference to active (blue) and preview (green) services
      activeService: fastapi-app-active
      previewService: fastapi-app-preview

      # Auto-promote after successful analysis
      autoPromotionEnabled: true
      autoPromotionSeconds: 300  # 5 minutes

      # Pre-promotion analysis (verify green before switching)
      prePromotionAnalysis:
        templates:
          - templateName: success-rate-analysis
          - templateName: latency-analysis
        args:
          - name: service-name
            value: fastapi-app-preview  # Analyze preview service

      # Post-promotion analysis (verify after switch)
      postPromotionAnalysis:
        templates:
          - templateName: success-rate-analysis
        args:
          - name: service-name
            value: fastapi-app-active

      # Scale down delay for rollback window
      scaleDownDelaySeconds: 600  # Keep old pods for 10 min

      # Anti-affinity rules
      previewReplicaCount: 5  # Match production replicas
---
apiVersion: v1
kind: Service
metadata:
  name: fastapi-app-active
  namespace: fastapi-app-prod
spec:
  selector:
    app: fastapi-app
  ports:
    - port: 80
      targetPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: fastapi-app-preview
  namespace: fastapi-app-prod
spec:
  selector:
    app: fastapi-app
  ports:
    - port: 80
      targetPort: 8000
```

### GitHub Actions with Argo Rollouts

```yaml
# .github/workflows/deploy-argo-rollouts.yml
name: Deploy with Argo Rollouts

on:
  push:
    branches: [main]
  release:
    types: [published]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  deploy:
    name: Deploy with Canary
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://api.example.com
    steps:
      - uses: actions/checkout@v4

      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          kubeconfig: ${{ secrets.KUBE_CONFIG_PRODUCTION }}

      - name: Install Argo Rollouts kubectl plugin
        run: |
          curl -LO https://github.com/argoproj/argo-rollouts/releases/latest/download/kubectl-argo-rollouts-linux-amd64
          chmod +x kubectl-argo-rollouts-linux-amd64
          sudo mv kubectl-argo-rollouts-linux-amd64 /usr/local/bin/kubectl-argo-rollouts

      - name: Update image and trigger rollout
        run: |
          kubectl argo rollouts set image fastapi-app \
            api=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
            -n fastapi-app-prod

      - name: Monitor rollout progress
        run: |
          # Watch rollout with timeout
          kubectl argo rollouts status fastapi-app \
            -n fastapi-app-prod \
            --timeout 15m

      - name: Get rollout status
        if: always()
        run: |
          kubectl argo rollouts get rollout fastapi-app \
            -n fastapi-app-prod \
            --watch=false

      - name: Abort on failure (auto-rollback)
        if: failure()
        run: |
          echo "Rollout failed - triggering abort for automatic rollback"
          kubectl argo rollouts abort fastapi-app \
            -n fastapi-app-prod

          # Wait for abort to complete
          kubectl argo rollouts status fastapi-app \
            -n fastapi-app-prod \
            --timeout 5m || true

          # Notify team
          echo "ROLLBACK_TRIGGERED=true" >> $GITHUB_ENV

      - name: Notify on rollback
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "🔴 Canary deployment failed - Auto-rollback triggered",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Deployment Rolled Back*\n- Commit: ${{ github.sha }}\n- Reason: Prometheus metrics failed threshold\n- Action: Investigate before retry"
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### Manual Rollout Commands

```bash
# Monitor rollout in real-time
kubectl argo rollouts get rollout fastapi-app -n fastapi-app-prod --watch

# Promote canary to next step manually
kubectl argo rollouts promote fastapi-app -n fastapi-app-prod

# Skip all steps and promote immediately (use with caution)
kubectl argo rollouts promote fastapi-app -n fastapi-app-prod --full

# Abort rollout (triggers automatic rollback)
kubectl argo rollouts abort fastapi-app -n fastapi-app-prod

# Retry a failed rollout
kubectl argo rollouts retry rollout fastapi-app -n fastapi-app-prod

# Rollback to specific revision
kubectl argo rollouts undo fastapi-app -n fastapi-app-prod --to-revision=2

# Pause rollout at current step
kubectl argo rollouts pause fastapi-app -n fastapi-app-prod

# Resume paused rollout
kubectl argo rollouts resume fastapi-app -n fastapi-app-prod
```

### Prometheus Alert Rules for Rollout

```yaml
# prometheus/rollout-alerts.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: argo-rollouts-alerts
  namespace: monitoring
spec:
  groups:
    - name: argo-rollouts
      rules:
        - alert: RolloutFailed
          expr: |
            kube_rollout_status_phase{phase="Degraded"} == 1
          for: 1m
          labels:
            severity: critical
          annotations:
            summary: "Argo Rollout {{ $labels.rollout }} is degraded"
            description: "Rollout failed and was automatically rolled back"

        - alert: RolloutStuck
          expr: |
            kube_rollout_status_phase{phase="Paused"} == 1
          for: 30m
          labels:
            severity: warning
          annotations:
            summary: "Argo Rollout {{ $labels.rollout }} is paused"
            description: "Rollout has been paused for over 30 minutes"

        - alert: CanaryHighErrorRate
          expr: |
            sum(rate(http_requests_total{status=~"5..",role="canary"}[5m]))
            / sum(rate(http_requests_total{role="canary"}[5m])) > 0.05
          for: 2m
          labels:
            severity: critical
          annotations:
            summary: "Canary has high error rate"
            description: "Canary pods have >5% error rate"

        - alert: CanaryHighLatency
          expr: |
            histogram_quantile(0.99,
              sum(rate(http_request_duration_seconds_bucket{role="canary"}[5m])) by (le)
            ) > 1.0
          for: 2m
          labels:
            severity: warning
          annotations:
            summary: "Canary has high latency"
            description: "Canary P99 latency exceeds 1 second"
```

### Metrics-Based Rollback Summary

| Metric | Threshold | Action | Response Time |
|--------|-----------|--------|---------------|
| Error Rate | > 5% | Auto Rollback | < 2 min |
| Success Rate | < 95% | Auto Rollback | < 2 min |
| Latency P99 | > 1s | Auto Rollback | < 3 min |
| Pod Restarts | > 0 | Auto Rollback | < 1 min |
| CPU Saturation | > 90% | Alert | Manual review |
| Memory Usage | > 85% | Alert | Manual review |

### Deployment Strategy Comparison

| Strategy | Use Case | Risk | Rollback Speed |
|----------|----------|------|----------------|
| **Rolling Update** | Low-risk changes | Medium | Slow (minutes) |
| **Canary** | New features, risky changes | Low | Fast (seconds) |
| **Blue-Green** | Zero-downtime, instant switch | Very Low | Instant |
| **A/B Testing** | Feature experiments | Low | Instant |

---

## Analysis 실패 시 동작

AnalysisTemplate 분석이 실패하면 Argo Rollouts가 자동으로 롤백을 수행합니다.

### 실패 시나리오별 동작

| 시나리오 | 조건 | Argo Rollouts 동작 |
|----------|------|-------------------|
| **Hard Failure** | `failureCondition` 충족 + `failureLimit` 초과 | 즉시 롤백, Rollout status = `Degraded` |
| **Timeout** | `count` 완료 전 시간 초과 | 롤백, status = `Error` |
| **Prometheus 연결 실패** | 쿼리 실행 불가 | 기본적으로 실패 처리, 롤백 |
| **Inconclusive** | success도 failure도 아닌 결과 | `inconclusiveLimit` 초과 시 롤백 |

### 롤백 흐름

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Canary     │ ──▶ │  Analysis    │ ──▶ │   Result     │
│  Deployment  │     │  Running     │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
                                                 │
                     ┌───────────────────────────┼───────────────────────────┐
                     │                           │                           │
                     ▼                           ▼                           ▼
              ┌──────────────┐           ┌──────────────┐           ┌──────────────┐
              │   Success    │           │   Failed     │           │  Inconclusive│
              │   Promote    │           │   Rollback   │           │   Rollback   │
              └──────────────┘           └──────────────┘           └──────────────┘
                     │                           │                           │
                     ▼                           ▼                           ▼
              ┌──────────────┐           ┌──────────────┐           ┌──────────────┐
              │  100% Canary │           │  0% Canary   │           │  0% Canary   │
              │  (New Ver.)  │           │ (Old Ver.)   │           │ (Old Ver.)   │
              └──────────────┘           └──────────────┘           └──────────────┘
```

### Analysis 재시도 설정

```yaml
# 분석 실패 시 재시도 옵션
spec:
  metrics:
    - name: success-rate
      failureLimit: 3          # 3번까지 실패 허용
      inconclusiveLimit: 2     # 2번까지 불확실 결과 허용
      consecutiveErrorLimit: 4 # 4번 연속 쿼리 에러 시 실패
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
```

---

## Argo Rollouts 로컬 테스트 환경

실제 배포 전 로컬에서 Argo Rollouts를 테스트하는 방법입니다.

### 1. Kind 클러스터 + Argo Rollouts 설치

```bash
# Kind 클러스터 생성
cat <<EOF | kind create cluster --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
- role: worker
EOF

# Argo Rollouts 설치
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml

# Prometheus Operator 설치 (메트릭 분석용)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false
```

### 2. 테스트용 Rollout 배포

```bash
# 네임스페이스 생성
kubectl create namespace test-rollout

# 테스트 Rollout 배포
kubectl apply -f kubernetes/rollout.yaml -n test-rollout

# ServiceMonitor 배포 (Prometheus 수집용)
kubectl apply -f kubernetes/servicemonitor.yaml -n test-rollout

# 상태 확인
kubectl argo rollouts get rollout fastapi-app -n test-rollout --watch
```

### 3. 이미지 업데이트로 Canary 테스트

```bash
# 새 이미지로 업데이트 (Canary 배포 시작)
kubectl argo rollouts set image fastapi-app \
  api=ghcr.io/org/fastapi-app:v2 \
  -n test-rollout

# Canary 진행 상황 모니터링
kubectl argo rollouts get rollout fastapi-app -n test-rollout --watch

# 수동으로 다음 단계 진행 (테스트용)
kubectl argo rollouts promote fastapi-app -n test-rollout

# 롤백 테스트
kubectl argo rollouts abort fastapi-app -n test-rollout
```

### 4. 메트릭 기반 분석 테스트

```bash
# Prometheus UI에서 메트릭 확인
kubectl port-forward svc/prometheus-kube-prometheus-prometheus -n monitoring 9090:9090

# 브라우저에서 http://localhost:9090 접속
# 쿼리: http_requests_total{service="fastapi-app"}

# AnalysisRun 상태 확인
kubectl get analysisrun -n test-rollout
kubectl describe analysisrun <analysisrun-name> -n test-rollout
```

### 5. 정리

```bash
# 테스트 리소스 삭제
kubectl delete namespace test-rollout
kubectl delete namespace argo-rollouts
kubectl delete namespace monitoring

# Kind 클러스터 삭제
kind delete cluster
```

## References

- `_references/DEPLOYMENT-PATTERN.md`
- `34-observability/SKILL.md` - Prometheus 메트릭 설정
