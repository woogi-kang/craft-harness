---
name: schema
description: |
  Zod를 사용하여 타입 안전한 스키마를 정의합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Schema Skill

Zod 4를 사용하여 타입 안전한 스키마를 정의합니다.

## Triggers

- "스키마 정의", "zod 스키마", "유효성 검증", "validation"

---

## 버전 기준

- 기본 기준은 `zod@4.x`입니다.
- `ZodError`의 상세 오류는 `error.issues`를 사용합니다.
- 스키마는 클라이언트 폼, Server Action, Route Handler, 환경 변수 검증에서 공유합니다.

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `featureName` | ✅ | Feature 이름 |
| `fields` | ✅ | 필드 정의 목록 |

---

## 기본 스키마 패턴

```typescript
// features/{feature}/schemas/{feature}.schema.ts
import { z } from 'zod';

// 기본 엔티티 스키마
export const {feature}Schema = z.object({
  id: z.string().cuid2(),
  title: z.string().min(1, '제목을 입력하세요').max(255),
  description: z.string().optional(),
  status: z.enum(['draft', 'published', 'archived']).default('draft'),
  createdAt: z.date(),
  updatedAt: z.date(),
});

// 생성 스키마 (id, timestamps 제외)
export const create{Feature}Schema = {feature}Schema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

// 수정 스키마 (모든 필드 선택적)
export const update{Feature}Schema = create{Feature}Schema.partial();

// 필터/검색 스키마
export const {feature}FilterSchema = z.object({
  search: z.string().optional(),
  status: z.enum(['draft', 'published', 'archived']).optional(),
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().positive().max(100).default(20),
});

// 타입 추론
export type {Feature} = z.infer<typeof {feature}Schema>;
export type Create{Feature}Input = z.infer<typeof create{Feature}Schema>;
export type Update{Feature}Input = z.infer<typeof update{Feature}Schema>;
export type {Feature}Filter = z.infer<typeof {feature}FilterSchema>;
```

---

## 일반적인 검증 패턴

### 문자열

```typescript
const stringSchemas = {
  required: z.string().min(1, '필수 입력 항목입니다'),
  email: z.string().email('유효한 이메일을 입력하세요'),
  url: z.string().url('유효한 URL을 입력하세요'),
  phone: z.string().regex(/^01[0-9]-?\d{3,4}-?\d{4}$/, '유효한 전화번호를 입력하세요'),
  password: z.string()
    .min(8, '8자 이상 입력하세요')
    .regex(/[A-Z]/, '대문자를 포함하세요')
    .regex(/[a-z]/, '소문자를 포함하세요')
    .regex(/[0-9]/, '숫자를 포함하세요'),
  slug: z.string().regex(/^[a-z0-9-]+$/, '소문자, 숫자, 하이픈만 허용됩니다'),
};
```

### 숫자

```typescript
const numberSchemas = {
  positive: z.number().positive('양수를 입력하세요'),
  percentage: z.number().min(0).max(100),
  price: z.number().positive().multipleOf(0.01),
  integer: z.number().int(),
  // 문자열에서 숫자로 변환
  coerced: z.coerce.number(),
};
```

### 날짜

```typescript
const dateSchemas = {
  date: z.date(),
  dateString: z.string().datetime(),
  // ISO 문자열 → Date 변환
  coercedDate: z.coerce.date(),
  futureDate: z.date().min(new Date(), '미래 날짜를 선택하세요'),
};
```

### 배열

```typescript
const arraySchemas = {
  tags: z.array(z.string()).min(1, '최소 1개 선택하세요').max(10),
  uniqueIds: z.array(z.string().cuid2()).refine(
    (ids) => new Set(ids).size === ids.length,
    '중복된 항목이 있습니다'
  ),
};
```

---

## 고급 패턴

### 조건부 검증 (refine)

```typescript
const passwordConfirmSchema = z.object({
  password: z.string().min(8),
  confirmPassword: z.string(),
}).refine(
  (data) => data.password === data.confirmPassword,
  {
    message: '비밀번호가 일치하지 않습니다',
    path: ['confirmPassword'],
  }
);
```

### 여러 검증 (superRefine)

```typescript
const registrationSchema = z.object({
  email: z.string().email(),
  username: z.string().min(3),
}).superRefine(async (data, ctx) => {
  // 이메일 중복 체크
  const emailExists = await checkEmailExists(data.email);
  if (emailExists) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: '이미 사용 중인 이메일입니다',
      path: ['email'],
    });
  }

  // 사용자명 중복 체크
  const usernameExists = await checkUsernameExists(data.username);
  if (usernameExists) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: '이미 사용 중인 사용자명입니다',
      path: ['username'],
    });
  }
});
```

### Discriminated Union

```typescript
const notificationSchema = z.discriminatedUnion('type', [
  z.object({
    type: z.literal('email'),
    email: z.string().email(),
    subject: z.string(),
  }),
  z.object({
    type: z.literal('sms'),
    phone: z.string(),
    message: z.string().max(160),
  }),
  z.object({
    type: z.literal('push'),
    deviceToken: z.string(),
    title: z.string(),
    body: z.string(),
  }),
]);
```

### Transform

```typescript
const slugSchema = z.string().transform((val) =>
  val.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
);

const trimmedSchema = z.string().trim();

const currencySchema = z.string()
  .transform((val) => parseFloat(val.replace(/[^0-9.-]/g, '')));
```

---

## 클라이언트/서버 공유

```typescript
// features/users/schemas/user.schema.ts
import { z } from 'zod';

// 공통 스키마 (클라이언트 + 서버)
export const loginSchema = z.object({
  email: z.string().email('유효한 이메일을 입력하세요'),
  password: z.string().min(8, '8자 이상 입력하세요'),
});

export type LoginInput = z.infer<typeof loginSchema>;

// 클라이언트: React Hook Form에서 사용
// 서버: Server Action에서 사용
```

---

## 테스트 예제

### 스키마 검증 테스트

```typescript
// features/user/__tests__/user.schema.test.ts
import { describe, it, expect } from 'vitest';
import {
  userSchema,
  createUserSchema,
  updateUserSchema,
  userFilterSchema,
} from '../schemas/user.schema';

describe('User Schema', () => {
  describe('userSchema', () => {
    it('validates correct user data', () => {
      const validUser = {
        id: 'clx123abc',
        email: 'test@example.com',
        name: 'Test User',
        status: 'active',
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      expect(() => userSchema.parse(validUser)).not.toThrow();
    });

    it('rejects invalid email', () => {
      const invalidUser = {
        id: 'clx123abc',
        email: 'not-an-email',
        name: 'Test',
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      expect(() => userSchema.parse(invalidUser)).toThrow();
    });

    it('rejects empty name', () => {
      const result = userSchema.safeParse({
        id: 'clx123abc',
        email: 'test@example.com',
        name: '',
        createdAt: new Date(),
        updatedAt: new Date(),
      });

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].path).toContain('name');
      }
    });
  });

  describe('createUserSchema', () => {
    it('excludes id and timestamps', () => {
      const createData = {
        email: 'new@example.com',
        name: 'New User',
      };

      expect(() => createUserSchema.parse(createData)).not.toThrow();
    });

    it('requires email and name', () => {
      expect(() => createUserSchema.parse({})).toThrow();
      expect(() => createUserSchema.parse({ email: 'test@test.com' })).toThrow();
    });
  });

  describe('updateUserSchema', () => {
    it('allows partial updates', () => {
      expect(() => updateUserSchema.parse({ name: 'Updated' })).not.toThrow();
      expect(() => updateUserSchema.parse({})).not.toThrow();
    });
  });

  describe('userFilterSchema', () => {
    it('coerces string to number for pagination', () => {
      const result = userFilterSchema.parse({
        page: '2',
        limit: '10',
      });

      expect(result.page).toBe(2);
      expect(result.limit).toBe(10);
    });

    it('uses default pagination values', () => {
      const result = userFilterSchema.parse({});

      expect(result.page).toBe(1);
      expect(result.limit).toBe(20);
    });

    it('enforces max limit', () => {
      expect(() =>
        userFilterSchema.parse({ limit: 1000 })
      ).toThrow();
    });
  });
});

describe('Password Schema', () => {
  const passwordSchema = z.string()
    .min(8, '8자 이상')
    .regex(/[A-Z]/, '대문자 필수')
    .regex(/[a-z]/, '소문자 필수')
    .regex(/[0-9]/, '숫자 필수');

  it('validates strong password', () => {
    expect(() => passwordSchema.parse('StrongPass1')).not.toThrow();
  });

  it('rejects weak password', () => {
    expect(() => passwordSchema.parse('weak')).toThrow();
    expect(() => passwordSchema.parse('nouppercas1')).toThrow();
    expect(() => passwordSchema.parse('NOLOWERCASE1')).toThrow();
    expect(() => passwordSchema.parse('NoNumbers')).toThrow();
  });
});
```

### React Hook Form 통합 테스트

```typescript
// features/user/__tests__/user-form.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UserForm } from '../components/user-form';

describe('UserForm with Zod validation', () => {
  it('shows validation errors', async () => {
    const user = userEvent.setup();
    render(<UserForm onSubmit={vi.fn()} />);

    await user.click(screen.getByRole('button', { name: /제출/i }));

    await waitFor(() => {
      expect(screen.getByText(/이메일을 입력하세요/i)).toBeInTheDocument();
      expect(screen.getByText(/이름을 입력하세요/i)).toBeInTheDocument();
    });
  });

  it('validates email format', async () => {
    const user = userEvent.setup();
    render(<UserForm onSubmit={vi.fn()} />);

    await user.type(screen.getByLabelText(/이메일/i), 'invalid');
    await user.click(screen.getByRole('button', { name: /제출/i }));

    await waitFor(() => {
      expect(screen.getByText(/유효한 이메일/i)).toBeInTheDocument();
    });
  });

  it('submits valid data', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<UserForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/이메일/i), 'test@example.com');
    await user.type(screen.getByLabelText(/이름/i), 'Test User');
    await user.click(screen.getByRole('button', { name: /제출/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        email: 'test@example.com',
        name: 'Test User',
      });
    });
  });
});
```

---

## 안티패턴 (❌ Bad → ✅ Good)

### 1. any 타입 사용

```typescript
// ❌ Bad: 타입 안전성 없음
function createUser(data: any) {
  return db.insert(users).values(data);
}

// ✅ Good: 스키마 기반 타입
import { CreateUserInput, createUserSchema } from './user.schema';

function createUser(data: CreateUserInput) {
  const validated = createUserSchema.parse(data);
  return db.insert(users).values(validated);
}
```

### 2. 스키마 중복 정의

```typescript
// ❌ Bad: 같은 검증 여러 곳에서 정의
// form-component.tsx
const schema = z.object({ email: z.string().email() });
// api-route.ts
const validateEmail = (email: string) => /^.+@.+$/.test(email);

// ✅ Good: 단일 스키마 공유
// schemas/user.schema.ts
export const emailSchema = z.string().email('유효한 이메일을 입력하세요');

export const createUserSchema = z.object({
  email: emailSchema,
  // ...
});
```

### 3. 타입과 스키마 분리

```typescript
// ❌ Bad: 타입과 스키마가 따로
interface User {
  id: string;
  email: string;
  name: string;
}

const userSchema = z.object({
  id: z.string(),
  email: z.string(),  // User 인터페이스와 동기화 안 됨
  name: z.string(),
});

// ✅ Good: 스키마에서 타입 추론
const userSchema = z.object({
  id: z.string().cuid2(),
  email: z.string().email(),
  name: z.string().min(1),
});

type User = z.infer<typeof userSchema>;  // 항상 동기화됨
```

### 4. 에러 메시지 누락

```typescript
// ❌ Bad: 기본 에러 메시지 (영어, 불친절)
const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

// ✅ Good: 사용자 친화적 메시지
const schema = z.object({
  email: z.string().email('유효한 이메일을 입력하세요'),
  password: z.string().min(8, '비밀번호는 8자 이상이어야 합니다'),
});
```

### 5. 검증 없는 transform

```typescript
// ❌ Bad: 검증 없이 변환
const schema = z.string().transform((val) => parseInt(val, 10));
// "abc" → NaN

// ✅ Good: 검증 후 변환
const schema = z.string()
  .refine((val) => !isNaN(parseInt(val, 10)), '숫자를 입력하세요')
  .transform((val) => parseInt(val, 10));

// 또는 coerce 사용
const schema = z.coerce.number().int().positive();
```

---

## 에러 처리

### Zod 에러 포맷팅

```typescript
// lib/utils/zod-error.ts
import { ZodError, ZodIssue } from 'zod';

export function formatZodError(error: ZodError): Record<string, string> {
  const formatted: Record<string, string> = {};

  error.issues.forEach((issue: ZodIssue) => {
    const path = issue.path.join('.');
    if (!formatted[path]) {
      formatted[path] = issue.message;
    }
  });

  return formatted;
}

// 사용
try {
  createUserSchema.parse(data);
} catch (error) {
  if (error instanceof ZodError) {
    const errors = formatZodError(error);
    // { email: '유효한 이메일을 입력하세요', name: '필수 입력' }
    return { success: false, errors };
  }
  throw error;
}
```

### Server Action 에러 처리

```typescript
// features/user/actions/create-user.action.ts
'use server';

import { actionClient } from '@/lib/actions';
import { createUserSchema } from '../schemas/user.schema';

export const createUserAction = actionClient
  .schema(createUserSchema)
  .action(async ({ parsedInput }) => {
    // parsedInput은 이미 검증됨
    const user = await createUser(parsedInput);
    return { success: true, user };
  });

// 클라이언트에서
const { execute, result, status } = useAction(createUserAction);

if (result.validationErrors) {
  // 스키마 검증 실패
  console.log(result.validationErrors);
}
```

---

## 성능 고려사항

### 스키마 캐싱

```typescript
// ❌ Bad: 매번 스키마 생성
function validateUser(data: unknown) {
  const schema = z.object({
    email: z.string().email(),
    // ...
  });
  return schema.parse(data);
}

// ✅ Good: 모듈 레벨에서 한 번만 생성
const userSchema = z.object({
  email: z.string().email(),
  // ...
});

function validateUser(data: unknown) {
  return userSchema.parse(data);
}
```

### Lazy 스키마 (순환 참조)

```typescript
// 순환 참조가 있는 경우
const categorySchema: z.ZodType<Category> = z.lazy(() =>
  z.object({
    id: z.string(),
    name: z.string(),
    parent: categorySchema.nullable(),
    children: z.array(categorySchema),
  })
);
```

---

## 보안 고려사항

### 입력 정제

```typescript
// 위험한 문자 제거
const safeStringSchema = z.string()
  .trim()
  .transform((val) => val.replace(/<[^>]*>/g, ''));  // HTML 태그 제거

// SQL Injection 방지 (Drizzle ORM 사용 권장)
// 직접 쿼리 시 파라미터화 필수
```

### 최대 길이 제한

```typescript
// DoS 방지를 위한 길이 제한
const commentSchema = z.object({
  content: z.string().min(1).max(10000),  // 최대 10KB
  attachments: z.array(z.string().url()).max(5),  // 최대 5개
});
```

### 민감 데이터 처리

```typescript
// 비밀번호 로깅 방지
const loginSchema = z.object({
  email: z.string().email(),
  password: z.string(),
}).transform((data) => {
  // 로깅 시 비밀번호 마스킹
  console.log('Login attempt:', { email: data.email, password: '***' });
  return data;
});
```

---

## References

- `_references/ARCHITECTURE-PATTERN.md` - Clean Architecture 가이드
- `_references/TEST-PATTERN.md` - 테스트 패턴
