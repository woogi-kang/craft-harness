---
name: performance
description: |
  Next.js 애플리케이션 성능을 최적화합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Performance Skill

Extends: `../../_shared/performance/SKILL.md` (공통 성능 최적화 원칙 참조)

Next.js 애플리케이션 성능을 최적화합니다.

> **Reference**: `_references/REACT-PERF-RULES.md` - Vercel 45개 성능 규칙 참조
> **Reference**: `_references/UI-GUIDELINES.md` - UI 성능 가이드라인 참조

## Triggers

- "성능 최적화", "performance", "최적화", "lighthouse"

---

## Impact Level System

코드 생성 및 리뷰 시 다음 우선순위를 적용합니다:

| Level | Symbol | 의미 | 액션 |
|-------|--------|------|------|
| CRITICAL | 🔴 | 2-10x 성능 영향 | 반드시 적용 |
| HIGH | 🟠 | 현저한 성능 개선 | 강력 권고 |
| MEDIUM | 🔵 | 점진적 개선 | 고려 |
| LOW | ⬜ | 마이크로 최적화 | 핫패스만 |

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `target` | ✅ | 최적화 대상 (images, fonts, bundle, api) |
| `metrics` | ❌ | 목표 메트릭 (LCP, FID, CLS) |

---

## 🔴 CRITICAL: Waterfall 제거

### Promise.all로 병렬 실행

```typescript
// ❌ Bad: Sequential awaits (3초 = 1+1+1초)
async function loadData() {
  const user = await fetchUser()
  const posts = await fetchPosts()
  const comments = await fetchComments()
}

// ✅ Good: Parallel execution (1초 = max(1,1,1)초)
async function loadData() {
  const [user, posts, comments] = await Promise.all([
    fetchUser(),
    fetchPosts(),
    fetchComments()
  ])
}
```

### Suspense로 점진적 렌더링

```tsx
// ❌ Bad: 전체 페이지 대기
async function Dashboard() {
  const stats = await getStats()
  const posts = await getPosts()
  return (
    <div>
      <Header />
      <Stats stats={stats} />
      <Posts posts={posts} />
    </div>
  )
}

// ✅ Good: 점진적 스트리밍
function Dashboard() {
  return (
    <div>
      <Header />  {/* 즉시 렌더 */}
      <Suspense fallback={<StatsSkeleton />}>
        <StatsSection />  {/* 준비되면 스트리밍 */}
      </Suspense>
      <Suspense fallback={<PostsSkeleton />}>
        <PostsSection />  {/* 독립적으로 스트리밍 */}
      </Suspense>
    </div>
  )
}
```

---

## 🔴 CRITICAL: Bundle 최적화

### Barrel File 회피

```typescript
// ❌ Bad: Barrel import (~10,000 모듈 로드)
import { Check, X, Menu } from 'lucide-react'

// ✅ Good: Direct imports
import Check from 'lucide-react/dist/esm/icons/check'
import X from 'lucide-react/dist/esm/icons/x'
import Menu from 'lucide-react/dist/esm/icons/menu'

// ✅ Better: optimizePackageImports 설정
// next.config.ts
const nextConfig = {
  experimental: {
    optimizePackageImports: [
      'lucide-react',
      '@radix-ui/react-icons',
      'lodash',
      'date-fns',
    ],
  },
}
```

**Barrel file 영향 라이브러리:**
- `lucide-react`, `@heroicons/react`, `react-icons` - 아이콘
- `@radix-ui/*` - UI 컴포넌트
- `lodash`, `date-fns` - 유틸리티

---

## 이미지 최적화

### next/image 사용

```tsx
// 기본 사용
import Image from 'next/image';

<Image
  src="/hero.jpg"
  alt="Hero"
  width={1200}
  height={600}
  priority // Above the fold 이미지
/>

// Fill 모드
<div className="relative aspect-video">
  <Image
    src={post.image}
    alt={post.title}
    fill
    className="object-cover"
    sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
  />
</div>

// Blur placeholder
<Image
  src={post.image}
  alt={post.title}
  width={400}
  height={300}
  placeholder="blur"
  blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRg..."
/>
```

### next.config.js 설정

```typescript
// next.config.ts
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '*.cloudinary.com',
      },
      {
        protocol: 'https',
        hostname: '*.vercel-storage.com',
      },
    ],
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
};

export default nextConfig;
```

---

## 폰트 최적화

```tsx
// app/layout.tsx
import { Inter, Noto_Sans_KR } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

const notoSansKR = Noto_Sans_KR({
  subsets: ['latin'],
  weight: ['400', '500', '700'],
  display: 'swap',
  variable: '--font-noto-sans-kr',
  preload: true,
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko" className={`${inter.variable} ${notoSansKR.variable}`}>
      <body className="font-sans">{children}</body>
    </html>
  );
}
```

```css
/* globals.css */
:root {
  --font-sans: var(--font-noto-sans-kr), var(--font-inter), ui-sans-serif, system-ui;
}

body {
  font-family: var(--font-sans);
}
```

---

## 🟠 HIGH: 서버 성능

### React.cache()로 요청 내 중복 제거

```typescript
import { cache } from 'react'

// ✅ 같은 요청 내 여러 컴포넌트에서 호출해도 1번만 실행
export const getCurrentUser = cache(async () => {
  const session = await auth()
  if (!session?.user?.id) return null
  return await db.user.findUnique({ where: { id: session.user.id } })
})

// Header.tsx, Sidebar.tsx, Dashboard.tsx에서 각각 호출해도
// DB 쿼리는 1번만 실행됨
```

### RSC 경계에서 데이터 최소화

```tsx
// ❌ Bad: 전체 객체 직렬화
async function Page() {
  const user = await getUser()  // 대용량 객체
  return <ClientComponent user={user} />
}

// ✅ Good: 필요한 필드만 전달
async function Page() {
  const user = await getUser()
  return <ClientComponent name={user.name} avatar={user.avatar} />
}
```

---

## 🟠 HIGH: 렌더링 성능

### content-visibility로 오프스크린 지연

```css
/* 긴 리스트에 적용 - 10x 빠른 초기 렌더 */
.list-item {
  content-visibility: auto;
  contain-intrinsic-size: 0 80px;
}

.page-section {
  content-visibility: auto;
  contain-intrinsic-size: 0 500px;
}
```

```tsx
// 50+ 아이템 리스트에 적용
function MessageList({ messages }) {
  return (
    <div className="overflow-y-auto h-screen">
      {messages.map(msg => (
        <div
          key={msg.id}
          style={{
            contentVisibility: 'auto',
            containIntrinsicSize: '0 80px'
          }}
        >
          <MessageItem message={msg} />
        </div>
      ))}
    </div>
  )
}
```

### 가상화 (50+ 아이템)

```tsx
import { useVirtualizer } from '@tanstack/react-virtual'

function VirtualList({ items }) {
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    overscan: 5,
  })

  return (
    <div ref={parentRef} className="h-[400px] overflow-auto">
      <div style={{ height: virtualizer.getTotalSize(), position: 'relative' }}>
        {virtualizer.getVirtualItems().map(row => (
          <div
            key={items[row.index].id}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              transform: `translateY(${row.start}px)`,
            }}
          >
            <ListItem {...items[row.index]} />
          </div>
        ))}
      </div>
    </div>
  )
}
```

---

## 번들 최적화

### Dynamic Import

```tsx
// 컴포넌트 지연 로딩
import dynamic from 'next/dynamic';

const HeavyChart = dynamic(() => import('@/components/charts/heavy-chart'), {
  loading: () => <Skeleton className="h-[400px]" />,
  ssr: false, // 클라이언트 전용
});

// 조건부 로딩
const AdminPanel = dynamic(() => import('@/features/admin/admin-panel'), {
  loading: () => <LoadingSpinner />,
});

export default function Dashboard({ isAdmin }: { isAdmin: boolean }) {
  return (
    <div>
      <HeavyChart />
      {isAdmin && <AdminPanel />}
    </div>
  );
}
```

### 번들 분석

```bash
npm install -D @next/bundle-analyzer
```

```typescript
// next.config.ts
import bundleAnalyzer from '@next/bundle-analyzer';

const withBundleAnalyzer = bundleAnalyzer({
  enabled: process.env.ANALYZE === 'true',
});

export default withBundleAnalyzer(nextConfig);
```

```bash
ANALYZE=true npm run build
```

---

## React 최적화

### memo, useMemo, useCallback

```tsx
'use client';

import { memo, useMemo, useCallback } from 'react';

// 컴포넌트 메모이제이션
const ExpensiveList = memo(function ExpensiveList({ items }: { items: Item[] }) {
  return (
    <ul>
      {items.map((item) => (
        <li key={item.id}>{item.name}</li>
      ))}
    </ul>
  );
});

// 값 메모이제이션
function Dashboard({ data }: { data: Data[] }) {
  const sortedData = useMemo(
    () => [...data].sort((a, b) => b.value - a.value),
    [data]
  );

  const handleClick = useCallback((id: string) => {
    console.log('Clicked:', id);
  }, []);

  return <ExpensiveList items={sortedData} onClick={handleClick} />;
}
```

### React Compiler (Next.js 16+)

```bash
npm install -D babel-plugin-react-compiler
```

```typescript
// next.config.ts
const nextConfig: NextConfig = {
  reactCompiler: true,
};
```

---

## 데이터 페칭 최적화

### Parallel Data Fetching

```tsx
// app/dashboard/page.tsx
async function Dashboard() {
  // Parallel fetching
  const [stats, posts, users] = await Promise.all([
    getStats(),
    getPosts(),
    getUsers(),
  ]);

  return (
    <div>
      <StatsCards stats={stats} />
      <PostList posts={posts} />
      <UserList users={users} />
    </div>
  );
}
```

### Streaming with Suspense

```tsx
// app/dashboard/page.tsx
import { Suspense } from 'react';

export default function Dashboard() {
  return (
    <div>
      {/* 즉시 렌더링 */}
      <DashboardHeader />

      {/* 병렬 스트리밍 */}
      <div className="grid grid-cols-3 gap-4">
        <Suspense fallback={<StatsSkeleton />}>
          <StatsSection />
        </Suspense>
        <Suspense fallback={<ChartSkeleton />}>
          <ChartSection />
        </Suspense>
        <Suspense fallback={<ActivitySkeleton />}>
          <ActivitySection />
        </Suspense>
      </div>
    </div>
  );
}

// 각 섹션은 독립적으로 데이터 페칭
async function StatsSection() {
  const stats = await getStats();
  return <StatsCards stats={stats} />;
}
```

### Cache Components 전략

Next.js 16에서는 `cacheComponents: true`와 `"use cache"` 지시어를 우선 검토합니다.

```typescript
// next.config.ts
const nextConfig: NextConfig = {
  cacheComponents: true,
};

export default nextConfig;
```

```typescript
// lib/api.ts
import { cacheLife, cacheTag } from 'next/cache';

export async function getStats() {
  'use cache';
  cacheLife('minutes');
  cacheTag('stats');

  return db.query.stats.findMany();
}
```

### unstable_cache 전략

```typescript
// lib/api.ts
import { unstable_cache } from 'next/cache';

/**
 * unstable_cache 주의사항:
 * - Cache Components로 표현하기 어려운 기존 캐시 래핑에 제한적으로 사용
 * - 신규 App Router 코드는 "use cache" + cacheTag/cacheLife를 우선 검토
 */
export const getStats = unstable_cache(
  async () => {
    const stats = await db.query.stats.findMany();
    return stats;
  },
  ['stats'],  // 캐시 키 - 고유해야 함
  {
    revalidate: 60,        // 60초 후 재검증 (Time-based)
    tags: ['stats'],       // 캐시 태그 (On-demand revalidation용)
  }
);

// 수동 재검증 (Server Action 또는 Route Handler에서)
// revalidateTag('stats', 'max'); // stale-while-revalidate
// updateTag('stats');            // Server Action 내 즉시 갱신
// revalidatePath('/dashboard');  // 경로 기반 - 해당 페이지 캐시 무효화
```

### React cache() 대안

```typescript
// lib/api.ts
import { cache } from 'react';

// React cache()는 요청 단위 메모이제이션
// 같은 렌더링 사이클에서 중복 호출 방지
export const getUser = cache(async (id: string) => {
  const user = await db.query.users.findFirst({
    where: eq(users.id, id),
  });
  return user;
});

// 사용: 같은 페이지에서 여러 번 호출해도 1번만 DB 쿼리
// <Header user={await getUser(id)} />
// <Sidebar user={await getUser(id)} />
```

---

## Core Web Vitals 최적화

### LCP (Largest Contentful Paint)

```tsx
// 우선순위 높은 리소스
<Image priority src="/hero.jpg" ... />
<link rel="preload" href="/fonts/custom.woff2" as="font" />

// 중요 CSS 인라인
// _document.tsx or layout.tsx에서 critical CSS 추출
```

### CLS (Cumulative Layout Shift)

```tsx
// 이미지 크기 명시
<Image width={400} height={300} ... />

// Skeleton으로 공간 예약
<Suspense fallback={<Skeleton className="h-[400px] w-full" />}>
  <HeavyComponent />
</Suspense>

// 폰트 display swap
const font = Inter({ display: 'swap' });
```

### INP (Interaction to Next Paint)

```tsx
'use client';

import { useTransition } from 'react';

function SearchForm() {
  const [isPending, startTransition] = useTransition();

  const handleSearch = (query: string) => {
    startTransition(() => {
      // 무거운 상태 업데이트
      setResults(search(query));
    });
  };

  return (
    <div>
      <input onChange={(e) => handleSearch(e.target.value)} />
      {isPending && <Spinner />}
    </div>
  );
}
```

---

## Lighthouse CI

```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI

on: [push]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm run build
      - name: Run Lighthouse CI
        uses: treosh/lighthouse-ci-action@v12
        with:
          urls: |
            http://localhost:3000
            http://localhost:3000/dashboard
          uploadArtifacts: true
          temporaryPublicStorage: true
```

```javascript
// lighthouserc.js
module.exports = {
  ci: {
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.9 }],
        'categories:best-practices': ['error', { minScore: 0.9 }],
        'categories:seo': ['error', { minScore: 0.9 }],
      },
    },
  },
};
```

---

## 테스트 예제

### Core Web Vitals 테스트

```typescript
// e2e/performance/web-vitals.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Core Web Vitals', () => {
  test('homepage should meet LCP threshold', async ({ page }) => {
    await page.goto('/');

    // LCP 측정
    const lcp = await page.evaluate(() => {
      return new Promise<number>((resolve) => {
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          resolve(lastEntry.startTime);
        }).observe({ type: 'largest-contentful-paint', buffered: true });
      });
    });

    // LCP < 2.5초 (Good)
    expect(lcp).toBeLessThan(2500);
  });

  test('homepage should meet CLS threshold', async ({ page }) => {
    await page.goto('/');

    // CLS 측정
    const cls = await page.evaluate(() => {
      return new Promise<number>((resolve) => {
        let clsValue = 0;
        new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (!(entry as any).hadRecentInput) {
              clsValue += (entry as any).value;
            }
          }
          resolve(clsValue);
        }).observe({ type: 'layout-shift', buffered: true });

        // 5초 후 결과 반환
        setTimeout(() => resolve(clsValue), 5000);
      });
    });

    // CLS < 0.1 (Good)
    expect(cls).toBeLessThan(0.1);
  });
});
```

### 번들 크기 테스트

```typescript
// scripts/check-bundle-size.ts
import { readFileSync, readdirSync, statSync } from 'fs';
import { join } from 'path';

const MAX_SIZES = {
  'page.js': 150 * 1024,      // 150KB
  'layout.js': 100 * 1024,    // 100KB
  'commons.js': 200 * 1024,   // 200KB
};

function checkBundleSizes() {
  const buildDir = '.next/static/chunks';
  const files = readdirSync(buildDir, { recursive: true });

  const oversized: string[] = [];

  for (const file of files) {
    const filePath = join(buildDir, file as string);
    const stats = statSync(filePath);

    for (const [pattern, maxSize] of Object.entries(MAX_SIZES)) {
      if (file.toString().includes(pattern) && stats.size > maxSize) {
        oversized.push(`${file}: ${(stats.size / 1024).toFixed(2)}KB > ${maxSize / 1024}KB`);
      }
    }
  }

  if (oversized.length > 0) {
    console.error('Bundle size exceeded:');
    oversized.forEach((msg) => console.error(`  - ${msg}`));
    process.exit(1);
  }

  console.log('Bundle sizes OK');
}

checkBundleSizes();
```

---

## 안티패턴 (❌ Bad → ✅ Good)

### 1. 불필요한 클라이언트 컴포넌트

```tsx
// ❌ Bad: 전체를 클라이언트 컴포넌트로
'use client';

export default function Page() {
  const data = useQuery(...);  // 클라이언트에서 fetch
  return <div>{data}</div>;
}

// ✅ Good: 서버 컴포넌트 활용
export default async function Page() {
  const data = await fetchData();  // 서버에서 fetch
  return <ClientInteraction data={data} />;
}
```

### 2. 이미지 최적화 미적용

```tsx
// ❌ Bad: 일반 img 태그
<img src="/large-image.jpg" alt="Large" />

// ✅ Good: next/image 사용
<Image
  src="/large-image.jpg"
  alt="Large"
  width={800}
  height={600}
  sizes="(max-width: 768px) 100vw, 50vw"
  priority={isAboveFold}
/>
```

### 3. 무분별한 Dynamic Import

```tsx
// ❌ Bad: 작은 컴포넌트도 dynamic import
const Button = dynamic(() => import('./Button'));  // 불필요한 네트워크 요청

// ✅ Good: 큰 컴포넌트만 dynamic import
// 작은 컴포넌트는 직접 import
import { Button } from './Button';

// 무거운 컴포넌트만 dynamic
const HeavyChart = dynamic(() => import('./HeavyChart'), {
  loading: () => <Skeleton />,
  ssr: false,
});
```

### 4. 캐싱 미활용

```typescript
// ❌ Bad: 매 요청마다 fetch
async function getData() {
  const res = await fetch('/api/data', { cache: 'no-store' });
  return res.json();
}

// ✅ Good: 적절한 캐싱
async function getData() {
  const res = await fetch('/api/data', {
    next: { revalidate: 60 },  // 60초 캐시
  });
  return res.json();
}
```

---

## 에러 처리

### 성능 모니터링 에러 핸들링

```typescript
// lib/performance/monitor.ts
export function reportWebVitals(metric: {
  id: string;
  name: string;
  value: number;
}) {
  try {
    // Analytics로 전송
    fetch('/api/analytics', {
      method: 'POST',
      body: JSON.stringify(metric),
      keepalive: true,  // 페이지 이탈 후에도 전송
    });
  } catch (error) {
    // 실패해도 사용자 경험에 영향 없음
    console.warn('[Performance] Failed to report metric:', error);
  }
}

// app/layout.tsx
export function reportWebVitals(metric: NextWebVitalsMetric) {
  if (metric.label === 'web-vital') {
    reportWebVitals(metric);
  }
}
```

### 로딩 실패 복구

```tsx
// 이미지 로딩 실패 처리
function OptimizedImage({ src, alt, ...props }) {
  const [error, setError] = useState(false);

  if (error) {
    return (
      <div className="bg-muted flex items-center justify-center" {...props}>
        <span className="text-muted-foreground">이미지를 불러올 수 없습니다</span>
      </div>
    );
  }

  return (
    <Image
      src={src}
      alt={alt}
      onError={() => setError(true)}
      {...props}
    />
  );
}
```

---

## 성능 고려사항

이 스킬의 핵심 성능 최적화 영역을 요약합니다:

### 핵심 메트릭 (Core Web Vitals)

| 메트릭 | 목표 | 최적화 방법 |
|--------|------|-------------|
| **LCP** | < 2.5s | 이미지 최적화, 폰트 프리로드, 서버 컴포넌트 |
| **INP** | < 200ms | React 메모이제이션, 디바운싱, 웹 워커 |
| **CLS** | < 0.1 | 이미지 크기 명시, 폰트 swap, 레이아웃 안정화 |

### 최적화 체크리스트

```typescript
// ✅ 성능 최적화 체크리스트
const performanceChecklist = {
  // 이미지
  images: {
    useNextImage: true,           // next/image 사용
    lazyLoading: true,            // 뷰포트 외 이미지 지연 로드
    webpAvif: true,               // 최신 포맷 자동 변환
    responsiveSizes: true,        // 반응형 sizes 속성
  },

  // 폰트
  fonts: {
    useNextFont: true,            // next/font 사용
    preload: true,                // 크리티컬 폰트 프리로드
    swap: true,                   // font-display: swap
  },

  // 번들
  bundle: {
    dynamicImports: true,         // 동적 임포트
    treeShaking: true,            // 미사용 코드 제거
    packageOptimization: true,    // 패키지 최적화 설정
  },

  // React
  react: {
    memoization: true,            // useMemo, useCallback
    suspense: true,               // Suspense 경계
    serverComponents: true,       // RSC 활용
  },

  // 데이터
  data: {
    caching: true,                // 적절한 캐시 전략
    prefetching: true,            // 데이터 프리페칭
    pagination: true,             // 페이지네이션/무한스크롤
  },
};
```

### 성능 모니터링

```typescript
// lib/performance.ts
export function reportWebVitals(metric: {
  id: string;
  name: string;
  value: number;
}) {
  // Vercel Analytics 또는 커스텀 분석
  console.log(`[Web Vital] ${metric.name}: ${metric.value}`);

  // 임계값 초과 시 경고
  const thresholds = { LCP: 2500, INP: 200, CLS: 0.1 };
  if (metric.value > thresholds[metric.name as keyof typeof thresholds]) {
    console.warn(`⚠️ ${metric.name} exceeds threshold`);
  }
}
```

---

## 보안 고려사항

### 민감 데이터 캐싱 방지

```typescript
// 개인정보가 포함된 데이터는 캐시 X
async function getUserProfile(userId: string) {
  const res = await fetch(`/api/users/${userId}`, {
    cache: 'no-store',  // 캐시 비활성화
    headers: {
      'Cache-Control': 'private, no-cache, no-store',
    },
  });
  return res.json();
}

// 공개 데이터는 캐시 O
async function getPublicPosts() {
  const res = await fetch('/api/posts', {
    next: { revalidate: 300 },  // 5분 캐시
  });
  return res.json();
}
```

### 번들 내 민감 정보 방지

```typescript
// next.config.ts
const nextConfig: NextConfig = {
  // 서버 전용 모듈이 클라이언트 번들에 포함되지 않도록
  serverExternalPackages: ['@prisma/client', 'bcrypt'],

  // 환경 변수 노출 방지
  env: {
    // NEXT_PUBLIC_ 접두사 없는 변수는 서버에서만 사용
  },
};
```

### 성능 데이터 수집 동의

```typescript
// 성능 모니터링 전 사용자 동의 확인
export function initPerformanceMonitoring() {
  // 쿠키 동의 확인
  const consent = getCookieConsent();

  if (consent.analytics) {
    // Web Vitals 수집
    reportWebVitals((metric) => {
      sendToAnalytics(metric);
    });
  }
}
```

---

## Lighthouse CI 확장

```javascript
// lighthouserc.js
module.exports = {
  ci: {
    collect: {
      url: [
        'http://localhost:3000/',
        'http://localhost:3000/dashboard',
        'http://localhost:3000/posts',
      ],
      numberOfRuns: 3,
    },
    assert: {
      preset: 'lighthouse:recommended',
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.95 }],
        'categories:best-practices': ['error', { minScore: 0.9 }],
        'categories:seo': ['error', { minScore: 0.9 }],
        // 개별 메트릭
        'first-contentful-paint': ['error', { maxNumericValue: 1800 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'total-blocking-time': ['error', { maxNumericValue: 300 }],
      },
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
```

---

## Performance Checklist by Impact

### 🔴 CRITICAL (반드시 적용)

- [ ] 독립적인 비동기 작업 → `Promise.all()`
- [ ] 데이터 의존 컴포넌트만 → `<Suspense>`
- [ ] 서버 컴포넌트 형제 구성 → 병렬 fetch
- [ ] Barrel file import → `optimizePackageImports` 또는 직접 import
- [ ] 대용량 컴포넌트 → `dynamic(() => import())`

### 🟠 HIGH (강력 권고)

- [ ] 동일 요청 내 중복 호출 → `React.cache()`
- [ ] 요청 간 캐싱 → `"use cache"` + `cacheTag`/`cacheLife`, 필요시 `unstable_cache()`
- [ ] RSC 경계 → 필요한 데이터만 전달
- [ ] 긴 리스트 → `content-visibility` 또는 가상화
- [ ] hover 시 → 다음 경로/컴포넌트 프리로드

### 🔵 MEDIUM (권고)

- [ ] 비용 높은 계산 → 메모된 별도 컴포넌트
- [ ] 빈번한 UI 업데이트 → `startTransition`
- [ ] 정적 JSX → 컴포넌트 밖 호이스팅
- [ ] 인라인 객체/함수 → `useMemo`/`useCallback`

---

## References

- `_references/REACT-PERF-RULES.md` - **Vercel 45개 성능 규칙**
- `_references/UI-GUIDELINES.md` - **UI 성능/접근성 가이드라인**
- `_references/ARCHITECTURE-PATTERN.md`
- `_references/TEST-PATTERN.md`
