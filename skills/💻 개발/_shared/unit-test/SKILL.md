---
name: unit-test-shared
description: |
  유닛 테스트 공통 방법론 및 베스트 프랙티스.
  FastAPI, Flutter, Next.js 에이전트가 공유하는 단위 테스트 원칙.
metadata:
  category: "💻 개발"
  type: shared
  version: "1.0.0"
  consumers:
    - fastapi-agent-skills/28-unit-test
    - flutter-agent-skills/14-unit-test
    - nextjs-agent-skills/20-unit-test
---
# Unit Test Skill (Shared)

프레임워크에 관계없이 적용되는 유닛 테스트 공통 방법론입니다.

## Triggers

- "유닛 테스트", "unit test", "단위 테스트"

---

## Input (공통)

| 항목 | 필수 | 설명 |
|------|------|------|
| `target` | ✅ | 테스트 대상 |
| `coverage` | ❌ | 커버리지 목표 (기본 80%) |

---

## 테스트 원칙

### 1. AAA 패턴

모든 테스트는 Arrange-Act-Assert 패턴을 따릅니다:

```
// Arrange - 테스트 데이터 준비
// Act - 테스트 대상 실행
// Assert - 결과 검증
```

### 2. 테스트 작성 규칙

| 규칙 | 설명 |
|------|------|
| **하나의 동작** | 테스트당 하나의 동작만 검증 |
| **설명적 이름** | 테스트 이름이 기대 동작을 설명 |
| **독립적** | 각 테스트는 다른 테스트에 의존하지 않음 |
| **I/O 없음** | 유닛 테스트는 DB/네트워크 접근 금지 |
| **빠른 실행** | 개별 테스트 100ms 미만 |
| **결정적** | 동일 입력에 항상 동일 결과 |

### 3. 테스트 디렉토리 구조 (공통)

아키텍처 레이어에 맞춰 테스트 파일을 구성합니다:

```
tests/ (또는 test/)
├── unit/
│   ├── domain/          # 엔티티, 값 객체 테스트
│   ├── application/     # 서비스, 유즈케이스 테스트
│   └── infrastructure/  # 리포지토리 구현 테스트
├── helpers/             # 테스트 헬퍼, 팩토리
└── mocks/               # Mock 정의
```

### 4. Mock 사용 원칙

- **외부 의존성만 Mock**: DB, API, 파일시스템 등 시스템 경계만 모킹
- **내부 코드는 실제 사용**: 순수 함수, 유틸리티는 실제 코드 사용
- **Mock 과다 사용 금지**: Mock이 3개 이상이면 설계 재검토
- **행동 검증 우선**: 내부 구현이 아닌 동작(결과)을 테스트

### 5. 테스트 데이터 관리

- **팩토리 패턴** 사용하여 테스트 데이터 생성 (하드코딩 방지)
- **최소한의 데이터**: 테스트에 필요한 최소한의 속성만 지정
- **민감 정보 금지**: 실제 API 키, 비밀번호 등 절대 사용 금지
- **테스트 간 격리**: 각 테스트는 독립된 데이터 사용

### 6. 커버리지 정책

| 레이어 | 목표 커버리지 | 우선순위 |
|--------|-------------|---------|
| Domain (Entity) | 90%+ | 최우선 |
| Application (Service/UseCase) | 85%+ | 높음 |
| Infrastructure (Repository) | 70%+ | 보통 |
| Presentation (Controller/View) | 60%+ | 낮음 |

### 7. 실행 명령 패턴

모든 프레임워크에서 공통적으로 지원해야 하는 실행 방식:

```bash
# 전체 유닛 테스트 실행
{runner} tests/unit/

# 커버리지 포함 실행
{runner} --coverage

# 특정 파일 실행
{runner} tests/unit/application/test_services.{ext}

# Watch 모드 (개발 중)
{runner} --watch
```

---

## 안티패턴

### 1. 구현 세부사항 테스트

내부 상태나 메서드 호출 순서를 검증하지 않는다. 공개 API의 동작(결과)을 테스트한다.

### 2. 테스트 간 상태 공유

전역 변수나 싱글턴에 의존하지 않는다. 각 테스트는 독립적으로 셋업/정리한다.

### 3. 비동기 처리 미흡

비동기 코드는 반드시 올바르게 대기(await/waitFor)한다. 타이밍 의존 테스트를 피한다.

### 4. 하드코딩된 테스트 데이터

매직 넘버나 하드코딩된 문자열 대신 팩토리/빌더를 사용한다.

---

## 프레임워크별 오버라이드

각 에이전트별 스킬에서 다음 항목을 프레임워크에 맞게 구체화합니다:

| 항목 | FastAPI | Flutter | Next.js |
|------|---------|---------|---------|
| 테스트 러너 | pytest | flutter test | vitest |
| Mock 라이브러리 | unittest.mock, AsyncMock | mocktail | vi.mock, vi.fn |
| 팩토리 | factory-boy | 직접 구현 | 직접 구현 |
| 비동기 | pytest-asyncio | - | waitFor (testing-library) |
| 설정 파일 | pyproject.toml [tool.pytest] | - | vitest.config.ts |
| 환경 | - | - | jsdom |

## References

- `_references/TEST-PATTERN.md`
