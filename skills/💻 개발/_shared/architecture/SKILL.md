---
name: architecture-shared
description: |
  Clean Architecture 기반 프로젝트 구조 설계 공통 방법론.
  FastAPI, Flutter, Next.js 에이전트가 공유하는 아키텍처 원칙.
metadata:
  category: "💻 개발"
  type: shared
  version: "1.0.0"
  consumers:
    - fastapi-agent-skills/2-architecture
    - flutter-agent-skills/2-architecture
    - nextjs-agent-skills/2-architecture
---
# Architecture Skill (Shared)

Clean Architecture 기반 프로젝트 구조를 설계하는 공통 방법론입니다.

## Triggers

- "아키텍처 설계", "구조 설계", "clean architecture", "폴더 구조"

---

## Input (공통)

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |
| `features` | ❌ | 초기 생성할 Feature 목록 |

---

## 핵심 원칙

### 1. 의존성 방향 규칙

모든 프레임워크에서 동일하게 적용:

```
외부 (UI / API) → 비즈니스 로직 → 도메인 ← 인프라스트럭처
```

- **도메인 레이어**는 외부 의존성 없음 (순수 언어 코드)
- **인프라스트럭처 레이어**는 도메인 인터페이스를 구현
- **비즈니스 로직 레이어**는 도메인에만 의존
- **외부 레이어** (UI/API)는 비즈니스 로직에 의존

### 2. 레이어 구조 (공통)

```
┌─────────────────────────────────────┐
│       Presentation / API Layer      │ ← 외부 입출력
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│        Application Layer            │ ← 비즈니스 로직
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│          Domain Layer               │ ← 핵심 엔티티 + 인터페이스
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│       Infrastructure Layer          │ ← 외부 시스템 구현
└─────────────────────────────────────┘
```

### 3. 레이어별 책임 (공통)

| 레이어 | 책임 | 포함 요소 |
|--------|------|-----------|
| **Presentation / API** | 외부 입출력 처리, 요청 검증 | 라우터, 컨트롤러, 뷰, 위젯 |
| **Application** | 비즈니스 로직, 트랜잭션 | 서비스, 유즈케이스 |
| **Domain** | 핵심 엔티티, 인터페이스 정의 | 엔티티, 리포지토리 인터페이스 |
| **Infrastructure** | 외부 시스템 통신, 구현 | DB 모델, 리포지토리 구현, API 클라이언트 |

### 4. Feature 기반 모듈화

Feature 단위로 코드를 그룹화하여 응집도를 높입니다:

```
features/{feature}/
├── presentation/     # UI 또는 API 엔드포인트
├── application/      # 비즈니스 로직
├── domain/           # 엔티티, 인터페이스
├── infrastructure/   # 외부 시스템 구현
└── __tests__/        # 테스트
```

### 5. Entity ↔ Model 분리

- **Entity**: 도메인 객체 (비즈니스 규칙 포함)
- **Model**: 인프라스트럭처 객체 (DB 스키마, API 응답 형태)
- 변환은 항상 인프라스트럭처 레이어에서 수행

---

## 안티패턴 (프레임워크 공통)

### 1. 레이어 건너뛰기

외부 레이어에서 인프라스트럭처를 직접 호출하지 않는다.
항상 Application(Service/UseCase) 레이어를 경유한다.

### 2. 순환 참조

Feature 간 직접 import를 피한다.
이벤트 기반 통신 또는 Public API(barrel export)를 사용한다.

### 3. God Service

하나의 서비스에 모든 로직을 넣지 않는다.
단일 책임 원칙에 따라 기능별로 분리한다.

### 4. Domain에 외부 의존성 추가

Domain 레이어는 프레임워크, DB, HTTP 등 외부 라이브러리에 의존하지 않는다.

---

## 프레임워크별 오버라이드

각 에이전트별 스킬에서 다음 항목을 프레임워크에 맞게 구체화합니다:

| 항목 | FastAPI | Flutter | Next.js |
|------|---------|---------|---------|
| Presentation | Router + Dependencies | View + Notifier | Page (RSC) + Hook |
| Application | Service | UseCase | Service + Server Action |
| Domain | Entity (Pydantic) + ABC | Entity (Freezed) + Repository | Schema (Zod) + Types |
| Infrastructure | SQLAlchemy Model + Impl | DataSource + Model | Drizzle Repository |
| DI | FastAPI Depends | Injectable + GetIt | 직접 import |
| 상태 관리 | - | Riverpod | TanStack Query + Zustand |

## References

- `_references/ARCHITECTURE-PATTERN.md`
