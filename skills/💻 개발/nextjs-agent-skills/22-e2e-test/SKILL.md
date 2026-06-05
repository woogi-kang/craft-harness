---
name: e2e-test
description: |
  Playwright를 사용하여 E2E 테스트를 작성합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# E2E Test Skill

Extends: `../../_shared/e2e-test/SKILL.md` (공통 E2E 테스트 원칙 참조)

Playwright를 사용하여 E2E 테스트를 작성합니다.

## Triggers

- "e2e 테스트", "e2e test", "playwright", "end-to-end"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `flow` | ✅ | 테스트할 사용자 흐름 |
| `browsers` | ❌ | 테스트 브라우저 (chromium, firefox, webkit) |

---

## 설치

```bash
npm install -D @playwright/test
npx playwright install
```

---

## Playwright 설정

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['html', { open: 'never' }]],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'mobile',
      use: { ...devices['iPhone 13'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
```

---

## 인증 Setup

```typescript
// e2e/auth.setup.ts
import { test as setup, expect } from '@playwright/test';
import path from 'path';

const authFile = path.join(__dirname, '../.auth/user.json');

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('이메일').fill('test@example.com');
  await page.getByLabel('비밀번호').fill('password123');
  await page.getByRole('button', { name: '로그인' }).click();

  await expect(page).toHaveURL('/dashboard');

  await page.context().storageState({ path: authFile });
});
```

```typescript
// playwright.config.ts (projects 수정)
projects: [
  { name: 'setup', testMatch: /.*\.setup\.ts/ },
  {
    name: 'chromium',
    use: {
      ...devices['Desktop Chrome'],
      storageState: '.auth/user.json',
    },
    dependencies: ['setup'],
  },
],
```

---

## Page Object Model

```typescript
// e2e/pages/login.page.ts
import { Page, Locator, expect } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel('이메일');
    this.passwordInput = page.getByLabel('비밀번호');
    this.submitButton = page.getByRole('button', { name: '로그인' });
    this.errorMessage = page.getByRole('alert');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async expectError(message: string) {
    await expect(this.errorMessage).toContainText(message);
  }
}
```

```typescript
// e2e/pages/dashboard.page.ts
import { Page, Locator, expect } from '@playwright/test';

export class DashboardPage {
  readonly page: Page;
  readonly heading: Locator;
  readonly createButton: Locator;
  readonly postCards: Locator;
  readonly searchInput: Locator;
  readonly statusFilter: Locator;

  constructor(page: Page) {
    this.page = page;
    this.heading = page.getByRole('heading', { name: '대시보드' });
    this.createButton = page.getByRole('link', { name: '새 글 작성' });
    this.postCards = page.getByTestId('post-card');
    this.searchInput = page.getByPlaceholder('검색');
    this.statusFilter = page.getByRole('combobox', { name: '상태' });
  }

  async goto() {
    await this.page.goto('/dashboard');
  }

  async expectLoaded() {
    await expect(this.heading).toBeVisible();
  }

  async search(query: string) {
    await this.searchInput.fill(query);
    await this.page.waitForLoadState('networkidle');
  }

  async filterByStatus(status: string) {
    await this.statusFilter.click();
    await this.page.getByRole('option', { name: status }).click();
  }

  async getPostCount() {
    return this.postCards.count();
  }
}
```

```typescript
// e2e/pages/post-form.page.ts
import { Page, Locator, expect } from '@playwright/test';

export class PostFormPage {
  readonly page: Page;
  readonly titleInput: Locator;
  readonly contentInput: Locator;
  readonly statusSelect: Locator;
  readonly submitButton: Locator;
  readonly successToast: Locator;

  constructor(page: Page) {
    this.page = page;
    this.titleInput = page.getByLabel('제목');
    this.contentInput = page.getByLabel('내용');
    this.statusSelect = page.getByRole('combobox', { name: '상태' });
    this.submitButton = page.getByRole('button', { name: '저장' });
    this.successToast = page.getByText('저장되었습니다');
  }

  async goto() {
    await this.page.goto('/posts/new');
  }

  async fillForm(data: { title: string; content: string; status?: string }) {
    await this.titleInput.fill(data.title);
    await this.contentInput.fill(data.content);
    if (data.status) {
      await this.statusSelect.click();
      await this.page.getByRole('option', { name: data.status }).click();
    }
  }

  async submit() {
    await this.submitButton.click();
  }

  async expectSuccess() {
    await expect(this.successToast).toBeVisible();
  }
}
```

---

## E2E 테스트

### 인증 플로우

```typescript
// e2e/auth.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/login.page';

test.describe('Authentication', () => {
  test('should login with valid credentials', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('test@example.com', 'password123');

    await expect(page).toHaveURL('/dashboard');
  });

  test('should show error with invalid credentials', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('wrong@example.com', 'wrongpassword');

    await loginPage.expectError('이메일 또는 비밀번호가 올바르지 않습니다');
  });

  test('should redirect to login when accessing protected route', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/login/);
  });

  test('should logout successfully', async ({ page }) => {
    await page.goto('/dashboard');
    await page.getByRole('button', { name: '로그아웃' }).click();

    await expect(page).toHaveURL('/login');
  });
});
```

### CRUD 플로우

```typescript
// e2e/posts.spec.ts
import { test, expect } from '@playwright/test';
import { DashboardPage } from './pages/dashboard.page';
import { PostFormPage } from './pages/post-form.page';

test.describe('Posts CRUD', () => {
  test('should create a new post', async ({ page }) => {
    const formPage = new PostFormPage(page);
    await formPage.goto();

    await formPage.fillForm({
      title: 'E2E Test Post',
      content: 'This is a test post created by Playwright',
      status: '발행',
    });
    await formPage.submit();
    await formPage.expectSuccess();

    await expect(page).toHaveURL(/\/posts\/[a-z0-9-]+/);
  });

  test('should display posts in dashboard', async ({ page }) => {
    const dashboard = new DashboardPage(page);
    await dashboard.goto();
    await dashboard.expectLoaded();

    const count = await dashboard.getPostCount();
    expect(count).toBeGreaterThan(0);
  });

  test('should filter posts by status', async ({ page }) => {
    const dashboard = new DashboardPage(page);
    await dashboard.goto();

    await dashboard.filterByStatus('발행');
    await page.waitForLoadState('networkidle');

    // All visible posts should be published
    const cards = page.getByTestId('post-card');
    const count = await cards.count();

    for (let i = 0; i < count; i++) {
      await expect(cards.nth(i).getByText('발행')).toBeVisible();
    }
  });

  test('should search posts', async ({ page }) => {
    const dashboard = new DashboardPage(page);
    await dashboard.goto();

    await dashboard.search('E2E Test');

    const cards = page.getByTestId('post-card');
    await expect(cards.first()).toContainText('E2E Test');
  });

  test('should edit a post', async ({ page }) => {
    await page.goto('/dashboard');
    await page.getByTestId('post-card').first().click();
    await page.getByRole('button', { name: '수정' }).click();

    await page.getByLabel('제목').fill('Updated Title');
    await page.getByRole('button', { name: '저장' }).click();

    await expect(page.getByText('수정되었습니다')).toBeVisible();
  });

  test('should delete a post', async ({ page }) => {
    await page.goto('/dashboard');
    const initialCount = await page.getByTestId('post-card').count();

    await page.getByTestId('post-card').first().click();
    await page.getByRole('button', { name: '삭제' }).click();
    await page.getByRole('button', { name: '확인' }).click();

    await expect(page.getByText('삭제되었습니다')).toBeVisible();
    await expect(page).toHaveURL('/dashboard');

    const newCount = await page.getByTestId('post-card').count();
    expect(newCount).toBe(initialCount - 1);
  });
});
```

### 네비게이션 플로우

```typescript
// e2e/navigation.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
  test('should navigate between pages', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/My App/);

    await page.getByRole('link', { name: '대시보드' }).click();
    await expect(page).toHaveURL('/dashboard');

    await page.getByRole('link', { name: '설정' }).click();
    await expect(page).toHaveURL('/settings');

    await page.goBack();
    await expect(page).toHaveURL('/dashboard');
  });

  test('should show 404 for unknown routes', async ({ page }) => {
    await page.goto('/unknown-page');
    await expect(page.getByText('404')).toBeVisible();
  });
});
```

---

## 실행 명령어

```bash
# 전체 E2E 테스트
npx playwright test

# UI 모드
npx playwright test --ui

# 특정 브라우저
npx playwright test --project=chromium

# Headed 모드
npx playwright test --headed

# 디버그 모드
npx playwright test --debug

# 특정 파일
npx playwright test e2e/auth.spec.ts

# 리포트 보기
npx playwright show-report
```

```json
// package.json
{
  "scripts": {
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:debug": "playwright test --debug"
  }
}
```

---

## 테스트 예제

이 스킬의 주요 섹션들이 E2E 테스트 예제입니다:

- **Page Object Model**: 페이지별 추상화 패턴
- **인증 Setup**: 인증 상태 저장 및 재사용
- **E2E 테스트**: 실제 사용자 시나리오 테스트

### Playwright 설정 검증 테스트

```typescript
// e2e/setup.spec.ts
import { test, expect } from '@playwright/test';

test.describe('E2E Test Setup', () => {
  test('Playwright is configured correctly', async ({ page }) => {
    // 페이지 로드 확인
    await page.goto('/');
    await expect(page).toHaveTitle(/.+/);
  });

  test('authentication state is available', async ({ page }) => {
    // 인증 상태가 올바르게 저장/복원되는지 확인
    await page.goto('/dashboard');
    // 인증된 상태에서 접근 가능해야 함
    await expect(page.locator('h1')).toBeVisible();
  });

  test('API mocking works in E2E', async ({ page }) => {
    // API 응답 모킹
    await page.route('/api/users', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify([{ id: 1, name: 'Test User' }]),
      });
    });

    await page.goto('/users');
    await expect(page.getByText('Test User')).toBeVisible();
  });

  test('screenshots are captured on failure', async ({ page }, testInfo) => {
    // 실패 시 스크린샷 캡처 설정 확인
    expect(testInfo.project.use.screenshot).toBeDefined();
  });
});
```

### Page Object 테스트

```typescript
// e2e/page-objects.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage, DashboardPage } from './pages';

test.describe('Page Objects', () => {
  test('LoginPage methods work correctly', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();

    // 페이지 객체 메서드 검증
    await expect(loginPage.emailInput).toBeVisible();
    await expect(loginPage.passwordInput).toBeVisible();
    await expect(loginPage.submitButton).toBeEnabled();
  });

  test('DashboardPage navigation works', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    await dashboardPage.goto();

    // 네비게이션 메서드 검증
    await dashboardPage.navigateToSettings();
    await expect(page).toHaveURL(/\/settings/);
  });
});
```

---

## 안티패턴

### 1. 하드코딩된 대기

```typescript
// ❌ Bad: 고정 시간 대기
await page.waitForTimeout(3000);
await expect(page.locator('text=Data')).toBeVisible();

// ✅ Good: 조건 기반 대기
await expect(page.locator('text=Data')).toBeVisible({ timeout: 10000 });
```

### 2. 취약한 셀렉터

```typescript
// ❌ Bad: 구현 의존 셀렉터
await page.locator('.btn-primary.mt-4.px-6').click();
await page.locator('div > div > div > button').click();

// ✅ Good: 안정적인 셀렉터
await page.getByRole('button', { name: '저장' }).click();
await page.getByTestId('submit-button').click();
```

### 3. 테스트 간 의존성

```typescript
// ❌ Bad: 이전 테스트에 의존
test('should edit post', async ({ page }) => {
  // 이전 테스트에서 생성된 게시물에 의존!
  await page.goto('/posts/1');
});

// ✅ Good: 독립적 테스트
test('should edit post', async ({ page }) => {
  // 테스트용 데이터 직접 생성
  const postId = await createTestPost({ title: 'Test Post' });
  await page.goto(`/posts/${postId}`);
});
```

### 4. 환경 의존 테스트

```typescript
// ❌ Bad: 로컬 환경에만 동작
await page.goto('http://localhost:3000');

// ✅ Good: baseURL 사용
await page.goto('/');  // playwright.config.ts의 baseURL 사용

// playwright.config.ts
use: {
  baseURL: process.env.BASE_URL || 'http://localhost:3000',
}
```

---

## 에러 처리

### 실패 시 디버깅 정보

```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    // 실패 시 스크린샷
    screenshot: 'only-on-failure',
    // 실패 시 비디오
    video: 'retain-on-failure',
    // 실패 시 trace
    trace: 'retain-on-failure',
  },
  // 상세 리포트
  reporter: [
    ['html', { open: 'never' }],
    ['json', { outputFile: 'test-results/results.json' }],
  ],
});
```

### 에러 시나리오 테스트

```typescript
test.describe('Error Scenarios', () => {
  test('should handle server errors gracefully', async ({ page }) => {
    // API 에러 모킹
    await page.route('/api/posts', (route) => {
      route.fulfill({
        status: 500,
        body: JSON.stringify({ error: 'Internal Server Error' }),
      });
    });

    await page.goto('/dashboard');

    // 에러 UI 확인
    await expect(page.getByRole('alert')).toContainText(/오류가 발생했습니다/);
    await expect(page.getByRole('button', { name: /다시 시도/ })).toBeVisible();
  });

  test('should handle network timeout', async ({ page }) => {
    await page.route('/api/posts', async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 30000));
      route.abort('timedout');
    });

    await page.goto('/dashboard');

    await expect(page.getByText(/연결 시간이 초과되었습니다/)).toBeVisible({
      timeout: 35000,
    });
  });
});
```

### 재시도 로직

```typescript
// playwright.config.ts
export default defineConfig({
  retries: process.env.CI ? 2 : 0,  // CI에서만 재시도
  expect: {
    timeout: 10000,  // expect 타임아웃
  },
  timeout: 60000,  // 테스트 전체 타임아웃
});

// 특정 테스트만 재시도
test('flaky test', async ({ page }) => {
  test.info().annotations.push({ type: 'flaky', description: 'Known flaky test' });
  // ...
});
```

---

## 성능 고려사항

### 병렬 실행

```typescript
// playwright.config.ts
export default defineConfig({
  fullyParallel: true,
  workers: process.env.CI ? 1 : undefined,  // CI에서는 순차, 로컬은 병렬
});

// 순차 실행이 필요한 테스트
test.describe.serial('Sequential tests', () => {
  test('step 1', async ({ page }) => { /* ... */ });
  test('step 2', async ({ page }) => { /* ... */ });
});
```

### 인증 상태 재사용

```typescript
// e2e/auth.setup.ts
const authFile = '.auth/user.json';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('이메일').fill(process.env.TEST_USER_EMAIL!);
  await page.getByLabel('비밀번호').fill(process.env.TEST_USER_PASSWORD!);
  await page.getByRole('button', { name: '로그인' }).click();

  await page.waitForURL('/dashboard');
  await page.context().storageState({ path: authFile });
});

// playwright.config.ts
projects: [
  { name: 'setup', testMatch: /.*\.setup\.ts/ },
  {
    name: 'chromium',
    use: { storageState: authFile },
    dependencies: ['setup'],
  },
],
```

### API 모킹으로 속도 향상

```typescript
test('should display posts quickly', async ({ page }) => {
  // 실제 API 대신 모킹
  await page.route('/api/posts', (route) => {
    route.fulfill({
      status: 200,
      body: JSON.stringify({ data: mockPosts }),
    });
  });

  await page.goto('/dashboard');
  await expect(page.getByTestId('post-card')).toHaveCount(mockPosts.length);
});
```

---

## 보안 고려사항

### 테스트 자격 증명 관리

```typescript
// 환경 변수로 관리 (절대 커밋하지 않음)
// .env.test
TEST_USER_EMAIL=test@example.com
TEST_USER_PASSWORD=securepassword123

// GitHub Secrets 사용
// playwright.config.ts
use: {
  httpCredentials: {
    username: process.env.BASIC_AUTH_USER!,
    password: process.env.BASIC_AUTH_PASS!,
  },
}
```

### 민감 데이터 마스킹

```typescript
// 스크린샷에서 민감 정보 숨기기
test('profile page', async ({ page }) => {
  await page.goto('/profile');

  // 민감 정보 숨기기
  await page.evaluate(() => {
    document.querySelectorAll('[data-sensitive]').forEach((el) => {
      (el as HTMLElement).style.visibility = 'hidden';
    });
  });

  await expect(page).toHaveScreenshot('profile-page.png');
});
```

### 테스트 환경 격리

```typescript
// playwright.config.ts
export default defineConfig({
  webServer: {
    command: 'npm run dev:test',  // 테스트 전용 환경
    url: 'http://localhost:3001',
    reuseExistingServer: !process.env.CI,
  },
  use: {
    baseURL: 'http://localhost:3001',
  },
});
```

---

---

## agent-browser (Alternative)

Vercel Labs의 **agent-browser**는 AI 에이전트를 위한 헤드리스 브라우저 자동화 CLI입니다.
Refs 시스템을 통해 결정론적 요소 선택이 가능하며, 접근성 트리 기반으로 LLM 워크플로우에 최적화되어 있습니다.

### Playwright vs agent-browser

| 항목 | Playwright | agent-browser |
|------|-----------|---------------|
| **설치** | `npm i -D @playwright/test` | `npm i -g agent-browser` |
| **요소 선택** | CSS/XPath/Role | Refs 시스템 (결정론적) |
| **AI 최적화** | 일반적 | 접근성 트리 기반 |
| **세션 관리** | 별도 구현 | 내장 (`--session`) |
| **출력 형식** | JavaScript API | CLI + JSON |
| **사용 사례** | 전통적 E2E | AI 에이전트 자동화 |

### 설치

```bash
npm install -g agent-browser
agent-browser install  # Chromium 설치
```

### 핵심 명령어

```bash
# 스냅샷 (요소 맵 획득)
agent-browser open http://localhost:3000
agent-browser snapshot -i  # 상호작용 요소만

# 출력 예시:
# - button "로그인" [ref=e1]
# - textbox "이메일" [ref=e2]
# - textbox "비밀번호" [ref=e3]

# Refs로 상호작용
agent-browser fill @e2 "user@example.com"
agent-browser fill @e3 "password123"
agent-browser click @e1
agent-browser wait network-idle
agent-browser screenshot result.png
```

### 테스트 스크립트 예시

```bash
#!/bin/bash
# tests/e2e/login.sh

SESSION="auth-test"

# 로그인 페이지 접근
agent-browser --session $SESSION open http://localhost:3000/login
agent-browser --session $SESSION snapshot -i

# 로그인 수행
agent-browser --session $SESSION fill @email "test@test.com"
agent-browser --session $SESSION fill @password "password123"
agent-browser --session $SESSION click @submit
agent-browser --session $SESSION wait network-idle

# 결과 검증
agent-browser --session $SESSION snapshot -i
agent-browser --session $SESSION screenshot test-results/login.png
```

### CI/CD 통합 (GitHub Actions)

```yaml
# .github/workflows/e2e-agent-browser.yml
- name: Install agent-browser
  run: |
    npm install -g agent-browser
    agent-browser install

- name: Run E2E tests
  run: bash tests/e2e/run-all.sh
```

### 언제 사용할까?

| 상황 | 권장 도구 |
|------|----------|
| 전통적 E2E 테스트 스위트 | **Playwright** |
| AI 에이전트 자동화 | **agent-browser** |
| Visual Regression | Playwright 또는 agent-browser |
| 접근성 트리 기반 테스트 | **agent-browser** |
| 복잡한 테스트 시나리오 | **Playwright** |
| 빠른 프로토타이핑 | **agent-browser** |

> 상세한 agent-browser 가이드는 `agent-browser-test-skill/SKILL.md` 참조

---

## References

- `_references/TEST-PATTERN.md`
- `_references/ARCHITECTURE-PATTERN.md`
- `agent-browser-test-skill/SKILL.md`

