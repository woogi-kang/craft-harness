---
name: pagination
description: |
  Offset 및 Cursor 기반 페이지네이션을 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Pagination Skill

Offset 및 Cursor 기반 페이지네이션을 구현합니다.

## Triggers

- "페이지네이션", "pagination", "무한스크롤", "infinite scroll"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `type` | ✅ | offset 또는 cursor |
| `pageSize` | ❌ | 페이지당 항목 수 (기본 20) |

---

## Offset Pagination

### API Route

```typescript
// app/api/posts/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db';
import { posts } from '@/lib/db/schema';
import { count, desc, ilike, sql } from 'drizzle-orm';
import { z } from 'zod';

// 입력 검증 스키마
const paginationSchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
  search: z.string().max(100).default(''),
});

// 검색어 sanitization - SQL LIKE 특수문자 이스케이프
function sanitizeSearchTerm(term: string): string {
  return term.replace(/[%_\\]/g, '\\$&');
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;

  // Zod로 입력값 검증 및 파싱
  const parsed = paginationSchema.safeParse({
    page: searchParams.get('page'),
    limit: searchParams.get('limit'),
    search: searchParams.get('search'),
  });

  if (!parsed.success) {
    return NextResponse.json(
      { error: 'Invalid parameters', details: parsed.error.flatten() },
      { status: 400 }
    );
  }

  const { page, limit, search } = parsed.data;
  const offset = (page - 1) * limit;

  // 검색어 sanitization 후 parameterized query 사용
  const sanitizedSearch = sanitizeSearchTerm(search);
  const whereClause = search
    ? ilike(posts.title, `%${sanitizedSearch}%`)
    : undefined;

  const [data, [{ total }]] = await Promise.all([
    db
      .select()
      .from(posts)
      .where(whereClause)
      .orderBy(desc(posts.createdAt))
      .limit(limit)
      .offset(offset),
    db
      .select({ total: count() })
      .from(posts)
      .where(whereClause),
  ]);

  return NextResponse.json({
    data,
    pagination: {
      page,
      limit,
      total,
      totalPages: Math.ceil(total / limit),
    },
  });
}
```

### Pagination 컴포넌트

```tsx
// components/ui/pagination-controls.tsx
'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';

interface PaginationControlsProps {
  page: number;
  totalPages: number;
  total: number;
}

export function PaginationControls({ page, totalPages, total }: PaginationControlsProps) {
  const router = useRouter();
  const searchParams = useSearchParams();

  const goToPage = (newPage: number) => {
    const params = new URLSearchParams(searchParams);
    params.set('page', String(newPage));
    router.push(`?${params.toString()}`);
  };

  const pages = getVisiblePages(page, totalPages);

  return (
    <div className="flex items-center justify-between">
      <p className="text-sm text-muted-foreground">
        총 {total.toLocaleString()}개
      </p>
      <div className="flex items-center gap-1">
        <Button variant="outline" size="icon" onClick={() => goToPage(1)} disabled={page === 1}>
          <ChevronsLeft className="h-4 w-4" />
        </Button>
        <Button variant="outline" size="icon" onClick={() => goToPage(page - 1)} disabled={page === 1}>
          <ChevronLeft className="h-4 w-4" />
        </Button>

        {pages.map((p, i) =>
          p === '...' ? (
            <span key={`ellipsis-${i}`} className="px-2">...</span>
          ) : (
            <Button
              key={p}
              variant={page === p ? 'default' : 'outline'}
              size="icon"
              onClick={() => goToPage(p as number)}
            >
              {p}
            </Button>
          )
        )}

        <Button variant="outline" size="icon" onClick={() => goToPage(page + 1)} disabled={page === totalPages}>
          <ChevronRight className="h-4 w-4" />
        </Button>
        <Button variant="outline" size="icon" onClick={() => goToPage(totalPages)} disabled={page === totalPages}>
          <ChevronsRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}

function getVisiblePages(current: number, total: number): (number | '...')[] {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);

  if (current <= 3) return [1, 2, 3, 4, '...', total];
  if (current >= total - 2) return [1, '...', total - 3, total - 2, total - 1, total];

  return [1, '...', current - 1, current, current + 1, '...', total];
}
```

---

## Cursor Pagination (무한 스크롤)

### API Route

```typescript
// app/api/posts/infinite/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db';
import { posts } from '@/lib/db/schema';
import { desc, lt, and, ilike, SQL } from 'drizzle-orm';
import { z } from 'zod';

// 입력 검증 스키마
const cursorPaginationSchema = z.object({
  cursor: z.string().datetime().optional(),
  limit: z.coerce.number().int().min(1).max(50).default(20),
  search: z.string().max(100).default(''),
});

// 검색어 sanitization - SQL LIKE 특수문자 이스케이프
function sanitizeSearchTerm(term: string): string {
  return term.replace(/[%_\\]/g, '\\$&');
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;

  // Zod로 입력값 검증 및 파싱
  const parsed = cursorPaginationSchema.safeParse({
    cursor: searchParams.get('cursor') || undefined,
    limit: searchParams.get('limit'),
    search: searchParams.get('search'),
  });

  if (!parsed.success) {
    return NextResponse.json(
      { error: 'Invalid parameters', details: parsed.error.flatten() },
      { status: 400 }
    );
  }

  const { cursor, limit, search } = parsed.data;

  const conditions: SQL[] = [];
  if (cursor) conditions.push(lt(posts.createdAt, new Date(cursor)));
  if (search) {
    const sanitizedSearch = sanitizeSearchTerm(search);
    conditions.push(ilike(posts.title, `%${sanitizedSearch}%`));
  }

  const data = await db
    .select()
    .from(posts)
    .where(conditions.length ? and(...conditions) : undefined)
    .orderBy(desc(posts.createdAt))
    .limit(limit + 1);

  const hasMore = data.length > limit;
  const items = hasMore ? data.slice(0, -1) : data;
  const nextCursor = hasMore ? items[items.length - 1].createdAt.toISOString() : null;

  return NextResponse.json({
    data: items,
    nextCursor,
  });
}
```

### Infinite Query Hook

```typescript
// features/posts/hooks/use-infinite-posts.ts
'use client';

import { useInfiniteQuery } from '@tanstack/react-query';

interface Post {
  id: string;
  title: string;
  createdAt: string;
}

interface InfinitePostsResponse {
  data: Post[];
  nextCursor: string | null;
}

export function useInfinitePosts(search?: string) {
  return useInfiniteQuery({
    queryKey: ['posts', 'infinite', { search }],
    queryFn: async ({ pageParam }) => {
      const params = new URLSearchParams();
      if (pageParam) params.set('cursor', pageParam);
      if (search) params.set('search', search);

      const res = await fetch(`/api/posts/infinite?${params}`);
      if (!res.ok) throw new Error('Failed to fetch posts');
      return res.json() as Promise<InfinitePostsResponse>;
    },
    initialPageParam: null as string | null,
    getNextPageParam: (lastPage) => lastPage.nextCursor,
  });
}
```

### Infinite Scroll 컴포넌트

```tsx
// features/posts/components/infinite-post-list.tsx
'use client';

import { useEffect, useRef } from 'react';
import { useInfinitePosts } from '../hooks/use-infinite-posts';
import { PostCard } from './post-card';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';

interface InfinitePostListProps {
  search?: string;
}

export function InfinitePostList({ search }: InfinitePostListProps) {
  const loadMoreRef = useRef<HTMLDivElement>(null);

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    error,
  } = useInfinitePosts(search);

  // Intersection Observer for auto-loading
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasNextPage && !isFetchingNextPage) {
          fetchNextPage();
        }
      },
      { rootMargin: '100px' }
    );

    if (loadMoreRef.current) {
      observer.observe(loadMoreRef.current);
    }

    return () => observer.disconnect();
  }, [fetchNextPage, hasNextPage, isFetchingNextPage]);

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

  const posts = data?.pages.flatMap((page) => page.data) ?? [];

  if (!posts.length) {
    return <div className="text-muted-foreground">게시글이 없습니다</div>;
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {posts.map((post) => (
          <PostCard key={post.id} post={post} />
        ))}
      </div>

      {/* Load More Trigger */}
      <div ref={loadMoreRef} className="flex justify-center py-4">
        {isFetchingNextPage ? (
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        ) : hasNextPage ? (
          <Button variant="outline" onClick={() => fetchNextPage()}>
            더 보기
          </Button>
        ) : (
          <p className="text-sm text-muted-foreground">모든 게시글을 불러왔습니다</p>
        )}
      </div>
    </div>
  );
}
```

---

## 가상화 (대량 데이터)

```bash
npm install @tanstack/react-virtual
```

```tsx
// features/posts/components/virtualized-list.tsx
'use client';

import { useRef } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import { useInfinitePosts } from '../hooks/use-infinite-posts';
import { PostCard } from './post-card';

export function VirtualizedPostList() {
  const parentRef = useRef<HTMLDivElement>(null);
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfinitePosts();

  const posts = data?.pages.flatMap((page) => page.data) ?? [];

  const virtualizer = useVirtualizer({
    count: hasNextPage ? posts.length + 1 : posts.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 200,
    overscan: 5,
  });

  const items = virtualizer.getVirtualItems();

  // Fetch more when scrolling near the end
  const lastItem = items[items.length - 1];
  if (lastItem && lastItem.index >= posts.length - 1 && hasNextPage && !isFetchingNextPage) {
    fetchNextPage();
  }

  return (
    <div ref={parentRef} className="h-[600px] overflow-auto">
      <div
        style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}
      >
        {items.map((virtualItem) => {
          const post = posts[virtualItem.index];
          return (
            <div
              key={virtualItem.key}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: `${virtualItem.size}px`,
                transform: `translateY(${virtualItem.start}px)`,
              }}
            >
              {post ? <PostCard post={post} /> : <div>Loading...</div>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

---

## 테스트 예제

### Pagination API 테스트

```typescript
// app/api/posts/__tests__/pagination.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { GET } from '../route';
import { NextRequest } from 'next/server';
import { db } from '@/lib/db';

vi.mock('@/lib/db');

describe('GET /api/posts (Pagination)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should return paginated results with default params', async () => {
    const mockData = [{ id: '1', title: 'Post 1' }];
    vi.mocked(db.select).mockReturnValue({
      from: vi.fn().mockReturnValue({
        where: vi.fn().mockReturnValue({
          orderBy: vi.fn().mockReturnValue({
            limit: vi.fn().mockReturnValue({
              offset: vi.fn().mockResolvedValue(mockData),
            }),
          }),
        }),
      }),
    } as any);

    const request = new NextRequest('http://localhost/api/posts');
    const response = await GET(request);
    const json = await response.json();

    expect(json.data).toBeDefined();
    expect(json.pagination).toMatchObject({
      page: 1,
      limit: 20,
    });
  });

  it('should validate page parameter', async () => {
    const request = new NextRequest('http://localhost/api/posts?page=-1');
    const response = await GET(request);

    expect(response.status).toBe(400);
  });

  it('should limit max page size', async () => {
    const request = new NextRequest('http://localhost/api/posts?limit=500');
    const response = await GET(request);
    const json = await response.json();

    // limit이 100으로 제한되어야 함
    expect(json.error || json.pagination.limit <= 100).toBeTruthy();
  });

  it('should sanitize search input', async () => {
    vi.mocked(db.select).mockReturnValue({
      from: vi.fn().mockReturnValue({
        where: vi.fn().mockReturnValue({
          orderBy: vi.fn().mockReturnValue({
            limit: vi.fn().mockReturnValue({
              offset: vi.fn().mockResolvedValue([]),
            }),
          }),
        }),
      }),
    } as any);

    // SQL Injection 시도
    const request = new NextRequest("http://localhost/api/posts?search=%'; DROP TABLE posts; --");
    const response = await GET(request);

    expect(response.status).toBe(200); // 에러 없이 처리됨
  });
});
```

### Infinite Query Hook 테스트

```typescript
// features/posts/hooks/__tests__/use-infinite-posts.test.ts
import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useInfinitePosts } from '../use-infinite-posts';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useInfinitePosts', () => {
  it('should fetch initial page', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        data: [{ id: '1', title: 'Post 1' }],
        nextCursor: '2024-01-01',
      }),
    });

    const { result } = renderHook(() => useInfinitePosts(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data?.pages).toHaveLength(1);
    expect(result.current.hasNextPage).toBe(true);
  });

  it('should fetch next page with cursor', async () => {
    let callCount = 0;
    global.fetch = vi.fn().mockImplementation(() => {
      callCount++;
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          data: [{ id: String(callCount), title: `Post ${callCount}` }],
          nextCursor: callCount < 2 ? '2024-01-02' : null,
        }),
      });
    });

    const { result } = renderHook(() => useInfinitePosts(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    // Fetch next page
    result.current.fetchNextPage();

    await waitFor(() => expect(result.current.data?.pages).toHaveLength(2));
    expect(result.current.hasNextPage).toBe(false);
  });
});
```

---

## 안티패턴 (❌ Bad → ✅ Good)

### 1. Offset 계산 오류

```typescript
// ❌ Bad: 잘못된 offset 계산
const offset = page * limit;  // page 1일 때 limit개 건너뜀!

// ✅ Good: 올바른 offset 계산
const offset = (page - 1) * limit;  // page 1일 때 0부터 시작
```

### 2. N+1 쿼리 문제

```typescript
// ❌ Bad: count를 별도 쿼리로 매번 실행
const data = await db.select().from(posts).limit(limit).offset(offset);
const total = await db.select({ count: count() }).from(posts);

// ✅ Good: Promise.all로 병렬 실행
const [data, [{ total }]] = await Promise.all([
  db.select().from(posts).limit(limit).offset(offset),
  db.select({ total: count() }).from(posts),
]);
```

### 3. 무한 스크롤 메모리 누수

```typescript
// ❌ Bad: Observer cleanup 누락
useEffect(() => {
  const observer = new IntersectionObserver(...);
  observer.observe(ref.current);
  // cleanup 없음!
}, []);

// ✅ Good: 적절한 cleanup
useEffect(() => {
  const observer = new IntersectionObserver(...);
  const current = ref.current;
  if (current) observer.observe(current);
  return () => observer.disconnect();  // cleanup!
}, []);
```

### 4. 검색어 미검증

```typescript
// ❌ Bad: SQL LIKE 특수문자 미처리
const whereClause = ilike(posts.title, `%${search}%`);  // SQL Injection 위험

// ✅ Good: 특수문자 이스케이프
function sanitizeSearchTerm(term: string): string {
  return term.replace(/[%_\\]/g, '\\$&');
}
const sanitized = sanitizeSearchTerm(search);
const whereClause = ilike(posts.title, `%${sanitized}%`);
```

---

## 에러 처리

### 페이지네이션 에러 타입

```typescript
// lib/errors/pagination.ts
export class PaginationError extends Error {
  constructor(
    message: string,
    public code: PaginationErrorCode,
    public statusCode = 400
  ) {
    super(message);
    this.name = 'PaginationError';
  }
}

export type PaginationErrorCode =
  | 'INVALID_PAGE'
  | 'INVALID_LIMIT'
  | 'INVALID_CURSOR'
  | 'PAGE_OUT_OF_RANGE';

export function validatePaginationParams(params: {
  page?: number;
  limit?: number;
  cursor?: string;
}) {
  if (params.page !== undefined && params.page < 1) {
    throw new PaginationError('페이지는 1 이상이어야 합니다', 'INVALID_PAGE');
  }
  if (params.limit !== undefined && (params.limit < 1 || params.limit > 100)) {
    throw new PaginationError('limit은 1-100 사이여야 합니다', 'INVALID_LIMIT');
  }
  if (params.cursor !== undefined && isNaN(Date.parse(params.cursor))) {
    throw new PaginationError('유효하지 않은 cursor입니다', 'INVALID_CURSOR');
  }
}
```

### 클라이언트 에러 핸들링

```tsx
function InfinitePostList() {
  const { data, error, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfinitePosts();

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-destructive">데이터를 불러오는데 실패했습니다</p>
        <Button onClick={() => window.location.reload()} className="mt-4">
          새로고침
        </Button>
      </div>
    );
  }

  // 다음 페이지 로드 실패 시 재시도 버튼
  return (
    <div>
      {/* ... posts ... */}
      {hasNextPage && (
        <Button
          onClick={() => fetchNextPage()}
          disabled={isFetchingNextPage}
        >
          {isFetchingNextPage ? '로딩 중...' : '더 보기'}
        </Button>
      )}
    </div>
  );
}
```

---

## 성능 고려사항

### Keyset/Cursor Pagination 선호

```typescript
// Offset은 대용량에서 느림 (전체 스캔 필요)
// Cursor는 인덱스 활용으로 일정한 성능

// 성능 비교:
// - Offset: O(offset + limit) - 페이지가 깊어질수록 느려짐
// - Cursor: O(limit) - 항상 일정한 성능
```

### 가상화로 DOM 최적화

```tsx
// 수천 개 항목 렌더링 시 가상화 필수
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualizedList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null);
  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    overscan: 5,  // 버퍼 영역
  });

  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
      <div style={{ height: virtualizer.getTotalSize() }}>
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: virtualItem.start,
              height: virtualItem.size,
            }}
          >
            {items[virtualItem.index].title}
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 쿼리 캐싱

```typescript
// TanStack Query의 staleTime 활용
const { data } = useInfiniteQuery({
  queryKey: ['posts', 'infinite'],
  queryFn: fetchPosts,
  staleTime: 5 * 60 * 1000,  // 5분간 fresh
  gcTime: 30 * 60 * 1000,    // 30분간 캐시 유지
  // ...
});
```

---

## 보안 고려사항

### 입력값 검증

```typescript
// Zod로 강력한 입력 검증
const paginationSchema = z.object({
  page: z.coerce.number().int().min(1).max(10000).default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
  search: z.string().max(100).default('').transform((s) => s.trim()),
});
```

### SQL Injection 방지

```typescript
// 1. Parameterized Query 사용 (Drizzle ORM)
const data = await db
  .select()
  .from(posts)
  .where(ilike(posts.title, `%${sanitizedSearch}%`))  // Drizzle이 parameterize
  .limit(limit)
  .offset(offset);

// 2. LIKE 특수문자 이스케이프
function sanitizeSearchTerm(term: string): string {
  return term.replace(/[%_\\]/g, '\\$&');
}
```

### Rate Limiting

```typescript
// 무한 스크롤 남용 방지
import { Ratelimit } from '@upstash/ratelimit';

const ratelimit = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(100, '1 m'),  // 분당 100회
});

export async function GET(request: NextRequest) {
  const ip = request.ip ?? '127.0.0.1';
  const { success } = await ratelimit.limit(`pagination:${ip}`);

  if (!success) {
    return NextResponse.json(
      { error: '요청이 너무 많습니다' },
      { status: 429 }
    );
  }

  // ... pagination logic
}
```

---

## References

- `_references/STATE-PATTERN.md`
- `_references/DATABASE-PATTERN.md`
- `_references/TEST-PATTERN.md`

