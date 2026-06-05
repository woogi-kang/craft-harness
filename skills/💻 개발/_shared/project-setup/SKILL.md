---
name: project-setup-shared
description: |
  프레임워크 공통 프로젝트 초기 설정 방법론.
  FastAPI, Flutter, Next.js 에이전트가 공유하는 프로젝트 셋업 공통 프로세스.
metadata:
  category: "💻 개발"
  type: shared
  version: "1.0.0"
  consumers:
    - fastapi-agent-skills/1-project-setup
    - flutter-agent-skills/1-project-setup
    - nextjs-agent-skills/1-project-setup
---
# Project Setup Skill (Shared)

프레임워크에 관계없이 적용되는 프로젝트 초기 설정 공통 방법론입니다.

## Triggers

- "프로젝트 생성", "프로젝트 설정", "프로젝트 init", "프로젝트 create"

---

## Input (공통)

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectName` | ✅ | 프로젝트 이름 |

---

## 공통 프로세스

### 1. 프로젝트 초기화

모든 프레임워크에서 동일하게 적용되는 단계:

1. **프로젝트 디렉토리 생성** - 프레임워크 CLI로 스캐폴딩
2. **의존성 설치** - 패키지 매니저로 설치
3. **환경 변수 설정** - `.env.example` 생성 및 복사
4. **개발 서버 실행** - 정상 동작 확인

### 2. 필수 설정 파일

모든 프로젝트에 반드시 포함해야 하는 파일:

| 파일 | 용도 |
|------|------|
| `.env.example` | 환경 변수 템플릿 (값 비워둠) |
| `.gitignore` | Git 추적 제외 파일 |
| 패키지 매니저 설정 | `pyproject.toml` / `pubspec.yaml` / `package.json` |

### 3. .gitignore 공통 항목

```gitignore
# 환경 변수
.env
.env.local
.env.*.local

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# 로그
*.log
logs/
```

### 4. 디렉토리 구조 원칙

모든 프레임워크에 공통 적용되는 구조 원칙:

```
{project}/
├── 소스 코드/          # app/ | lib/ | src/
│   ├── core/           # 핵심 설정, 유틸리티
│   ├── features/       # Feature 기반 모듈 (권장)
│   └── ...
├── 테스트/             # tests/ | test/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── 환경 설정 파일       # .env.example, 설정 파일
└── 문서                # README.md
```

### 5. 환경 변수 관리 원칙

- `.env` 파일은 절대 Git에 커밋하지 않는다
- `.env.example`에는 키만 남기고 값은 비운다
- 프로덕션 시크릿은 CI/CD 환경 변수 또는 시크릿 매니저 사용
- 타입 안전한 환경 변수 검증 적용 (각 프레임워크별 도구 사용)

### 6. 의존성 관리 원칙

- Lock 파일을 반드시 커밋한다 (`uv.lock` / `pubspec.lock` / `package-lock.json`)
- 버전 범위는 호환 가능한 최소 범위로 지정한다
- 개발 의존성과 프로덕션 의존성을 분리한다
- 보안 취약점이 있는 패키지는 즉시 업데이트한다

### 7. 실행 확인 체크리스트

프로젝트 설정 완료 후 반드시 확인:

```
✓ 개발 서버 시작 및 접속 확인
✓ 린트/포맷 실행 에러 없음
✓ 테스트 프레임워크 동작 확인
✓ 빌드 성공
✓ .env.example 존재 및 필수 키 포함
✓ .gitignore에 민감 파일 포함
```

---

## 프레임워크별 오버라이드

각 에이전트별 스킬에서 다음 항목을 프레임워크에 맞게 구체화합니다:

| 항목 | FastAPI | Flutter | Next.js |
|------|---------|---------|---------|
| CLI 명령 | `mkdir` + `uv init` | `flutter create` | `create-next-app` |
| 패키지 매니저 | uv | pub | npm/pnpm |
| 의존성 파일 | `pyproject.toml` | `pubspec.yaml` | `package.json` |
| 소스 디렉토리 | `app/` | `lib/` | `src/` |
| 테스트 디렉토리 | `tests/` | `test/` | `tests/` |
| 설정 파일 | ruff, mypy, pytest | analysis_options | next.config, vitest.config |
| 환경 변수 검증 | pydantic-settings | envied | @t3-oss/env-nextjs |

## References

- `_references/ARCHITECTURE-PATTERN.md`
