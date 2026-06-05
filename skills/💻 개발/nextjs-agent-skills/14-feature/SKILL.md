---
name: feature
description: |
  Feature 기반 모듈을 생성합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Feature Skill

Feature 기반 모듈을 생성합니다.

## Triggers

- "피처", "feature", "도메인 모듈", "기능 추가"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `featureName` | ✅ | 피처 이름 |
| `entities` | ✅ | 엔티티 목록 |

---

## Feature 디렉토리 구조

```
features/{feature}/
├── api/
│   └── {feature}.service.ts        # API 호출 서비스
├── components/
│   ├── {feature}-list.tsx
│   ├── {feature}-card.tsx
│   ├── {feature}-form.tsx
│   └── {feature}-detail.tsx
├── hooks/
│   ├── use-{feature}s.ts           # Query hooks
│   ├── use-{feature}-mutations.ts  # Mutation hooks
│   └── {feature}-keys.ts           # Query key factory
├── actions/
│   ├── create-{feature}.action.ts
│   ├── update-{feature}.action.ts
│   └── delete-{feature}.action.ts
├── schemas/
│   └── {feature}.schema.ts         # Zod schemas
├── types/
│   └── {feature}.types.ts          # TypeScript types
└── stores/
    └── {feature}.store.ts          # Zustand store (optional)
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

// 사용 예시
// {feature}Keys.all          → ['{feature}s']
// {feature}Keys.lists()      → ['{feature}s', 'list']
// {feature}Keys.list({status:'published'}) → ['{feature}s', 'list', {status: 'published'}]
// {feature}Keys.detail('1')  → ['{feature}s', 'detail', '1']
```

---

## Types 정의

```typescript
// features/{feature}/types/{feature}.types.ts
export interface {Feature} {
  id: string;
  title: string;
  description: string | null;
  status: 'draft' | 'published' | 'archived';
  createdAt: Date;
  updatedAt: Date;
}

export interface {Feature}Filter {
  status?: 'draft' | 'published' | 'archived';
  search?: string;
  page?: number;
  limit?: number;
}

export interface {Feature}ListResponse {
  data: {Feature}[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}
```

---

## Schema 정의

```typescript
// features/{feature}/schemas/{feature}.schema.ts
import { z } from 'zod';

export const {feature}Schema = z.object({
  id: z.string().uuid(),
  title: z.string().min(1).max(200),
  description: z.string().nullable(),
  status: z.enum(['draft', 'published', 'archived']),
  createdAt: z.coerce.date(),
  updatedAt: z.coerce.date(),
});

export const create{Feature}Schema = {feature}Schema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export const update{Feature}Schema = create{Feature}Schema.partial();

export type Create{Feature}Input = z.infer<typeof create{Feature}Schema>;
export type Update{Feature}Input = z.infer<typeof update{Feature}Schema>;
```

---

## API Service

```typescript
// features/{feature}/api/{feature}.service.ts
import type { {Feature}, {Feature}Filter, {Feature}ListResponse, Create{Feature}Input, Update{Feature}Input } from '../types/{feature}.types';

const API_BASE = '/api/{feature}s';

export const {feature}sService = {
  async get{Feature}s(filter?: {Feature}Filter): Promise<{Feature}ListResponse> {
    const params = new URLSearchParams();
    if (filter?.status) params.set('status', filter.status);
    if (filter?.search) params.set('search', filter.search);
    if (filter?.page) params.set('page', String(filter.page));
    if (filter?.limit) params.set('limit', String(filter.limit));

    const res = await fetch(`${API_BASE}?${params}`);
    if (!res.ok) throw new Error('Failed to fetch {feature}s');
    return res.json();
  },

  async get{Feature}(id: string): Promise<{Feature}> {
    const res = await fetch(`${API_BASE}/${id}`);
    if (!res.ok) throw new Error('{Feature} not found');
    return res.json();
  },

  async create{Feature}(data: Create{Feature}Input): Promise<{Feature}> {
    const res = await fetch(API_BASE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create {feature}');
    return res.json();
  },

  async update{Feature}(id: string, data: Update{Feature}Input): Promise<{Feature}> {
    const res = await fetch(`${API_BASE}/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to update {feature}');
    return res.json();
  },

  async delete{Feature}(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete {feature}');
  },
};
```

---

## Query Hooks

```typescript
// features/{feature}/hooks/use-{feature}s.ts
'use client';

import { useQuery, useSuspenseQuery } from '@tanstack/react-query';
import { {feature}Keys } from './{feature}-keys';
import { {feature}sService } from '../api/{feature}.service';
import type { {Feature}Filter } from '../types/{feature}.types';

// 기본 Query
export function use{Feature}s(filter?: {Feature}Filter) {
  return useQuery({
    queryKey: {feature}Keys.list(filter ?? {}),
    queryFn: () => {feature}sService.get{Feature}s(filter),
  });
}

// Suspense Query
export function use{Feature}sSuspense(filter?: {Feature}Filter) {
  return useSuspenseQuery({
    queryKey: {feature}Keys.list(filter ?? {}),
    queryFn: () => {feature}sService.get{Feature}s(filter),
  });
}

// 단일 아이템 Query
export function use{Feature}(id: string) {
  return useQuery({
    queryKey: {feature}Keys.detail(id),
    queryFn: () => {feature}sService.get{Feature}(id),
    enabled: !!id,
  });
}
```

---

## Mutation Hooks (Optimistic Update 포함)

```typescript
// features/{feature}/hooks/use-{feature}-mutations.ts
'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { {feature}Keys } from './{feature}-keys';
import { create{Feature}Action, update{Feature}Action, delete{Feature}Action } from '../actions';
import { toast } from 'sonner';
import type { {Feature} } from '../types/{feature}.types';

// Create Mutation
export function useCreate{Feature}() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: create{Feature}Action,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: {feature}Keys.lists() });
      toast.success('{Feature}가 생성되었습니다');
    },
    onError: (error) => {
      toast.error(error.message || '생성에 실패했습니다');
    },
  });
}

// Update Mutation with Optimistic Update
export function useUpdate{Feature}() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: update{Feature}Action,
    onMutate: async ({ id, data }) => {
      // 진행 중인 쿼리 취소
      await queryClient.cancelQueries({ queryKey: {feature}Keys.detail(id) });

      // 이전 값 스냅샷
      const previous{Feature} = queryClient.getQueryData<{Feature}>({feature}Keys.detail(id));

      // Optimistic update
      if (previous{Feature}) {
        queryClient.setQueryData<{Feature}>({feature}Keys.detail(id), {
          ...previous{Feature},
          ...data,
          updatedAt: new Date(),
        });
      }

      return { previous{Feature} };
    },
    onError: (err, { id }, context) => {
      // 에러 시 롤백
      if (context?.previous{Feature}) {
        queryClient.setQueryData({feature}Keys.detail(id), context.previous{Feature});
      }
      toast.error('업데이트에 실패했습니다');
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: {feature}Keys.detail(id) });
      queryClient.invalidateQueries({ queryKey: {feature}Keys.lists() });
      toast.success('업데이트되었습니다');
    },
  });
}

// Delete Mutation with Optimistic Update
export function useDelete{Feature}() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: delete{Feature}Action,
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: {feature}Keys.lists() });

      const previousList = queryClient.getQueryData<{ data: {Feature}[] }>({feature}Keys.lists());

      // Optimistic update - 목록에서 제거
      if (previousList) {
        queryClient.setQueryData({feature}Keys.lists(), {
          ...previousList,
          data: previousList.data.filter((item) => item.id !== id),
        });
      }

      return { previousList };
    },
    onError: (err, id, context) => {
      if (context?.previousList) {
        queryClient.setQueryData({feature}Keys.lists(), context.previousList);
      }
      toast.error('삭제에 실패했습니다');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: {feature}Keys.lists() });
      toast.success('삭제되었습니다');
    },
  });
}
```

---

## 컴포넌트 템플릿

### List 컴포넌트

```tsx
// features/{feature}/components/{feature}-list.tsx
'use client';

import { use{Feature}s } from '../hooks/use-{feature}s';
import { {Feature}Card } from './{feature}-card';
import { Skeleton } from '@/components/ui/skeleton';

export function {Feature}List() {
  const { data, isLoading, error } = use{Feature}s();

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-48" />
        ))}
      </div>
    );
  }

  if (error) {
    return <div className="text-destructive">오류가 발생했습니다</div>;
  }

  if (!data?.data.length) {
    return <div className="text-muted-foreground">데이터가 없습니다</div>;
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {data.data.map((item) => (
        <{Feature}Card key={item.id} {feature}={item} />
      ))}
    </div>
  );
}
```

### Card 컴포넌트

```tsx
// features/{feature}/components/{feature}-card.tsx
import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { {Feature} } from '../types/{feature}.types';

interface {Feature}CardProps {
  {feature}: {Feature};
}

export function {Feature}Card({ {feature} }: {Feature}CardProps) {
  return (
    <Link href={`/{feature}s/${{{feature}}.id}`}>
      <Card className="hover:shadow-md transition-shadow">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="line-clamp-1">{{feature}.title}</CardTitle>
            <Badge variant={{{feature}}.status === 'published' ? 'default' : 'secondary'}>
              {{feature}.status}
            </Badge>
          </div>
          <CardDescription className="line-clamp-2">
            {{feature}.description}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <time className="text-sm text-muted-foreground">
            {new Date({feature}.createdAt).toLocaleDateString('ko-KR')}
          </time>
        </CardContent>
      </Card>
    </Link>
  );
}
```

---

## 테스트 예제

### Service 레이어 테스트

```typescript
// features/posts/__tests__/posts.service.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { postsService } from '../api/posts.service';

// fetch 모킹
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('PostsService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getPosts', () => {
    it('fetches posts list', async () => {
      const mockResponse = {
        data: [{ id: '1', title: 'Test' }],
        pagination: { page: 1, limit: 20, total: 1 },
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await postsService.getPosts();

      expect(result).toEqual(mockResponse);
      expect(mockFetch).toHaveBeenCalledWith('/api/posts?');
    });

    it('includes filter parameters', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ data: [] }),
      });

      await postsService.getPosts({ status: 'published', page: 2 });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('status=published')
      );
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('page=2')
      );
    });

    it('throws error on fetch failure', async () => {
      mockFetch.mockResolvedValueOnce({ ok: false });

      await expect(postsService.getPosts()).rejects.toThrow('Failed to fetch');
    });
  });

  describe('getPost', () => {
    it('fetches single post by id', async () => {
      const mockPost = { id: '1', title: 'Test Post' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockPost),
      });

      const result = await postsService.getPost('1');

      expect(result).toEqual(mockPost);
      expect(mockFetch).toHaveBeenCalledWith('/api/posts/1');
    });
  });
});
```

### 컴포넌트 통합 테스트

```tsx
// features/posts/__tests__/post-list.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { PostList } from '../components/post-list';
import { postsService } from '../api/posts.service';

vi.mock('../api/posts.service');

const wrapper = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('PostList', () => {
  it('displays loading skeleton', () => {
    vi.mocked(postsService.getPosts).mockImplementation(
      () => new Promise(() => {})  // 무한 pending
    );

    render(<PostList />, { wrapper });

    expect(screen.getAllByTestId('skeleton')).toHaveLength(6);
  });

  it('displays posts when loaded', async () => {
    vi.mocked(postsService.getPosts).mockResolvedValue({
      data: [
        { id: '1', title: 'Post 1', status: 'published' },
        { id: '2', title: 'Post 2', status: 'draft' },
      ],
      pagination: { page: 1, limit: 20, total: 2, totalPages: 1 },
    });

    render(<PostList />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText('Post 1')).toBeInTheDocument();
      expect(screen.getByText('Post 2')).toBeInTheDocument();
    });
  });

  it('displays empty state', async () => {
    vi.mocked(postsService.getPosts).mockResolvedValue({
      data: [],
      pagination: { page: 1, limit: 20, total: 0, totalPages: 0 },
    });

    render(<PostList />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText(/데이터가 없습니다/)).toBeInTheDocument();
    });
  });
});
```

---

## 안티패턴 (❌ Bad → ✅ Good)

### 1. 순환 의존성

```
// ❌ Bad: features 간 직접 import
features/users/
└── hooks/use-users.ts
    import { postsService } from '@/features/posts/api';  // 순환!

// ✅ Good: 공유 타입/인터페이스 사용
lib/types/
└── shared.types.ts  # 공통 타입 정의

features/users/
└── hooks/use-users.ts
    import type { User } from '@/lib/types';  # 공통 타입만 import
```

### 2. 비즈니스 로직 컴포넌트 분산

```tsx
// ❌ Bad: 컴포넌트에 로직 혼재
function PostCard({ post }) {
  const formattedDate = new Date(post.createdAt).toLocaleDateString('ko-KR');
  const isExpired = new Date() > new Date(post.expiresAt);
  const canEdit = post.authorId === currentUser.id || currentUser.role === 'admin';
  // ...
}

// ✅ Good: 로직 분리
// utils/date.ts
export function formatDate(date: Date) { ... }

// domain/post.ts
export function isPostExpired(post: Post) { ... }
export function canEditPost(post: Post, user: User) { ... }

// components/post-card.tsx
function PostCard({ post }) {
  const { user } = useAuth();
  const canEdit = canEditPost(post, user);
  // ...
}
```

### 3. 타입 정의 중복

```typescript
// ❌ Bad: 여러 곳에서 같은 타입 정의
// hooks/use-posts.ts
interface Post { id: string; title: string; }

// components/post-card.tsx
interface Post { id: string; title: string; status: string; }  // 불일치!

// ✅ Good: 단일 진실 공급원
// types/post.types.ts
export interface Post {
  id: string;
  title: string;
  status: 'draft' | 'published' | 'archived';
}

// 모든 곳에서 import
import type { Post } from '../types/post.types';
```

### 4. API 응답 직접 노출

```typescript
// ❌ Bad: API 응답 구조 그대로 노출
const { data } = await fetch('/api/posts');
return data;  // { posts: [...], meta: {...} }

// ✅ Good: 도메인 모델로 변환
async getPosts(filter?: PostFilter): Promise<PostListResponse> {
  const res = await fetch(`${API_BASE}?${params}`);
  const data = await res.json();
  return {
    data: data.posts.map(transformPost),  // 변환
    pagination: {
      page: data.meta.page,
      total: data.meta.total_count,
    },
  };
}
```

---

## 에러 처리

### Service 레이어 에러 처리

```typescript
// features/posts/api/posts.service.ts
import { ApiError, NotFoundError, ValidationError } from '@/lib/errors';

export const postsService = {
  async getPost(id: string): Promise<Post> {
    const res = await fetch(`${API_BASE}/${id}`);

    if (!res.ok) {
      if (res.status === 404) {
        throw new NotFoundError('게시물');
      }
      if (res.status === 400) {
        const data = await res.json();
        throw new ValidationError(data.errors);
      }
      throw new ApiError(`Failed to fetch post: ${res.statusText}`);
    }

    return res.json();
  },
};
```

---

## 성능 고려사항

### 지연 로딩

```typescript
// 컴포넌트 지연 로딩
const PostForm = dynamic(() => import('../components/post-form'), {
  loading: () => <Skeleton className="h-64" />,
});

// 모달에서 사용
{isOpen && <PostForm />}
```

### 데이터 프리페치

```typescript
// 목록에서 상세 데이터 프리페치
function PostListItem({ post }: { post: Post }) {
  const queryClient = useQueryClient();

  return (
    <Link
      href={`/posts/${post.id}`}
      onMouseEnter={() => {
        queryClient.prefetchQuery({
          queryKey: postKeys.detail(post.id),
          queryFn: () => postsService.getPost(post.id),
        });
      }}
    >
      {post.title}
    </Link>
  );
}
```

---

## 보안 고려사항

### API 응답 필터링

```typescript
// 클라이언트에 전달 전 민감 정보 제거
function sanitizePost(post: PostRaw): Post {
  const { internalNotes, ...safe } = post;
  return safe;
}
```

### 권한 검증

```typescript
// 수정/삭제 전 권한 확인
export function useDeletePost() {
  const { user } = useAuth();

  return useMutation({
    mutationFn: async (postId: string) => {
      const post = await postsService.getPost(postId);

      if (post.authorId !== user.id && user.role !== 'admin') {
        throw new Error('권한이 없습니다');
      }

      return deletePostAction(postId);
    },
  });
}
```

---

## References

- `_references/ARCHITECTURE-PATTERN.md` - Clean Architecture 가이드
- `_references/STATE-PATTERN.md` - TanStack Query 패턴
- `_references/TEST-PATTERN.md` - 테스트 피라미드

