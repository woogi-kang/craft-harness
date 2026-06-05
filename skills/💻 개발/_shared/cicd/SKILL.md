---
name: cicd-shared
description: |
  GitHub Actions 기반 CI/CD 파이프라인 공통 방법론.
  FastAPI, Flutter, Next.js 에이전트가 공유하는 CI/CD 원칙.
metadata:
  category: "💻 개발"
  type: shared
  version: "1.0.0"
  consumers:
    - fastapi-agent-skills/33-cicd
    - flutter-agent-skills/22-cicd
    - nextjs-agent-skills/26-cicd
---
# CI/CD Skill (Shared)

프레임워크에 관계없이 적용되는 CI/CD 파이프라인 공통 방법론입니다.

## Triggers

- "ci/cd", "github actions", "배포 자동화", "ci 설정", "파이프라인"

---

## Input (공통)

| 항목 | 필수 | 설명 |
|------|------|------|
| `platform` | ❌ | CI/CD 플랫폼 (기본: github) |

---

## 공통 CI 파이프라인 구조

모든 프레임워크에서 동일한 파이프라인 단계를 따릅니다:

```
┌──────┐    ┌───────────┐    ┌──────┐    ┌───────┐    ┌────────┐
│ Lint │    │ Type Check│    │ Test │    │ Build │    │ Deploy │
└──┬───┘    └─────┬─────┘    └──┬───┘    └───┬───┘    └────────┘
   │              │              │            │
   └──────────────┴──────────────┘            │
              병렬 실행                    의존적 실행
```

### 1. 워크플로우 트리거

```yaml
# 공통 트리거 패턴
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
```

### 2. Concurrency 제어

중복 워크플로우를 자동 취소하여 리소스를 절약합니다:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### 3. Job 병렬화

Lint, Type Check, Test는 독립적이므로 병렬 실행합니다.
Build는 이들이 모두 성공한 후 실행합니다:

```yaml
jobs:
  lint:       # 병렬
  typecheck:  # 병렬
  test:       # 병렬
  build:
    needs: [lint, typecheck, test]  # 의존적
```

### 4. 캐싱 전략

의존성 설치 시간을 줄이기 위해 반드시 캐싱을 적용합니다.

### 5. 시크릿 관리 원칙

- 시크릿은 절대 워크플로우 파일에 하드코딩하지 않는다
- `${{ secrets.KEY_NAME }}` 형태로만 참조한다
- 환경별로 시크릿을 분리한다 (production, staging)
- Fork PR에서 시크릿 접근을 제한한다

### 6. 환경 분리

```yaml
# PR → Preview 환경
# main 브랜치 → Production 환경
# develop 브랜치 → Staging 환경
```

---

## 공통 안티패턴

### 1. 시크릿 하드코딩

```yaml
# Bad
- run: DATABASE_URL=postgres://user:pass@host/db npm run deploy

# Good
- run: npm run deploy
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

### 2. 캐시 미사용

매번 전체 의존성을 설치하면 CI 시간이 2-5배 증가합니다.

### 3. 병렬화 미활용

모든 단계를 순차 실행하면 CI 시간이 불필요하게 길어집니다.

### 4. 환경 분리 미흡

모든 브랜치에서 동일한 환경에 배포하면 위험합니다.

---

## 공통 보안 체크리스트

- [ ] 시크릿이 하드코딩되지 않았는가?
- [ ] Fork PR에서 시크릿 접근이 제한되었는가?
- [ ] 의존성 감사(audit)가 CI에 포함되었는가?
- [ ] 프로덕션 배포에 환경 보호(environment protection)가 설정되었는가?
- [ ] OIDC 인증을 사용하고 있는가? (클라우드 배포 시)

---

## Release 워크플로우 (공통)

태그 기반 릴리스 패턴:

```yaml
on:
  push:
    tags:
      - 'v*'

# 1. Changelog 자동 생성
# 2. GitHub Release 생성
# 3. 빌드 아티팩트 첨부
# 4. 프로덕션 배포
```

---

## 프레임워크별 오버라이드

각 에이전트별 스킬에서 다음 항목을 프레임워크에 맞게 구체화합니다:

| 항목 | FastAPI | Flutter | Next.js |
|------|---------|---------|---------|
| 패키지 매니저 셋업 | astral-sh/setup-uv | subosito/flutter-action | pnpm/action-setup + setup-node |
| Lint | ruff check + ruff format | flutter analyze + dart format | next lint |
| Type Check | mypy | (dart analyzer 포함) | tsc --noEmit |
| Test | pytest --cov | flutter test --coverage | vitest run --coverage |
| Build | docker build | flutter build (apk/ipa/web) | next build |
| Deploy 대상 | Docker Registry, AWS/GCP | Play Store, App Store, Firebase Hosting | Vercel, Docker |
| 코드 생성 | - | build_runner build | - |
| E2E in CI | docker-compose e2e | patrol test --ci | playwright test |

## References

- `_references/TEST-PATTERN.md`
- `_references/ARCHITECTURE-PATTERN.md`
