---
name: integration-test
description: |
  컴포넌트 통합 테스트를 작성합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Integration Test Skill

컴포넌트 통합 테스트를 작성합니다.

## Triggers

- "통합 테스트", "integration test", "컴포넌트 테스트", "rtl"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `component` | ✅ | 테스트 대상 컴포넌트 |
| `interactions` | ❌ | 테스트할 상호작용 |

---

## 테스트 유틸리티 설정

```typescript
// test/utils.tsx
import { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from 'next-themes';

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  queryClient?: QueryClient;
}

export function customRender(ui: ReactElement, options: CustomRenderOptions = {}) {
  const { queryClient = createTestQueryClient(), ...renderOptions } = options;

  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        <ThemeProvider attribute="class" defaultTheme="light">
          {children}
        </ThemeProvider>
      </QueryClientProvider>
    );
  }

  return {
    ...render(ui, { wrapper: Wrapper, ...renderOptions }),
    queryClient,
  };
}

export * from '@testing-library/react';
export { customRender as render };
```

---

## MSW 설정

```bash
npm install -D msw
```

```typescript
// test/mocks/handlers.ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  // Posts
  http.get('/api/posts', () => {
    return HttpResponse.json({
      data: [
        { id: '1', title: 'First Post', status: 'published' },
        { id: '2', title: 'Second Post', status: 'draft' },
      ],
      pagination: { page: 1, limit: 20, total: 2, totalPages: 1 },
    });
  }),

  http.get('/api/posts/:id', ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      title: 'Test Post',
      content: 'Test content',
      status: 'published',
    });
  }),

  http.post('/api/posts', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ id: '3', ...body }, { status: 201 });
  }),

  http.patch('/api/posts/:id', async ({ params, request }) => {
    const body = await request.json();
    return HttpResponse.json({ id: params.id, ...body });
  }),

  http.delete('/api/posts/:id', () => {
    return new HttpResponse(null, { status: 204 });
  }),
];
```

```typescript
// test/mocks/server.ts
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);
```

```typescript
// vitest.setup.ts (추가)
import { server } from './test/mocks/server';

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

---

## 폼 컴포넌트 테스트

```typescript
// features/posts/components/__tests__/post-form.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@/test/utils';
import userEvent from '@testing-library/user-event';
import { PostForm } from '../post-form';
import { server } from '@/test/mocks/server';
import { http, HttpResponse } from 'msw';

describe('PostForm', () => {
  it('should render form fields', () => {
    render(<PostForm />);

    expect(screen.getByLabelText(/제목/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/내용/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/상태/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /저장/i })).toBeInTheDocument();
  });

  it('should show validation errors for empty fields', async () => {
    const user = userEvent.setup();
    render(<PostForm />);

    await user.click(screen.getByRole('button', { name: /저장/i }));

    await waitFor(() => {
      expect(screen.getByText(/필수 입력/i)).toBeInTheDocument();
    });
  });

  it('should submit form with valid data', async () => {
    const user = userEvent.setup();
    const onSuccess = vi.fn();
    render(<PostForm onSuccess={onSuccess} />);

    await user.type(screen.getByLabelText(/제목/i), 'Test Title');
    await user.type(screen.getByLabelText(/내용/i), 'Test content');
    await user.click(screen.getByRole('button', { name: /저장/i }));

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalled();
    });
  });

  it('should show error toast on submission failure', async () => {
    server.use(
      http.post('/api/posts', () => {
        return HttpResponse.json({ error: 'Server error' }, { status: 500 });
      })
    );

    const user = userEvent.setup();
    render(<PostForm />);

    await user.type(screen.getByLabelText(/제목/i), 'Test');
    await user.type(screen.getByLabelText(/내용/i), 'Content');
    await user.click(screen.getByRole('button', { name: /저장/i }));

    await waitFor(() => {
      expect(screen.getByText(/오류/i)).toBeInTheDocument();
    });
  });

  it('should populate form with default values', () => {
    render(<PostForm defaultValues={{ title: 'Existing', content: 'Content' }} />);

    expect(screen.getByLabelText(/제목/i)).toHaveValue('Existing');
    expect(screen.getByLabelText(/내용/i)).toHaveValue('Content');
  });

  it('should disable submit button while submitting', async () => {
    const user = userEvent.setup();
    render(<PostForm />);

    await user.type(screen.getByLabelText(/제목/i), 'Test');
    await user.type(screen.getByLabelText(/내용/i), 'Content');

    const submitButton = screen.getByRole('button', { name: /저장/i });
    await user.click(submitButton);

    expect(submitButton).toBeDisabled();
  });
});
```

---

## 리스트 컴포넌트 테스트

```typescript
// features/posts/components/__tests__/post-list.test.tsx
import { describe, it, expect } from 'vitest';
import { render, screen, waitFor, within } from '@/test/utils';
import userEvent from '@testing-library/user-event';
import { PostList } from '../post-list';
import { server } from '@/test/mocks/server';
import { http, HttpResponse } from 'msw';

describe('PostList', () => {
  it('should render loading skeleton initially', () => {
    render(<PostList />);

    expect(screen.getAllByTestId('skeleton')).toHaveLength(6);
  });

  it('should render posts after loading', async () => {
    render(<PostList />);

    await waitFor(() => {
      expect(screen.getByText('First Post')).toBeInTheDocument();
      expect(screen.getByText('Second Post')).toBeInTheDocument();
    });
  });

  it('should show empty state when no posts', async () => {
    server.use(
      http.get('/api/posts', () => {
        return HttpResponse.json({
          data: [],
          pagination: { page: 1, limit: 20, total: 0, totalPages: 0 },
        });
      })
    );

    render(<PostList />);

    await waitFor(() => {
      expect(screen.getByText(/데이터가 없습니다/i)).toBeInTheDocument();
    });
  });

  it('should show error state on fetch failure', async () => {
    server.use(
      http.get('/api/posts', () => {
        return HttpResponse.json({ error: 'Failed' }, { status: 500 });
      })
    );

    render(<PostList />);

    await waitFor(() => {
      expect(screen.getByText(/오류가 발생했습니다/i)).toBeInTheDocument();
    });
  });

  it('should navigate to post detail on card click', async () => {
    const user = userEvent.setup();
    render(<PostList />);

    await waitFor(() => {
      expect(screen.getByText('First Post')).toBeInTheDocument();
    });

    const firstCard = screen.getByText('First Post').closest('a');
    expect(firstCard).toHaveAttribute('href', '/posts/1');
  });

  it('should filter posts by status', async () => {
    const user = userEvent.setup();
    render(<PostList />);

    await waitFor(() => {
      expect(screen.getByText('First Post')).toBeInTheDocument();
    });

    // Open status filter
    await user.click(screen.getByRole('combobox', { name: /상태/i }));
    await user.click(screen.getByRole('option', { name: /발행/i }));

    // Should only show published posts
    await waitFor(() => {
      expect(screen.getByText('First Post')).toBeInTheDocument();
      expect(screen.queryByText('Second Post')).not.toBeInTheDocument();
    });
  });
});
```

---

## 모달/다이얼로그 테스트

```typescript
// features/posts/components/__tests__/delete-dialog.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@/test/utils';
import userEvent from '@testing-library/user-event';
import { DeletePostDialog } from '../delete-post-dialog';

describe('DeletePostDialog', () => {
  const defaultProps = {
    postId: '1',
    postTitle: 'Test Post',
    isOpen: true,
    onOpenChange: vi.fn(),
    onConfirm: vi.fn(),
  };

  it('should render dialog content', () => {
    render(<DeletePostDialog {...defaultProps} />);

    expect(screen.getByRole('alertdialog')).toBeInTheDocument();
    expect(screen.getByText(/Test Post/)).toBeInTheDocument();
    expect(screen.getByText(/삭제하시겠습니까/i)).toBeInTheDocument();
  });

  it('should call onOpenChange when cancel clicked', async () => {
    const user = userEvent.setup();
    render(<DeletePostDialog {...defaultProps} />);

    await user.click(screen.getByRole('button', { name: /취소/i }));

    expect(defaultProps.onOpenChange).toHaveBeenCalledWith(false);
  });

  it('should call onConfirm when delete clicked', async () => {
    const user = userEvent.setup();
    render(<DeletePostDialog {...defaultProps} />);

    await user.click(screen.getByRole('button', { name: /삭제/i }));

    expect(defaultProps.onConfirm).toHaveBeenCalledWith('1');
  });

  it('should not render when isOpen is false', () => {
    render(<DeletePostDialog {...defaultProps} isOpen={false} />);

    expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument();
  });
});
```

---

## 검색/필터 컴포넌트 테스트

```typescript
// features/posts/components/__tests__/post-filters.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@/test/utils';
import userEvent from '@testing-library/user-event';
import { PostFilters } from '../post-filters';

// Mock nuqs - 올바른 타입 반환
vi.mock('nuqs', () => {
  const setQueryStates = vi.fn();
  return {
    useQueryStates: vi.fn(() => [
      { q: '', status: '', page: 1 },
      setQueryStates,
    ] as const),
    parseAsString: {
      withDefault: (value: string) => ({ defaultValue: value, parse: (v: string) => v }),
    },
    parseAsInteger: {
      withDefault: (value: number) => ({ defaultValue: value, parse: (v: string) => parseInt(v, 10) }),
    },
  };
});

describe('PostFilters', () => {
  it('should render search input and status filter', () => {
    render(<PostFilters />);

    expect(screen.getByPlaceholderText(/검색/i)).toBeInTheDocument();
    expect(screen.getByRole('combobox')).toBeInTheDocument();
  });

  it('should debounce search input', async () => {
    const user = userEvent.setup();
    render(<PostFilters />);

    const searchInput = screen.getByPlaceholderText(/검색/i);
    await user.type(searchInput, 'test');

    // Should debounce - check after delay
    await waitFor(
      () => {
        expect(searchInput).toHaveValue('test');
      },
      { timeout: 500 }
    );
  });

  it('should update status filter immediately', async () => {
    const user = userEvent.setup();
    render(<PostFilters />);

    await user.click(screen.getByRole('combobox'));
    await user.click(screen.getByRole('option', { name: /발행/i }));

    // Status should update immediately
    expect(screen.getByRole('combobox')).toHaveTextContent(/발행/i);
  });
});
```

---

## 접근성 테스트

```bash
npm install -D vitest-axe
```

```typescript
// features/posts/components/__tests__/a11y.test.tsx
import { describe, it, expect } from 'vitest';
import { render } from '@/test/utils';
import { axe } from 'vitest-axe';
import 'vitest-axe/extend-expect';
import { PostForm } from '../post-form';
import { PostList } from '../post-list';
import { PostCard } from '../post-card';

describe('Accessibility', () => {
  it('PostForm should have no a11y violations', async () => {
    const { container } = render(<PostForm />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('PostCard should have no a11y violations', async () => {
    const { container } = render(
      <PostCard post={{ id: '1', title: 'Test', status: 'published', createdAt: new Date() }} />
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('PostList should have no a11y violations', async () => {
    const { container } = render(<PostList />);
    // MSW handler에서 데이터 로드 대기
    await new Promise((resolve) => setTimeout(resolve, 100));
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

```typescript
// vitest.setup.ts (추가)
import 'vitest-axe/extend-expect';
```

---

## 실행 명령어

```bash
# 통합 테스트만 실행
npm run test -- --grep "integration"

# 특정 컴포넌트 테스트
npm run test -- post-form.test.tsx
```

---

## 테스트 예제

이 스킬의 주요 섹션들이 통합 테스트 예제입니다:

- **폼 컴포넌트 테스트**: 사용자 입력, 제출, 에러 처리 통합 테스트
- **리스트 컴포넌트 테스트**: 데이터 로딩, 페이지네이션, CRUD 통합
- **모달/다이얼로그 테스트**: 열기/닫기, 폼 제출, 상태 관리
- **검색/필터 테스트**: URL 상태, 디바운스, 결과 렌더링
- **접근성 테스트**: axe-core 통합 테스트

### 테스트 유틸리티 검증 테스트

```typescript
// tests/utils/render-utils.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { renderWithProviders, createMockQueryClient } from '../test-utils';

describe('Integration Test Utilities', () => {
  describe('renderWithProviders', () => {
    it('wraps component with all required providers', () => {
      const TestComponent = () => <div data-testid="test">Test</div>;
      const { getByTestId } = renderWithProviders(<TestComponent />);

      expect(getByTestId('test')).toBeInTheDocument();
    });

    it('provides custom QueryClient when specified', () => {
      const customClient = createMockQueryClient();
      const TestComponent = () => <div>Test</div>;

      const { unmount } = renderWithProviders(<TestComponent />, {
        queryClient: customClient,
      });

      // 정리 시 QueryClient도 정리됨
      unmount();
      expect(customClient.isFetching()).toBe(0);
    });
  });

  describe('MSW Integration', () => {
    it('mocks API calls correctly', async () => {
      // MSW 핸들러가 올바르게 설정되었는지 검증
      const response = await fetch('/api/posts');
      expect(response.ok).toBe(true);
    });
  });
});
```

---

## 안티패턴

### 1. 불완전한 Provider Wrapper

```tsx
// ❌ Bad: Provider 누락
const { container } = render(<PostForm />);  // QueryClient 없음!

// ✅ Good: 모든 필요한 Provider 포함
function AllProviders({ children }: { children: React.ReactNode }) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class">
        {children}
      </ThemeProvider>
    </QueryClientProvider>
  );
}

const { container } = render(<PostForm />, { wrapper: AllProviders });
```

### 2. 타이밍 의존 테스트

```typescript
// ❌ Bad: 고정 시간 대기
await new Promise((resolve) => setTimeout(resolve, 1000));
expect(screen.getByText('Data')).toBeInTheDocument();

// ✅ Good: 조건 기반 대기
await waitFor(() => {
  expect(screen.getByText('Data')).toBeInTheDocument();
});
```

### 3. 테스트 ID 남용

```tsx
// ❌ Bad: 모든 곳에 data-testid
<div data-testid="container">
  <button data-testid="submit-button">Submit</button>
</div>

// ✅ Good: 접근성 기반 쿼리 우선
<form aria-label="Create Post">
  <button type="submit">Submit</button>
</form>

// 테스트
screen.getByRole('form', { name: /create post/i });
screen.getByRole('button', { name: /submit/i });
```

### 4. MSW Handler 중복

```typescript
// ❌ Bad: 각 테스트에서 handler 반복
it('test 1', () => {
  server.use(http.get('/api/posts', () => HttpResponse.json(mockData)));
  // ...
});

it('test 2', () => {
  server.use(http.get('/api/posts', () => HttpResponse.json(mockData)));  // 중복!
  // ...
});

// ✅ Good: 기본 handler 정의 + 필요시 override
// handlers.ts에 기본 handler 정의
export const handlers = [
  http.get('/api/posts', () => HttpResponse.json(defaultMockData)),
];

// 테스트에서 필요시만 override
it('should show empty state', () => {
  server.use(http.get('/api/posts', () => HttpResponse.json({ data: [] })));
  // ...
});
```

---

## 에러 처리

### 컴포넌트 에러 테스트

```typescript
describe('Error States', () => {
  it('should show error message on API failure', async () => {
    server.use(
      http.get('/api/posts', () => {
        return HttpResponse.json({ error: 'Server Error' }, { status: 500 });
      })
    );

    render(<PostList />);

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(/오류가 발생했습니다/i);
    });
  });

  it('should allow retry on error', async () => {
    let callCount = 0;
    server.use(
      http.get('/api/posts', () => {
        callCount++;
        if (callCount === 1) {
          return HttpResponse.json({ error: 'Error' }, { status: 500 });
        }
        return HttpResponse.json({ data: mockPosts });
      })
    );

    render(<PostList />);

    // 에러 상태 대기
    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    // 재시도 버튼 클릭
    await userEvent.click(screen.getByRole('button', { name: /다시 시도/i }));

    // 성공 상태 확인
    await waitFor(() => {
      expect(screen.getByText(mockPosts[0].title)).toBeInTheDocument();
    });
  });
});
```

### 폼 검증 에러 테스트

```typescript
describe('Form Validation', () => {
  it('should show field-level errors', async () => {
    const user = userEvent.setup();
    render(<PostForm />);

    // 빈 폼 제출
    await user.click(screen.getByRole('button', { name: /저장/i }));

    // 필드별 에러 메시지 확인
    expect(await screen.findByText(/제목을 입력하세요/i)).toBeInTheDocument();
    expect(await screen.findByText(/내용을 입력하세요/i)).toBeInTheDocument();
  });

  it('should clear errors on valid input', async () => {
    const user = userEvent.setup();
    render(<PostForm />);

    await user.click(screen.getByRole('button', { name: /저장/i }));
    expect(await screen.findByText(/제목을 입력하세요/i)).toBeInTheDocument();

    // 유효한 값 입력
    await user.type(screen.getByLabelText(/제목/i), 'Valid Title');

    // 에러 사라짐
    expect(screen.queryByText(/제목을 입력하세요/i)).not.toBeInTheDocument();
  });
});
```

---

## 성능 고려사항

### MSW 서버 설정 최적화

```typescript
// vitest.setup.ts
import { server } from './test/mocks/server';

// 모든 테스트 전 한 번만 서버 시작
beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }));

// 각 테스트 후 handler 리셋
afterEach(() => server.resetHandlers());

// 모든 테스트 후 서버 종료
afterAll(() => server.close());
```

### userEvent 최적화

```typescript
// userEvent는 setup() 후 재사용
describe('Form', () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
  });

  it('test 1', async () => {
    await user.type(input, 'text');
  });

  it('test 2', async () => {
    await user.click(button);
  });
});
```

### 컴포넌트 렌더링 최소화

```typescript
// ❌ Bad: 매 assert마다 렌더링
expect(render(<Button />).container).toHaveTextContent('Click');
expect(render(<Button />).container).toHaveClass('btn');

// ✅ Good: 한 번 렌더링 후 여러 assert
const { container } = render(<Button />);
expect(container).toHaveTextContent('Click');
expect(container).toHaveClass('btn');
```

---

## 보안 고려사항

### XSS 테스트

```typescript
describe('XSS Prevention', () => {
  it('should sanitize user input', async () => {
    const maliciousScript = '<script>alert("xss")</script>';

    server.use(
      http.get('/api/posts', () => {
        return HttpResponse.json({
          data: [{ id: '1', title: maliciousScript, content: 'Test' }],
        });
      })
    );

    render(<PostList />);

    await waitFor(() => {
      // 스크립트가 실행되지 않고 이스케이프되어 표시
      expect(screen.queryByText(maliciousScript)).not.toBeInTheDocument();
      // 또는 안전하게 렌더링
      expect(document.querySelector('script')).toBeNull();
    });
  });
});
```

### 인증 상태 테스트

```typescript
describe('Protected Components', () => {
  it('should redirect unauthenticated users', async () => {
    vi.mocked(auth).mockResolvedValue(null);

    render(<ProtectedPage />);

    await waitFor(() => {
      expect(mockRouter.push).toHaveBeenCalledWith('/login');
    });
  });

  it('should show content for authenticated users', async () => {
    vi.mocked(auth).mockResolvedValue({ user: { id: '1', name: 'Test' } });

    render(<ProtectedPage />);

    await waitFor(() => {
      expect(screen.getByText(/welcome/i)).toBeInTheDocument();
    });
  });
});
```

---

## References

- `_references/TEST-PATTERN.md`
- `_references/COMPONENT-PATTERN.md`

