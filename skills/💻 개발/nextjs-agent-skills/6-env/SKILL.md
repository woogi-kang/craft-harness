---
name: env
description: |
  T3 Env를 사용하여 타입 안전한 환경 변수를 설정합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Environment Variables Skill

T3 Env를 사용하여 타입 안전한 환경 변수를 설정합니다.

## Triggers

- "환경 변수", "env 설정", "t3 env", "environment"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | Next.js 프로젝트 경로 |
| `variables` | ❌ | 추가할 환경 변수 목록 |

---

## 설치

```bash
npm install @t3-oss/env-nextjs zod
```

---

## 환경 변수 스키마

```typescript
// env.ts
import { createEnv } from '@t3-oss/env-nextjs';
import { z } from 'zod';

export const env = createEnv({
  /**
   * 서버 환경 변수 (클라이언트에서 접근 불가)
   */
  server: {
    // Database
    DATABASE_URL: z.string().url(),

    // Auth
    AUTH_SECRET: z.string().min(32),
    GOOGLE_CLIENT_ID: z.string().optional(),
    GOOGLE_CLIENT_SECRET: z.string().optional(),
    GITHUB_CLIENT_ID: z.string().optional(),
    GITHUB_CLIENT_SECRET: z.string().optional(),

    // External APIs
    STRIPE_SECRET_KEY: z.string().optional(),
    RESEND_API_KEY: z.string().optional(),

    // Storage
    UPLOADTHING_SECRET: z.string().optional(),
    UPLOADTHING_APP_ID: z.string().optional(),

    // Node
    NODE_ENV: z.enum(['development', 'test', 'production']).default('development'),
  },

  /**
   * 클라이언트 환경 변수 (NEXT_PUBLIC_ 접두사 필수)
   */
  client: {
    NEXT_PUBLIC_APP_URL: z.string().url(),
    NEXT_PUBLIC_APP_NAME: z.string().default('My App'),
    NEXT_PUBLIC_POSTHOG_KEY: z.string().optional(),
    NEXT_PUBLIC_POSTHOG_HOST: z.string().optional(),
  },

  /**
   * 런타임 환경 변수 (Next.js 빌드 시 필수)
   */
  runtimeEnv: {
    // Server
    DATABASE_URL: process.env.DATABASE_URL,
    AUTH_SECRET: process.env.AUTH_SECRET,
    GOOGLE_CLIENT_ID: process.env.GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET,
    GITHUB_CLIENT_ID: process.env.GITHUB_CLIENT_ID,
    GITHUB_CLIENT_SECRET: process.env.GITHUB_CLIENT_SECRET,
    STRIPE_SECRET_KEY: process.env.STRIPE_SECRET_KEY,
    RESEND_API_KEY: process.env.RESEND_API_KEY,
    UPLOADTHING_SECRET: process.env.UPLOADTHING_SECRET,
    UPLOADTHING_APP_ID: process.env.UPLOADTHING_APP_ID,
    NODE_ENV: process.env.NODE_ENV,

    // Client
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL,
    NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME,
    NEXT_PUBLIC_POSTHOG_KEY: process.env.NEXT_PUBLIC_POSTHOG_KEY,
    NEXT_PUBLIC_POSTHOG_HOST: process.env.NEXT_PUBLIC_POSTHOG_HOST,
  },

  /**
   * 빈 문자열을 undefined로 처리
   */
  emptyStringAsUndefined: true,

  /**
   * 빌드 시 검증 건너뛰기 (CI/CD용)
   */
  skipValidation: !!process.env.SKIP_ENV_VALIDATION,
});
```

---

## 빌드 시 검증

```typescript
// next.config.ts
import './env';

const nextConfig = {
  // ...
};

export default nextConfig;
```

이렇게 하면 빌드 시 환경 변수가 누락되면 에러가 발생합니다.

---

## 사용 방법

### 서버 컴포넌트/API

```typescript
// app/api/users/route.ts
import { env } from '@/env';

export async function GET() {
  // ✅ 타입 안전 + 자동완성
  const dbUrl = env.DATABASE_URL;
  const authSecret = env.AUTH_SECRET;

  // ...
}
```

### 클라이언트 컴포넌트

```tsx
// components/analytics.tsx
'use client';

import { env } from '@/env';

export function Analytics() {
  // ✅ NEXT_PUBLIC_ 변수만 접근 가능
  const appUrl = env.NEXT_PUBLIC_APP_URL;
  const appName = env.NEXT_PUBLIC_APP_NAME;

  // ❌ 서버 변수 접근 시 타입 에러
  // const dbUrl = env.DATABASE_URL; // Error!

  return <script data-app-url={appUrl} />;
}
```

---

## 환경별 파일

```
.env                    # 기본값 (Git 추적 가능)
.env.local             # 로컬 개발 (Git 무시)
.env.development       # 개발 환경
.env.production        # 프로덕션 환경
.env.test              # 테스트 환경
```

### .env.example

```bash
# Database
DATABASE_URL="postgresql://user:password@host:5432/database?sslmode=require"

# Auth
AUTH_SECRET="your-auth-secret-at-least-32-characters-long"
GOOGLE_CLIENT_ID=""
GOOGLE_CLIENT_SECRET=""
GITHUB_CLIENT_ID=""
GITHUB_CLIENT_SECRET=""

# App
NEXT_PUBLIC_APP_URL="http://localhost:3000"
NEXT_PUBLIC_APP_NAME="My App"

# External Services (Optional)
STRIPE_SECRET_KEY=""
RESEND_API_KEY=""
```

### .env.local

```bash
# 실제 값 (Git에 추가하지 않음)
DATABASE_URL="postgresql://..."
AUTH_SECRET="actual-secret-value..."
NEXT_PUBLIC_APP_URL="http://localhost:3000"
```

---

## 테스트 환경

```typescript
// tests/setup.ts
process.env.DATABASE_URL = 'postgresql://test:test@localhost:5432/test';
process.env.AUTH_SECRET = 'test-secret-at-least-32-characters-long';
process.env.NEXT_PUBLIC_APP_URL = 'http://localhost:3000';
```

---

## CI/CD 설정

### GitHub Actions

```yaml
# .github/workflows/test.yml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  AUTH_SECRET: ${{ secrets.AUTH_SECRET }}
  NEXT_PUBLIC_APP_URL: ${{ vars.NEXT_PUBLIC_APP_URL }}
```

### Vercel

Vercel 대시보드 → Settings → Environment Variables에서 설정

---

## 고급: Preset 사용

```typescript
// env.ts
import { createEnv } from '@t3-oss/env-nextjs';
import { vercel } from '@t3-oss/env-nextjs/presets';

export const env = createEnv({
  extends: [vercel()], // Vercel 환경 변수 자동 포함
  server: {
    DATABASE_URL: z.string().url(),
    // ...
  },
  // ...
});
```

Vercel Preset 포함 변수:
- `VERCEL`
- `VERCEL_ENV`
- `VERCEL_URL`
- `VERCEL_GIT_COMMIT_SHA`
- 등등

---

## 베스트 프랙티스

1. **모든 환경 변수는 env.ts에 정의** - `process.env` 직접 사용 금지
2. **기본값 활용** - `.default()` 메서드로 기본값 설정
3. **선택적 변수 명시** - `.optional()` 메서드 사용
4. **민감 정보 보호** - 서버 변수는 `server`에, 공개 변수만 `client`에
5. **.env.example 유지** - 필요한 변수 문서화

---

## 테스트 예제

### 환경 변수 검증 테스트

```typescript
// tests/env.test.ts
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { z } from 'zod';

describe('Environment Variables', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    vi.resetModules();
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  it('validates DATABASE_URL format', () => {
    const schema = z.string().url().startsWith('postgresql://');

    expect(() =>
      schema.parse('postgresql://user:pass@localhost:5432/db')
    ).not.toThrow();

    expect(() =>
      schema.parse('invalid-url')
    ).toThrow();
  });

  it('validates AUTH_SECRET minimum length', () => {
    const schema = z.string().min(32);

    expect(() =>
      schema.parse('a'.repeat(32))
    ).not.toThrow();

    expect(() =>
      schema.parse('short')
    ).toThrow();
  });

  it('validates NEXT_PUBLIC_ prefix for client variables', () => {
    // Client 변수는 NEXT_PUBLIC_ 접두사 필수
    const clientVars = ['APP_URL', 'API_URL'];

    clientVars.forEach((v) => {
      const publicVar = `NEXT_PUBLIC_${v}`;
      expect(publicVar).toMatch(/^NEXT_PUBLIC_/);
    });
  });

  it('coerces string to number correctly', () => {
    const schema = z.coerce.number().int().positive();

    expect(schema.parse('3000')).toBe(3000);
    expect(() => schema.parse('invalid')).toThrow();
  });
});

describe('Environment Loading', () => {
  it('loads from .env.local in development', async () => {
    process.env.NODE_ENV = 'development';
    // .env.local이 .env보다 우선순위 높음
    expect(process.env.NODE_ENV).toBe('development');
  });

  it('has skip validation option for CI', () => {
    process.env.SKIP_ENV_VALIDATION = 'true';
    expect(process.env.SKIP_ENV_VALIDATION).toBe('true');
  });
});
```

---

## 안티패턴 (❌ Bad → ✅ Good)

### 1. process.env 직접 사용

```typescript
// ❌ Bad: 타입 안전하지 않음
const apiUrl = process.env.API_URL;  // string | undefined
fetch(`${apiUrl}/users`);  // 런타임 에러 가능

// ✅ Good: T3 Env로 타입 안전하게
import { env } from '@/env';
const apiUrl = env.NEXT_PUBLIC_APP_URL;  // string (검증됨)
```

### 2. 하드코딩된 값

```typescript
// ❌ Bad: 환경별 값 하드코딩
const stripeKey = process.env.NODE_ENV === 'production'
  ? 'sk_live_xxx'
  : 'sk_test_xxx';

// ✅ Good: 환경 변수로 분리
// .env.production: STRIPE_SECRET_KEY=sk_live_xxx
// .env.development: STRIPE_SECRET_KEY=sk_test_xxx
import { env } from '@/env';
const stripeKey = env.STRIPE_SECRET_KEY;
```

### 3. 클라이언트에서 서버 변수 접근 시도

```typescript
// ❌ Bad: 클라이언트에서 서버 변수 접근 (undefined)
'use client';
const dbUrl = process.env.DATABASE_URL;  // undefined!

// ✅ Good: NEXT_PUBLIC_ 접두사 사용 또는 서버에서 처리
'use client';
import { env } from '@/env';
const appUrl = env.NEXT_PUBLIC_APP_URL;  // 타입 에러로 방지됨
```

### 4. 중복 정의

```typescript
// ❌ Bad: 여러 곳에서 환경 변수 정의
// api/route.ts
const DB_URL = z.string().parse(process.env.DATABASE_URL);

// lib/db.ts
const dbUrl = process.env.DATABASE_URL!;

// ✅ Good: 단일 소스 (env.ts)
// env.ts에서만 정의, 전체 앱에서 import
import { env } from '@/env';
```

### 5. 빌드 시 검증 건너뛰기

```typescript
// ❌ Bad: 항상 검증 건너뛰기
skipValidation: true,  // 런타임에 undefined 에러

// ✅ Good: CI에서만 조건부 건너뛰기
skipValidation: !!process.env.SKIP_ENV_VALIDATION,
// CI 워크플로우에서: SKIP_ENV_VALIDATION=true npm run build
```

---

## 에러 처리

### 누락된 환경 변수 에러

```typescript
// env.ts
import { createEnv } from '@t3-oss/env-nextjs';
import { z } from 'zod';

export const env = createEnv({
  server: {
    DATABASE_URL: z.string().url({
      message: 'DATABASE_URL은 유효한 PostgreSQL URL이어야 합니다',
    }),
    AUTH_SECRET: z.string().min(32, {
      message: 'AUTH_SECRET은 최소 32자 이상이어야 합니다',
    }),
  },
  client: {
    NEXT_PUBLIC_APP_URL: z.string().url(),
  },
  runtimeEnv: {
    DATABASE_URL: process.env.DATABASE_URL,
    AUTH_SECRET: process.env.AUTH_SECRET,
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL,
  },
  // 커스텀 에러 처리
  onValidationError: (error) => {
    console.error('❌ 환경 변수 검증 실패:');
    console.error(error.flatten().fieldErrors);
    throw new Error('필수 환경 변수가 누락되었습니다');
  },
  onInvalidAccess: (variable) => {
    throw new Error(
      `❌ 클라이언트에서 서버 변수 ${variable}에 접근할 수 없습니다`
    );
  },
});
```

### 런타임 에러 fallback

```typescript
// 선택적 변수에 fallback 제공
export const env = createEnv({
  server: {
    SENTRY_DSN: z.string().url().optional(),
    LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
  },
  // ...
});

// 사용 시
const sentryDsn = env.SENTRY_DSN ?? undefined;
if (sentryDsn) {
  Sentry.init({ dsn: sentryDsn });
}
```

---

## 성능 고려사항

### 빌드 타임 검증

```typescript
// next.config.ts
// 빌드 시작할 때 한 번만 검증
import './env';

const nextConfig = {};
export default nextConfig;
```

### 환경 변수 번들링

```typescript
// 클라이언트 번들에 포함되는 NEXT_PUBLIC_ 변수는 최소화
client: {
  // 필요한 것만 포함
  NEXT_PUBLIC_APP_URL: z.string().url(),
  NEXT_PUBLIC_APP_NAME: z.string(),
  // 큰 설정 객체는 피함
},
```

---

## 보안 고려사항

### 서버 변수 보호

```typescript
// ✅ 서버 변수는 절대 클라이언트로 전달하지 않음
server: {
  DATABASE_URL: z.string(),        // DB 연결 정보
  AUTH_SECRET: z.string(),         // 인증 시크릿
  STRIPE_SECRET_KEY: z.string(),   // 결제 시크릿
  API_SECRET: z.string(),          // API 키
},
```

### Git 보안

```gitignore
# .gitignore
.env
.env.local
.env.*.local

# 절대 커밋하지 않음
.env.production.local
```

### 시크릿 로테이션

```typescript
// 여러 시크릿 키 지원 (마이그레이션용)
server: {
  AUTH_SECRET: z.string(),
  AUTH_SECRET_OLD: z.string().optional(),  // 이전 키
},

// 사용
const secrets = [env.AUTH_SECRET];
if (env.AUTH_SECRET_OLD) {
  secrets.push(env.AUTH_SECRET_OLD);
}
```

---

## References

- `_references/ARCHITECTURE-PATTERN.md` - Clean Architecture 가이드
- `_references/TEST-PATTERN.md` - 테스트 패턴
