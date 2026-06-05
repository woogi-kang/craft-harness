# Test Pattern Reference

Vitest + React Testing Library + Playwright 테스트 패턴 및 샘플 코드 레퍼런스입니다.

## 테스트 피라미드

```
           ┌───────────┐
           │   E2E     │  5-10%  Playwright
           │  Tests    │
          ┌┴───────────┴┐
          │   Visual    │  5-10%  Playwright Snapshots
          │   Tests     │
         ┌┴─────────────┴┐
         │  Integration  │  15-20%  React Testing Library
         │    Tests      │
        ┌┴───────────────┴┐
        │    Unit Tests   │  60-70%  Vitest
        └─────────────────┘
```

---

## 디렉토리 구조

```
src/
├── features/
│   └── users/
│       ├── __tests__/
│       │   ├── users.service.test.ts      # Unit
│       │   ├── use-users.test.ts          # Hook Unit
│       │   └── users-table.test.tsx       # Integration
│       └── ...
│
├── components/
│   └── molecules/
│       └── __tests__/
│           └── search-bar.test.tsx
│
tests/
├── setup.ts                               # Vitest 설정
├── utils/
│   ├── render.tsx                         # Custom render
│   └── mocks.ts                           # 공통 Mock
└── e2e/
    ├── auth.spec.ts                       # E2E
    ├── users.spec.ts
    └── fixtures/
        └── auth.fixture.ts
```

---

## Vitest 설정

### vitest.config.ts

```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import tsconfigPaths from 'vite-tsconfig-paths';

export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/types/**',
      ],
    },
  },
});
```

### tests/setup.ts

```typescript
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';
import { server } from './mocks/server';

// MSW 서버 설정
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => {
  cleanup();
  server.resetHandlers();
});
afterAll(() => server.close());

// Next.js Router Mock
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
    back: vi.fn(),
  }),
  usePathname: () => '/',
  useSearchParams: () => new URLSearchParams(),
}));

// ResizeObserver Mock
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));
```

---

## Unit Test 패턴

### Service Test

```typescript
// features/users/api/__tests__/users.service.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { usersService } from '../users.service';
import { usersRepository } from '../users.repository';

vi.mock('../users.repository');

const mockUser = {
  id: '1',
  email: 'test@example.com',
  name: 'Test User',
  avatarUrl: null,
  isVerified: false,
  createdAt: new Date(),
  updatedAt: new Date(),
};

describe('usersService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getUser', () => {
    it('사용자를 찾으면 반환한다', async () => {
      vi.mocked(usersRepository.findById).mockResolvedValue(mockUser);

      const result = await usersService.getUser('1');

      expect(result).toEqual(mockUser);
      expect(usersRepository.findById).toHaveBeenCalledWith('1');
    });

    it('사용자가 없으면 에러를 던진다', async () => {
      vi.mocked(usersRepository.findById).mockResolvedValue(null);

      await expect(usersService.getUser('1')).rejects.toThrow('User not found');
    });
  });

  describe('createUser', () => {
    it('새 사용자를 생성한다', async () => {
      vi.mocked(usersRepository.findByEmail).mockResolvedValue(null);
      vi.mocked(usersRepository.create).mockResolvedValue(mockUser);

      const input = { email: 'test@example.com', name: 'Test User' };
      const result = await usersService.createUser(input);

      expect(result).toEqual(mockUser);
      expect(usersRepository.create).toHaveBeenCalledWith(input);
    });

    it('이메일이 중복되면 에러를 던진다', async () => {
      vi.mocked(usersRepository.findByEmail).mockResolvedValue(mockUser);

      const input = { email: 'test@example.com', name: 'Test User' };
      await expect(usersService.createUser(input)).rejects.toThrow(
        'Email already exists'
      );
    });
  });
});
```

### Zod Schema Test

```typescript
// features/users/schemas/__tests__/user.schema.test.ts
import { describe, it, expect } from 'vitest';
import { createUserSchema, updateUserSchema } from '../user.schema';

describe('userSchema', () => {
  describe('createUserSchema', () => {
    it('유효한 입력을 통과시킨다', () => {
      const input = {
        email: 'test@example.com',
        name: 'Test User',
      };

      const result = createUserSchema.safeParse(input);

      expect(result.success).toBe(true);
      expect(result.data).toEqual(input);
    });

    it('잘못된 이메일을 거부한다', () => {
      const input = {
        email: 'invalid-email',
        name: 'Test User',
      };

      const result = createUserSchema.safeParse(input);

      expect(result.success).toBe(false);
      expect(result.error?.issues[0].message).toBe('유효한 이메일을 입력하세요');
    });

    it('짧은 이름을 거부한다', () => {
      const input = {
        email: 'test@example.com',
        name: 'A',
      };

      const result = createUserSchema.safeParse(input);

      expect(result.success).toBe(false);
      expect(result.error?.issues[0].message).toBe('이름은 2자 이상이어야 합니다');
    });
  });

  describe('updateUserSchema', () => {
    it('부분 업데이트를 허용한다', () => {
      const result = updateUserSchema.safeParse({ name: 'New Name' });

      expect(result.success).toBe(true);
      expect(result.data).toEqual({ name: 'New Name' });
    });
  });
});
```

### Hook Test (with TanStack Query)

```typescript
// features/users/hooks/__tests__/use-users.test.ts
import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useUsers, useUser } from '../use-users';

// QueryClient Wrapper
function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

const mockUsers = [
  { id: '1', name: 'User 1', email: 'user1@example.com' },
  { id: '2', name: 'User 2', email: 'user2@example.com' },
];

describe('useUsers', () => {
  it('사용자 목록을 가져온다', async () => {
    // MSW handler가 설정되어 있다고 가정
    const { result } = renderHook(() => useUsers(), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toHaveLength(2);
  });
});

describe('useUser', () => {
  it('id가 없으면 쿼리를 실행하지 않는다', () => {
    const { result } = renderHook(() => useUser(''), {
      wrapper: createWrapper(),
    });

    expect(result.current.fetchStatus).toBe('idle');
  });
});
```

---

## Integration Test 패턴

### Custom Render

```tsx
// tests/utils/render.tsx
import { render as rtlRender, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@/components/theme-provider';

interface WrapperProps {
  children: React.ReactNode;
}

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
}

function AllProviders({ children }: WrapperProps) {
  const queryClient = createTestQueryClient();

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="light">
        {children}
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export function render(
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  return rtlRender(ui, { wrapper: AllProviders, ...options });
}

export * from '@testing-library/react';
export { render };
```

### Component Integration Test

```tsx
// features/users/components/__tests__/users-table.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render } from '@/tests/utils/render';
import { UsersTable } from '../users-table';
import { server } from '@/tests/mocks/server';
import { http, HttpResponse } from 'msw';

const mockUsers = [
  { id: '1', name: 'John Doe', email: 'john@example.com', isVerified: true },
  { id: '2', name: 'Jane Smith', email: 'jane@example.com', isVerified: false },
];

describe('UsersTable', () => {
  it('사용자 목록을 렌더링한다', async () => {
    render(<UsersTable initialData={mockUsers} />);

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });

  it('삭제 버튼을 클릭하면 확인 모달이 표시된다', async () => {
    const user = userEvent.setup();
    render(<UsersTable initialData={mockUsers} />);

    const deleteButtons = screen.getAllByRole('button', { name: /삭제/i });
    await user.click(deleteButtons[0]);

    expect(
      await screen.findByText(/정말 삭제하시겠습니까/i)
    ).toBeInTheDocument();
  });

  it('삭제 확인 시 API를 호출하고 목록을 업데이트한다', async () => {
    const user = userEvent.setup();

    // 삭제 API Mock
    server.use(
      http.delete('/api/users/:id', () => {
        return HttpResponse.json({ success: true });
      })
    );

    render(<UsersTable initialData={mockUsers} />);

    const deleteButtons = screen.getAllByRole('button', { name: /삭제/i });
    await user.click(deleteButtons[0]);

    const confirmButton = await screen.findByRole('button', { name: /확인/i });
    await user.click(confirmButton);

    await waitFor(() => {
      expect(screen.queryByText('John Doe')).not.toBeInTheDocument();
    });
  });
});
```

### Form Integration Test

```tsx
// features/users/components/__tests__/user-form.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render } from '@/tests/utils/render';
import { UserForm } from '../user-form';

describe('UserForm', () => {
  it('폼을 렌더링한다', () => {
    render(<UserForm onSubmit={vi.fn()} />);

    expect(screen.getByLabelText(/이메일/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/이름/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /저장/i })).toBeInTheDocument();
  });

  it('유효성 검증 에러를 표시한다', async () => {
    const user = userEvent.setup();
    render(<UserForm onSubmit={vi.fn()} />);

    await user.click(screen.getByRole('button', { name: /저장/i }));

    expect(await screen.findByText(/유효한 이메일을 입력하세요/i)).toBeInTheDocument();
    expect(await screen.findByText(/이름은 2자 이상/i)).toBeInTheDocument();
  });

  it('유효한 데이터로 제출하면 onSubmit을 호출한다', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<UserForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/이메일/i), 'test@example.com');
    await user.type(screen.getByLabelText(/이름/i), 'Test User');
    await user.click(screen.getByRole('button', { name: /저장/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        email: 'test@example.com',
        name: 'Test User',
      });
    });
  });
});
```

---

## MSW (Mock Service Worker)

### Handler 설정

```typescript
// tests/mocks/handlers.ts
import { http, HttpResponse } from 'msw';

const users = [
  { id: '1', name: 'John Doe', email: 'john@example.com', isVerified: true },
  { id: '2', name: 'Jane Smith', email: 'jane@example.com', isVerified: false },
];

export const handlers = [
  http.get('/api/users', () => {
    return HttpResponse.json(users);
  }),

  http.get('/api/users/:id', ({ params }) => {
    const user = users.find((u) => u.id === params.id);
    if (!user) {
      return new HttpResponse(null, { status: 404 });
    }
    return HttpResponse.json(user);
  }),

  http.post('/api/users', async ({ request }) => {
    const body = await request.json();
    const newUser = { ...body, id: '3', isVerified: false };
    return HttpResponse.json(newUser, { status: 201 });
  }),

  http.delete('/api/users/:id', () => {
    return HttpResponse.json({ success: true });
  }),
];
```

### Server 설정

```typescript
// tests/mocks/server.ts
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);
```

---

## E2E Test (Playwright)

### playwright.config.ts

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

### Auth Fixture

```typescript
// tests/e2e/fixtures/auth.fixture.ts
import { test as base, expect, type Page } from '@playwright/test';

type AuthFixtures = {
  authenticatedPage: Page;
};

export const test = base.extend<AuthFixtures>({
  authenticatedPage: async ({ page }, use) => {
    // 로그인
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    // 로그인 완료 대기
    await page.waitForURL('/dashboard');

    await use(page);
  },
});

export { expect };
```

### Storage State 기반 Auth (권장)

```typescript
// tests/e2e/auth.setup.ts
import { test as setup, expect } from '@playwright/test';
import path from 'path';

const authFile = path.join(__dirname, '../.auth/user.json');

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[name="email"]', process.env.TEST_USER_EMAIL!);
  await page.fill('[name="password"]', process.env.TEST_USER_PASSWORD!);
  await page.click('button[type="submit"]');

  await page.waitForURL('/dashboard');
  await expect(page.getByRole('heading', { name: /대시보드/i })).toBeVisible();

  // 인증 상태 저장
  await page.context().storageState({ path: authFile });
});
```

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  projects: [
    // 인증 setup
    { name: 'setup', testMatch: /.*\.setup\.ts/ },

    // 인증된 상태로 테스트
    {
      name: 'chromium',
      use: {
        storageState: 'tests/.auth/user.json',
      },
      dependencies: ['setup'],
    },
  ],
});
```

### E2E Test

```typescript
// tests/e2e/users.spec.ts
import { test, expect } from './fixtures/auth.fixture';

test.describe('Users Management', () => {
  test('사용자 목록을 표시한다', async ({ authenticatedPage: page }) => {
    await page.goto('/users');

    await expect(page.getByRole('heading', { name: '사용자 관리' })).toBeVisible();
    await expect(page.getByRole('table')).toBeVisible();
  });

  test('새 사용자를 생성한다', async ({ authenticatedPage: page }) => {
    await page.goto('/users');

    // 생성 버튼 클릭
    await page.click('button:has-text("새 사용자")');

    // 폼 작성
    await page.fill('[name="email"]', 'new@example.com');
    await page.fill('[name="name"]', 'New User');

    // 제출
    await page.click('button[type="submit"]');

    // 성공 토스트 확인
    await expect(page.getByText('사용자가 생성되었습니다')).toBeVisible();

    // 목록에 표시 확인
    await expect(page.getByText('new@example.com')).toBeVisible();
  });

  test('사용자를 삭제한다', async ({ authenticatedPage: page }) => {
    await page.goto('/users');

    // 첫 번째 삭제 버튼 클릭
    await page.click('table tbody tr:first-child button[aria-label="삭제"]');

    // 확인 모달
    await page.click('button:has-text("확인")');

    // 성공 토스트 확인
    await expect(page.getByText('사용자가 삭제되었습니다')).toBeVisible();
  });
});
```

### Visual Regression Test

```typescript
// tests/e2e/visual.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Visual Regression', () => {
  test('로그인 페이지 스냅샷', async ({ page }) => {
    await page.goto('/login');
    await expect(page).toHaveScreenshot('login-page.png');
  });

  test('대시보드 스냅샷', async ({ page }) => {
    // 로그인 후
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');

    await expect(page).toHaveScreenshot('dashboard.png', {
      maxDiffPixels: 100, // 허용 오차
    });
  });

  test('다크 모드 스냅샷', async ({ page }) => {
    await page.emulateMedia({ colorScheme: 'dark' });
    await page.goto('/');
    await expect(page).toHaveScreenshot('home-dark.png');
  });
});
```

---

## 테스트 명령어

```bash
# Unit + Integration Tests
npm run test                    # Watch 모드
npm run test:run               # 단일 실행
npm run test:coverage          # 커버리지

# E2E Tests
npm run test:e2e               # Playwright 실행
npm run test:e2e:ui            # Playwright UI 모드
npm run test:e2e:headed        # 브라우저 표시

# Visual Regression
npm run test:e2e -- --update-snapshots  # 스냅샷 업데이트
```
