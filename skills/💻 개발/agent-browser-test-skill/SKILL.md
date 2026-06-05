---
name: agent-browser-test
description: "Vercel agent-browser 기반 E2E 테스트 — 접근성 트리 Refs 시스템 활용"
triggers:
  - "agent-browser"
  - "e2e 테스트"
  - "브라우저 테스트"
  - "자동화 테스트"
  - "UI 테스트"
---

# Agent Browser Test Skill

Vercel Labs의 agent-browser CLI를 활용한 AI 친화적 E2E 테스트 자동화 스킬입니다.

## 개요

agent-browser는 AI 에이전트를 위해 설계된 헤드리스 브라우저 자동화 CLI입니다.
**Refs 시스템**을 통해 결정론적 요소 선택이 가능하며, 접근성 트리 기반으로 LLM 워크플로우에 최적화되어 있습니다.

### Playwright MCP 대비 장점

| 항목 | agent-browser | Playwright MCP |
|------|--------------|----------------|
| **요소 선택** | Refs 시스템 (결정론적) | CSS/XPath (불안정) |
| **AI 최적화** | 접근성 트리 기반 | DOM 기반 |
| **세션 관리** | 내장 (`--session`) | 별도 구현 필요 |
| **성능** | Rust CLI (빠름) | IPC 오버헤드 |
| **JSON 출력** | `--json` 플래그 | 기본 제공 |

---

## 설치

```bash
# agent-browser CLI 설치
npm install -g agent-browser

# Chromium 브라우저 설치
agent-browser install

# 설치 확인
agent-browser --version
```

---

## 핵심 명령어

### 네비게이션

```bash
# 페이지 열기
agent-browser open http://localhost:3000

# 히스토리 이동
agent-browser back
agent-browser forward

# 새로고침
agent-browser reload
```

### 스냅샷 (핵심 기능)

```bash
# 전체 접근성 트리
agent-browser snapshot

# 상호작용 요소만 (AI 권장)
agent-browser snapshot -i

# JSON 형식 출력
agent-browser snapshot -i --json

# 압축된 트리
agent-browser snapshot --compact
```

**스냅샷 출력 예시:**
```
- button "로그인" [ref=e1]
- textbox "이메일" [ref=e2]
- textbox "비밀번호" [ref=e3]
- button "제출" [ref=e4]
- link "비밀번호 찾기" [ref=e5]
```

### 상호작용 (Refs 사용)

```bash
# 클릭
agent-browser click @e1

# 텍스트 입력
agent-browser fill @e2 "user@example.com"

# 입력 필드 초기화
agent-browser clear @e2

# 호버
agent-browser hover @e3

# 스크롤
agent-browser scroll down 500
agent-browser scroll up 300
```

### 정보 조회

```bash
# 텍스트 추출
agent-browser get text @e1

# 입력 값 조회
agent-browser get value @e2

# 속성 조회
agent-browser get attribute @e1 href

# 가시성 확인
agent-browser is visible @e3
```

### 대기

```bash
# 요소 대기
agent-browser wait @e1

# 요소 사라질 때까지 대기
agent-browser wait @e1 hidden

# 네트워크 유휴 대기
agent-browser wait network-idle

# 지정 시간 대기
agent-browser wait 2000
```

### 캡처

```bash
# 스크린샷
agent-browser screenshot test-result.png

# 전체 페이지 스크린샷
agent-browser screenshot --full full-page.png

# PDF 생성
agent-browser pdf report.pdf
```

### 세션 관리

```bash
# 세션 생성 및 사용
agent-browser --session login open http://localhost:3000/login
agent-browser --session login fill @email "test@test.com"
agent-browser --session login fill @password "password123"
agent-browser --session login click @submit

# 다른 세션
agent-browser --session admin open http://localhost:3000/admin
```

---

## 테스트 패턴

### 1. 기본 테스트 워크플로우

```bash
#!/bin/bash
# test-login.sh

# 1. 페이지 열기
agent-browser open http://localhost:3000/login

# 2. 스냅샷으로 요소 맵 획득
agent-browser snapshot -i

# 3. 로그인 수행
agent-browser fill @e2 "test@example.com"
agent-browser fill @e3 "password123"
agent-browser click @e4

# 4. 대기
agent-browser wait network-idle

# 5. 결과 확인
agent-browser snapshot -i
agent-browser screenshot test-results/login-success.png
```

### 2. 로그인 테스트

```bash
#!/bin/bash
# tests/e2e/auth/login.sh

SESSION="auth-test"

# 로그인 페이지 접근
agent-browser --session $SESSION open http://localhost:3000/login
agent-browser --session $SESSION snapshot -i

# 유효한 로그인
agent-browser --session $SESSION fill @email "user@test.com"
agent-browser --session $SESSION fill @password "validPassword123"
agent-browser --session $SESSION click @submit-btn
agent-browser --session $SESSION wait network-idle

# 대시보드 리다이렉트 확인
agent-browser --session $SESSION snapshot -i
agent-browser --session $SESSION screenshot test-results/login-success.png

# 검증: URL 확인
CURRENT_URL=$(agent-browser --session $SESSION get url)
if [[ $CURRENT_URL == *"/dashboard"* ]]; then
    echo "✅ Login test passed"
else
    echo "❌ Login test failed"
    exit 1
fi
```

### 3. 폼 검증 테스트

```bash
#!/bin/bash
# tests/e2e/forms/validation.sh

agent-browser open http://localhost:3000/register

# 빈 폼 제출 → 에러 메시지 확인
agent-browser click @submit-btn
agent-browser snapshot -i  # 에러 메시지 포함된 스냅샷

# 잘못된 이메일 형식
agent-browser fill @email "invalid-email"
agent-browser click @submit-btn
ERROR_MSG=$(agent-browser get text @email-error)
echo "Email error: $ERROR_MSG"

# 비밀번호 불일치
agent-browser clear @email
agent-browser fill @email "valid@email.com"
agent-browser fill @password "password123"
agent-browser fill @confirm-password "different456"
agent-browser click @submit-btn
ERROR_MSG=$(agent-browser get text @password-error)
echo "Password error: $ERROR_MSG"

agent-browser screenshot test-results/form-validation.png
```

### 4. 접근성 테스트

```bash
#!/bin/bash
# tests/e2e/a11y/accessibility.sh

agent-browser open http://localhost:3000
agent-browser snapshot --json > a11y-tree.json

# AI 분석용 데이터 추출
# 스냅샷에서 다음을 확인:
# - 모든 버튼에 접근 가능한 이름 (aria-label 또는 텍스트)
# - 폼 요소에 레이블 연결 여부
# - 이미지에 alt 텍스트 존재 여부
# - 헤딩 구조 적절성

echo "Accessibility tree saved to a11y-tree.json"
echo "Review with AI for accessibility issues"
```

### 5. Visual Regression 테스트

```bash
#!/bin/bash
# tests/e2e/visual/regression.sh

BASELINE_DIR="test-results/baseline"
CURRENT_DIR="test-results/current"

# 기준 이미지가 없으면 생성
if [ ! -d "$BASELINE_DIR" ]; then
    mkdir -p $BASELINE_DIR
    agent-browser open http://localhost:3000
    agent-browser screenshot $BASELINE_DIR/home.png

    agent-browser open http://localhost:3000/about
    agent-browser screenshot $BASELINE_DIR/about.png

    echo "Baseline images created"
    exit 0
fi

# 현재 상태 캡처
mkdir -p $CURRENT_DIR
agent-browser open http://localhost:3000
agent-browser screenshot $CURRENT_DIR/home.png

agent-browser open http://localhost:3000/about
agent-browser screenshot $CURRENT_DIR/about.png

# 이미지 비교 (별도 도구 사용)
# pixelmatch, resemblejs 등으로 diff 생성
echo "Compare images in $BASELINE_DIR vs $CURRENT_DIR"
```

### 6. CRUD 작업 테스트

```bash
#!/bin/bash
# tests/e2e/crud/create-item.sh

SESSION="crud-test"

# 로그인
agent-browser --session $SESSION open http://localhost:3000/login
agent-browser --session $SESSION fill @email "admin@test.com"
agent-browser --session $SESSION fill @password "admin123"
agent-browser --session $SESSION click @submit
agent-browser --session $SESSION wait network-idle

# 아이템 생성 페이지로 이동
agent-browser --session $SESSION click @nav-items
agent-browser --session $SESSION click @create-btn
agent-browser --session $SESSION snapshot -i

# 폼 작성
agent-browser --session $SESSION fill @name "Test Item"
agent-browser --session $SESSION fill @description "This is a test item"
agent-browser --session $SESSION fill @price "99.99"
agent-browser --session $SESSION click @save-btn
agent-browser --session $SESSION wait network-idle

# 생성 확인
agent-browser --session $SESSION snapshot -i
SUCCESS_MSG=$(agent-browser --session $SESSION get text @success-toast)
echo "Result: $SUCCESS_MSG"

agent-browser --session $SESSION screenshot test-results/create-item.png
```

---

## AI 에이전트 통합 패턴

### 스냅샷 기반 테스트 시나리오 생성

```typescript
// AI Agent가 스냅샷을 분석하여 테스트 생성
async function generateTestFromSnapshot(url: string) {
  // 1. 스냅샷 획득
  const snapshot = await exec(`agent-browser open ${url} && agent-browser snapshot -i --json`);
  const elements = JSON.parse(snapshot);

  // 2. AI가 요소 분석
  const testScenarios = await analyzeWithAI(elements);

  // 3. 테스트 스크립트 생성
  return generateScript(testScenarios);
}
```

### 동적 테스트 실행

```typescript
// AI Agent가 실시간으로 테스트 수행
async function runDynamicTest(session: string, scenario: TestScenario) {
  for (const step of scenario.steps) {
    switch (step.action) {
      case 'click':
        await exec(`agent-browser --session ${session} click @${step.ref}`);
        break;
      case 'fill':
        await exec(`agent-browser --session ${session} fill @${step.ref} "${step.value}"`);
        break;
      case 'verify':
        const result = await exec(`agent-browser --session ${session} get text @${step.ref}`);
        assert(result.includes(step.expected));
        break;
    }

    // 각 단계 후 스냅샷으로 상태 확인
    await exec(`agent-browser --session ${session} snapshot -i`);
  }
}
```

---

## CI/CD 통합

### GitHub Actions 예시

```yaml
# .github/workflows/e2e.yml
name: E2E Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  e2e:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Install agent-browser
        run: |
          npm install -g agent-browser
          agent-browser install

      - name: Start dev server
        run: npm run dev &
        env:
          PORT: 3000

      - name: Wait for server
        run: npx wait-on http://localhost:3000

      - name: Run E2E tests
        run: |
          chmod +x tests/e2e/*.sh
          for test in tests/e2e/*.sh; do
            echo "Running $test"
            bash "$test"
          done

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: e2e-results
          path: test-results/
```

### 로컬 테스트 스크립트

```json
// package.json
{
  "scripts": {
    "test:e2e": "bash tests/e2e/run-all.sh",
    "test:e2e:login": "bash tests/e2e/auth/login.sh",
    "test:e2e:a11y": "bash tests/e2e/a11y/accessibility.sh",
    "test:e2e:visual": "bash tests/e2e/visual/regression.sh"
  }
}
```

---

## 디렉토리 구조

```
project/
├── tests/
│   └── e2e/
│       ├── run-all.sh           # 전체 테스트 실행
│       ├── auth/
│       │   ├── login.sh
│       │   ├── logout.sh
│       │   └── register.sh
│       ├── forms/
│       │   ├── validation.sh
│       │   └── submission.sh
│       ├── crud/
│       │   ├── create-item.sh
│       │   ├── update-item.sh
│       │   └── delete-item.sh
│       ├── a11y/
│       │   └── accessibility.sh
│       └── visual/
│           └── regression.sh
├── test-results/
│   ├── baseline/                # 기준 스크린샷
│   ├── current/                 # 현재 스크린샷
│   └── *.png                    # 테스트 결과 캡처
└── .github/
    └── workflows/
        └── e2e.yml              # CI/CD 설정
```

---

## 트러블슈팅

### 일반적인 문제

| 문제 | 원인 | 해결 |
|------|------|------|
| `Command not found` | agent-browser 미설치 | `npm i -g agent-browser` |
| `Browser not found` | Chromium 미설치 | `agent-browser install` |
| `Ref not found` | 잘못된 Ref 또는 페이지 변경 | `snapshot -i`로 최신 Refs 확인 |
| `Timeout` | 페이지 로딩 지연 | `wait network-idle` 추가 |
| `Session error` | 세션 만료 | 새 세션으로 재시작 |

### 디버깅 팁

```bash
# 상세 로깅
agent-browser --verbose open http://localhost:3000

# JSON 출력으로 파싱
agent-browser snapshot -i --json | jq '.elements'

# 세션 목록 확인
agent-browser sessions

# 세션 종료
agent-browser --session test close
```

---

## Best Practices

### 1. 세션 관리
- 관련 테스트는 같은 세션에서 실행
- 독립적인 테스트는 별도 세션 사용
- 테스트 완료 후 세션 정리

### 2. 스냅샷 활용
- 각 주요 액션 후 스냅샷으로 상태 확인
- `--json` 플래그로 프로그래밍 가능한 출력 획득
- `-i` 플래그로 노이즈 제거 (상호작용 요소만)

### 3. 대기 전략
- 액션 후 `wait network-idle` 사용
- 특정 요소는 `wait @ref` 사용
- 하드코딩된 대기 시간 지양

### 4. 에러 처리
- 각 단계에서 성공 여부 확인
- 스크린샷으로 실패 상태 캡처
- 명확한 에러 메시지 출력

### 5. 유지보수
- Refs 대신 시맨틱 로케이터 사용 고려
- 테스트를 작은 단위로 분리
- 공통 작업 (로그인 등)은 함수화
