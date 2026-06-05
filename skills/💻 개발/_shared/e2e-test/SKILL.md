---
name: e2e-test-shared
description: |
  End-to-End 테스트 공통 방법론 및 전략.
  FastAPI, Flutter, Next.js 에이전트가 공유하는 E2E 테스트 원칙.
metadata:
  category: "💻 개발"
  type: shared
  version: "1.0.0"
  consumers:
    - fastapi-agent-skills/30-e2e-test
    - flutter-agent-skills/17-e2e-test
    - nextjs-agent-skills/22-e2e-test
---
# E2E Test Skill (Shared)

프레임워크에 관계없이 적용되는 E2E 테스트 공통 방법론입니다.

## Triggers

- "e2e 테스트", "end to end", "시나리오 테스트"

---

## Input (공통)

| 항목 | 필수 | 설명 |
|------|------|------|
| `flow` | ✅ | 테스트할 사용자 흐름 |

---

## 테스트 피라미드

E2E 테스트는 피라미드 최상위에 위치하며, 전체 테스트의 5-10%만 차지합니다:

```
        ┌───────────┐
        │   E2E     │  5-10% of tests
        │  (10%)    │  ← Critical flows only
        ├───────────┤
        │Integration│  15-25% of tests
        │  (20%)    │  ← Component interaction
        ├───────────┤
        │   Unit    │  60-70% of tests
        │  (70%)    │  ← Fast, isolated tests
        └───────────┘
```

## E2E 테스트 선택 기준

E2E 테스트에 포함해야 할 시나리오:

- **인증 흐름**: 회원가입, 로그인, 로그아웃, 비밀번호 재설정
- **핵심 비즈니스 트랜잭션**: 결제, 주문, 핵심 CRUD 플로우
- **크리티컬 패스**: 사용자가 반드시 거치는 주요 경로

E2E 테스트에 포함하지 말아야 할 것:

- 모든 API 엔드포인트 (통합 테스트 영역)
- 엣지 케이스 (유닛 테스트 영역)
- UI 스타일/레이아웃 (비주얼 테스트 영역)

## 공통 원칙

### 1. Page Object Model (POM)

모든 프레임워크에서 Page Object 패턴을 사용하여 테스트 코드를 구조화합니다:

```
테스트 파일  →  Page Object  →  실제 UI/API
(시나리오)     (추상화 계층)     (구현 세부사항)
```

- Page Object는 UI 요소 찾기와 상호작용을 캡슐화
- 테스트 파일은 비즈니스 흐름에만 집중
- UI 변경 시 Page Object만 수정

### 2. 테스트 독립성

- 각 E2E 테스트는 독립적으로 실행 가능해야 함
- 이전 테스트의 결과에 의존하지 않음
- 필요한 데이터는 테스트 시작 시 직접 생성

### 3. 안정적인 셀렉터

```
Bad:  CSS 클래스, 구조 의존 셀렉터 (.btn-primary.mt-4)
Bad:  DOM 경로 의존 (div > div > div > button)
Good: 역할 기반 (role="button", name="저장")
Good: 테스트 ID (data-testid="submit-button")
Good: 접근성 레이블 (aria-label, getByLabel)
```

### 4. 조건 기반 대기

```
Bad:  고정 시간 대기 (sleep 3초, waitForTimeout)
Good: 조건 충족까지 대기 (waitUntilVisible, expect.toBeVisible)
```

### 5. 실패 시 디버깅 정보

- 테스트 실패 시 스크린샷 자동 캡처
- 네트워크 요청 로그 보존
- 콘솔 에러 기록

### 6. 인증 상태 재사용

로그인이 필요한 테스트는 인증 상태를 사전에 설정하여 재사용합니다.
매 테스트마다 로그인을 반복하지 않습니다.

### 7. 환경 격리

```
Bad:  하드코딩된 URL (http://localhost:3000)
Good: 환경 변수 또는 baseURL 설정 사용
```

---

## E2E 테스트 시나리오 템플릿

### 인증 플로우

```
1. 회원가입 → 이메일/비밀번호 입력 → 가입 완료 확인
2. 로그인 → 자격 증명 입력 → 대시보드 이동 확인
3. 로그아웃 → 로그아웃 클릭 → 로그인 페이지 리다이렉트
4. 잘못된 자격 증명 → 에러 메시지 표시
```

### CRUD 플로우

```
1. Create → 폼 입력 → 저장 → 목록에서 확인
2. Read → 목록에서 항목 클릭 → 상세 내용 확인
3. Update → 수정 클릭 → 내용 변경 → 저장 → 변경 확인
4. Delete → 삭제 클릭 → 확인 → 목록에서 제거 확인
```

## CI/CD 통합

- E2E 테스트는 CI에서 main/develop 브랜치 푸시 시 실행
- 실패 시 아티팩트(스크린샷, 리포트) 업로드
- CI에서는 재시도(retry) 설정으로 flaky 테스트 대응

---

## 프레임워크별 오버라이드

각 에이전트별 스킬에서 다음 항목을 프레임워크에 맞게 구체화합니다:

| 항목 | FastAPI | Flutter | Next.js |
|------|---------|---------|---------|
| E2E 도구 | API: httpx + Testcontainers / UI: Playwright (Python) | Patrol | Playwright (TS) |
| 인증 Setup | conftest.py fixture | patrolTest helper | auth.setup.ts |
| POM 구현 | Python class | - | TypeScript class |
| CI 환경 | Docker Compose | flutter test integration_test | Playwright CI |
| 브라우저 테스트 | Playwright (Python) | 네이티브 디바이스 | Playwright (TS) |
| 셀렉터 | CSS, data-testid | Key, 텍스트, 타입 | getByRole, getByTestId |

## References

- `_references/TEST-PATTERN.md`
