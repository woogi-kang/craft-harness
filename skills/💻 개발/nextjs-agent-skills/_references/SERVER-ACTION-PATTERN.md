# Server Action Pattern Reference

Server Actions + next-safe-action 패턴 및 샘플 코드 레퍼런스입니다.

## 개요

```
┌─────────────────────────────────────────────────────────────┐
│                    Server Actions                            │
│  • 서버에서 실행되는 비동기 함수                              │
│  • 폼 제출, 데이터 변경에 적합                                │
│  • 자동으로 POST 요청으로 처리                               │
│  • revalidatePath/revalidateTag로 캐시 무효화                │
├─────────────────────────────────────────────────────────────┤
│                   next-safe-action                           │
│  • 타입 안전한 Server Actions                                │
│  • Zod 스키마 유효성 검증                                    │
│  • 미들웨어 체인 지원                                        │
│  • 에러 핸들링 표준화                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## next-safe-action 설정

### 설치

```bash
npm install next-safe-action zod
```

### Base Client 설정

```typescript
// lib/actions/safe-action.ts
import { createSafeActionClient, DEFAULT_SERVER_ERROR_MESSAGE } from 'next-safe-action';
import { z } from 'zod';

// 기본 클라이언트
export const actionClient = createSafeActionClient({
  handleServerError: (e) => {
    console.error('Action error:', e.message);

    if (e instanceof Error) {
      return e.message;
    }

    return DEFAULT_SERVER_ERROR_MESSAGE;
  },
});

// 인증된 사용자용 클라이언트
export const authActionClient = actionClient
  .use(async ({ next }) => {
    const session = await auth(); // Auth.js

    if (!session?.user) {
      throw new Error('Unauthorized');
    }

    return next({
      ctx: {
        user: session.user,
      },
    });
  });

// 관리자용 클라이언트
export const adminActionClient = authActionClient
  .use(async ({ next, ctx }) => {
    if (ctx.user.role !== 'admin') {
      throw new Error('Forbidden');
    }

    return next({ ctx });
  });
```

---

## 기본 Server Action 패턴

### Create Action

```typescript
// features/users/actions/create-user.action.ts
'use server';

import { actionClient } from '@/lib/actions/safe-action';
import { createUserSchema } from '../schemas/user.schema';
import { usersService } from '../api/users.service';
import { revalidatePath } from 'next/cache';

export const createUserAction = actionClient
  .schema(createUserSchema)
  .action(async ({ parsedInput }) => {
    const user = await usersService.createUser(parsedInput);

    revalidatePath('/users');

    return {
      success: true,
      data: user,
    };
  });
```

### Update Action

```typescript
// features/users/actions/update-user.action.ts
'use server';

import { authActionClient } from '@/lib/actions/safe-action';
import { updateUserSchema } from '../schemas/user.schema';
import { usersService } from '../api/users.service';
import { revalidatePath } from 'next/cache';
import { z } from 'zod';

const updateUserInputSchema = z.object({
  id: z.string(),
  data: updateUserSchema,
});

export const updateUserAction = authActionClient
  .schema(updateUserInputSchema)
  .action(async ({ parsedInput: { id, data }, ctx }) => {
    // 권한 확인 (자신만 수정 가능)
    if (ctx.user.id !== id && ctx.user.role !== 'admin') {
      throw new Error('권한이 없습니다');
    }

    const user = await usersService.updateUser(id, data);

    revalidatePath('/users');
    revalidatePath(`/users/${id}`);

    return {
      success: true,
      data: user,
    };
  });
```

### Delete Action

```typescript
// features/users/actions/delete-user.action.ts
'use server';

import { adminActionClient } from '@/lib/actions/safe-action';
import { usersService } from '../api/users.service';
import { revalidatePath } from 'next/cache';
import { z } from 'zod';

export const deleteUserAction = adminActionClient
  .schema(z.object({ id: z.string() }))
  .action(async ({ parsedInput: { id } }) => {
    await usersService.deleteUser(id);

    revalidatePath('/users');

    return { success: true };
  });
```

---

## 폼 통합 패턴

### React Hook Form + next-safe-action

```tsx
// features/users/components/user-form.tsx
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAction } from 'next-safe-action/hooks';
import { createUserSchema, type CreateUserInput } from '../schemas/user.schema';
import { createUserAction } from '../actions/create-user.action';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

export function UserForm() {
  const form = useForm<CreateUserInput>({
    resolver: zodResolver(createUserSchema),
    defaultValues: {
      email: '',
      name: '',
    },
  });

  const { execute, isPending } = useAction(createUserAction, {
    onSuccess: ({ data }) => {
      toast.success('사용자가 생성되었습니다');
      form.reset();
    },
    onError: ({ error }) => {
      if (error.serverError) {
        toast.error(error.serverError);
      }
      if (error.validationErrors) {
        // 유효성 검증 에러 처리
        Object.entries(error.validationErrors).forEach(([field, errors]) => {
          form.setError(field as keyof CreateUserInput, {
            message: errors?.[0],
          });
        });
      }
    },
  });

  const onSubmit = (data: CreateUserInput) => {
    execute(data);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>이메일</FormLabel>
              <FormControl>
                <Input placeholder="email@example.com" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>이름</FormLabel>
              <FormControl>
                <Input placeholder="홍길동" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" disabled={isPending} className="w-full">
          {isPending ? '처리 중...' : '생성'}
        </Button>
      </form>
    </Form>
  );
}
```

### useAction Hook 사용

```tsx
// features/users/hooks/use-delete-user.ts
'use client';

import { useAction } from 'next-safe-action/hooks';
import { deleteUserAction } from '../actions/delete-user.action';
import { toast } from 'sonner';

export function useDeleteUser() {
  const { execute, isPending, hasSucceeded, hasErrored } = useAction(
    deleteUserAction,
    {
      onSuccess: () => {
        toast.success('사용자가 삭제되었습니다');
      },
      onError: ({ error }) => {
        toast.error(error.serverError || '삭제에 실패했습니다');
      },
    }
  );

  return {
    deleteUser: (id: string) => execute({ id }),
    isPending,
    hasSucceeded,
    hasErrored,
  };
}
```

### useOptimisticAction Hook

```tsx
// features/tasks/hooks/use-toggle-task.ts
'use client';

import { useOptimisticAction } from 'next-safe-action/hooks';
import { toggleTaskAction } from '../actions/toggle-task.action';
import type { Task } from '../types';

export function useToggleTask(task: Task) {
  const { execute, optimisticState, isPending } = useOptimisticAction(
    toggleTaskAction,
    {
      currentState: task,
      updateFn: (state, input) => ({
        ...state,
        completed: !state.completed,
      }),
    }
  );

  return {
    toggle: () => execute({ id: task.id }),
    task: optimisticState,
    isPending,
  };
}
```

---

## 미들웨어 패턴

### Rate Limiting

```typescript
// lib/actions/middlewares/rate-limit.ts
import { createSafeActionClient } from 'next-safe-action';
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';
import { headers } from 'next/headers';

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, '10 s'),
});

export const rateLimitedActionClient = actionClient
  .use(async ({ next, clientInput }) => {
    const headersList = await headers();
    const ip = headersList.get('x-forwarded-for') ?? 'unknown';
    const { success, limit, reset, remaining } = await ratelimit.limit(ip);

    if (!success) {
      throw new Error('Too many requests. Please try again later.');
    }

    return next({ ctx: { rateLimit: { limit, reset, remaining } } });
  });
```

### Logging

```typescript
// lib/actions/middlewares/logging.ts
export const loggingActionClient = actionClient
  .use(async ({ next, clientInput, metadata }) => {
    const startTime = performance.now();

    const result = await next();

    const duration = performance.now() - startTime;

    console.log({
      action: metadata?.actionName,
      input: clientInput,
      duration: `${duration.toFixed(2)}ms`,
      success: result.success,
    });

    return result;
  });
```

### 조합

```typescript
// lib/actions/safe-action.ts
export const protectedActionClient = actionClient
  .use(loggingMiddleware)
  .use(rateLimitMiddleware)
  .use(authMiddleware);
```

---

## 에러 처리 패턴

### 커스텀 에러 클래스

```typescript
// lib/errors.ts
export class ActionError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 400
  ) {
    super(message);
    this.name = 'ActionError';
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

export class ForbiddenError extends ActionError {
  constructor() {
    super('권한이 없습니다', 'FORBIDDEN', 403);
  }
}

export class ValidationError extends ActionError {
  constructor(message: string) {
    super(message, 'VALIDATION_ERROR', 422);
  }
}
```

### 에러 핸들러

```typescript
// lib/actions/safe-action.ts
import { createSafeActionClient } from 'next-safe-action';
import { ActionError } from '@/lib/errors';

export const actionClient = createSafeActionClient({
  handleServerError: (e) => {
    // 커스텀 에러 처리
    if (e instanceof ActionError) {
      return e.message;
    }

    // Prisma 에러 처리
    if (e.code === 'P2002') {
      return '이미 존재하는 데이터입니다';
    }
    if (e.code === 'P2025') {
      return '데이터를 찾을 수 없습니다';
    }

    // Drizzle 에러 처리
    if (e.message?.includes('UNIQUE constraint failed')) {
      return '이미 존재하는 데이터입니다';
    }
    if (e.message?.includes('FOREIGN KEY constraint failed')) {
      return '참조하는 데이터가 존재하지 않습니다';
    }
    if (e.message?.includes('NOT NULL constraint failed')) {
      return '필수 항목이 누락되었습니다';
    }

    // 개발 환경에서만 상세 에러 표시
    if (process.env.NODE_ENV === 'development') {
      console.error(e);
      return e.message;
    }

    // 프로덕션에서는 일반 에러 메시지
    return '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
  },
});
```

---

## 파일 업로드 패턴

```typescript
// features/files/actions/upload.action.ts
'use server';

import { authActionClient } from '@/lib/actions/safe-action';
import { z } from 'zod';
import { put } from '@vercel/blob';

const uploadSchema = z.object({
  file: z.instanceof(File),
  folder: z.string().optional(),
});

export const uploadFileAction = authActionClient
  .schema(uploadSchema)
  .action(async ({ parsedInput: { file, folder }, ctx }) => {
    const filename = `${folder ?? 'uploads'}/${Date.now()}-${file.name}`;

    const blob = await put(filename, file, {
      access: 'public',
    });

    return {
      url: blob.url,
      filename: blob.pathname,
    };
  });
```

### 클라이언트 사용

```tsx
// features/files/components/file-upload.tsx
'use client';

import { useAction } from 'next-safe-action/hooks';
import { uploadFileAction } from '../actions/upload.action';
import { Input } from '@/components/ui/input';

export function FileUpload({ onUpload }: { onUpload: (url: string) => void }) {
  const { execute, isPending } = useAction(uploadFileAction, {
    onSuccess: ({ data }) => {
      if (data?.url) {
        onUpload(data.url);
      }
    },
  });

  const handleChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      execute({ file });
    }
  };

  return (
    <Input
      type="file"
      onChange={handleChange}
      disabled={isPending}
    />
  );
}
```

---

## TanStack Query와 통합

```typescript
// features/users/hooks/use-create-user.ts
'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useAction } from 'next-safe-action/hooks';
import { createUserAction } from '../actions/create-user.action';
import { userKeys } from './user-keys';
import { toast } from 'sonner';

export function useCreateUser() {
  const queryClient = useQueryClient();

  // next-safe-action의 execute를 mutation으로 래핑
  return useMutation({
    mutationFn: async (data: CreateUserInput) => {
      const result = await createUserAction(data);

      if (result?.serverError) {
        throw new Error(result.serverError);
      }

      if (result?.validationErrors) {
        throw new Error('유효성 검증 실패');
      }

      return result?.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
      toast.success('사용자가 생성되었습니다');
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });
}
```

---

## 베스트 프랙티스

### 1. 액션 파일 구조

```
features/{feature}/
├── actions/
│   ├── create-{feature}.action.ts
│   ├── update-{feature}.action.ts
│   ├── delete-{feature}.action.ts
│   └── index.ts  # 재export
```

### 2. 네이밍 컨벤션

```typescript
// ✅ Good: 동사 + 명사 + Action
createUserAction
updateUserAction
deleteUserAction
toggleTaskAction
uploadFileAction

// ❌ Bad
userCreate
handleUser
doSomething
```

### 3. revalidate 전략

```typescript
import { revalidatePath, revalidateTag, updateTag } from 'next/cache';

// 단일 경로 무효화
revalidatePath('/users');

// 동적 경로 무효화
revalidatePath(`/users/${id}`);

// 레이아웃 무효화
revalidatePath('/users', 'layout');

// 태그 기반 stale-while-revalidate
revalidateTag('users', 'max');

// Server Action 안에서 즉시 읽기 일관성이 필요할 때
updateTag('users');
```

### 4. 응답 구조 표준화

```typescript
// 성공 응답
return {
  success: true,
  data: user,
  message: '성공적으로 생성되었습니다',
};

// 페이지네이션 응답
return {
  success: true,
  data: users,
  meta: {
    page: 1,
    limit: 10,
    total: 100,
    totalPages: 10,
  },
};
```
