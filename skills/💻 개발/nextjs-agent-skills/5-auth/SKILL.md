---
name: auth
description: |
  인증 시스템을 설정합니다 (Auth.js v5 또는 Clerk).
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Auth Skill

인증 시스템을 설정합니다 (Auth.js v5 또는 Clerk).

## Triggers

- "인증 설정", "auth 설정", "로그인 구현", "next-auth", "clerk"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | Next.js 프로젝트 경로 |
| `provider` | ❌ | 인증 제공자 (authjs, clerk) |
| `oauthProviders` | ❌ | OAuth 제공자 (google, github 등) |

---

## Option 1: Auth.js v5

> ⚠️ **안정성 경고**: Auth.js v5는 현재 Beta 상태입니다. 프로덕션 사용은 가능하나 다음 사항을 고려하세요:
> - API 변경 가능성 존재
> - 커뮤니티 지원 및 문서가 제한적
> - 대안: [Clerk](https://clerk.com), [Supabase Auth](https://supabase.com/auth), [Better Auth](https://www.better-auth.com/)
>
> 안정적인 인증이 필요한 B2B SaaS는 Clerk, 빠른 프로토타이핑은 Supabase Auth 권장

### 설치

```bash
npm install next-auth@beta
# 정식 릴리스 시 npm install next-auth@latest 사용
```

### 설정 파일

```typescript
// lib/auth/auth.config.ts
import type { NextAuthConfig } from 'next-auth';
import Credentials from 'next-auth/providers/credentials';
import Google from 'next-auth/providers/google';
import GitHub from 'next-auth/providers/github';
import { z } from 'zod';
import { getUserByEmail } from './user';
import { verifyPassword } from './password';

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

export const authConfig: NextAuthConfig = {
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    }),
    GitHub({
      clientId: process.env.GITHUB_CLIENT_ID,
      clientSecret: process.env.GITHUB_CLIENT_SECRET,
    }),
    Credentials({
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        const parsed = loginSchema.safeParse(credentials);
        if (!parsed.success) return null;

        // DB에서 사용자 조회
        const user = await getUserByEmail(parsed.data.email);
        if (!user || !user.password) {
          return null;  // 사용자 없음 또는 OAuth 전용 계정
        }

        // 비밀번호 검증
        const isValid = await verifyPassword(parsed.data.password, user.password);
        if (!isValid) {
          return null;
        }

        return {
          id: user.id,
          email: user.email,
          name: user.name,
          image: user.image,
          role: user.role,
        };
      },
    }),
  ],
  pages: {
    signIn: '/login',
    error: '/login',
  },
  callbacks: {
    authorized({ auth, request: { nextUrl } }) {
      const isLoggedIn = !!auth?.user;
      const isOnDashboard = nextUrl.pathname.startsWith('/dashboard');

      if (isOnDashboard) {
        if (isLoggedIn) return true;
        return false; // 로그인 페이지로 리다이렉트
      }

      return true;
    },
    jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.role = user.role;
      }
      return token;
    },
    session({ session, token }) {
      if (token) {
        session.user.id = token.id as string;
        session.user.role = token.role as string;
      }
      return session;
    },
  },
};
```

### 비밀번호 유틸리티

```typescript
// lib/auth/password.ts
import bcrypt from 'bcryptjs';  // Edge 호환 (bcrypt 대신)

const SALT_ROUNDS = 12;

export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, SALT_ROUNDS);
}

export async function verifyPassword(
  password: string,
  hashedPassword: string
): Promise<boolean> {
  return bcrypt.compare(password, hashedPassword);
}
```

### 사용자 조회

```typescript
// lib/auth/user.ts
import { db } from '@/lib/db';
import { users } from '@/lib/db/schema';
import { eq } from 'drizzle-orm';

export async function getUserByEmail(email: string) {
  return db.query.users.findFirst({
    where: eq(users.email, email),
  });
}

export async function getUserById(id: string) {
  return db.query.users.findFirst({
    where: eq(users.id, id),
  });
}
```

### Auth 인스턴스

```typescript
// lib/auth/index.ts
import NextAuth from 'next-auth';
import { authConfig } from './auth.config';

export const { handlers, signIn, signOut, auth } = NextAuth(authConfig);

// Re-export utilities
export { hashPassword, verifyPassword } from './password';
export { getUserByEmail, getUserById } from './user';
```

### Proxy

```typescript
// proxy.ts
export { auth as proxy } from '@/lib/auth';

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
```

### API Route

```typescript
// app/api/auth/[...nextauth]/route.ts
import { handlers } from '@/lib/auth';

export const { GET, POST } = handlers;
```

### 타입 확장

```typescript
// types/next-auth.d.ts
import 'next-auth';

declare module 'next-auth' {
  interface User {
    id: string;
    role?: string;
  }

  interface Session {
    user: User & {
      id: string;
      role?: string;
    };
  }
}
```

### 서버 컴포넌트에서 사용

```tsx
// app/(dashboard)/page.tsx
import { auth } from '@/lib/auth';
import { redirect } from 'next/navigation';

export default async function DashboardPage() {
  const session = await auth();

  if (!session) {
    redirect('/login');
  }

  return (
    <div>
      <h1>안녕하세요, {session.user.name}님</h1>
    </div>
  );
}
```

### 클라이언트 컴포넌트에서 사용

```tsx
// components/user-menu.tsx
'use client';

import { useSession, signOut } from 'next-auth/react';
import { Button } from '@/components/ui/button';

export function UserMenu() {
  const { data: session, status } = useSession();

  if (status === 'loading') return null;

  if (!session) {
    return <Button href="/login">로그인</Button>;
  }

  return (
    <div className="flex items-center gap-4">
      <span>{session.user.name}</span>
      <Button variant="outline" onClick={() => signOut()}>
        로그아웃
      </Button>
    </div>
  );
}
```

---

## Option 2: Clerk

### 설치

```bash
npm install @clerk/nextjs
```

### 환경 변수

```bash
# .env.local
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_xxx
CLERK_SECRET_KEY=sk_xxx
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/login
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/register
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

### ClerkProvider

```tsx
// app/layout.tsx
import { ClerkProvider } from '@clerk/nextjs';
import { koKR } from '@clerk/localizations';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider localization={koKR}>
      <html lang="ko">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  );
}
```

### Proxy

```typescript
// proxy.ts
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';

const isProtectedRoute = createRouteMatcher(['/dashboard(.*)']);

export default clerkMiddleware(async (auth, req) => {
  if (isProtectedRoute(req)) {
    await auth.protect();
  }
});

export const config = {
  matcher: ['/((?!.*\\..*|_next).*)', '/', '/(api|trpc)(.*)'],
};
```

### 로그인 페이지

```tsx
// app/(auth)/login/page.tsx
import { SignIn } from '@clerk/nextjs';

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <SignIn />
    </div>
  );
}
```

### 사용자 메뉴

```tsx
// components/user-menu.tsx
import { UserButton, SignedIn, SignedOut, SignInButton } from '@clerk/nextjs';
import { Button } from '@/components/ui/button';

export function UserMenu() {
  return (
    <>
      <SignedIn>
        <UserButton afterSignOutUrl="/" />
      </SignedIn>
      <SignedOut>
        <SignInButton mode="modal">
          <Button>로그인</Button>
        </SignInButton>
      </SignedOut>
    </>
  );
}
```

### 서버에서 사용자 조회

```typescript
// lib/auth/clerk.ts
import { currentUser, auth } from '@clerk/nextjs/server';

export async function getUser() {
  const user = await currentUser();
  return user;
}

export async function getUserId() {
  const { userId } = await auth();
  return userId;
}
```

---

## 환경 변수

```bash
# Auth.js
AUTH_SECRET="your-auth-secret-32-characters"
GOOGLE_CLIENT_ID="xxx"
GOOGLE_CLIENT_SECRET="xxx"
GITHUB_CLIENT_ID="xxx"
GITHUB_CLIENT_SECRET="xxx"

# Clerk
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="pk_xxx"
CLERK_SECRET_KEY="sk_xxx"
```

---

## 비교

| 기능 | Auth.js v5 | Clerk |
|------|------------|-------|
| **가격** | 무료 | 10K MAU 무료, 이후 유료 |
| **셋업 시간** | 중간 | 빠름 |
| **커스터마이징** | 높음 | 중간 |
| **MFA** | 직접 구현 | 내장 |
| **조직 관리** | 직접 구현 | 내장 |
| **Edge 호환** | JWT만 가능 | 완벽 지원 |

**권장 선택:**
- **Auth.js**: 완전한 제어 필요, 비용 절감 중요
- **Clerk**: 빠른 출시, B2B SaaS, 조직 관리 필요

---

## 테스트 예제

### Auth 설정 테스트

```typescript
// lib/auth/__tests__/auth.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { authConfig } from '../auth.config';

describe('Auth Configuration', () => {
  it('has required providers', () => {
    const providerNames = authConfig.providers.map(
      (p) => (p as { id?: string }).id || p.name
    );
    expect(providerNames).toContain('google');
    expect(providerNames).toContain('credentials');
  });

  it('has custom sign-in page configured', () => {
    expect(authConfig.pages?.signIn).toBe('/login');
  });

  it('has required callbacks', () => {
    expect(authConfig.callbacks?.jwt).toBeDefined();
    expect(authConfig.callbacks?.session).toBeDefined();
    expect(authConfig.callbacks?.authorized).toBeDefined();
  });
});

describe('Authorized Callback', () => {
  const authorized = authConfig.callbacks!.authorized!;

  it('allows access to public routes', async () => {
    const result = await authorized({
      auth: null,
      request: { nextUrl: new URL('http://localhost:3000/') } as any,
    });
    expect(result).toBe(true);
  });

  it('blocks dashboard access for unauthenticated users', async () => {
    const result = await authorized({
      auth: null,
      request: { nextUrl: new URL('http://localhost:3000/dashboard') } as any,
    });
    expect(result).toBe(false);
  });

  it('allows dashboard access for authenticated users', async () => {
    const result = await authorized({
      auth: { user: { id: '1', email: 'test@test.com' } } as any,
      request: { nextUrl: new URL('http://localhost:3000/dashboard') } as any,
    });
    expect(result).toBe(true);
  });
});
```

### Credentials 검증 테스트

```typescript
// lib/auth/__tests__/credentials.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { hashPassword, verifyPassword } from '../password';

describe('Password Utilities', () => {
  it('hashes password correctly', async () => {
    const password = 'TestPassword123!';
    const hash = await hashPassword(password);

    expect(hash).not.toBe(password);
    expect(hash).toMatch(/^\$2[aby]?\$/);
  });

  it('verifies correct password', async () => {
    const password = 'TestPassword123!';
    const hash = await hashPassword(password);

    const isValid = await verifyPassword(password, hash);
    expect(isValid).toBe(true);
  });

  it('rejects incorrect password', async () => {
    const password = 'TestPassword123!';
    const hash = await hashPassword(password);

    const isValid = await verifyPassword('WrongPassword', hash);
    expect(isValid).toBe(false);
  });
});
```

### 통합 테스트

```typescript
// tests/e2e/auth.spec.ts (Playwright)
import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('redirects unauthenticated users to login', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/login/);
  });

  test('shows login form', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByRole('textbox', { name: /email/i })).toBeVisible();
    await expect(page.getByRole('textbox', { name: /password/i })).toBeVisible();
  });

  test('shows validation errors for empty form', async ({ page }) => {
    await page.goto('/login');
    await page.getByRole('button', { name: /로그인/i }).click();
    await expect(page.getByText(/이메일을 입력하세요/i)).toBeVisible();
  });
});
```

---

## 안티패턴 (❌ Bad → ✅ Good)

### 1. 클라이언트에서 세션 직접 조회

```typescript
// ❌ Bad: 매 요청마다 세션 조회
'use client';
export function UserAvatar() {
  const [user, setUser] = useState(null);
  useEffect(() => {
    fetch('/api/auth/session').then(r => r.json()).then(setUser);
  }, []);
  return <Avatar src={user?.image} />;
}

// ✅ Good: useSession 훅 사용 (캐시됨)
'use client';
import { useSession } from 'next-auth/react';

export function UserAvatar() {
  const { data: session } = useSession();
  return <Avatar src={session?.user?.image} />;
}
```

### 2. 미들웨어 없이 페이지별 인증 체크

```typescript
// ❌ Bad: 모든 페이지에서 수동 체크
export default async function DashboardPage() {
  const session = await auth();
  if (!session) redirect('/login');  // 반복되는 코드
  // ...
}

// ✅ Good: Proxy에서 일괄 처리
// proxy.ts
export { auth as proxy } from '@/lib/auth';

export const config = {
  matcher: ['/dashboard/:path*', '/settings/:path*'],
};
```

### 3. JWT에 민감 정보 포함

```typescript
// ❌ Bad: JWT에 비밀번호/카드정보 포함
callbacks: {
  jwt({ token, user }) {
    if (user) {
      token.password = user.password;  // 절대 금지!
      token.cardNumber = user.cardNumber;
    }
    return token;
  },
}

// ✅ Good: 최소한의 정보만 포함
callbacks: {
  jwt({ token, user }) {
    if (user) {
      token.id = user.id;
      token.role = user.role;  // 권한만
    }
    return token;
  },
}
```

### 4. Credentials 에러 메시지 노출

```typescript
// ❌ Bad: 구체적인 에러 메시지 (계정 탐색 공격 취약)
async authorize(credentials) {
  const user = await getUserByEmail(email);
  if (!user) throw new Error('사용자를 찾을 수 없습니다');
  if (!await verifyPassword(password, user.password)) {
    throw new Error('비밀번호가 틀렸습니다');
  }
}

// ✅ Good: 일반적인 에러 메시지
async authorize(credentials) {
  const user = await getUserByEmail(email);
  if (!user) return null;  // 동일한 응답
  if (!await verifyPassword(password, user.password)) return null;
  return user;
}
```

### 5. OAuth 상태 검증 누락

```typescript
// ❌ Bad: state 파라미터 검증 없음
// (CSRF 공격 취약)

// ✅ Good: Auth.js 사용 (자동으로 state 검증)
// Auth.js가 자동으로 OAuth state, PKCE를 처리합니다.
// 직접 OAuth 구현하지 마세요.
```

---

## 에러 처리

### 인증 에러 분류

```typescript
// lib/auth/errors.ts
export class AuthError extends Error {
  constructor(
    message: string,
    public code: AuthErrorCode,
    public statusCode: number = 401
  ) {
    super(message);
    this.name = 'AuthError';
  }
}

export type AuthErrorCode =
  | 'INVALID_CREDENTIALS'
  | 'ACCOUNT_LOCKED'
  | 'EMAIL_NOT_VERIFIED'
  | 'SESSION_EXPIRED'
  | 'INSUFFICIENT_PERMISSIONS';

// 사용 예시
export async function requireRole(role: string) {
  const session = await auth();
  if (!session) {
    throw new AuthError('로그인이 필요합니다', 'SESSION_EXPIRED');
  }
  if (session.user.role !== role) {
    throw new AuthError('권한이 없습니다', 'INSUFFICIENT_PERMISSIONS', 403);
  }
  return session;
}
```

### 로그인 실패 처리

```typescript
// app/(auth)/login/page.tsx
import { auth, signIn } from '@/lib/auth';
import { AuthError } from 'next-auth';

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string }>;
}) {
  const { error } = await searchParams;

  const errorMessages: Record<string, string> = {
    CredentialsSignin: '이메일 또는 비밀번호가 올바르지 않습니다.',
    OAuthAccountNotLinked: '이미 다른 방법으로 가입된 이메일입니다.',
    SessionRequired: '로그인이 필요합니다.',
    default: '로그인 중 오류가 발생했습니다.',
  };

  return (
    <div>
      {error && (
        <Alert variant="destructive">
          {errorMessages[error] || errorMessages.default}
        </Alert>
      )}
      {/* Login Form */}
    </div>
  );
}
```

---

## 성능 고려사항

### 세션 캐싱

```typescript
// lib/auth/auth.config.ts
export const authConfig: NextAuthConfig = {
  session: {
    strategy: 'jwt',  // JWT가 세션 DB 조회보다 빠름
    maxAge: 30 * 24 * 60 * 60,  // 30일
  },
  // JWT 토큰 크기 최소화
  callbacks: {
    jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.role = user.role;
        // 큰 객체 포함 금지
      }
      return token;
    },
  },
};
```

### Provider 최적화

```typescript
// 필요한 OAuth 스코프만 요청
Google({
  clientId: process.env.GOOGLE_CLIENT_ID,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  authorization: {
    params: {
      scope: 'openid email profile',  // 최소 스코프
    },
  },
}),
```

---

## 보안 고려사항

### Rate Limiting

```typescript
// proxy.ts
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(5, '1 m'),  // 분당 5회
});

export async function proxy(request: NextRequest) {
  // 로그인 엔드포인트 rate limiting
  if (request.nextUrl.pathname === '/api/auth/callback/credentials') {
    const ip = request.ip ?? '127.0.0.1';
    const { success } = await ratelimit.limit(ip);

    if (!success) {
      return new Response('Too Many Requests', { status: 429 });
    }
  }
}
```

### CSRF 보호

```typescript
// Auth.js는 자동으로 CSRF 토큰을 생성하고 검증합니다.
// 커스텀 폼 사용 시 csrfToken 포함:

import { getCsrfToken } from 'next-auth/react';

export default function LoginForm() {
  const [csrfToken, setCsrfToken] = useState('');

  useEffect(() => {
    getCsrfToken().then(setCsrfToken);
  }, []);

  return (
    <form method="post" action="/api/auth/callback/credentials">
      <input type="hidden" name="csrfToken" value={csrfToken} />
      {/* form fields */}
    </form>
  );
}
```

### 보안 헤더 설정

```typescript
// next.config.ts
const securityHeaders = [
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=63072000; includeSubDomains; preload',
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff',
  },
];

export default {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: securityHeaders,
      },
    ];
  },
};
```

---

## References

- `_references/ARCHITECTURE-PATTERN.md` - Clean Architecture 가이드
- `_references/TEST-PATTERN.md` - 테스트 피라미드
