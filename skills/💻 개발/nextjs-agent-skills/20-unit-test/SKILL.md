---
name: unit-test
description: |
  Vitest를 사용하여 단위 테스트를 작성합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Unit Test Skill

Extends: `../../_shared/unit-test/SKILL.md` (공통 테스트 원칙 참조)

Vitest를 사용하여 단위 테스트를 작성합니다.

## Triggers

- "유닛 테스트", "unit test", "vitest", "단위 테스트"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `target` | ✅ | 테스트 대상 (service, schema, hook, util) |
| `coverage` | ❌ | 커버리지 목표 (기본 80%) |

---

## 설치

```bash
# 테스트 프레임워크 (Next.js 16 / React 19 기준)
npm install -D vitest@^4.1.7 @vitejs/plugin-react@^6.0.2

# Testing Library
npm install -D @testing-library/react@^16.3.2 @testing-library/dom@^10.4.1 @testing-library/jest-dom@^6.9.1

# 환경
npm install -D jsdom@^29.1.1
```

---

## Vitest 설정

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./vitest.setup.ts'],
    include: ['**/*.{test,spec}.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      include: ['src/**/*.{ts,tsx}', 'features/**/*.{ts,tsx}'],
      exclude: ['**/*.d.ts', '**/*.test.{ts,tsx}', '**/types/**'],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80,
        },
      },
    },
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './'),
    },
  },
});
```

```typescript
// vitest.setup.ts
import '@testing-library/jest-dom/vitest';
import { vi } from 'vitest';

// Mock Next.js router
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    refresh: vi.fn(),
  }),
  usePathname: () => '/',
  useSearchParams: () => new URLSearchParams(),
}));

// Mock sonner toast
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  },
}));
```

---

## Service 테스트

```typescript
// features/posts/api/__tests__/posts.service.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { postsService } from '../posts.service';

// Mock fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('postsService', () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  describe('getPosts', () => {
    it('should fetch posts with default params', async () => {
      const mockData = {
        data: [{ id: '1', title: 'Test' }],
        pagination: { page: 1, limit: 20, total: 1, totalPages: 1 },
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockData),
      });

      const result = await postsService.getPosts();

      expect(mockFetch).toHaveBeenCalledWith('/api/posts?');
      expect(result).toEqual(mockData);
    });

    it('should include filters in query params', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ data: [], pagination: {} }),
      });

      await postsService.getPosts({ status: 'published', search: 'test' });

      const [url] = mockFetch.mock.calls[0];
      expect(url).toContain('status=published');
      expect(url).toContain('search=test');
    });

    it('should throw error on failed response', async () => {
      mockFetch.mockResolvedValueOnce({ ok: false });

      await expect(postsService.getPosts()).rejects.toThrow('Failed to fetch posts');
    });
  });

  describe('getPost', () => {
    it('should fetch single post by id', async () => {
      const mockPost = { id: '1', title: 'Test' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockPost),
      });

      const result = await postsService.getPost('1');

      expect(mockFetch).toHaveBeenCalledWith('/api/posts/1');
      expect(result).toEqual(mockPost);
    });
  });

  describe('createPost', () => {
    it('should create post with correct body', async () => {
      const newPost = { title: 'New Post', content: 'Content' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ id: '1', ...newPost }),
      });

      await postsService.createPost(newPost);

      expect(mockFetch).toHaveBeenCalledWith('/api/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newPost),
      });
    });
  });
});
```

---

## Schema 테스트

```typescript
// features/posts/schemas/__tests__/post.schema.test.ts
import { describe, it, expect } from 'vitest';
import { createPostSchema, updatePostSchema } from '../post.schema';

describe('createPostSchema', () => {
  it('should validate valid input', () => {
    const validInput = {
      title: 'Test Title',
      content: 'Test content',
      status: 'draft',
    };

    const result = createPostSchema.safeParse(validInput);

    expect(result.success).toBe(true);
  });

  it('should reject empty title', () => {
    const invalidInput = {
      title: '',
      content: 'Content',
      status: 'draft',
    };

    const result = createPostSchema.safeParse(invalidInput);

    expect(result.success).toBe(false);
    expect(result.error?.issues[0].path).toContain('title');
  });

  it('should reject invalid status', () => {
    const invalidInput = {
      title: 'Title',
      content: 'Content',
      status: 'invalid',
    };

    const result = createPostSchema.safeParse(invalidInput);

    expect(result.success).toBe(false);
  });

  it('should transform trimmed values', () => {
    const input = {
      title: '  Test Title  ',
      content: 'Content',
      status: 'draft',
    };

    const result = createPostSchema.safeParse(input);

    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.title).toBe('Test Title');
    }
  });
});

describe('updatePostSchema', () => {
  it('should allow partial updates', () => {
    const partialInput = { title: 'Updated Title' };

    const result = updatePostSchema.safeParse(partialInput);

    expect(result.success).toBe(true);
  });

  it('should allow empty object', () => {
    const result = updatePostSchema.safeParse({});

    expect(result.success).toBe(true);
  });
});
```

---

## Hook 테스트

```typescript
// features/posts/hooks/__tests__/use-posts.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { usePosts, usePost } from '../use-posts';
import { postsService } from '../../api/posts.service';

vi.mock('../../api/posts.service');

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('usePosts', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('should fetch posts successfully', async () => {
    const mockData = {
      data: [{ id: '1', title: 'Test' }],
      pagination: { page: 1, limit: 20, total: 1, totalPages: 1 },
    };
    vi.mocked(postsService.getPosts).mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => usePosts(), { wrapper: createWrapper() });

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockData);
  });

  it('should handle error state', async () => {
    vi.mocked(postsService.getPosts).mockRejectedValueOnce(new Error('Failed'));

    const { result } = renderHook(() => usePosts(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error?.message).toBe('Failed');
  });
});

describe('usePost', () => {
  it('should fetch single post', async () => {
    const mockPost = { id: '1', title: 'Test' };
    vi.mocked(postsService.getPost).mockResolvedValueOnce(mockPost);

    const { result } = renderHook(() => usePost('1'), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockPost);
    expect(postsService.getPost).toHaveBeenCalledWith('1');
  });

  it('should not fetch when id is empty', () => {
    const { result } = renderHook(() => usePost(''), { wrapper: createWrapper() });

    expect(result.current.fetchStatus).toBe('idle');
    expect(postsService.getPost).not.toHaveBeenCalled();
  });
});
```

---

## Utility 테스트

```typescript
// lib/__tests__/utils.test.ts
import { describe, it, expect } from 'vitest';
import { cn, formatDate, formatCurrency, truncate } from '../utils';

describe('cn', () => {
  it('should merge class names', () => {
    expect(cn('foo', 'bar')).toBe('foo bar');
  });

  it('should handle conditional classes', () => {
    expect(cn('foo', false && 'bar', 'baz')).toBe('foo baz');
  });

  it('should merge tailwind classes correctly', () => {
    expect(cn('px-2 py-1', 'px-4')).toBe('py-1 px-4');
  });
});

describe('formatDate', () => {
  it('should format date in Korean locale', () => {
    const date = new Date('2024-01-15');
    expect(formatDate(date)).toBe('2024. 1. 15.');
  });

  it('should handle string input', () => {
    expect(formatDate('2024-01-15')).toBe('2024. 1. 15.');
  });
});

describe('formatCurrency', () => {
  it('should format number as KRW', () => {
    expect(formatCurrency(1000)).toBe('₩1,000');
  });

  it('should format large numbers', () => {
    expect(formatCurrency(1000000)).toBe('₩1,000,000');
  });
});

describe('truncate', () => {
  it('should truncate long text', () => {
    expect(truncate('Hello World', 5)).toBe('Hello...');
  });

  it('should not truncate short text', () => {
    expect(truncate('Hello', 10)).toBe('Hello');
  });
});
```

---

## 실행 명령어

```bash
# 전체 테스트
npm run test

# Watch 모드
npm run test:watch

# 커버리지
npm run test:coverage

# 특정 파일
npm run test -- posts.service.test.ts

# 특정 패턴
npm run test -- --grep "should fetch"
```

```json
// package.json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "test:ui": "vitest --ui"
  }
}
```

---

## 테스트 예제

이 스킬의 주요 섹션들이 유닛 테스트 예제입니다:

- **Service 테스트**: 비즈니스 로직 테스트 패턴
- **Schema 테스트**: Zod 스키마 검증 테스트
- **Hook 테스트**: React 훅 테스트 (renderHook)
- **Utility 테스트**: 순수 함수 테스트

### 테스트 유틸리티 테스트 (Meta-testing)

```typescript
// tests/utils/test-utils.test.ts
import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { createQueryWrapper } from '../test-utils';

describe('Test Utilities', () => {
  describe('createQueryWrapper', () => {
    it('provides QueryClient to children', () => {
      const wrapper = createQueryWrapper();
      expect(wrapper).toBeDefined();
      expect(typeof wrapper).toBe('function');
    });

    it('creates isolated QueryClient for each test', () => {
      const wrapper1 = createQueryWrapper();
      const wrapper2 = createQueryWrapper();
      // 각 테스트는 독립된 QueryClient를 가져야 함
      expect(wrapper1).not.toBe(wrapper2);
    });
  });

  describe('Mock Router', () => {
    it('mocks useRouter correctly', async () => {
      const { useRouter } = await import('next/navigation');
      const router = useRouter();

      router.push('/test');
      expect(router.push).toHaveBeenCalledWith('/test');
    });
  });
});
```

---

## 안티패턴

### 1. 구현 세부사항 테스트

```typescript
// ❌ Bad: 내부 상태 직접 테스트
it('should set loading state', () => {
  const { result } = renderHook(() => usePosts());
  expect(result.current.state.isLoading).toBe(true);  // 내부 구현에 의존
});

// ✅ Good: 동작 테스트
it('should show loading initially', () => {
  const { result } = renderHook(() => usePosts(), { wrapper });
  expect(result.current.isLoading).toBe(true);  // 공개 API 테스트
});
```

### 2. Mock 과다 사용

```typescript
// ❌ Bad: 모든 것을 mock
vi.mock('@/lib/db');
vi.mock('@/lib/auth');
vi.mock('@/lib/api');
vi.mock('@/components/ui/button');  // 너무 많은 mock!

// ✅ Good: 경계만 mock
vi.mock('@/lib/db');  // 외부 의존성만 mock
// 내부 함수, 컴포넌트는 실제 사용
```

### 3. 비동기 처리 미흡

```typescript
// ❌ Bad: async 대기 없음
it('should fetch data', () => {
  const { result } = renderHook(() => useData(), { wrapper });
  expect(result.current.data).toBeDefined();  // 실패! 아직 로딩 중
});

// ✅ Good: waitFor로 대기
it('should fetch data', async () => {
  const { result } = renderHook(() => useData(), { wrapper });

  await waitFor(() => {
    expect(result.current.isSuccess).toBe(true);
  });

  expect(result.current.data).toBeDefined();
});
```

### 4. 테스트 간 상태 공유

```typescript
// ❌ Bad: 전역 상태 공유
const queryClient = new QueryClient();  // 모든 테스트가 공유!

// ✅ Good: 테스트별 독립 인스턴스
const createTestQueryClient = () => new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

// 각 테스트에서
const wrapper = createWrapper();  // 새 QueryClient 생성
```

---

## 에러 처리

### 테스트 에러 명확화

```typescript
// lib/test-utils/errors.ts
export class TestSetupError extends Error {
  constructor(message: string) {
    super(`[Test Setup] ${message}`);
    this.name = 'TestSetupError';
  }
}

// 명확한 에러 메시지
it('should handle error response', async () => {
  mockFetch.mockResolvedValueOnce({ ok: false, status: 500 });

  await expect(postsService.getPosts()).rejects.toThrow(
    expect.objectContaining({
      message: expect.stringContaining('Failed to fetch'),
    })
  );
});
```

### 에러 케이스 테스트

```typescript
describe('Error Handling', () => {
  it('should throw on network error', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    await expect(postsService.getPosts()).rejects.toThrow('Network error');
  });

  it('should throw on 404', async () => {
    mockFetch.mockResolvedValueOnce({ ok: false, status: 404 });

    await expect(postsService.getPost('999')).rejects.toThrow('Not found');
  });

  it('should retry on 5xx errors', async () => {
    mockFetch
      .mockResolvedValueOnce({ ok: false, status: 500 })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({}) });

    // retry 설정된 hook 사용 시
    const { result } = renderHook(() => useDataWithRetry(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockFetch).toHaveBeenCalledTimes(2);
  });
});
```

---

## 성능 고려사항

### 테스트 속도 최적화

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    // 병렬 실행
    pool: 'threads',
    poolOptions: {
      threads: { singleThread: false },
    },

    // 느린 테스트 리포팅
    slowTestThreshold: 500,

    // 불필요한 재실행 방지
    isolate: true,
    passWithNoTests: true,
  },
});
```

### 무거운 설정 캐싱

```typescript
// test/setup/query-client.ts
let cachedQueryClient: QueryClient | null = null;

export function getTestQueryClient() {
  if (!cachedQueryClient) {
    cachedQueryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
  }
  return cachedQueryClient;
}

// 각 테스트 후 상태만 리셋
afterEach(() => {
  cachedQueryClient?.clear();
});
```

### 선택적 테스트 실행

```bash
# 변경된 파일만 테스트
npm run test -- --changed

# 특정 패턴만
npm run test -- --grep "service"

# 커버리지 없이 빠르게
npm run test -- --no-coverage
```

---

## 보안 고려사항

### 민감 정보 테스트 방지

```typescript
// ❌ Bad: 실제 API 키 사용
const API_KEY = 'sk-real-api-key-12345';

// ✅ Good: 테스트용 더미 값
const API_KEY = 'test-api-key';

// 환경 변수 mock
vi.stubEnv('API_KEY', 'test-api-key');
```

### 인증 테스트 분리

```typescript
// 인증 관련 테스트는 별도 파일로 분리
// __tests__/auth.test.ts

describe('Auth Service', () => {
  // 민감한 테스트는 CI에서만 실행
  it.skipIf(process.env.CI !== 'true')('should validate real tokens', async () => {
    // ...
  });
});
```

### 테스트 데이터 격리

```typescript
// 테스트 데이터는 실제 DB와 분리
beforeAll(async () => {
  // 테스트용 DB 또는 in-memory DB 사용
  await setupTestDatabase();
});

afterAll(async () => {
  // 테스트 데이터 정리
  await cleanupTestDatabase();
});
```

---

## References

- `_references/TEST-PATTERN.md`
- `_references/ARCHITECTURE-PATTERN.md`
