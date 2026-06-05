---
name: architecture
description: |
  Clean Architecture 기반 프로젝트 구조를 설계합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Architecture Skill

Extends: `../../_shared/architecture/SKILL.md` (공통 아키텍처 원칙 참조)

Clean Architecture 기반 프로젝트 구조를 설계합니다.

## Triggers

- "아키텍처 설계", "구조 설계", "clean architecture", "폴더 구조"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | Next.js 프로젝트 경로 |
| `features` | ❌ | 초기 생성할 Feature 목록 |

---

## 레이어 구조

```
┌─────────────────────────────────────┐
│           UI Layer                   │
│  Page (RSC) ◄──► Hook (Client)      │
│  Component ◄──► TanStack Query      │
└─────────────────────────────────────┘
                  │
┌─────────────────────────────────────┐
│         Domain Layer                 │
│  Service → Server Action            │
│        Schema (Zod)                 │
└─────────────────────────────────────┘
                  │
┌─────────────────────────────────────┐
│          Data Layer                  │
│  Repository (Drizzle) → DB          │
└─────────────────────────────────────┘
```

## Feature 구조

```
features/{feature}/
├── actions/                  # Server Actions
│   ├── create-{feature}.action.ts
│   ├── update-{feature}.action.ts
│   ├── delete-{feature}.action.ts
│   └── index.ts
│
├── api/                      # Data Layer
│   ├── {feature}.repository.ts
│   ├── {feature}.service.ts
│   └── index.ts
│
├── components/               # Feature UI
│   ├── {feature}-list.tsx
│   ├── {feature}-form.tsx
│   ├── {feature}-card.tsx
│   └── index.ts
│
├── hooks/                    # Client Hooks
│   ├── use-{feature}.ts
│   ├── use-{feature}-mutations.ts
│   ├── {feature}-keys.ts
│   └── index.ts
│
├── schemas/                  # Zod Schemas
│   └── {feature}.schema.ts
│
├── stores/                   # Zustand Stores
│   └── {feature}.store.ts
│
├── types/                    # TypeScript Types
│   └── {feature}.types.ts
│
├── __tests__/                # Tests
│   ├── {feature}.service.test.ts
│   ├── {feature}.schema.test.ts
│   └── {feature}-form.test.tsx
│
└── index.ts                  # Public API
```

## 의존성 방향

```
UI Layer → Domain Layer ← Data Layer
    │           │              │
    ▼           ▼              ▼
  Pages      Services      Repository
  Hooks      Actions         Schema
Components   Schemas       (Drizzle)
```

- **Domain Layer**: 프레임워크 독립적 (순수 TypeScript)
- **Data Layer**: Domain 인터페이스 구현
- **UI Layer**: Domain에 의존

## 파일 템플릿

### Repository

```typescript
// features/{feature}/api/{feature}.repository.ts
import { db } from '@/lib/db';
import { {feature}s, type {Feature}, type New{Feature} } from '@/lib/db/schema';
import { eq, desc } from 'drizzle-orm';

export const {feature}sRepository = {
  async findById(id: string): Promise<{Feature} | null> {
    const [item] = await db
      .select()
      .from({feature}s)
      .where(eq({feature}s.id, id))
      .limit(1);
    return item ?? null;
  },

  async findAll(): Promise<{Feature}[]> {
    return db.select().from({feature}s).orderBy(desc({feature}s.createdAt));
  },

  async create(data: New{Feature}): Promise<{Feature}> {
    const [item] = await db.insert({feature}s).values(data).returning();
    return item;
  },

  async update(id: string, data: Partial<New{Feature}>): Promise<{Feature}> {
    const [item] = await db
      .update({feature}s)
      .set(data)
      .where(eq({feature}s.id, id))
      .returning();
    return item;
  },

  async delete(id: string): Promise<void> {
    await db.delete({feature}s).where(eq({feature}s.id, id));
  },
};
```

### Service

```typescript
// features/{feature}/api/{feature}.service.ts
import { {feature}sRepository } from './{feature}.repository';
import type { Create{Feature}Input, Update{Feature}Input } from '../schemas/{feature}.schema';

export const {feature}sService = {
  async get{Feature}(id: string) {
    const item = await {feature}sRepository.findById(id);
    if (!item) {
      throw new Error('{Feature} not found');
    }
    return item;
  },

  async get{Feature}s() {
    return {feature}sRepository.findAll();
  },

  async create{Feature}(data: Create{Feature}Input) {
    return {feature}sRepository.create(data);
  },

  async update{Feature}(id: string, data: Update{Feature}Input) {
    await this.get{Feature}(id); // 존재 확인
    return {feature}sRepository.update(id, data);
  },

  async delete{Feature}(id: string) {
    await this.get{Feature}(id); // 존재 확인
    return {feature}sRepository.delete(id);
  },
};
```

### Hook

```typescript
// features/{feature}/hooks/use-{feature}.ts
'use client';

import { useQuery } from '@tanstack/react-query';
import { {feature}Keys } from './{feature}-keys';

export function use{Feature}s() {
  return useQuery({
    queryKey: {feature}Keys.lists(),
    queryFn: () => fetch('/api/{feature}s').then((res) => res.json()),
  });
}

export function use{Feature}(id: string) {
  return useQuery({
    queryKey: {feature}Keys.detail(id),
    queryFn: () => fetch(`/api/{feature}s/${id}`).then((res) => res.json()),
    enabled: !!id,
  });
}
```

---

## 테스트 예제

### Repository 테스트

```typescript
// features/{feature}/__tests__/{feature}.repository.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { {feature}sRepository } from '../api/{feature}.repository';
import { db } from '@/lib/db';

// DB 모킹
vi.mock('@/lib/db', () => ({
  db: {
    select: vi.fn().mockReturnThis(),
    from: vi.fn().mockReturnThis(),
    where: vi.fn().mockReturnThis(),
    limit: vi.fn(),
    insert: vi.fn().mockReturnThis(),
    values: vi.fn().mockReturnThis(),
    returning: vi.fn(),
    update: vi.fn().mockReturnThis(),
    set: vi.fn().mockReturnThis(),
    delete: vi.fn().mockReturnThis(),
    orderBy: vi.fn(),
  },
}));

describe('{feature}sRepository', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('findById', () => {
    it('returns item when found', async () => {
      const mock{Feature} = { id: '1', name: 'Test' };
      vi.mocked(db.select().from({feature}s).where({feature}s.id).limit).mockResolvedValue([mock{Feature}]);

      const result = await {feature}sRepository.findById('1');
      expect(result).toEqual(mock{Feature});
    });

    it('returns null when not found', async () => {
      vi.mocked(db.select().from({feature}s).where({feature}s.id).limit).mockResolvedValue([]);

      const result = await {feature}sRepository.findById('999');
      expect(result).toBeNull();
    });
  });

  describe('create', () => {
    it('creates and returns new item', async () => {
      const newData = { name: 'New Item' };
      const created = { id: '1', ...newData };
      vi.mocked(db.insert({feature}s).values(newData).returning).mockResolvedValue([created]);

      const result = await {feature}sRepository.create(newData);
      expect(result).toEqual(created);
    });
  });
});
```

### Service 테스트

```typescript
// features/{feature}/__tests__/{feature}.service.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { {feature}sService } from '../api/{feature}.service';
import { {feature}sRepository } from '../api/{feature}.repository';

vi.mock('../api/{feature}.repository');

describe('{feature}sService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('get{Feature}', () => {
    it('returns item when exists', async () => {
      const mock{Feature} = { id: '1', name: 'Test' };
      vi.mocked({feature}sRepository.findById).mockResolvedValue(mock{Feature});

      const result = await {feature}sService.get{Feature}('1');
      expect(result).toEqual(mock{Feature});
    });

    it('throws error when not found', async () => {
      vi.mocked({feature}sRepository.findById).mockResolvedValue(null);

      await expect({feature}sService.get{Feature}('999'))
        .rejects.toThrow('{Feature} not found');
    });
  });

  describe('update{Feature}', () => {
    it('validates existence before update', async () => {
      vi.mocked({feature}sRepository.findById).mockResolvedValue(null);

      await expect({feature}sService.update{Feature}('999', { name: 'Updated' }))
        .rejects.toThrow('{Feature} not found');

      expect({feature}sRepository.update).not.toHaveBeenCalled();
    });
  });
});
```

### Hook 테스트

```typescript
// features/{feature}/__tests__/use-{feature}.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { use{Feature}s, use{Feature} } from '../hooks/use-{feature}';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('use{Feature}s', () => {
  it('fetches and returns {feature}s list', async () => {
    const mock{Feature}s = [{ id: '1', name: 'Test' }];
    global.fetch = vi.fn().mockResolvedValue({
      json: () => Promise.resolve(mock{Feature}s),
    });

    const { result } = renderHook(() => use{Feature}s(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mock{Feature}s);
  });
});

describe('use{Feature}', () => {
  it('does not fetch when id is empty', () => {
    const { result } = renderHook(() => use{Feature}(''), {
      wrapper: createWrapper(),
    });

    expect(result.current.isFetching).toBe(false);
  });
});
```

---

## 안티패턴 (❌ Bad → ✅ Good)

### 1. 순환 참조

```typescript
// ❌ Bad: 순환 의존성
// features/user/api/user.service.ts
import { orderService } from '@/features/order/api/order.service';  // ❌

// features/order/api/order.service.ts
import { userService } from '@/features/user/api/user.service';  // ❌ 순환!

// ✅ Good: 이벤트 기반 통신
// lib/events/domain-events.ts
type DomainEvent = { type: string; payload: unknown };
const listeners = new Map<string, ((payload: unknown) => void)[]>();

export const domainEvents = {
  emit(event: DomainEvent) {
    listeners.get(event.type)?.forEach(fn => fn(event.payload));
  },
  on(type: string, callback: (payload: unknown) => void) {
    if (!listeners.has(type)) listeners.set(type, []);
    listeners.get(type)!.push(callback);
  },
};

// features/user/api/user.service.ts
import { domainEvents } from '@/lib/events/domain-events';

export const userService = {
  async deleteUser(id: string) {
    await usersRepository.delete(id);
    domainEvents.emit({ type: 'USER_DELETED', payload: { userId: id } });
  },
};
```

### 2. 레이어 건너뛰기

```typescript
// ❌ Bad: UI에서 직접 Repository 접근
// app/users/page.tsx
import { usersRepository } from '@/features/user/api/user.repository';  // ❌

export default async function UsersPage() {
  const users = await usersRepository.findAll();  // ❌ 레이어 건너뛰기
}

// ✅ Good: Service 레이어를 통한 접근
// app/users/page.tsx
import { usersService } from '@/features/user/api/user.service';

export default async function UsersPage() {
  const users = await usersService.getUsers();  // ✅ 비즈니스 로직 경유
}
```

### 3. 잘못된 의존성 방향

```typescript
// ❌ Bad: Domain이 Infrastructure에 의존
// features/user/api/user.service.ts
import { neon } from '@neondatabase/serverless';  // ❌ 직접 DB 의존

// ✅ Good: Repository 추상화 사용
// features/user/api/user.service.ts
import { usersRepository } from './user.repository';  // ✅ 추상화된 Repository
```

### 4. Feature 간 직접 컴포넌트 import

```typescript
// ❌ Bad: 다른 Feature 내부 컴포넌트 직접 import
// features/dashboard/components/dashboard-sidebar.tsx
import { UserAvatar } from '@/features/user/components/user-avatar';  // ❌

// ✅ Good: Feature의 Public API 사용
// features/user/index.ts (Public API)
export { UserAvatar } from './components/user-avatar';

// features/dashboard/components/dashboard-sidebar.tsx
import { UserAvatar } from '@/features/user';  // ✅ Public API
```

### 5. God Service

```typescript
// ❌ Bad: 모든 로직을 하나의 Service에
// features/user/api/user.service.ts
export const userService = {
  getUser, createUser, updateUser, deleteUser,
  sendWelcomeEmail,      // ❌ Email 도메인
  processPayment,        // ❌ Payment 도메인
  generateReport,        // ❌ Report 도메인
};

// ✅ Good: 단일 책임 원칙
// features/user/api/user.service.ts
export const userService = { getUser, createUser, updateUser, deleteUser };

// features/notification/api/email.service.ts
export const emailService = { sendWelcomeEmail };

// features/payment/api/payment.service.ts
export const paymentService = { processPayment };
```

---

## 에러 처리

### 레이어별 에러 전파

```typescript
// lib/errors/app-error.ts
export class AppError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 500,
    public isOperational = true
  ) {
    super(message);
    this.name = 'AppError';
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super(`${resource} with id ${id} not found`, 'NOT_FOUND', 404);
  }
}

export class ValidationError extends AppError {
  constructor(message: string) {
    super(message, 'VALIDATION_ERROR', 400);
  }
}

// features/{feature}/api/{feature}.service.ts
import { NotFoundError } from '@/lib/errors/app-error';

export const {feature}sService = {
  async get{Feature}(id: string) {
    const item = await {feature}sRepository.findById(id);
    if (!item) {
      throw new NotFoundError('{Feature}', id);
    }
    return item;
  },
};

// app/api/{feature}s/[id]/route.ts
import { AppError } from '@/lib/errors/app-error';

export async function GET(req: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const item = await {feature}sService.get{Feature}(id);
    return Response.json(item);
  } catch (error) {
    if (error instanceof AppError) {
      return Response.json(
        { error: error.message, code: error.code },
        { status: error.statusCode }
      );
    }
    return Response.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

---

## 성능 고려사항

### 1. Repository 쿼리 최적화

```typescript
// features/{feature}/api/{feature}.repository.ts

// ✅ 페이지네이션 지원
async findAllPaginated(page: number, limit: number) {
  const offset = (page - 1) * limit;
  const [items, [{ count }]] = await Promise.all([
    db.select().from({feature}s).limit(limit).offset(offset),
    db.select({ count: sql<number>`count(*)` }).from({feature}s),
  ]);
  return { items, total: count, page, limit };
}

// ✅ 필요한 필드만 선택
async findAllSummary() {
  return db.select({
    id: {feature}s.id,
    name: {feature}s.name,
  }).from({feature}s);
}
```

### 2. Service 레이어 캐싱

```typescript
// features/{feature}/api/{feature}.service.ts
import { unstable_cache } from 'next/cache';

export const {feature}sService = {
  get{Feature}sCached: unstable_cache(
    async () => {feature}sRepository.findAll(),
    ['{feature}s-list'],
    { revalidate: 60, tags: ['{feature}s'] }
  ),
};
```

---

## 보안 고려사항

### 1. 입력 검증 레이어

```typescript
// features/{feature}/api/{feature}.service.ts
import { create{Feature}Schema } from '../schemas/{feature}.schema';

export const {feature}sService = {
  async create{Feature}(input: unknown) {
    // 항상 Service 레이어에서 검증
    const validated = create{Feature}Schema.parse(input);
    return {feature}sRepository.create(validated);
  },
};
```

### 2. 권한 검사 패턴

```typescript
// features/{feature}/api/{feature}.service.ts
import { auth } from '@/lib/auth';
import { ForbiddenError } from '@/lib/errors/app-error';

export const {feature}sService = {
  async update{Feature}(id: string, data: Update{Feature}Input) {
    const session = await auth();
    const item = await this.get{Feature}(id);

    // 소유권 또는 권한 확인
    if (item.userId !== session?.user?.id && session?.user?.role !== 'admin') {
      throw new ForbiddenError('Not authorized to update this resource');
    }

    return {feature}sRepository.update(id, data);
  },
};
```

---

## References

- `_references/ARCHITECTURE-PATTERN.md` - Clean Architecture 상세 가이드
- `_references/TEST-PATTERN.md` - 테스트 피라미드 및 패턴
- `_references/STATE-PATTERN.md` - TanStack Query + Zustand 패턴
