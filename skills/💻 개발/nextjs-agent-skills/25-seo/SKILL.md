---
name: seo
description: |
  Next.js 애플리케이션 SEO를 최적화합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# SEO Skill

Next.js 애플리케이션 SEO를 최적화합니다.

## Triggers

- "seo", "메타데이터", "metadata", "sitemap", "검색 최적화"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `type` | ✅ | metadata, sitemap, structured-data |
| `pages` | ❌ | 대상 페이지 |

---

## Metadata API

### Root Metadata

```typescript
// app/layout.tsx
import type { Metadata, Viewport } from 'next';

export const metadata: Metadata = {
  metadataBase: new URL('https://example.com'),
  title: {
    default: 'My App',
    template: '%s | My App',
  },
  description: '나의 멋진 애플리케이션입니다.',
  keywords: ['Next.js', 'React', 'TypeScript'],
  authors: [{ name: 'Your Name' }],
  creator: 'Your Company',
  publisher: 'Your Company',
  openGraph: {
    type: 'website',
    locale: 'ko_KR',
    url: 'https://example.com',
    siteName: 'My App',
    title: 'My App',
    description: '나의 멋진 애플리케이션입니다.',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'My App',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'My App',
    description: '나의 멋진 애플리케이션입니다.',
    images: ['/og-image.png'],
    creator: '@yourhandle',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'google-site-verification-code',
    naver: 'naver-site-verification-code',
  },
};

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#000000' },
  ],
  width: 'device-width',
  initialScale: 1,
};
```

### Dynamic Metadata

```typescript
// app/posts/[id]/page.tsx
import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { getPost } from '@/features/posts/api/posts.service';

interface PageProps {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { id } = await params;
  const post = await getPost(id);

  if (!post) {
    return { title: 'Not Found' };
  }

  return {
    title: post.title,
    description: post.excerpt || post.content.slice(0, 160),
    openGraph: {
      title: post.title,
      description: post.excerpt,
      type: 'article',
      publishedTime: post.createdAt,
      modifiedTime: post.updatedAt,
      authors: [post.author.name],
      images: post.image
        ? [
            {
              url: post.image,
              width: 1200,
              height: 630,
              alt: post.title,
            },
          ]
        : [],
    },
    twitter: {
      card: 'summary_large_image',
      title: post.title,
      description: post.excerpt,
      images: post.image ? [post.image] : [],
    },
  };
}

export default async function PostPage({ params }: PageProps) {
  const { id } = await params;
  const post = await getPost(id);
  if (!post) notFound();

  return <article>{/* ... */}</article>;
}
```

---

## Sitemap

### Static Sitemap

```typescript
// app/sitemap.ts
import type { MetadataRoute } from 'next';

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: 'https://example.com',
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 1,
    },
    {
      url: 'https://example.com/about',
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.8,
    },
    {
      url: 'https://example.com/blog',
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.9,
    },
  ];
}
```

### Dynamic Sitemap

```typescript
// app/sitemap.ts
import type { MetadataRoute } from 'next';
import { db } from '@/lib/db';
import { posts } from '@/lib/db/schema';
import { eq } from 'drizzle-orm';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = 'https://example.com';

  // Static pages
  const staticPages: MetadataRoute.Sitemap = [
    { url: baseUrl, lastModified: new Date(), changeFrequency: 'daily', priority: 1 },
    { url: `${baseUrl}/about`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.8 },
  ];

  // Dynamic pages from DB
  const allPosts = await db
    .select({ id: posts.id, updatedAt: posts.updatedAt })
    .from(posts)
    .where(eq(posts.status, 'published'));

  const postPages: MetadataRoute.Sitemap = allPosts.map((post) => ({
    url: `${baseUrl}/posts/${post.id}`,
    lastModified: post.updatedAt,
    changeFrequency: 'weekly',
    priority: 0.7,
  }));

  return [...staticPages, ...postPages];
}
```

### Multiple Sitemaps

```typescript
// app/sitemap/[id]/route.ts
import { NextResponse } from 'next/server';

const POSTS_PER_SITEMAP = 50000;

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const page = parseInt(id);

  const posts = await db.query.posts.findMany({
    limit: POSTS_PER_SITEMAP,
    offset: page * POSTS_PER_SITEMAP,
    where: eq(posts.status, 'published'),
  });

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      ${posts
        .map(
          (post) => `
        <url>
          <loc>https://example.com/posts/${post.id}</loc>
          <lastmod>${post.updatedAt.toISOString()}</lastmod>
          <changefreq>weekly</changefreq>
          <priority>0.7</priority>
        </url>
      `
        )
        .join('')}
    </urlset>`;

  return new NextResponse(xml, {
    headers: { 'Content-Type': 'application/xml' },
  });
}
```

---

## Robots.txt

```typescript
// app/robots.ts
import type { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/api/', '/admin/', '/private/'],
      },
      {
        userAgent: 'Googlebot',
        allow: '/',
      },
    ],
    sitemap: 'https://example.com/sitemap.xml',
  };
}
```

---

## Structured Data (JSON-LD)

### 조직/웹사이트

```tsx
// app/layout.tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'My Company',
    url: 'https://example.com',
    logo: 'https://example.com/logo.png',
    sameAs: [
      'https://twitter.com/mycompany',
      'https://www.linkedin.com/company/mycompany',
    ],
  };

  return (
    <html>
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

### 블로그 포스트

```tsx
// app/posts/[id]/page.tsx
export default async function PostPage({ params }: PageProps) {
  const { id } = await params;
  const post = await getPost(id);

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: post.title,
    description: post.excerpt,
    image: post.image,
    datePublished: post.createdAt,
    dateModified: post.updatedAt,
    author: {
      '@type': 'Person',
      name: post.author.name,
      url: `https://example.com/authors/${post.author.id}`,
    },
    publisher: {
      '@type': 'Organization',
      name: 'My Company',
      logo: {
        '@type': 'ImageObject',
        url: 'https://example.com/logo.png',
      },
    },
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': `https://example.com/posts/${post.id}`,
    },
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <article>{/* ... */}</article>
    </>
  );
}
```

### 제품

```tsx
const productJsonLd = {
  '@context': 'https://schema.org',
  '@type': 'Product',
  name: product.name,
  description: product.description,
  image: product.images,
  sku: product.sku,
  brand: {
    '@type': 'Brand',
    name: product.brand,
  },
  offers: {
    '@type': 'Offer',
    price: product.price,
    priceCurrency: 'KRW',
    availability: product.inStock
      ? 'https://schema.org/InStock'
      : 'https://schema.org/OutOfStock',
    url: `https://example.com/products/${product.id}`,
  },
  aggregateRating: {
    '@type': 'AggregateRating',
    ratingValue: product.rating,
    reviewCount: product.reviewCount,
  },
};
```

### FAQ

```tsx
const faqJsonLd = {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: faqs.map((faq) => ({
    '@type': 'Question',
    name: faq.question,
    acceptedAnswer: {
      '@type': 'Answer',
      text: faq.answer,
    },
  })),
};
```

---

## Canonical URL

```typescript
// app/posts/[id]/page.tsx
export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { id } = await params;

  return {
    alternates: {
      canonical: `https://example.com/posts/${id}`,
      languages: {
        'ko-KR': `https://example.com/ko/posts/${id}`,
        'en-US': `https://example.com/en/posts/${id}`,
      },
    },
  };
}
```

---

## Open Graph Image Generation

```typescript
// app/api/og/route.tsx
import { ImageResponse } from 'next/og';

export const runtime = 'edge';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const title = searchParams.get('title') || 'My App';

  return new ImageResponse(
    (
      <div
        style={{
          height: '100%',
          width: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#000',
          color: '#fff',
          fontSize: 60,
          fontWeight: 700,
        }}
      >
        {title}
      </div>
    ),
    {
      width: 1200,
      height: 630,
    }
  );
}
```

```typescript
// 메타데이터에서 사용
openGraph: {
  images: [
    {
      url: `/api/og?title=${encodeURIComponent(post.title)}`,
      width: 1200,
      height: 630,
    },
  ],
},
```

---

## 테스트 예제

### Metadata 테스트

```typescript
// features/posts/api/__tests__/post-metadata.test.ts
import { describe, it, expect, vi } from 'vitest';
import { generateMetadata } from '@/app/posts/[id]/page';

vi.mock('@/features/posts/api/posts.service', () => ({
  getPost: vi.fn(),
}));

import { getPost } from '@/features/posts/api/posts.service';

describe('generateMetadata', () => {
  it('게시물 메타데이터를 생성한다', async () => {
    vi.mocked(getPost).mockResolvedValue({
      id: '1',
      title: 'Test Post',
      excerpt: 'Test excerpt',
      image: 'https://example.com/image.jpg',
      createdAt: '2025-01-01',
      updatedAt: '2025-01-02',
      author: { name: 'Test Author', id: '1' },
    });

    const metadata = await generateMetadata({ params: Promise.resolve({ id: '1' }) });

    expect(metadata.title).toBe('Test Post');
    expect(metadata.description).toBe('Test excerpt');
    expect(metadata.openGraph?.title).toBe('Test Post');
  });

  it('게시물이 없으면 Not Found 메타데이터를 반환한다', async () => {
    vi.mocked(getPost).mockResolvedValue(null);

    const metadata = await generateMetadata({ params: Promise.resolve({ id: '999' }) });

    expect(metadata.title).toBe('Not Found');
  });
});
```

### Sitemap 테스트

```typescript
// app/__tests__/sitemap.test.ts
import { describe, it, expect, vi } from 'vitest';
import sitemap from '@/app/sitemap';

vi.mock('@/lib/db', () => ({
  db: {
    select: vi.fn().mockReturnThis(),
    from: vi.fn().mockReturnThis(),
    where: vi.fn().mockResolvedValue([
      { id: '1', updatedAt: new Date('2025-01-01') },
      { id: '2', updatedAt: new Date('2025-01-02') },
    ]),
  },
}));

describe('sitemap', () => {
  it('정적 페이지와 동적 페이지를 포함한다', async () => {
    const result = await sitemap();

    // 정적 페이지 확인
    expect(result).toContainEqual(
      expect.objectContaining({ url: expect.stringContaining('/about') })
    );

    // 동적 페이지 확인
    expect(result).toContainEqual(
      expect.objectContaining({ url: expect.stringContaining('/posts/1') })
    );
  });

  it('priority와 changeFrequency를 포함한다', async () => {
    const result = await sitemap();

    result.forEach((entry) => {
      expect(entry).toHaveProperty('priority');
      expect(entry).toHaveProperty('changeFrequency');
    });
  });
});
```

---

## 안티패턴

### 1. 메타데이터 누락

```typescript
// ❌ Bad: 메타데이터 없이 페이지 생성
export default function ProductPage() {
  return <div>Product</div>;
}

// ✅ Good: 완전한 메타데이터 제공
export const metadata: Metadata = {
  title: 'Products | My Store',
  description: '최고의 상품을 만나보세요',
  openGraph: {
    title: 'Products | My Store',
    description: '최고의 상품을 만나보세요',
    images: ['/og-products.png'],
  },
};

export default function ProductPage() {
  return <div>Product</div>;
}
```

### 2. 하드코딩된 URL

```typescript
// ❌ Bad: 환경별로 다른 URL 하드코딩
export const metadata: Metadata = {
  metadataBase: new URL('https://example.com'),
};

// ✅ Good: 환경 변수 사용
export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL!),
};
```

### 3. 중복 JSON-LD

```tsx
// ❌ Bad: 모든 페이지에 동일한 JSON-LD 반복
export default function Page() {
  return (
    <>
      <script type="application/ld+json">
        {JSON.stringify({ '@context': 'https://schema.org', ... })}
      </script>
      {/* 내용 */}
    </>
  );
}

// ✅ Good: JSON-LD 컴포넌트로 추출
function JsonLd({ data }: { data: Record<string, unknown> }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  );
}

export default function Page() {
  const jsonLd = createProductJsonLd(product);
  return (
    <>
      <JsonLd data={jsonLd} />
      {/* 내용 */}
    </>
  );
}
```

### 4. 캐싱 무시

```typescript
// ❌ Bad: sitemap 매번 새로 생성
export default async function sitemap() {
  const posts = await db.query.posts.findMany(); // 매 요청마다 쿼리
  return posts.map(...);
}

// ✅ Good: 캐싱과 revalidate 활용
export const revalidate = 3600; // 1시간 캐싱

export default async function sitemap() {
  const posts = await db.query.posts.findMany();
  return posts.map(...);
}
```

---

## 에러 처리

### SEO 에러 타입

```typescript
// lib/seo/errors.ts
export class SEOError extends Error {
  constructor(
    message: string,
    public code: 'METADATA_GENERATION_FAILED' | 'SITEMAP_GENERATION_FAILED' | 'INVALID_SCHEMA',
    public context?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'SEOError';
  }
}
```

### 안전한 메타데이터 생성

```typescript
// lib/seo/metadata.ts
import { Metadata } from 'next';

export async function generateSafeMetadata(
  fetcher: () => Promise<{ title: string; description?: string } | null>,
  fallback: Metadata
): Promise<Metadata> {
  try {
    const data = await fetcher();

    if (!data) {
      return fallback;
    }

    return {
      title: data.title,
      description: data.description || fallback.description,
    };
  } catch (error) {
    console.error('Metadata generation failed:', error);
    return fallback;
  }
}
```

---

## 성능 고려사항

### 1. 메타데이터 캐싱

```typescript
// lib/seo/cache.ts
import { unstable_cache } from 'next/cache';

export const getCachedMetadata = unstable_cache(
  async (id: string) => {
    const post = await getPost(id);
    return post ? { title: post.title, description: post.excerpt } : null;
  },
  ['post-metadata'],
  { revalidate: 3600, tags: ['posts'] }
);
```

### 2. Sitemap 분할

```typescript
// 대규모 사이트: 여러 sitemap으로 분할
// app/sitemap/[id]/route.ts
const URLS_PER_SITEMAP = 50000;

export async function generateSitemaps() {
  const totalPosts = await getPostCount();
  const sitemapCount = Math.ceil(totalPosts / URLS_PER_SITEMAP);

  return Array.from({ length: sitemapCount }, (_, i) => ({ id: i }));
}
```

### 3. OG 이미지 최적화

```typescript
// Edge Runtime에서 OG 이미지 생성
export const runtime = 'edge';

// 폰트 미리 로드
const interSemiBold = fetch(
  new URL('../fonts/Inter-SemiBold.ttf', import.meta.url)
).then((res) => res.arrayBuffer());
```

---

## 보안 고려사항

### 1. 입력 검증

```typescript
// OG 이미지 생성 시 입력 검증
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const title = searchParams.get('title');

  // XSS 방지: HTML 이스케이프
  const safeTitle = title
    ?.replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .slice(0, 100); // 길이 제한

  return new ImageResponse(/* ... */);
}
```

### 2. URL 검증

```typescript
// canonical URL 생성 시 검증
function getCanonicalUrl(path: string): string {
  const baseUrl = new URL(process.env.NEXT_PUBLIC_APP_URL!);

  // Path traversal 방지
  const safePath = path.replace(/\.\./g, '').replace(/\/\//g, '/');

  return new URL(safePath, baseUrl).toString();
}
```

### 3. JSON-LD 이스케이프

```typescript
// JSON-LD 데이터 안전하게 삽입
function JsonLd({ data }: { data: Record<string, unknown> }) {
  // 스크립트 인젝션 방지
  const safeJson = JSON.stringify(data)
    .replace(/</g, '\\u003c')
    .replace(/>/g, '\\u003e')
    .replace(/&/g, '\\u0026');

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: safeJson }}
    />
  );
}
```

---

## References

- `_references/ARCHITECTURE-PATTERN.md`
- `_references/TEST-PATTERN.md`

