---
name: routing
description: |
  Next.js App Router 기반 라우팅을 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Routing Skill

Next.js App Router 기반 라우팅을 구현합니다.

## Triggers

- "라우팅", "routing", "app router", "네비게이션"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `routes` | ✅ | 라우트 구조 |
| `layouts` | ❌ | 레이아웃 정의 |

---

## 디렉토리 구조

```
app/
├── (auth)/
│   ├── login/
│   │   └── page.tsx
│   ├── register/
│   │   └── page.tsx
│   └── layout.tsx           # Auth 전용 레이아웃
├── (dashboard)/
│   ├── dashboard/
│   │   └── page.tsx
│   ├── settings/
│   │   ├── page.tsx
│   │   ├── profile/
│   │   │   └── page.tsx
│   │   └── security/
│   │       └── page.tsx
│   └── layout.tsx           # Dashboard 레이아웃 (Sidebar)
├── (marketing)/
│   ├── page.tsx             # 홈
│   ├── about/
│   │   └── page.tsx
│   ├── pricing/
│   │   └── page.tsx
│   └── layout.tsx           # Marketing 레이아웃
├── api/
│   └── [...slug]/
│       └── route.ts
├── layout.tsx               # Root 레이아웃
├── not-found.tsx
└── error.tsx
```

---

## Layout 패턴

### Root Layout

```tsx
// app/layout.tsx
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { Providers } from './providers';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: { default: 'My App', template: '%s | My App' },
  description: 'My awesome application',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

### Dashboard Layout (with Sidebar)

```tsx
// app/(dashboard)/layout.tsx
import { auth } from '@/lib/auth';
import { redirect } from 'next/navigation';
import { Sidebar } from '@/components/layout/sidebar';
import { Header } from '@/components/layout/header';

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const session = await auth();
  if (!session) redirect('/login');

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header user={session.user} />
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  );
}
```

### Auth Layout

```tsx
// app/(auth)/layout.tsx
export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/50">
      <div className="w-full max-w-md">{children}</div>
    </div>
  );
}
```

---

## Page 패턴

### 동적 라우트

```tsx
// app/(dashboard)/posts/[id]/page.tsx
import { notFound } from 'next/navigation';
import { getPost } from '@/features/posts/api/posts.service';

interface PageProps {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: PageProps) {
  const { id } = await params;
  const post = await getPost(id);
  if (!post) return { title: 'Not Found' };
  return { title: post.title };
}

export default async function PostPage({ params }: PageProps) {
  const { id } = await params;
  const post = await getPost(id);
  if (!post) notFound();

  return (
    <article>
      <h1>{post.title}</h1>
      <p>{post.content}</p>
    </article>
  );
}
```

### 검색 파라미터

```tsx
// app/(dashboard)/posts/page.tsx
import { PostList } from '@/features/posts/components/post-list';
import { SearchInput } from '@/components/ui/search-input';
import { StatusFilter } from '@/features/posts/components/status-filter';

interface PageProps {
  searchParams: Promise<{ q?: string; status?: string; page?: string }>;
}

export default async function PostsPage({ searchParams }: PageProps) {
  const { q, status, page } = await searchParams;

  return (
    <div className="space-y-6">
      <div className="flex gap-4">
        <SearchInput defaultValue={q} />
        <StatusFilter defaultValue={status} />
      </div>
      <PostList search={q} status={status} page={Number(page) || 1} />
    </div>
  );
}
```

---

## Navigation

### Link 컴포넌트

```tsx
// components/layout/nav-link.tsx
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

interface NavLinkProps {
  href: string;
  children: React.ReactNode;
  exact?: boolean;
}

export function NavLink({ href, children, exact = false }: NavLinkProps) {
  const pathname = usePathname();
  const isActive = exact ? pathname === href : pathname.startsWith(href);

  return (
    <Link
      href={href}
      className={cn(
        'flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors',
        isActive
          ? 'bg-primary text-primary-foreground'
          : 'text-muted-foreground hover:bg-muted hover:text-foreground'
      )}
    >
      {children}
    </Link>
  );
}
```

### Programmatic Navigation

```tsx
'use client';

import { useRouter } from 'next/navigation';

export function NavigationExample() {
  const router = useRouter();

  const handleClick = () => {
    router.push('/dashboard');
    // router.replace('/dashboard');  // 히스토리 교체
    // router.back();                  // 뒤로가기
    // router.refresh();               // 현재 페이지 새로고침
  };

  return <button onClick={handleClick}>이동</button>;
}
```

---

## URL State (nuqs)

```bash
npm install nuqs
```

```tsx
// app/providers.tsx
import { NuqsAdapter } from 'nuqs/adapters/next/app';

export function Providers({ children }: { children: React.ReactNode }) {
  return <NuqsAdapter>{children}</NuqsAdapter>;
}
```

```tsx
// features/posts/hooks/use-post-filters.ts
'use client';

import { parseAsString, parseAsInteger, useQueryStates } from 'nuqs';

export function usePostFilters() {
  return useQueryStates({
    q: parseAsString.withDefault(''),
    status: parseAsString.withDefault(''),
    page: parseAsInteger.withDefault(1),
  });
}
```

```tsx
// features/posts/components/post-filters.tsx
'use client';

import { usePostFilters } from '../hooks/use-post-filters';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export function PostFilters() {
  const [filters, setFilters] = usePostFilters();

  return (
    <div className="flex gap-4">
      <Input
        placeholder="검색..."
        value={filters.q}
        onChange={(e) => setFilters({ q: e.target.value, page: 1 })}
      />
      <Select value={filters.status} onValueChange={(v) => setFilters({ status: v, page: 1 })}>
        <SelectTrigger className="w-32">
          <SelectValue placeholder="상태" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="">전체</SelectItem>
          <SelectItem value="draft">초안</SelectItem>
          <SelectItem value="published">발행</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}
```

---

## Parallel Routes

```
app/
├── @modal/
│   ├── default.tsx
│   └── (.)posts/[id]/
│       └── page.tsx         # Intercepted route (Modal)
├── layout.tsx
└── page.tsx
```

```tsx
// app/layout.tsx
export default function Layout({
  children,
  modal,
}: {
  children: React.ReactNode;
  modal: React.ReactNode;
}) {
  return (
    <>
      {children}
      {modal}
    </>
  );
}
```

```tsx
// app/@modal/default.tsx
export default function Default() {
  return null;
}
```

```tsx
// app/@modal/(.)posts/[id]/page.tsx
import { Modal } from '@/components/ui/modal';
import { getPost } from '@/features/posts/api/posts.service';

export default async function PostModal({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const post = await getPost(id);

  return (
    <Modal>
      <h2>{post.title}</h2>
      <p>{post.content}</p>
    </Modal>
  );
}
```

---

## 테스트 예제

### 동적 라우트 테스트

```typescript
// app/(dashboard)/posts/[id]/__tests__/page.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import PostPage from '../page';
import { getPost } from '@/features/posts/api/posts.service';

vi.mock('@/features/posts/api/posts.service');
vi.mock('next/navigation', () => ({
  notFound: vi.fn(),
}));

describe('PostPage', () => {
  it('renders post content', async () => {
    vi.mocked(getPost).mockResolvedValue({
      id: '1',
      title: 'Test Post',
      content: 'Post content here',
    });

    const page = await PostPage({ params: Promise.resolve({ id: '1' }) });
    render(page);

    expect(screen.getByText('Test Post')).toBeInTheDocument();
    expect(screen.getByText('Post content here')).toBeInTheDocument();
  });

  it('calls notFound for non-existent post', async () => {
    const { notFound } = await import('next/navigation');
    vi.mocked(getPost).mockResolvedValue(null);

    await PostPage({ params: Promise.resolve({ id: 'invalid' }) });

    expect(notFound).toHaveBeenCalled();
  });
});
```

### Navigation 컴포넌트 테스트

```tsx
// components/__tests__/nav-link.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { NavLink } from '../nav-link';

vi.mock('next/navigation', () => ({
  usePathname: vi.fn(),
}));

describe('NavLink', () => {
  it('applies active styles when path matches', () => {
    const { usePathname } = require('next/navigation');
    usePathname.mockReturnValue('/dashboard');

    render(<NavLink href="/dashboard">Dashboard</NavLink>);

    expect(screen.getByRole('link')).toHaveClass('bg-primary');
  });

  it('applies inactive styles when path does not match', () => {
    const { usePathname } = require('next/navigation');
    usePathname.mockReturnValue('/settings');

    render(<NavLink href="/dashboard">Dashboard</NavLink>);

    expect(screen.getByRole('link')).toHaveClass('text-muted-foreground');
  });

  it('matches prefix with exact=false', () => {
    const { usePathname } = require('next/navigation');
    usePathname.mockReturnValue('/dashboard/settings');

    render(<NavLink href="/dashboard">Dashboard</NavLink>);

    expect(screen.getByRole('link')).toHaveClass('bg-primary');
  });
});
```

### URL State (nuqs) 테스트

```tsx
// features/posts/__tests__/post-filters.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PostFilters } from '../components/post-filters';
import { NuqsAdapter } from 'nuqs/adapters/next/app';

vi.mock('nuqs', () => ({
  parseAsString: {
    withDefault: (v: string) => ({ defaultValue: v }),
  },
  parseAsInteger: {
    withDefault: (v: number) => ({ defaultValue: v }),
  },
  useQueryStates: vi.fn(() => [
    { q: '', status: '', page: 1 },
    vi.fn(),
  ]),
}));

describe('PostFilters', () => {
  it('renders search input', () => {
    render(
      <NuqsAdapter>
        <PostFilters />
      </NuqsAdapter>
    );

    expect(screen.getByPlaceholderText('검색...')).toBeInTheDocument();
  });

  it('updates URL on search input', async () => {
    const setFilters = vi.fn();
    const { useQueryStates } = require('nuqs');
    useQueryStates.mockReturnValue([{ q: '', status: '', page: 1 }, setFilters]);

    const user = userEvent.setup();
    render(
      <NuqsAdapter>
        <PostFilters />
      </NuqsAdapter>
    );

    await user.type(screen.getByPlaceholderText('검색...'), 'test');

    expect(setFilters).toHaveBeenCalled();
  });
});
```

---

## 안티패턴 (❌ Bad → ✅ Good)

### 1. 하드코딩된 경로

```tsx
// ❌ Bad: 경로 문자열 하드코딩
<Link href="/dashboard/settings/profile">프로필</Link>
router.push('/dashboard/settings/profile');

// ✅ Good: 경로 상수화
// lib/routes.ts
export const routes = {
  home: '/',
  dashboard: '/dashboard',
  settings: {
    root: '/dashboard/settings',
    profile: '/dashboard/settings/profile',
    security: '/dashboard/settings/security',
  },
  post: (id: string) => `/posts/${id}`,
} as const;

// 사용
<Link href={routes.settings.profile}>프로필</Link>
router.push(routes.post('123'));
```

### 2. 불필요한 클라이언트 라우팅

```tsx
// ❌ Bad: 간단한 링크에 useRouter 사용
'use client';
function Nav() {
  const router = useRouter();
  return <button onClick={() => router.push('/about')}>About</button>;
}

// ✅ Good: Link 컴포넌트 사용 (프리페치 지원)
function Nav() {
  return <Link href="/about">About</Link>;
}
```

### 3. Layout에서 params 재조회

```tsx
// ❌ Bad: Layout에서 params 다시 조회
// app/(dashboard)/posts/[id]/layout.tsx
export default async function Layout({ children }) {
  const params = useParams();  // 클라이언트 훅!
  const post = await getPost(params.id);
  return <div><PostHeader post={post} />{children}</div>;
}

// ✅ Good: params를 props로 전달
export default async function Layout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const post = await getPost(id);
  return <div><PostHeader post={post} />{children}</div>;
}
```

### 4. 검색 파라미터 직접 파싱

```tsx
// ❌ Bad: URLSearchParams 직접 사용
'use client';
function Filters() {
  const searchParams = useSearchParams();
  const page = parseInt(searchParams.get('page') || '1', 10);  // 타입 안전하지 않음
}

// ✅ Good: nuqs 사용
'use client';
import { parseAsInteger, useQueryState } from 'nuqs';

function Filters() {
  const [page, setPage] = useQueryState('page', parseAsInteger.withDefault(1));
  // page: number (타입 안전)
}
```

---

## 에러 처리

### 잘못된 동적 세그먼트 처리

```tsx
// app/(dashboard)/posts/[id]/page.tsx
export default async function PostPage({ params }: PageProps) {
  const { id } = await params;

  // ID 형식 검증
  if (!id || !/^[a-zA-Z0-9-]+$/.test(id)) {
    notFound();
  }

  const post = await getPost(id);
  if (!post) {
    notFound();
  }

  return <PostContent post={post} />;
}
```

### 로케일 검증

```tsx
// app/[locale]/layout.tsx
const validLocales = ['ko', 'en'] as const;

export default async function LocaleLayout({ params, children }: Props) {
  const { locale } = await params;

  if (!validLocales.includes(locale as any)) {
    notFound();
  }

  return (/* layout */);
}
```

---

## 성능 고려사항

### 정적 생성

```tsx
// 동적 라우트 정적 생성
export async function generateStaticParams() {
  const posts = await getAllPostIds();
  return posts.map((post) => ({ id: post.id }));
}

// 재검증 주기 설정
export const revalidate = 3600;  // 1시간
```

### Link 프리페치 제어

```tsx
// 조건부 프리페치
<Link href="/heavy-page" prefetch={false}>
  무거운 페이지
</Link>

// hover 시만 프리페치
<Link href="/page" prefetch={false} onMouseEnter={() => router.prefetch('/page')}>
  Page
</Link>
```

---

## 보안 고려사항

### Redirect 검증

```typescript
// 악의적 리다이렉트 방지
function safeRedirect(url: string, fallback = '/') {
  // 상대 경로만 허용
  if (!url.startsWith('/') || url.startsWith('//')) {
    return fallback;
  }

  // 허용된 경로 목록
  const allowedPaths = ['/dashboard', '/settings', '/profile'];
  if (!allowedPaths.some((path) => url.startsWith(path))) {
    return fallback;
  }

  return url;
}

// 사용
const redirectTo = safeRedirect(searchParams.get('redirect'));
redirect(redirectTo);
```

### 인증 보호 라우트

```tsx
// app/(dashboard)/layout.tsx
import { auth } from '@/lib/auth';
import { redirect } from 'next/navigation';

export default async function DashboardLayout({ children }: Props) {
  const session = await auth();

  if (!session) {
    redirect('/login?callbackUrl=/dashboard');
  }

  return children;
}
```

---

## References

- `_references/ARCHITECTURE-PATTERN.md` - Clean Architecture 가이드
- `_references/TEST-PATTERN.md` - 테스트 피라미드

