---
name: server-action
description: |
  next-safe-action을 사용하여 타입 안전한 Server Actions를 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Server Action Skill

next-safe-action을 사용하여 타입 안전한 Server Actions를 구현합니다.

## Triggers

- "서버 액션", "server action", "next-safe-action", "mutation"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `actionName` | ✅ | 액션 이름 |
| `schema` | ✅ | 입력 스키마 |

---

## 설치

```bash
npm install next-safe-action zod @upstash/ratelimit @upstash/redis
```

### 환경 변수 설정

```bash
# .env.local
# Upstash Redis (https://console.upstash.com에서 발급)
UPSTASH_REDIS_REST_URL="https://your-redis.upstash.io"
UPSTASH_REDIS_REST_TOKEN="your-token"
```

> **Note**: Rate Limiting을 사용하지 않는 경우 `@upstash/ratelimit`, `@upstash/redis`는 선택사항입니다.

---

## Base Client 설정

```typescript
// lib/actions/safe-action.ts
import { createSafeActionClient, DEFAULT_SERVER_ERROR_MESSAGE } from 'next-safe-action';
import { auth } from '@/lib/auth';
import { headers } from 'next/headers';
import { z } from 'zod';

// 커스텀 에러 클래스
export class ActionError extends Error {
  constructor(
    message: string,
    public code: 'UNAUTHORIZED' | 'FORBIDDEN' | 'NOT_FOUND' | 'RATE_LIMITED' | 'VALIDATION' | 'INTERNAL' = 'INTERNAL'
  ) {
    super(message);
    this.name = 'ActionError';
  }
}

export const actionClient = createSafeActionClient({
  handleServerError: (e) => {
    console.error('Action error:', e);

    // ActionError는 그대로 반환
    if (e instanceof ActionError) {
      return e.message;
    }

    // Zod 에러
    if (e instanceof z.ZodError) {
      return e.issues.map((err) => err.message).join(', ');
    }

    // 개발 환경에서만 상세 에러 표시
    if (process.env.NODE_ENV === 'development') {
      return e.message;
    }

    return DEFAULT_SERVER_ERROR_MESSAGE;
  },
});

export const authActionClient = actionClient.use(async ({ next }) => {
  const session = await auth();
  if (!session?.user) {
    throw new ActionError('로그인이 필요합니다', 'UNAUTHORIZED');
  }
  return next({ ctx: { user: session.user } });
});

export const adminActionClient = authActionClient.use(async ({ next, ctx }) => {
  if (ctx.user.role !== 'admin') {
    throw new ActionError('권한이 없습니다', 'FORBIDDEN');
  }
  return next({ ctx });
});
```

---

## Rate Limiting Middleware

```typescript
// lib/actions/rate-limit.ts
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';
import { headers } from 'next/headers';
import { ActionError } from './safe-action';

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
});

// Rate Limiter 인스턴스들
export const rateLimiters = {
  // 일반 API: 분당 60회
  default: new Ratelimit({
    redis,
    limiter: Ratelimit.slidingWindow(60, '1 m'),
    prefix: 'action:default',
  }),

  // 인증 관련: 분당 5회 (브루트포스 방지)
  auth: new Ratelimit({
    redis,
    limiter: Ratelimit.slidingWindow(5, '1 m'),
    prefix: 'action:auth',
  }),

  // 데이터 생성: 분당 10회
  create: new Ratelimit({
    redis,
    limiter: Ratelimit.slidingWindow(10, '1 m'),
    prefix: 'action:create',
  }),

  // 민감한 작업: 시간당 10회
  sensitive: new Ratelimit({
    redis,
    limiter: Ratelimit.slidingWindow(10, '1 h'),
    prefix: 'action:sensitive',
  }),
};

type RateLimitType = keyof typeof rateLimiters;

export async function checkRateLimit(type: RateLimitType = 'default') {
  const headersList = await headers();
  const ip = headersList.get('x-forwarded-for')?.split(',')[0] ?? '127.0.0.1';

  const { success, remaining, reset } = await rateLimiters[type].limit(ip);

  if (!success) {
    const retryAfter = Math.ceil((reset - Date.now()) / 1000);
    throw new ActionError(
      `요청이 너무 많습니다. ${retryAfter}초 후 다시 시도해주세요.`,
      'RATE_LIMITED'
    );
  }

  return { remaining, reset };
}

// Rate Limited Action Client
export function createRateLimitedClient(type: RateLimitType = 'default') {
  return actionClient.use(async ({ next }) => {
    await checkRateLimit(type);
    return next({ ctx: {} });
  });
}

// Auth + Rate Limit 결합
export function createAuthRateLimitedClient(type: RateLimitType = 'default') {
  return authActionClient.use(async ({ next, ctx }) => {
    await checkRateLimit(type);
    return next({ ctx });
  });
}
```

---

## Rate Limited Action 예시

```typescript
// features/auth/actions/login.action.ts
'use server';

import { createRateLimitedClient } from '@/lib/actions/rate-limit';
import { z } from 'zod';

const loginSchema = z.object({
  email: z.string().email('유효한 이메일을 입력하세요'),
  password: z.string().min(8, '비밀번호는 8자 이상이어야 합니다'),
});

// auth 타입 Rate Limiter 사용 (분당 5회)
const rateLimitedAction = createRateLimitedClient('auth');

export const loginAction = rateLimitedAction
  .schema(loginSchema)
  .action(async ({ parsedInput }) => {
    const { email, password } = parsedInput;

    // 로그인 로직...
    const user = await authenticate(email, password);

    return { success: true, user };
  });
```

---

## Action 패턴

```typescript
// features/{feature}/actions/create-{feature}.action.ts
'use server';

import { actionClient } from '@/lib/actions/safe-action';
import { create{Feature}Schema } from '../schemas/{feature}.schema';
import { {feature}sService } from '../api/{feature}.service';
import { revalidatePath } from 'next/cache';

export const create{Feature}Action = actionClient
  .schema(create{Feature}Schema)
  .action(async ({ parsedInput }) => {
    const item = await {feature}sService.create{Feature}(parsedInput);
    revalidatePath('/{feature}s');
    return { success: true, data: item };
  });
```

---

## 클라이언트 사용 (useAction)

```tsx
'use client';

import { useAction } from 'next-safe-action/hooks';
import { create{Feature}Action } from '../actions';
import { toast } from 'sonner';

export function use{Feature}Form() {
  const { execute, isPending } = useAction(create{Feature}Action, {
    onSuccess: () => toast.success('생성되었습니다'),
    onError: ({ error }) => toast.error(error.serverError || '오류 발생'),
  });

  return { execute, isPending };
}
```

---

## 테스트 예제

### Server Action 유닛 테스트

```typescript
// features/posts/__tests__/create-post.action.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createPostAction } from '../actions/create-post.action';
import { postsService } from '../api/posts.service';

vi.mock('../api/posts.service');
vi.mock('@/lib/auth', () => ({
  auth: vi.fn(() => ({ user: { id: '1', role: 'user' } })),
}));

describe('createPostAction', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('creates post with valid input', async () => {
    const mockPost = { id: '1', title: 'Test', status: 'draft' };
    vi.mocked(postsService.createPost).mockResolvedValue(mockPost);

    const result = await createPostAction({
      title: 'Test Post',
      description: 'Description',
      status: 'draft',
    });

    expect(result).toEqual({ success: true, data: mockPost });
    expect(postsService.createPost).toHaveBeenCalledWith({
      title: 'Test Post',
      description: 'Description',
      status: 'draft',
    });
  });

  it('returns validation error for invalid input', async () => {
    const result = await createPostAction({
      title: '',  // 빈 제목
      status: 'draft',
    });

    expect(result.validationErrors).toBeDefined();
    expect(postsService.createPost).not.toHaveBeenCalled();
  });
});
```

### 인증된 Action 테스트

```typescript
// lib/actions/__tests__/auth-action.test.ts
import { describe, it, expect, vi } from 'vitest';
import { authActionClient, ActionError } from '../safe-action';

vi.mock('@/lib/auth', () => ({
  auth: vi.fn(),
}));

describe('authActionClient', () => {
  it('throws when not authenticated', async () => {
    const { auth } = await import('@/lib/auth');
    vi.mocked(auth).mockResolvedValue(null);

    const action = authActionClient.action(async () => ({ success: true }));

    await expect(action()).rejects.toThrow('로그인이 필요합니다');
  });

  it('passes user to context when authenticated', async () => {
    const { auth } = await import('@/lib/auth');
    vi.mocked(auth).mockResolvedValue({ user: { id: '1', role: 'admin' } });

    let capturedUser;
    const action = authActionClient.action(async ({ ctx }) => {
      capturedUser = ctx.user;
      return { success: true };
    });

    await action();
    expect(capturedUser).toEqual({ id: '1', role: 'admin' });
  });
});
```

---

## 안티패턴 (❌ Bad → ✅ Good)

### 1. 검증 없는 Server Action

```typescript
// ❌ Bad: 입력 검증 없음
'use server';
export async function createPost(data: any) {
  return db.insert(posts).values(data);  // 위험!
}

// ✅ Good: 스키마 검증 필수
'use server';
import { actionClient } from '@/lib/actions/safe-action';
import { createPostSchema } from '../schemas';

export const createPostAction = actionClient
  .schema(createPostSchema)  // 검증 포함
  .action(async ({ parsedInput }) => {
    return db.insert(posts).values(parsedInput);
  });
```

### 2. 에러 상세 정보 노출

```typescript
// ❌ Bad: 내부 에러 메시지 노출
handleServerError: (e) => e.message,  // DB 오류 등 노출!

// ✅ Good: 일반적인 메시지로 변환
handleServerError: (e) => {
  console.error('Action error:', e);

  if (e instanceof ActionError) return e.message;
  if (e instanceof z.ZodError) return '입력값이 올바르지 않습니다';

  return '오류가 발생했습니다';  // 일반 메시지
};
```

### 3. Rate Limiting 없음

```typescript
// ❌ Bad: 무제한 호출 가능
export const loginAction = actionClient
  .schema(loginSchema)
  .action(async ({ parsedInput }) => { ... });

// ✅ Good: Rate Limiting 적용
export const loginAction = createRateLimitedClient('auth')  // 분당 5회
  .schema(loginSchema)
  .action(async ({ parsedInput }) => { ... });
```

### 4. revalidate/updateTag 누락

```typescript
// ❌ Bad: 캐시 갱신 안 함
export const createPostAction = actionClient.action(async ({ parsedInput }) => {
  const post = await db.insert(posts).values(parsedInput);
  return { success: true, data: post };
  // 목록 페이지에 새 데이터 안 보임!
});

// ✅ Good: revalidatePath/updateTag 호출
import { revalidatePath, updateTag } from 'next/cache';

export const createPostAction = actionClient.action(async ({ parsedInput }) => {
  const post = await db.insert(posts).values(parsedInput);
  revalidatePath('/posts');  // 캐시 갱신
  updateTag('posts');        // Server Action 내 즉시 태그 갱신
  return { success: true, data: post };
});
```

Next.js 16에서 `revalidateTag`는 profile 인자가 필요합니다. Server Action에서 즉시 일관성이 필요하면 `updateTag`, stale-while-revalidate가 필요하면 `revalidateTag(tag, 'max')`를 사용합니다.

---

## 에러 처리

### ActionError 계층 구조

```typescript
// lib/actions/errors.ts
export class ActionError extends Error {
  constructor(
    message: string,
    public code: ActionErrorCode,
    public statusCode: number = 400
  ) {
    super(message);
    this.name = 'ActionError';
  }
}

export type ActionErrorCode =
  | 'UNAUTHORIZED'
  | 'FORBIDDEN'
  | 'NOT_FOUND'
  | 'RATE_LIMITED'
  | 'VALIDATION'
  | 'CONFLICT'
  | 'INTERNAL';

// 특화된 에러 클래스
export class NotFoundError extends ActionError {
  constructor(resource: string) {
    super(`${resource}을(를) 찾을 수 없습니다`, 'NOT_FOUND', 404);
  }
}
```

### 클라이언트 에러 핸들링

```tsx
const { execute, result, status } = useAction(createPostAction, {
  onError: ({ error }) => {
    // 에러 타입별 처리
    if (error.serverError?.includes('Rate')) {
      toast.error('요청이 너무 많습니다. 잠시 후 다시 시도하세요.');
    } else {
      toast.error(error.serverError || '오류가 발생했습니다');
    }
  },
});
```

---

## 성능 고려사항

### Optimistic Update와 함께 사용

```tsx
const { execute, optimisticState } = useOptimisticAction(updatePostAction, {
  currentState: post,
  updateFn: (state, input) => ({ ...state, ...input }),
});

// UI는 즉시 반영, 실패 시 롤백
return <div>{optimisticState.title}</div>;
```

---

## 보안 고려사항

### 권한 검증 필수

```typescript
// 관리자 전용 Action
export const deleteUserAction = adminActionClient
  .schema(z.object({ userId: z.string() }))
  .action(async ({ parsedInput, ctx }) => {
    // ctx.user.role === 'admin' 이미 검증됨
    await usersService.delete(parsedInput.userId);
    return { success: true };
  });
```

### 리소스 소유권 확인

```typescript
export const updatePostAction = authActionClient
  .schema(updatePostSchema)
  .action(async ({ parsedInput, ctx }) => {
    const post = await postsService.getPost(parsedInput.id);

    // 소유자 확인
    if (post.authorId !== ctx.user.id && ctx.user.role !== 'admin') {
      throw new ActionError('권한이 없습니다', 'FORBIDDEN', 403);
    }

    return postsService.updatePost(parsedInput);
  });
```

---

## References

- `_references/SERVER-ACTION-PATTERN.md` - next-safe-action 패턴 상세
- `_references/TEST-PATTERN.md` - 테스트 피라미드
