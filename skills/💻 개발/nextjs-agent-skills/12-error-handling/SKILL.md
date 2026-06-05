---
name: error-handling
description: |
  Error Boundary와 Sentry를 사용하여 에러를 처리합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Error Handling Skill

Error Boundary와 Sentry를 사용하여 에러를 처리합니다.

## Triggers

- "에러 처리", "error handling", "error boundary", "sentry"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | Next.js 프로젝트 경로 |
| `useSentry` | ❌ | Sentry 사용 여부 |

---

## Next.js Error Boundary

### error.tsx (Route Error)

```tsx
// app/error.tsx
'use client';

import { useEffect } from 'react';
import * as Sentry from '@sentry/nextjs';
import { Button } from '@/components/ui/button';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Sentry에 에러 전송 (환경 변수 확인)
    if (process.env.NEXT_PUBLIC_SENTRY_DSN) {
      Sentry.captureException(error, {
        tags: { digest: error.digest },
      });
    }

    // 개발 환경에서만 콘솔 출력
    if (process.env.NODE_ENV === 'development') {
      console.error('[Error Boundary]:', error);
    }
  }, [error]);

  const isDev = process.env.NODE_ENV === 'development';

  return (
    <div className="flex min-h-screen flex-col items-center justify-center">
      <h2 className="text-2xl font-bold">문제가 발생했습니다</h2>
      <p className="text-muted-foreground mt-2">
        {isDev ? error.message : '일시적 오류가 발생했습니다. 다시 시도해주세요.'}
      </p>
      {/* 개발 환경에서만 스택 트레이스 표시 */}
      {isDev && error.stack && (
        <details className="mt-4 max-w-2xl rounded-lg bg-destructive/10 p-4 text-sm">
          <summary className="cursor-pointer font-mono">스택 트레이스</summary>
          <pre className="mt-2 overflow-auto whitespace-pre-wrap">{error.stack}</pre>
        </details>
      )}
      <Button onClick={reset} className="mt-4">
        다시 시도
      </Button>
    </div>
  );
}
```

### global-error.tsx (Root Error)

```tsx
// app/global-error.tsx
'use client';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body>
        <h2>심각한 오류가 발생했습니다</h2>
        <button onClick={reset}>다시 시도</button>
      </body>
    </html>
  );
}
```

### not-found.tsx

```tsx
// app/not-found.tsx
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center">
      <h2 className="text-4xl font-bold">404</h2>
      <p className="text-muted-foreground mt-2">페이지를 찾을 수 없습니다</p>
      <Button asChild className="mt-4">
        <Link href="/">홈으로</Link>
      </Button>
    </div>
  );
}
```

---

## Sentry 설정

```bash
npx @sentry/wizard@latest -i nextjs
```

```typescript
// sentry.client.config.ts
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 1.0,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  integrations: [Sentry.replayIntegration()],
});
```

---

## 커스텀 에러 클래스

```typescript
// lib/errors.ts
export class ActionError extends Error {
  constructor(message: string, public code: string, public statusCode = 400) {
    super(message);
  }
}

export class NotFoundError extends ActionError {
  constructor(resource: string) {
    super(`${resource}을(를) 찾을 수 없습니다`, 'NOT_FOUND', 404);
  }
}

export class UnauthorizedError extends ActionError {
  constructor() {
    super('인증이 필요합니다', 'UNAUTHORIZED', 401);
  }
}
```

---

## 테스트 예제

### Error Boundary 테스트

```tsx
// app/__tests__/error.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import Error from '../error';

describe('Error Boundary', () => {
  it('displays error message', () => {
    const error = new Error('Test error message');
    const reset = vi.fn();

    render(<Error error={error} reset={reset} />);

    expect(screen.getByText(/문제가 발생했습니다/)).toBeInTheDocument();
  });

  it('calls reset on button click', () => {
    const error = new Error('Test error');
    const reset = vi.fn();

    render(<Error error={error} reset={reset} />);
    fireEvent.click(screen.getByRole('button', { name: /다시 시도/ }));

    expect(reset).toHaveBeenCalledTimes(1);
  });

  it('shows stack trace in development', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';

    const error = new Error('Dev error');
    error.stack = 'Error: Dev error\n    at Component';

    render(<Error error={error} reset={vi.fn()} />);

    expect(screen.getByText(/스택 트레이스/)).toBeInTheDocument();

    process.env.NODE_ENV = originalEnv;
  });
});
```

### 커스텀 에러 클래스 테스트

```typescript
// lib/__tests__/errors.test.ts
import { describe, it, expect } from 'vitest';
import { ActionError, NotFoundError, UnauthorizedError } from '../errors';

describe('ActionError', () => {
  it('creates error with code and status', () => {
    const error = new ActionError('테스트 에러', 'VALIDATION', 400);

    expect(error.message).toBe('테스트 에러');
    expect(error.code).toBe('VALIDATION');
    expect(error.statusCode).toBe(400);
    expect(error).toBeInstanceOf(Error);
  });
});

describe('NotFoundError', () => {
  it('creates not found error with resource name', () => {
    const error = new NotFoundError('게시물');

    expect(error.message).toBe('게시물을(를) 찾을 수 없습니다');
    expect(error.code).toBe('NOT_FOUND');
    expect(error.statusCode).toBe(404);
  });
});
```

---

## 안티패턴 (❌ Bad → ✅ Good)

### 1. 에러 무시

```typescript
// ❌ Bad: 에러 삼킴
try {
  await riskyOperation();
} catch (e) {
  // 아무것도 안 함
}

// ✅ Good: 적절한 에러 처리
try {
  await riskyOperation();
} catch (e) {
  console.error('[Operation failed]:', e);
  Sentry.captureException(e);
  toast.error('작업에 실패했습니다');
}
```

### 2. 사용자에게 내부 에러 노출

```tsx
// ❌ Bad: 기술적 에러 메시지 표시
<div>Error: ECONNREFUSED 127.0.0.1:5432</div>

// ✅ Good: 사용자 친화적 메시지
const isDev = process.env.NODE_ENV === 'development';

<div>
  {isDev ? error.message : '일시적 오류가 발생했습니다. 다시 시도해주세요.'}
</div>
```

### 3. 전역 에러 핸들링 누락

```tsx
// ❌ Bad: 루트 error.tsx만 있음

// ✅ Good: 계층별 error.tsx
app/
├── error.tsx              # 기본 에러 처리
├── global-error.tsx       # 루트 레이아웃 에러
├── (dashboard)/
│   ├── error.tsx          # 대시보드 전용 에러 UI
│   └── settings/
│       └── error.tsx      # 설정 페이지 전용 에러 UI
```

### 4. Error Boundary에서 리렌더링 무한 루프

```tsx
// ❌ Bad: 에러 컴포넌트에서 에러 발생 가능
export default function Error({ error }: { error: Error }) {
  const data = useSomeHookThatMayThrow();  // 에러 가능!
  return <div>{error.message}</div>;
}

// ✅ Good: 에러 컴포넌트는 최소한의 로직만
export default function Error({ error, reset }: Props) {
  return (
    <div>
      <h2>문제가 발생했습니다</h2>
      <button onClick={reset}>다시 시도</button>
    </div>
  );
}
```

---

## 에러 처리

### 계층화된 에러 클래스

```typescript
// lib/errors/index.ts
export abstract class AppError extends Error {
  abstract readonly code: string;
  abstract readonly statusCode: number;

  constructor(message: string) {
    super(message);
    this.name = this.constructor.name;
  }

  toJSON() {
    return {
      name: this.name,
      message: this.message,
      code: this.code,
      statusCode: this.statusCode,
    };
  }
}

export class ValidationError extends AppError {
  readonly code = 'VALIDATION_ERROR';
  readonly statusCode = 400;

  constructor(public readonly errors: Record<string, string>) {
    super('입력값이 올바르지 않습니다');
  }
}

export class AuthenticationError extends AppError {
  readonly code = 'AUTHENTICATION_ERROR';
  readonly statusCode = 401;

  constructor() {
    super('인증이 필요합니다');
  }
}

export class AuthorizationError extends AppError {
  readonly code = 'AUTHORIZATION_ERROR';
  readonly statusCode = 403;

  constructor(resource?: string) {
    super(resource ? `${resource}에 대한 권한이 없습니다` : '권한이 없습니다');
  }
}
```

### API Route 에러 핸들러

```typescript
// lib/api/error-handler.ts
import { NextResponse } from 'next/server';
import { AppError } from '@/lib/errors';

export function handleApiError(error: unknown) {
  console.error('[API Error]:', error);

  if (error instanceof AppError) {
    return NextResponse.json(
      { error: { message: error.message, code: error.code } },
      { status: error.statusCode }
    );
  }

  if (error instanceof z.ZodError) {
    return NextResponse.json(
      { error: { message: '입력값 검증 실패', errors: error.flatten().fieldErrors } },
      { status: 400 }
    );
  }

  // 알 수 없는 에러
  return NextResponse.json(
    { error: { message: '서버 오류가 발생했습니다', code: 'INTERNAL_ERROR' } },
    { status: 500 }
  );
}
```

---

## 성능 고려사항

### Sentry 선택적 로딩

```typescript
// 프로덕션에서만 Sentry 초기화
if (process.env.NODE_ENV === 'production' && process.env.NEXT_PUBLIC_SENTRY_DSN) {
  Sentry.init({
    dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
    tracesSampleRate: 0.1,  // 샘플링으로 비용 절감
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,
  });
}
```

---

## 보안 고려사항

### 에러 정보 필터링

```typescript
// 프로덕션에서 스택 트레이스 제거
function sanitizeError(error: Error): Error {
  if (process.env.NODE_ENV === 'production') {
    return new Error(getPublicMessage(error));
  }
  return error;
}

function getPublicMessage(error: Error): string {
  if (error instanceof AppError) return error.message;
  return '오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
}
```

### 민감 정보 로깅 방지

```typescript
// 민감 필드 마스킹
function sanitizeForLogging(data: Record<string, unknown>) {
  const sensitiveFields = ['password', 'token', 'secret', 'apiKey'];
  const sanitized = { ...data };

  for (const field of sensitiveFields) {
    if (field in sanitized) {
      sanitized[field] = '***';
    }
  }

  return sanitized;
}
```

---

## References

- `_references/ARCHITECTURE-PATTERN.md` - Clean Architecture 가이드
- `_references/TEST-PATTERN.md` - 테스트 피라미드
