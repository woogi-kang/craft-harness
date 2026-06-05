---
name: security
description: |
  보안 기능을 구현합니다 (Rate Limiting, CSRF, 입력 검증).
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Security Skill

보안 기능을 구현합니다 (Rate Limiting, CSRF, 입력 검증).

## Triggers

- "보안", "security", "rate limit", "csrf", "xss"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `features` | ✅ | rate-limit, csrf, headers, validation |
| `provider` | ❌ | upstash, redis |

---

## Rate Limiting (Upstash)

### 설치

```bash
npm install @upstash/ratelimit @upstash/redis
```

### 설정

```typescript
// lib/rate-limit.ts
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
});

// 기본 Rate Limiter: 10초당 10회
export const ratelimit = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(10, '10 s'),
  analytics: true,
});

// API별 커스텀 Rate Limiter
export const authRatelimit = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(5, '1 m'), // 분당 5회 (로그인 시도)
  prefix: 'auth',
});

export const apiRatelimit = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(100, '1 m'), // 분당 100회
  prefix: 'api',
});
```

### Proxy에서 사용

```typescript
// proxy.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { ratelimit } from '@/lib/rate-limit';

export async function proxy(request: NextRequest) {
  // API 라우트에만 적용
  if (request.nextUrl.pathname.startsWith('/api')) {
    const ip = request.headers.get('x-forwarded-for') ?? '127.0.0.1';
    const { success, limit, remaining, reset } = await ratelimit.limit(ip);

    if (!success) {
      return NextResponse.json(
        { error: 'Too many requests' },
        {
          status: 429,
          headers: {
            'X-RateLimit-Limit': limit.toString(),
            'X-RateLimit-Remaining': remaining.toString(),
            'X-RateLimit-Reset': reset.toString(),
            'Retry-After': Math.ceil((reset - Date.now()) / 1000).toString(),
          },
        }
      );
    }

    const response = NextResponse.next();
    response.headers.set('X-RateLimit-Limit', limit.toString());
    response.headers.set('X-RateLimit-Remaining', remaining.toString());
    return response;
  }

  return NextResponse.next();
}

export const config = {
  matcher: '/api/:path*',
};
```

### Server Action에서 Rate Limiting

```typescript
// lib/actions/safe-action.ts
import { createSafeActionClient } from 'next-safe-action';
import { authRatelimit } from '@/lib/rate-limit';
import { headers } from 'next/headers';

export const rateLimitedActionClient = createSafeActionClient({
  handleServerError: (e) => e.message,
}).use(async ({ next }) => {
  const headersList = await headers();
  const ip = headersList.get('x-forwarded-for') ?? '127.0.0.1';
  const { success } = await authRatelimit.limit(ip);

  if (!success) {
    throw new Error('Too many requests. Please try again later.');
  }

  return next({ ctx: {} });
});
```

---

## 보안 헤더

### next.config.ts

```typescript
// next.config.ts
import type { NextConfig } from 'next';

const securityHeaders = [
  {
    key: 'X-DNS-Prefetch-Control',
    value: 'on',
  },
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=63072000; includeSubDomains; preload',
  },
  {
    key: 'X-Frame-Options',
    value: 'SAMEORIGIN',
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff',
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin',
  },
  {
    key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=()',
  },
];

const nextConfig: NextConfig = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: securityHeaders,
      },
    ];
  },
};

export default nextConfig;
```

### Content Security Policy (CSP)

```typescript
// proxy.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function proxy(request: NextRequest) {
  // 암호학적으로 안전한 nonce 생성 (32바이트)
  const nonce = Buffer.from(crypto.getRandomValues(new Uint8Array(32))).toString('base64');

  const cspHeader = `
    default-src 'self';
    script-src 'self' 'nonce-${nonce}' 'strict-dynamic' https:;
    style-src 'self' 'unsafe-inline';
    img-src 'self' blob: data: https:;
    font-src 'self' https://fonts.gstatic.com;
    connect-src 'self' https://api.stripe.com https://vitals.vercel-insights.com;
    frame-src 'self' https://js.stripe.com;
    object-src 'none';
    base-uri 'self';
    form-action 'self';
    frame-ancestors 'none';
    upgrade-insecure-requests;
  `.replace(/\s{2,}/g, ' ').trim();

  const requestHeaders = new Headers(request.headers);
  requestHeaders.set('x-nonce', nonce);

  const response = NextResponse.next({
    request: {
      headers: requestHeaders,
    },
  });

  response.headers.set('Content-Security-Policy', cspHeader);
  response.headers.set('x-nonce', nonce);

  return response;
}

export const config = {
  matcher: [
    // 정적 파일 및 API 제외
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
```

### Nonce Provider 컴포넌트

```tsx
// components/security/nonce-provider.tsx
import { headers } from 'next/headers';
import Script from 'next/script';

interface NonceScriptProps {
  src?: string;
  children?: string;
  strategy?: 'beforeInteractive' | 'afterInteractive' | 'lazyOnload';
}

export async function NonceScript({ src, children, strategy = 'afterInteractive' }: NonceScriptProps) {
  const headersList = await headers();
  const nonce = headersList.get('x-nonce') ?? '';

  if (src) {
    return <Script src={src} nonce={nonce} strategy={strategy} />;
  }

  return (
    <Script
      nonce={nonce}
      strategy={strategy}
      dangerouslySetInnerHTML={{ __html: children ?? '' }}
    />
  );
}

// nonce 값을 가져오는 헬퍼
export async function getNonce(): Promise<string> {
  const headersList = await headers();
  return headersList.get('x-nonce') ?? '';
}
```

### Layout에서 Nonce 사용

```tsx
// app/layout.tsx
import { headers } from 'next/headers';
import Script from 'next/script';

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const headersList = await headers();
  const nonce = headersList.get('x-nonce') ?? '';

  return (
    <html lang="ko">
      <head>
        {/* Google Analytics with nonce */}
        <Script
          src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_ID}`}
          strategy="afterInteractive"
          nonce={nonce}
        />
        <Script
          id="gtag-init"
          strategy="afterInteractive"
          nonce={nonce}
          dangerouslySetInnerHTML={{
            __html: `
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', '${process.env.NEXT_PUBLIC_GA_ID}');
            `,
          }}
        />
      </head>
      <body>
        {children}
      </body>
    </html>
  );
}
```

### next.config.ts CSP 헤더 (정적 페이지용)

```typescript
// next.config.ts
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              // 개발 환경에서는 eval 허용 (HMR)
              process.env.NODE_ENV === 'development'
                ? "script-src 'self' 'unsafe-eval' 'unsafe-inline'"
                : "script-src 'self' 'strict-dynamic'",
              "style-src 'self' 'unsafe-inline'",
              "img-src 'self' blob: data: https:",
              "font-src 'self' https://fonts.gstatic.com",
              "connect-src 'self' https://api.stripe.com https://vitals.vercel-insights.com",
              "frame-src 'self' https://js.stripe.com",
              "object-src 'none'",
              "base-uri 'self'",
              "form-action 'self'",
              "frame-ancestors 'none'",
            ].join('; '),
          },
        ],
      },
    ];
  },
};

export default nextConfig;
```

---

## 입력 검증 & Sanitization

### XSS 방지

```typescript
// lib/sanitize.ts
import DOMPurify from 'isomorphic-dompurify';

export function sanitizeHtml(dirty: string): string {
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
    ALLOWED_ATTR: ['href', 'target', 'rel'],
  });
}

export function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  };
  return text.replace(/[&<>"']/g, (m) => map[m]);
}
```

### Zod 스키마 보안 패턴

```typescript
// lib/schemas/security.ts
import { z } from 'zod';

// SQL Injection 방지 패턴
const safeString = z
  .string()
  .regex(/^[^'"`;\\]+$/, 'Invalid characters detected');

// XSS 방지 - HTML 태그 제거
const noHtml = z
  .string()
  .transform((val) => val.replace(/<[^>]*>/g, ''));

// 이메일 정규화
const normalizedEmail = z
  .string()
  .email()
  .transform((val) => val.toLowerCase().trim());

// URL 검증
const safeUrl = z
  .string()
  .url()
  .refine(
    (url) => {
      try {
        const parsed = new URL(url);
        return ['http:', 'https:'].includes(parsed.protocol);
      } catch {
        return false;
      }
    },
    { message: 'Invalid URL protocol' }
  );

// 파일명 검증
const safeFilename = z
  .string()
  .regex(/^[\w\-. ]+$/, 'Invalid filename')
  .refine((name) => !name.includes('..'), 'Path traversal detected');

export const securitySchemas = {
  safeString,
  noHtml,
  normalizedEmail,
  safeUrl,
  safeFilename,
};
```

---

## CSRF 보호

Next.js Server Actions는 기본적으로 CSRF 보호가 내장되어 있습니다. 추가 보호가 필요한 경우:

```typescript
// lib/csrf.ts
import { cookies } from 'next/headers';
import { randomBytes } from 'crypto';

const CSRF_TOKEN_KEY = 'csrf-token';

export async function generateCsrfToken(): Promise<string> {
  const token = randomBytes(32).toString('hex');
  const cookieStore = await cookies();
  cookieStore.set(CSRF_TOKEN_KEY, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 60 * 60, // 1시간
  });
  return token;
}

export async function verifyCsrfToken(token: string): Promise<boolean> {
  const cookieStore = await cookies();
  const storedToken = cookieStore.get(CSRF_TOKEN_KEY)?.value;
  return storedToken === token;
}
```

```tsx
// components/csrf-form.tsx
import { generateCsrfToken } from '@/lib/csrf';

export async function CsrfForm({ children }: { children: React.ReactNode }) {
  const csrfToken = await generateCsrfToken();

  return (
    <form>
      <input type="hidden" name="csrf" value={csrfToken} />
      {children}
    </form>
  );
}
```

---

## 인증 보안

### 세션 검증 강화

```typescript
// lib/auth/session.ts
import { auth } from '@/lib/auth';
import { headers } from 'next/headers';
import { db } from '@/lib/db';
import { sessions } from '@/lib/db/schema';
import { eq, and } from 'drizzle-orm';

export async function validateSession() {
  const session = await auth();
  if (!session) return null;

  const headersList = await headers();
  const userAgent = headersList.get('user-agent');
  const ip = headersList.get('x-forwarded-for');

  // 세션 하이재킹 방지: User-Agent/IP 검증
  const dbSession = await db.query.sessions.findFirst({
    where: and(
      eq(sessions.userId, session.user.id),
      eq(sessions.userAgent, userAgent ?? ''),
    ),
  });

  if (!dbSession) {
    // 세션 무효화
    return null;
  }

  return session;
}
```

### 비밀번호 정책

```typescript
// lib/schemas/password.ts
import { z } from 'zod';

export const passwordSchema = z
  .string()
  .min(8, '최소 8자 이상')
  .max(100, '최대 100자 이하')
  .regex(/[A-Z]/, '대문자 포함 필수')
  .regex(/[a-z]/, '소문자 포함 필수')
  .regex(/[0-9]/, '숫자 포함 필수')
  .regex(/[^A-Za-z0-9]/, '특수문자 포함 필수');

export const passwordStrength = (password: string): number => {
  let strength = 0;
  if (password.length >= 8) strength++;
  if (password.length >= 12) strength++;
  if (/[A-Z]/.test(password)) strength++;
  if (/[a-z]/.test(password)) strength++;
  if (/[0-9]/.test(password)) strength++;
  if (/[^A-Za-z0-9]/.test(password)) strength++;
  return Math.min(strength, 5);
};
```

---

## 로깅 & 모니터링

```typescript
// lib/security-logger.ts
export const securityLogger = {
  loginAttempt: (email: string, success: boolean, ip: string) => {
    console.log(JSON.stringify({
      event: 'login_attempt',
      email,
      success,
      ip,
      timestamp: new Date().toISOString(),
    }));
  },

  rateLimitExceeded: (ip: string, endpoint: string) => {
    console.warn(JSON.stringify({
      event: 'rate_limit_exceeded',
      ip,
      endpoint,
      timestamp: new Date().toISOString(),
    }));
  },

  suspiciousActivity: (type: string, details: Record<string, unknown>) => {
    console.error(JSON.stringify({
      event: 'suspicious_activity',
      type,
      details,
      timestamp: new Date().toISOString(),
    }));
  },
};
```

---

## 환경 변수

```env
# .env.local
UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=xxxxx
```

---

## 테스트 예제

### Rate Limiter 테스트

```typescript
// lib/__tests__/rate-limit.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ratelimit } from '../rate-limit';

vi.mock('@upstash/redis', () => ({
  Redis: vi.fn().mockImplementation(() => ({
    eval: vi.fn(),
  })),
}));

describe('ratelimit', () => {
  it('limit 내에서 success를 반환한다', async () => {
    const result = await ratelimit.limit('test-ip');

    expect(result).toHaveProperty('success');
    expect(result).toHaveProperty('remaining');
    expect(result).toHaveProperty('limit');
  });
});
```

### Security Schema 테스트

```typescript
// lib/schemas/__tests__/security.test.ts
import { describe, it, expect } from 'vitest';
import { securitySchemas, passwordSchema } from '../security';

describe('securitySchemas', () => {
  describe('safeString', () => {
    it('일반 문자열을 허용한다', () => {
      const result = securitySchemas.safeString.safeParse('hello world');
      expect(result.success).toBe(true);
    });

    it('SQL 인젝션 문자를 거부한다', () => {
      const result = securitySchemas.safeString.safeParse("'; DROP TABLE users;");
      expect(result.success).toBe(false);
    });
  });

  describe('safeUrl', () => {
    it('https URL을 허용한다', () => {
      const result = securitySchemas.safeUrl.safeParse('https://example.com');
      expect(result.success).toBe(true);
    });

    it('javascript: URL을 거부한다', () => {
      const result = securitySchemas.safeUrl.safeParse('javascript:alert(1)');
      expect(result.success).toBe(false);
    });
  });
});

describe('passwordSchema', () => {
  it('강력한 비밀번호를 허용한다', () => {
    const result = passwordSchema.safeParse('MyP@ssw0rd!');
    expect(result.success).toBe(true);
  });

  it('약한 비밀번호를 거부한다', () => {
    const result = passwordSchema.safeParse('password');
    expect(result.success).toBe(false);
  });
});
```

### CSP Proxy 테스트

```typescript
// proxy/__tests__/csp.test.ts
import { describe, it, expect } from 'vitest';
import { proxy } from '../proxy';
import { NextRequest } from 'next/server';

describe('CSP Proxy', () => {
  it('CSP 헤더를 설정한다', async () => {
    const request = new NextRequest('http://localhost:3000/');
    const response = await proxy(request);

    const csp = response.headers.get('Content-Security-Policy');
    expect(csp).toContain("default-src 'self'");
    expect(csp).toContain('nonce-');
  });

  it('nonce를 생성한다', async () => {
    const request = new NextRequest('http://localhost:3000/');
    const response = await proxy(request);

    const nonce = response.headers.get('x-nonce');
    expect(nonce).toBeTruthy();
    expect(nonce?.length).toBeGreaterThan(20);
  });
});
```

---

## 안티패턴

### 1. 하드코딩된 시크릿

```typescript
// ❌ Bad: 코드에 시크릿 하드코딩
const API_KEY = 'sk_live_1234567890';

// ✅ Good: 환경 변수 사용
const API_KEY = process.env.API_KEY!;
```

### 2. 클라이언트 신뢰

```typescript
// ❌ Bad: 클라이언트 입력 신뢰
const userId = request.body.userId; // 위조 가능
await db.query.users.findFirst({ where: eq(users.id, userId) });

// ✅ Good: 서버에서 인증된 사용자 확인
const session = await auth();
await db.query.users.findFirst({ where: eq(users.id, session.user.id) });
```

### 3. 불충분한 입력 검증

```typescript
// ❌ Bad: 타입만 체크
const email = z.string();

// ✅ Good: 완전한 검증
const email = z.string()
  .email()
  .max(254)
  .transform((v) => v.toLowerCase().trim());
```

### 4. 에러 정보 노출

```typescript
// ❌ Bad: 내부 에러 노출
return NextResponse.json({ error: error.message, stack: error.stack });

// ✅ Good: 일반화된 에러 응답
console.error('Internal error:', error);
return NextResponse.json({ error: 'An error occurred' }, { status: 500 });
```

---

## 에러 처리

### Security 에러 타입

```typescript
// lib/security/errors.ts
export class SecurityError extends Error {
  constructor(
    message: string,
    public code: 'RATE_LIMITED' | 'CSRF_INVALID' | 'UNAUTHORIZED' | 'FORBIDDEN' | 'INPUT_INVALID',
    public statusCode: number = 400
  ) {
    super(message);
    this.name = 'SecurityError';
  }
}

export function handleSecurityError(error: unknown) {
  if (error instanceof SecurityError) {
    return {
      status: error.statusCode,
      body: { error: error.message, code: error.code },
    };
  }

  // 알 수 없는 에러는 로깅 후 일반 에러 반환
  console.error('Unexpected security error:', error);
  return {
    status: 500,
    body: { error: 'Internal server error' },
  };
}
```

### 실패한 인증 시도 추적

```typescript
// lib/security/auth-tracker.ts
const failedAttempts = new Map<string, { count: number; lastAttempt: Date }>();

export function trackFailedLogin(identifier: string): boolean {
  const record = failedAttempts.get(identifier);
  const now = new Date();

  if (record) {
    // 30분 후 리셋
    if (now.getTime() - record.lastAttempt.getTime() > 30 * 60 * 1000) {
      failedAttempts.set(identifier, { count: 1, lastAttempt: now });
      return true;
    }

    record.count++;
    record.lastAttempt = now;

    // 5회 이상 실패 시 잠금
    if (record.count >= 5) {
      return false;
    }
  } else {
    failedAttempts.set(identifier, { count: 1, lastAttempt: now });
  }

  return true;
}
```

---

## 성능 고려사항

### 1. Rate Limiting 최적화

```typescript
// Redis 연결 재사용
let redisInstance: Redis | null = null;

export function getRedis(): Redis {
  if (!redisInstance) {
    redisInstance = new Redis({
      url: process.env.UPSTASH_REDIS_REST_URL!,
      token: process.env.UPSTASH_REDIS_REST_TOKEN!,
    });
  }
  return redisInstance;
}
```

### 2. CSP 캐싱

```typescript
// 정적 CSP 헤더는 next.config.ts에서 설정
// 동적 nonce가 필요한 경우만 proxy 사용
```

### 3. 검증 캐싱

```typescript
// 자주 검증되는 값 캐싱
const validatedEmails = new Set<string>();

export function isValidatedEmail(email: string): boolean {
  if (validatedEmails.has(email)) return true;

  const result = emailSchema.safeParse(email);
  if (result.success) {
    validatedEmails.add(email);
  }
  return result.success;
}
```

---

## 보안 고려사항

### 1. 의존성 감사

```bash
# 정기적 보안 감사
npm audit --audit-level=high

# CI에서 자동 검사
- name: Security audit
  run: npm audit --audit-level=high
```

### 2. 환경별 설정

```typescript
// lib/security/config.ts
export const securityConfig = {
  rateLimitRequests: process.env.NODE_ENV === 'production' ? 100 : 1000,
  csrfEnabled: process.env.NODE_ENV === 'production',
  httpsOnly: process.env.NODE_ENV === 'production',
};
```

### 3. 로그 마스킹

```typescript
// lib/security/logging.ts
export function maskSensitiveData(data: Record<string, unknown>): Record<string, unknown> {
  const sensitiveKeys = ['password', 'token', 'secret', 'apiKey', 'creditCard'];
  const masked = { ...data };

  for (const key of Object.keys(masked)) {
    if (sensitiveKeys.some((sk) => key.toLowerCase().includes(sk))) {
      masked[key] = '[REDACTED]';
    }
  }

  return masked;
}
```

### 4. 보안 헤더 검증

```typescript
// scripts/check-security-headers.ts
const requiredHeaders = [
  'Strict-Transport-Security',
  'X-Content-Type-Options',
  'X-Frame-Options',
  'Content-Security-Policy',
];

async function checkHeaders(url: string) {
  const response = await fetch(url);

  for (const header of requiredHeaders) {
    if (!response.headers.has(header)) {
      console.error(`Missing: ${header}`);
    }
  }
}
```

---

## References

- `_references/ARCHITECTURE-PATTERN.md`
- `_references/SERVER-ACTION-PATTERN.md`
- `_references/TEST-PATTERN.md`
