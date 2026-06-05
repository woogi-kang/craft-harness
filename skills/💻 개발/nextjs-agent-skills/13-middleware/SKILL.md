---
name: middleware
description: |
  Next.js Proxy(기존 Middleware)를 설정합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Proxy / Middleware Skill

Next.js 16 기준 Proxy를 설정합니다. 기존 `proxy.ts` 관례는 `proxy.ts`로 이전합니다.

## Triggers

- "미들웨어", "middleware", "proxy", "인증 미들웨어", "edge"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | Next.js 프로젝트 경로 |
| `features` | ❌ | 활성화할 기능 (auth, i18n, rate-limit) |

---

## 기본 Proxy

```typescript
// proxy.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function proxy(request: NextRequest) {
  const response = NextResponse.next();

  // 보안 헤더 (OWASP 권장)
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-XSS-Protection', '1; mode=block');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');

  // CSP (Content Security Policy) - 프로덕션 환경에 맞게 조정 필요
  const cspHeader = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'", // 개발용, 프로덕션에서 강화
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: https:",
    "font-src 'self' data:",
    "connect-src 'self' https:",
    "frame-ancestors 'none'",
  ].join('; ');
  response.headers.set('Content-Security-Policy', cspHeader);

  return response;
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
```

---

## Auth.js Proxy

```typescript
// proxy.ts
export { auth as proxy } from '@/lib/auth';

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
```

---

## 조합 Proxy

```typescript
// proxy.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { auth } from '@/lib/auth';

const protectedPaths = ['/dashboard', '/settings', '/profile'];
const publicPaths = ['/login', '/register'];

export async function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const session = await auth();

  // 보호된 경로 체크
  const isProtected = protectedPaths.some((p) => pathname.startsWith(p));
  if (isProtected && !session) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // 로그인 상태에서 공개 경로 접근
  const isPublic = publicPaths.some((p) => pathname.startsWith(p));
  if (isPublic && session) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
```

---

## Proxy Runtime 제약사항

Next.js 16 Proxy는 Node.js Runtime이 기본값이며, `runtime` config를 Proxy 파일에 설정할 수 없습니다. 다만 렌더링 코드와 분리된 요청 전 처리 계층이므로 공유 module state에 의존하지 말고 짧고 예측 가능한 작업만 수행합니다.

### 사용 불가 API

```typescript
// ❌ Proxy에서 피할 패턴
import fs from 'fs';           // 요청마다 파일 시스템 접근
import { Pool } from 'pg';     // Proxy에서 DB 직접 연결
import bcrypt from 'bcrypt';   // 무거운 CPU 작업

// ✅ 가벼운 대안
crypto.subtle.digest('SHA-256', data);  // Web Crypto API
fetch('https://api.example.com/...');   // 짧은 HTTP 검증
```

### 실행 시간 제한

```typescript
// ⚠️ Proxy는 요청 렌더링 전 실행되므로 빠르게 반환해야 함

export function proxy(request: NextRequest) {
  // ❌ 긴 작업 금지
  // await heavyComputation();

  // ✅ 빠른 작업만 수행
  const token = request.cookies.get('token');
  if (!token) {
    return NextResponse.redirect('/login');
  }

  return NextResponse.next();
}
```

### 번들 크기 제한

```typescript
// 큰 라이브러리는 Proxy 경계 밖으로 이동

// ❌ 피해야 할 패턴
import { format } from 'date-fns';  // 전체 번들 포함

// ✅ 경량 대안
const formatted = new Intl.DateTimeFormat('ko-KR').format(date);
```

---

## i18n Proxy

```typescript
// proxy.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { match } from '@formatjs/intl-localematcher';
import Negotiator from 'negotiator';

const locales = ['ko', 'en', 'ja'];
const defaultLocale = 'ko';

function getLocale(request: NextRequest): string {
  const headers = { 'accept-language': request.headers.get('accept-language') || '' };
  const languages = new Negotiator({ headers }).languages();

  try {
    return match(languages, locales, defaultLocale);
  } catch {
    return defaultLocale;
  }
}

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // 정적 파일 및 API 제외
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.includes('.')
  ) {
    return NextResponse.next();
  }

  // 이미 locale prefix가 있는지 확인
  const pathnameHasLocale = locales.some(
    (locale) => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  );

  if (pathnameHasLocale) {
    return NextResponse.next();
  }

  // Locale redirect
  const locale = getLocale(request);
  const url = request.nextUrl.clone();
  url.pathname = `/${locale}${pathname}`;

  return NextResponse.redirect(url);
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
```

### next-intl 통합 (권장)

```typescript
// proxy.ts
import createMiddleware from 'next-intl/middleware';
import type { NextRequest } from 'next/server';
import { locales, defaultLocale } from './i18n.config';

const intlMiddleware = createMiddleware({
  locales,
  defaultLocale,
  localePrefix: 'as-needed', // 기본 locale은 prefix 생략
});

export function proxy(request: NextRequest) {
  return intlMiddleware(request);
}

export const config = {
  matcher: ['/((?!api|_next|.*\\..*).*)'],
};
```

---

## 성능 최적화

### 1. 조기 반환 패턴

```typescript
export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // 1️⃣ 가장 먼저: 정적 리소스 바이패스
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.match(/\.(ico|png|jpg|svg|css|js)$/)
  ) {
    return NextResponse.next();
  }

  // 2️⃣ 그 다음: 공개 경로 바이패스
  if (pathname === '/' || pathname === '/about') {
    return NextResponse.next();
  }

  // 3️⃣ 마지막: 인증 필요 경로만 체크
  // ... auth logic
}
```

### 2. Matcher 최적화

```typescript
export const config = {
  // ✅ 필요한 경로만 매칭 (성능 향상)
  matcher: [
    '/dashboard/:path*',
    '/settings/:path*',
    '/profile/:path*',
  ],

  // ❌ 모든 경로 매칭 (불필요한 실행)
  // matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
```

### 3. 캐싱 활용

```typescript
// 인증 토큰 검증 결과 캐싱 (메모리 내)
const tokenCache = new Map<string, { valid: boolean; expires: number }>();

export async function proxy(request: NextRequest) {
  const token = request.cookies.get('token')?.value;
  if (!token) return NextResponse.redirect('/login');

  // 캐시 확인
  const cached = tokenCache.get(token);
  if (cached && cached.expires > Date.now()) {
    if (!cached.valid) return NextResponse.redirect('/login');
    return NextResponse.next();
  }

  // 토큰 검증 (Proxy-compatible)
  const isValid = await verifyToken(token);
  tokenCache.set(token, { valid: isValid, expires: Date.now() + 60000 });

  if (!isValid) return NextResponse.redirect('/login');
  return NextResponse.next();
}
```

---

## 테스트 예제

### Proxy Unit Test

```typescript
// __tests__/proxy.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { proxy } from '@/proxy';
import { NextRequest } from 'next/server';

function createMockRequest(url: string, options: {
  cookies?: Record<string, string>;
  headers?: Record<string, string>;
} = {}): NextRequest {
  const request = new NextRequest(new URL(url, 'http://localhost:3000'));

  if (options.cookies) {
    Object.entries(options.cookies).forEach(([name, value]) => {
      request.cookies.set(name, value);
    });
  }

  return request;
}

describe('proxy', () => {
  describe('보안 헤더', () => {
    it('보안 헤더가 설정되어야 한다', async () => {
      const request = createMockRequest('/');
      const response = await proxy(request);

      expect(response.headers.get('X-Frame-Options')).toBe('DENY');
      expect(response.headers.get('X-Content-Type-Options')).toBe('nosniff');
      expect(response.headers.get('X-XSS-Protection')).toBe('1; mode=block');
      expect(response.headers.get('Referrer-Policy')).toBe('strict-origin-when-cross-origin');
    });

    it('CSP 헤더가 설정되어야 한다', async () => {
      const request = createMockRequest('/');
      const response = await proxy(request);

      const csp = response.headers.get('Content-Security-Policy');
      expect(csp).toContain("default-src 'self'");
      expect(csp).toContain("frame-ancestors 'none'");
    });
  });

  describe('인증 라우팅', () => {
    it('비인증 사용자가 보호 경로 접근 시 로그인으로 리다이렉트', async () => {
      const request = createMockRequest('/dashboard');
      const response = await proxy(request);

      expect(response.status).toBe(307);
      expect(response.headers.get('location')).toContain('/login');
    });

    it('인증된 사용자는 보호 경로 접근 가능', async () => {
      const request = createMockRequest('/dashboard', {
        cookies: { 'auth-token': 'valid-token' },
      });
      const response = await proxy(request);

      expect(response.status).toBe(200);
    });

    it('정적 리소스는 인증 체크 바이패스', async () => {
      const request = createMockRequest('/_next/static/chunk.js');
      const response = await proxy(request);

      expect(response.status).toBe(200);
    });
  });
});
```

### i18n Proxy Test

```typescript
// __tests__/i18n-proxy.test.ts
import { describe, it, expect } from 'vitest';
import { proxy } from '@/proxy';
import { NextRequest } from 'next/server';

describe('i18n proxy', () => {
  it('locale 없는 경로는 기본 locale로 리다이렉트', async () => {
    const request = new NextRequest('http://localhost:3000/about');
    const response = await proxy(request);

    expect(response.status).toBe(307);
    expect(response.headers.get('location')).toContain('/ko/about');
  });

  it('Accept-Language 헤더 기반 locale 결정', async () => {
    const request = new NextRequest('http://localhost:3000/about', {
      headers: { 'accept-language': 'en-US,en;q=0.9' },
    });
    const response = await proxy(request);

    expect(response.headers.get('location')).toContain('/en/about');
  });

  it('이미 locale prefix가 있는 경로는 바이패스', async () => {
    const request = new NextRequest('http://localhost:3000/ko/about');
    const response = await proxy(request);

    expect(response.status).toBe(200);
  });
});
```

---

## 안티패턴

### 1. 무거운 연산 수행

```typescript
// ❌ Bad: Proxy에서 무거운 연산
export async function proxy(request: NextRequest) {
  const users = await db.query('SELECT * FROM users'); // DB 직접 쿼리
  const token = jwt.verify(request.cookies.get('token'), secret); // 동기 검증

  return NextResponse.next();
}

// ✅ Good: 경량 검증만 수행
export async function proxy(request: NextRequest) {
  const token = request.cookies.get('token')?.value;
  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // JWT 서명만 빠르게 검증
  try {
    await jwtVerify(token, new TextEncoder().encode(secret));
  } catch {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}
```

### 2. 모든 경로에 Proxy 적용

```typescript
// ❌ Bad: 전체 경로에 적용
export const config = {
  matcher: ['/:path*'],
};

// ✅ Good: 필요한 경로만 명시적으로 적용
export const config = {
  matcher: [
    '/dashboard/:path*',
    '/settings/:path*',
    '/api/protected/:path*',
  ],
};
```

### 3. 동기식 리다이렉트 체인

```typescript
// ❌ Bad: 복잡한 리다이렉트 로직
export async function proxy(request: NextRequest) {
  const session = await getSession();
  if (!session) return NextResponse.redirect('/login');
  if (!session.verified) return NextResponse.redirect('/verify');
  if (!session.onboarded) return NextResponse.redirect('/onboarding');
  if (session.role === 'admin') return NextResponse.redirect('/admin');
  // 무한 리다이렉트 위험!
}

// ✅ Good: 단일 책임, 리다이렉트 루프 방지
export async function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // 리다이렉트 루프 방지
  if (['/login', '/verify', '/onboarding'].includes(pathname)) {
    return NextResponse.next();
  }

  const session = await getSession();
  if (!session) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}
```

### 4. Node.js 전용 API 사용

```typescript
// ❌ Bad: Node.js 전용 모듈
import fs from 'fs';
import crypto from 'crypto';

export function proxy(request: NextRequest) {
  const data = fs.readFileSync('./config.json'); // 불가
  const hash = crypto.createHash('sha256'); // 불가
}

// ✅ Good: Web API 사용
export async function proxy(request: NextRequest) {
  // Web Crypto API
  const encoder = new TextEncoder();
  const data = encoder.encode('secret');
  const hash = await crypto.subtle.digest('SHA-256', data);

  // Fetch API로 외부 설정 로드
  const config = await fetch('https://api.example.com/config').then(r => r.json());
}
```

---

## 에러 처리

### Proxy Error Handling

```typescript
// proxy.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export async function proxy(request: NextRequest) {
  try {
    // 인증 검증
    const token = request.cookies.get('token')?.value;
    if (!token) {
      return NextResponse.redirect(new URL('/login', request.url));
    }

    const verified = await verifyToken(token);
    if (!verified) {
      // 토큰 만료/무효 - 로그인 페이지로
      const response = NextResponse.redirect(new URL('/login', request.url));
      response.cookies.delete('token');
      return response;
    }

    return NextResponse.next();
  } catch (error) {
    // Proxy 계층에서는 가벼운 로깅만 수행
    console.error('[Proxy Error]', error instanceof Error ? error.message : error);

    // 에러 시 안전하게 처리 - 서비스 중단 방지
    // 옵션 1: 로그인 페이지로 리다이렉트
    // return NextResponse.redirect(new URL('/login', request.url));

    // 옵션 2: 에러 페이지로
    return NextResponse.redirect(new URL('/error', request.url));
  }
}
```

### 에러 유형별 처리

```typescript
// lib/proxy/errors.ts
export class ProxyError extends Error {
  constructor(
    message: string,
    public code: 'AUTH_FAILED' | 'TOKEN_EXPIRED' | 'RATE_LIMITED' | 'INVALID_REQUEST',
    public statusCode: number = 401
  ) {
    super(message);
    this.name = 'ProxyError';
  }
}

// proxy.ts
export async function proxy(request: NextRequest) {
  try {
    await authenticateRequest(request);
    return NextResponse.next();
  } catch (error) {
    if (error instanceof ProxyError) {
      switch (error.code) {
        case 'TOKEN_EXPIRED':
          // 토큰 갱신 시도 가능한 페이지로
          return NextResponse.redirect(new URL('/auth/refresh', request.url));
        case 'RATE_LIMITED':
          return new NextResponse('Too Many Requests', { status: 429 });
        case 'AUTH_FAILED':
        default:
          return NextResponse.redirect(new URL('/login', request.url));
      }
    }

    // 예상치 못한 에러 - 서비스 연속성 유지
    console.error('[Proxy] Unexpected error:', error);
    return NextResponse.next();
  }
}
```

---

## 성능 고려사항

### 1. Matcher 최적화

```typescript
// ✅ 구체적인 matcher로 불필요한 실행 방지
export const config = {
  matcher: [
    // 인증 필요 경로만
    '/dashboard/:path*',
    '/settings/:path*',
    '/api/protected/:path*',
    // 정적 리소스 제외 (기본적으로 제외됨)
  ],
};
```

### 2. 조기 반환 패턴

```typescript
export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // 1. 가장 빈번한 케이스 먼저 체크
  if (pathname.startsWith('/_next') || pathname.includes('.')) {
    return NextResponse.next();
  }

  // 2. 공개 경로 바이패스
  const publicPaths = ['/', '/about', '/pricing'];
  if (publicPaths.includes(pathname)) {
    return NextResponse.next();
  }

  // 3. 비용이 큰 연산은 마지막에
  return authenticateAndContinue(request);
}
```

### 3. 인메모리 캐싱 (주의 필요)

```typescript
// ⚠️ Proxy의 인메모리 캐시는 인스턴스 간 공유되지 않음
// 짧은 TTL로만 사용
const tokenCache = new Map<string, { valid: boolean; expires: number }>();
const CACHE_TTL = 30_000; // 30초

export async function proxy(request: NextRequest) {
  const token = request.cookies.get('token')?.value;
  if (!token) return redirectToLogin(request);

  const cached = tokenCache.get(token);
  if (cached && cached.expires > Date.now()) {
    return cached.valid ? NextResponse.next() : redirectToLogin(request);
  }

  const isValid = await verifyTokenFast(token);
  tokenCache.set(token, { valid: isValid, expires: Date.now() + CACHE_TTL });

  return isValid ? NextResponse.next() : redirectToLogin(request);
}
```

### 4. 외부 호출 최소화

```typescript
// ❌ Bad: 매 요청마다 외부 API 호출
export async function proxy(request: NextRequest) {
  const user = await fetch('https://api.example.com/me', {
    headers: { Authorization: request.cookies.get('token')?.value || '' },
  }).then(r => r.json());
}

// ✅ Good: JWT 페이로드에서 필요한 정보 추출
export async function proxy(request: NextRequest) {
  const token = request.cookies.get('token')?.value;
  if (!token) return redirectToLogin(request);

  // JWT 디코드 (서명 검증 없이 페이로드만 - 빠름)
  const payload = decodeJwtPayload(token);
  if (!payload || payload.exp < Date.now() / 1000) {
    return redirectToLogin(request);
  }

  // 필요한 정보를 헤더로 전달
  const response = NextResponse.next();
  response.headers.set('x-user-id', payload.sub);
  response.headers.set('x-user-role', payload.role);
  return response;
}
```

---

## 보안 고려사항

### 1. 보안 헤더 설정

```typescript
export function proxy(request: NextRequest) {
  const response = NextResponse.next();

  // OWASP 권장 보안 헤더
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-XSS-Protection', '1; mode=block');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');

  // HSTS (HTTPS 강제)
  response.headers.set(
    'Strict-Transport-Security',
    'max-age=31536000; includeSubDomains; preload'
  );

  return response;
}
```

### 2. CSP with Nonce

```typescript
// proxy.ts
export function proxy(request: NextRequest) {
  const nonce = Buffer.from(crypto.randomUUID()).toString('base64');

  const cspHeader = [
    "default-src 'self'",
    `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'`,
    "style-src 'self' 'unsafe-inline'", // CSS-in-JS 호환
    "img-src 'self' data: https:",
    "font-src 'self'",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    "upgrade-insecure-requests",
  ].join('; ');

  const response = NextResponse.next();
  response.headers.set('Content-Security-Policy', cspHeader);
  response.headers.set('x-nonce', nonce); // 레이아웃에서 사용

  return response;
}
```

### 3. Rate Limiting

```typescript
// proxy.ts
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, '10 s'),
  analytics: true,
});

export async function proxy(request: NextRequest) {
  // API 경로에만 Rate Limiting 적용
  if (request.nextUrl.pathname.startsWith('/api')) {
    const ip = request.headers.get('x-forwarded-for') ?? 'anonymous';
    const { success, limit, remaining, reset } = await ratelimit.limit(ip);

    if (!success) {
      return new NextResponse('Too Many Requests', {
        status: 429,
        headers: {
          'X-RateLimit-Limit': limit.toString(),
          'X-RateLimit-Remaining': remaining.toString(),
          'X-RateLimit-Reset': reset.toString(),
          'Retry-After': Math.ceil((reset - Date.now()) / 1000).toString(),
        },
      });
    }
  }

  return NextResponse.next();
}
```

### 4. CSRF 보호 (Double Submit Cookie)

```typescript
export async function proxy(request: NextRequest) {
  // State-changing 요청에만 CSRF 검증
  if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(request.method)) {
    const cookieToken = request.cookies.get('csrf-token')?.value;
    const headerToken = request.headers.get('x-csrf-token');

    if (!cookieToken || !headerToken || cookieToken !== headerToken) {
      return new NextResponse('CSRF validation failed', { status: 403 });
    }
  }

  // GET 요청 시 CSRF 토큰 설정
  if (request.method === 'GET' && !request.cookies.has('csrf-token')) {
    const token = crypto.randomUUID();
    const response = NextResponse.next();
    response.cookies.set('csrf-token', token, {
      httpOnly: false, // JavaScript에서 읽어야 함
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
    });
    return response;
  }

  return NextResponse.next();
}
```

---

## References

- `_references/ARCHITECTURE-PATTERN.md`
- `_references/TEST-PATTERN.md`
