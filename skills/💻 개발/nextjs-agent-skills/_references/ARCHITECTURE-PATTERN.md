# Clean Architecture Pattern Reference

Next.js Clean Architecture 구현을 위한 패턴 및 샘플 코드 레퍼런스입니다.

## 레이어 구조

```
┌─────────────────────────────────────┐
│           UI Layer                   │  ← Pages, Components, Hooks
├─────────────────────────────────────┤
│         Domain Layer                 │  ← Services, Business Logic
├─────────────────────────────────────┤
│          Data Layer                  │  ← Repository, Schema, DB
└─────────────────────────────────────┘
```

---

## 디렉토리 구조

```
src/
├── app/                           # Next.js App Router
│   ├── (auth)/                    # Route Group
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── api/                       # API Routes (필요시)
│   ├── layout.tsx
│   ├── page.tsx
│   ├── globals.css
│   └── providers.tsx
│
├── components/
│   ├── ui/                        # shadcn/ui 컴포넌트
│   ├── atoms/                     # 커스텀 기본 컴포넌트
│   ├── molecules/                 # 조합 컴포넌트
│   ├── organisms/                 # 복합 컴포넌트
│   └── templates/                 # 레이아웃 템플릿
│
├── features/                      # Feature 모듈
│   └── {feature}/
│       ├── actions/               # Server Actions
│       ├── api/                   # API Layer (TanStack Query)
│       ├── components/            # Feature 전용 UI
│       ├── hooks/                 # Feature 전용 훅
│       ├── schemas/               # Zod 스키마
│       ├── stores/                # Zustand 스토어
│       └── types/                 # TypeScript 타입
│
├── lib/
│   ├── db/                        # Drizzle ORM
│   │   ├── schema/
│   │   ├── migrations/
│   │   └── index.ts
│   ├── auth/                      # Auth.js
│   ├── api/                       # API 클라이언트
│   ├── actions/                   # next-safe-action
│   └── utils/
│
├── hooks/                         # 공통 훅
├── stores/                        # 글로벌 스토어
├── types/                         # 글로벌 타입
├── env.ts                         # T3 Env
└── proxy.ts                  # Next.js Proxy (기존 Middleware)
```

---

## Layer 별 패턴

### 1. Data Layer (데이터 액세스)

#### Drizzle Schema

```typescript
// lib/db/schema/users.ts
import { pgTable, text, timestamp, boolean } from 'drizzle-orm/pg-core';
import { createId } from '@paralleldrive/cuid2';

export const users = pgTable('users', {
  id: text('id').primaryKey().$defaultFn(() => createId()),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  avatarUrl: text('avatar_url'),
  isVerified: boolean('is_verified').default(false),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type NewUser = typeof users.$inferInsert;
```

#### Repository

```typescript
// features/users/api/users.repository.ts
import { db } from '@/lib/db';
import { users, type User, type NewUser } from '@/lib/db/schema/users';
import { eq } from 'drizzle-orm';

export const usersRepository = {
  async findById(id: string): Promise<User | null> {
    const [user] = await db
      .select()
      .from(users)
      .where(eq(users.id, id))
      .limit(1);
    return user ?? null;
  },

  async findByEmail(email: string): Promise<User | null> {
    const [user] = await db
      .select()
      .from(users)
      .where(eq(users.email, email))
      .limit(1);
    return user ?? null;
  },

  async findAll(): Promise<User[]> {
    return db.select().from(users);
  },

  async create(data: NewUser): Promise<User> {
    const [user] = await db.insert(users).values(data).returning();
    return user;
  },

  async update(id: string, data: Partial<NewUser>): Promise<User> {
    const [user] = await db
      .update(users)
      .set({ ...data, updatedAt: new Date() })
      .where(eq(users.id, id))
      .returning();
    return user;
  },

  async delete(id: string): Promise<void> {
    await db.delete(users).where(eq(users.id, id));
  },
};
```

---

### 2. Domain Layer (비즈니스 로직)

#### Zod Schema

```typescript
// features/users/schemas/user.schema.ts
import { z } from 'zod';

export const userSchema = z.object({
  id: z.string().cuid2(),
  email: z.string().email('유효한 이메일을 입력하세요'),
  name: z.string().min(2, '이름은 2자 이상이어야 합니다'),
  avatarUrl: z.string().url().nullable(),
  isVerified: z.boolean().default(false),
});

export const createUserSchema = userSchema.omit({ id: true, isVerified: true });
export const updateUserSchema = createUserSchema.partial();

export type UserSchema = z.infer<typeof userSchema>;
export type CreateUserInput = z.infer<typeof createUserSchema>;
export type UpdateUserInput = z.infer<typeof updateUserSchema>;
```

#### Service

```typescript
// features/users/api/users.service.ts
import { usersRepository } from './users.repository';
import type { CreateUserInput, UpdateUserInput } from '../schemas/user.schema';

export const usersService = {
  async getUser(id: string) {
    const user = await usersRepository.findById(id);
    if (!user) {
      throw new Error('User not found');
    }
    return user;
  },

  async getUserByEmail(email: string) {
    return usersRepository.findByEmail(email);
  },

  async getUsers() {
    return usersRepository.findAll();
  },

  async createUser(data: CreateUserInput) {
    // 비즈니스 로직: 이메일 중복 체크
    const existing = await usersRepository.findByEmail(data.email);
    if (existing) {
      throw new Error('Email already exists');
    }
    return usersRepository.create(data);
  },

  async updateUser(id: string, data: UpdateUserInput) {
    // 존재 여부 확인
    await this.getUser(id);
    return usersRepository.update(id, data);
  },

  async deleteUser(id: string) {
    await this.getUser(id);
    return usersRepository.delete(id);
  },
};
```

---

### 3. UI Layer (프레젠테이션)

#### Server Action

```typescript
// features/users/actions/user.action.ts
'use server';

import { actionClient } from '@/lib/actions/safe-action';
import { createUserSchema, updateUserSchema } from '../schemas/user.schema';
import { usersService } from '../api/users.service';
import { revalidatePath } from 'next/cache';
import { z } from 'zod';

export const createUserAction = actionClient
  .schema(createUserSchema)
  .action(async ({ parsedInput }) => {
    const user = await usersService.createUser(parsedInput);
    revalidatePath('/users');
    return { user };
  });

export const updateUserAction = actionClient
  .schema(z.object({ id: z.string(), data: updateUserSchema }))
  .action(async ({ parsedInput: { id, data } }) => {
    const user = await usersService.updateUser(id, data);
    revalidatePath('/users');
    revalidatePath(`/users/${id}`);
    return { user };
  });

export const deleteUserAction = actionClient
  .schema(z.object({ id: z.string() }))
  .action(async ({ parsedInput: { id } }) => {
    await usersService.deleteUser(id);
    revalidatePath('/users');
    return { success: true };
  });
```

#### TanStack Query Hook

```typescript
// features/users/hooks/use-users.ts
'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { usersService } from '../api/users.service';
import { createUserAction, updateUserAction, deleteUserAction } from '../actions/user.action';
import type { CreateUserInput, UpdateUserInput } from '../schemas/user.schema';

export const userKeys = {
  all: ['users'] as const,
  lists: () => [...userKeys.all, 'list'] as const,
  list: (filters: string) => [...userKeys.lists(), { filters }] as const,
  details: () => [...userKeys.all, 'detail'] as const,
  detail: (id: string) => [...userKeys.details(), id] as const,
};

export function useUsers() {
  return useQuery({
    queryKey: userKeys.lists(),
    queryFn: () => usersService.getUsers(),
  });
}

export function useUser(id: string) {
  return useQuery({
    queryKey: userKeys.detail(id),
    queryFn: () => usersService.getUser(id),
    enabled: !!id,
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateUserInput) => createUserAction(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
    },
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateUserInput }) =>
      updateUserAction({ id, data }),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
      queryClient.invalidateQueries({ queryKey: userKeys.detail(id) });
    },
  });
}

export function useDeleteUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => deleteUserAction({ id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
    },
  });
}
```

#### Page Component

```tsx
// app/(dashboard)/users/page.tsx
import { Suspense } from 'react';
import { usersService } from '@/features/users/api/users.service';
import { UsersTable } from '@/features/users/components/users-table';
import { UsersTableSkeleton } from '@/features/users/components/users-table-skeleton';

export default function UsersPage() {
  return (
    <div className="container py-8">
      <h1 className="text-3xl font-bold mb-8">사용자 관리</h1>
      <Suspense fallback={<UsersTableSkeleton />}>
        <UsersTableServer />
      </Suspense>
    </div>
  );
}

async function UsersTableServer() {
  const users = await usersService.getUsers();
  return <UsersTable initialData={users} />;
}
```

#### Client Component

```tsx
// features/users/components/users-table.tsx
'use client';

import { useUsers, useDeleteUser } from '../hooks/use-users';
import type { User } from '@/lib/db/schema/users';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Trash2 } from 'lucide-react';

interface UsersTableProps {
  initialData: User[];
}

export function UsersTable({ initialData }: UsersTableProps) {
  const { data: users = initialData } = useUsers();
  const deleteUser = useDeleteUser();

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>이름</TableHead>
          <TableHead>이메일</TableHead>
          <TableHead>상태</TableHead>
          <TableHead className="w-[100px]">액션</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {users.map((user) => (
          <TableRow key={user.id}>
            <TableCell className="font-medium">{user.name}</TableCell>
            <TableCell>{user.email}</TableCell>
            <TableCell>
              {user.isVerified ? '인증됨' : '미인증'}
            </TableCell>
            <TableCell>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => deleteUser.mutate(user.id)}
                disabled={deleteUser.isPending}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
```

---

## 의존성 방향

```
UI Layer → Domain Layer ← Data Layer
    │           │              │
    ▼           ▼              ▼
  Pages      Services      Repository
  Hooks      Schemas        Schema
Components              (Drizzle/Zod)
```

**핵심 원칙:**
- Domain Layer는 프레임워크에 독립적 (순수 TypeScript)
- Data Layer는 Domain Layer의 인터페이스 구현
- UI Layer는 Domain Layer에 의존
- Schema(Zod)는 클라이언트/서버 양쪽에서 공유
