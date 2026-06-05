---
name: api-client
description: |
  TanStack Query를 사용하여 데이터 fetching 및 캐싱을 설정합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# API Client Skill

TanStack Query를 사용하여 데이터 fetching 및 캐싱을 설정합니다.

## Triggers

- "api 클라이언트", "tanstack query", "react query", "데이터 페칭"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | Next.js 프로젝트 경로 |

---

## 설치

```bash
npm install @tanstack/react-query @tanstack/react-query-devtools
```

---

## Provider 설정

```tsx
// app/providers.tsx
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState } from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,       // 1분
            gcTime: 5 * 60 * 1000,      // 5분
            retry: 1,
            refetchOnWindowFocus: false,
          },
          mutations: {
            retry: 0,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

```tsx
// app/layout.tsx
import { Providers } from './providers';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

---

## Query Key Factory

```typescript
// features/{feature}/hooks/{feature}-keys.ts
export const {feature}Keys = {
  all: ['{feature}s'] as const,
  lists: () => [...{feature}Keys.all, 'list'] as const,
  list: (filters: Record<string, unknown>) => [...{feature}Keys.lists(), filters] as const,
  details: () => [...{feature}Keys.all, 'detail'] as const,
  detail: (id: string) => [...{feature}Keys.details(), id] as const,
};
```

---

## Query Hook 패턴

```typescript
// features/{feature}/hooks/use-{feature}.ts
'use client';

import { useQuery, useSuspenseQuery } from '@tanstack/react-query';
import { {feature}Keys } from './{feature}-keys';
import { {feature}sService } from '../api/{feature}.service';

// 기본 Query
export function use{Feature}s() {
  return useQuery({
    queryKey: {feature}Keys.lists(),
    queryFn: () => {feature}sService.get{Feature}s(),
  });
}

// Suspense Query
export function use{Feature}sSuspense() {
  return useSuspenseQuery({
    queryKey: {feature}Keys.lists(),
    queryFn: () => {feature}sService.get{Feature}s(),
  });
}

// 단일 아이템
export function use{Feature}(id: string) {
  return useQuery({
    queryKey: {feature}Keys.detail(id),
    queryFn: () => {feature}sService.get{Feature}(id),
    enabled: !!id,
  });
}

// 필터링
export function useFiltered{Feature}s(filters: {Feature}Filter) {
  return useQuery({
    queryKey: {feature}Keys.list(filters),
    queryFn: () => {feature}sService.get{Feature}s(filters),
  });
}
```

---

## Mutation Hook 패턴

```typescript
// features/{feature}/hooks/use-{feature}-mutations.ts
'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { {feature}Keys } from './{feature}-keys';
import { create{Feature}Action, update{Feature}Action, delete{Feature}Action } from '../actions';
import { toast } from 'sonner';

export function useCreate{Feature}() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: create{Feature}Action,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: {feature}Keys.lists() });
      toast.success('생성되었습니다');
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });
}

export function useUpdate{Feature}() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: update{Feature}Action,
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: {feature}Keys.detail(id) });

      // 타입 안전한 이전 데이터 저장
      const previous = queryClient.getQueryData<{Feature}>({feature}Keys.detail(id));

      // Optimistic Update - 타입 안전하게 업데이트
      if (previous) {
        queryClient.setQueryData<{Feature}>({feature}Keys.detail(id), {
          ...previous,
          ...data,
        });
      }

      return { previous };
    },
    onError: (err, { id }, context) => {
      // 에러 시 이전 데이터로 롤백
      if (context?.previous) {
        queryClient.setQueryData({feature}Keys.detail(id), context.previous);
      }
      toast.error(err instanceof Error ? err.message : '업데이트에 실패했습니다');
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: {feature}Keys.detail(id) });
      queryClient.invalidateQueries({ queryKey: {feature}Keys.lists() });
      toast.success('업데이트되었습니다');
    },
  });
}

export function useDelete{Feature}() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: delete{Feature}Action,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: {feature}Keys.lists() });
      toast.success('삭제되었습니다');
    },
    onError: () => {
      toast.error('삭제에 실패했습니다');
    },
  });
}
```

---

## Infinite Query

```typescript
// features/posts/hooks/use-infinite-posts.ts
'use client';

import { useInfiniteQuery } from '@tanstack/react-query';

export function useInfinitePosts() {
  return useInfiniteQuery({
    queryKey: ['posts', 'infinite'],
    queryFn: async ({ pageParam }) => {
      const res = await fetch(`/api/posts?cursor=${pageParam ?? ''}`);
      return res.json();
    },
    initialPageParam: null as string | null,
    getNextPageParam: (lastPage) => lastPage.nextCursor,
  });
}
```

---

## 테스트 예제

### Query Hook 테스트

```typescript
// features/posts/__tests__/use-posts.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { usePosts, usePost } from '../hooks/use-posts';
import { postsService } from '../api/posts.service';

vi.mock('../api/posts.service');

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('usePosts', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('fetches posts successfully', async () => {
    const mockPosts = { data: [{ id: '1', title: 'Test' }] };
    vi.mocked(postsService.getPosts).mockResolvedValue(mockPosts);

    const { result } = renderHook(() => usePosts(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockPosts);
    expect(postsService.getPosts).toHaveBeenCalledTimes(1);
  });

  it('handles error state', async () => {
    vi.mocked(postsService.getPosts).mockRejectedValue(new Error('Network error'));

    const { result } = renderHook(() => usePosts(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error?.message).toBe('Network error');
  });
});

describe('usePost', () => {
  it('fetches single post', async () => {
    const mockPost = { id: '1', title: 'Test Post' };
    vi.mocked(postsService.getPost).mockResolvedValue(mockPost);

    const { result } = renderHook(() => usePost('1'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockPost);
  });

  it('does not fetch when id is empty', () => {
    const { result } = renderHook(() => usePost(''), {
      wrapper: createWrapper(),
    });

    expect(result.current.fetchStatus).toBe('idle');
    expect(postsService.getPost).not.toHaveBeenCalled();
  });
});
```

### Mutation Hook 테스트

```typescript
// features/posts/__tests__/use-post-mutations.test.ts
import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { useCreatePost, useUpdatePost } from '../hooks/use-post-mutations';
import { createPostAction, updatePostAction } from '../actions';

vi.mock('../actions');
vi.mock('sonner', () => ({ toast: { success: vi.fn(), error: vi.fn() } }));

describe('useCreatePost', () => {
  it('creates post and invalidates cache', async () => {
    vi.mocked(createPostAction).mockResolvedValue({ success: true, data: { id: '1' } });

    const { result } = renderHook(() => useCreatePost(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      result.current.mutate({ title: 'New Post' });
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});
```

---

## 안티패턴 (❌ Bad → ✅ Good)

### 1. Query Key 하드코딩

```typescript
// ❌ Bad: 매번 다른 키 형식
useQuery({ queryKey: ['posts'], queryFn: ... });
useQuery({ queryKey: ['postsList'], queryFn: ... });
useQuery({ queryKey: ['post', id], queryFn: ... });

// ✅ Good: Query Key Factory 사용
const postsKeys = {
  all: ['posts'] as const,
  lists: () => [...postsKeys.all, 'list'] as const,
  detail: (id: string) => [...postsKeys.all, 'detail', id] as const,
};

useQuery({ queryKey: postsKeys.lists(), queryFn: ... });
useQuery({ queryKey: postsKeys.detail(id), queryFn: ... });
```

### 2. 매번 새로운 QueryClient 생성

```tsx
// ❌ Bad: 리렌더링마다 새 클라이언트
export function Providers({ children }) {
  const queryClient = new QueryClient();  // 매번 새로 생성!
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

// ✅ Good: useState로 한 번만 생성
export function Providers({ children }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: { queries: { staleTime: 60 * 1000 } },
  }));
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
```

### 3. Optimistic Update 없이 UX 저하

```typescript
// ❌ Bad: 서버 응답까지 UI 변경 없음
useMutation({
  mutationFn: updatePost,
  onSuccess: () => queryClient.invalidateQueries({ queryKey: postsKeys.all }),
});

// ✅ Good: Optimistic Update로 즉각 반영
useMutation({
  mutationFn: updatePost,
  onMutate: async (newData) => {
    await queryClient.cancelQueries({ queryKey: postsKeys.detail(id) });
    const previous = queryClient.getQueryData(postsKeys.detail(id));
    queryClient.setQueryData(postsKeys.detail(id), { ...previous, ...newData });
    return { previous };
  },
  onError: (err, _, context) => {
    queryClient.setQueryData(postsKeys.detail(id), context?.previous);
  },
  onSettled: () => queryClient.invalidateQueries({ queryKey: postsKeys.detail(id) }),
});
```

### 4. 불필요한 refetch

```typescript
// ❌ Bad: 윈도우 포커스마다 refetch (불필요한 API 호출)
useQuery({
  queryKey: ['static-data'],
  queryFn: fetchStaticData,
  // refetchOnWindowFocus: true (기본값)
});

// ✅ Good: 정적 데이터는 refetch 비활성화
useQuery({
  queryKey: ['static-data'],
  queryFn: fetchStaticData,
  staleTime: Infinity,
  refetchOnWindowFocus: false,
});
```

---

## 에러 처리

### 전역 에러 핸들러

```typescript
// app/providers.tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error) => {
        // 인증 에러는 재시도 안 함
        if (error instanceof AuthError) return false;
        return failureCount < 3;
      },
    },
    mutations: {
      onError: (error) => {
        if (error instanceof AuthError) {
          redirect('/login');
        }
        console.error('[Mutation Error]', error);
      },
    },
  },
  queryCache: new QueryCache({
    onError: (error, query) => {
      // 백그라운드 refetch 에러 토스트
      if (query.state.data !== undefined) {
        toast.error(`데이터 갱신 실패: ${error.message}`);
      }
    },
  }),
});
```

---

## 성능 고려사항

### Prefetching

```typescript
// 페이지 진입 전 데이터 프리페치
export function PostList() {
  const queryClient = useQueryClient();

  const prefetchPost = (id: string) => {
    queryClient.prefetchQuery({
      queryKey: postsKeys.detail(id),
      queryFn: () => postsService.getPost(id),
      staleTime: 60 * 1000,
    });
  };

  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id} onMouseEnter={() => prefetchPost(post.id)}>
          <Link href={`/posts/${post.id}`}>{post.title}</Link>
        </li>
      ))}
    </ul>
  );
}
```

### Select로 필요한 데이터만

```typescript
// 전체 데이터 중 필요한 필드만 선택
const { data: postTitles } = useQuery({
  queryKey: postsKeys.lists(),
  queryFn: postsService.getPosts,
  select: (data) => data.map((post) => ({ id: post.id, title: post.title })),
});
```

---

## 보안 고려사항

### 민감 데이터 캐싱 주의

```typescript
// 민감한 사용자 정보는 짧은 staleTime
useQuery({
  queryKey: ['user', 'profile'],
  queryFn: fetchUserProfile,
  staleTime: 30 * 1000,  // 30초
  gcTime: 60 * 1000,     // 1분 후 캐시 삭제
});

// 로그아웃 시 캐시 클리어
const handleLogout = () => {
  queryClient.clear();  // 모든 캐시 삭제
  router.push('/login');
};
```

---

## References

- `_references/STATE-PATTERN.md` - TanStack Query + Zustand 패턴
- `_references/TEST-PATTERN.md` - 테스트 피라미드
