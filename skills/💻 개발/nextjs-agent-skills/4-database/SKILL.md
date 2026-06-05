---
name: database
description: |
  Drizzle ORM + PostgreSQL 데이터베이스를 설정합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Database Skill

Drizzle ORM + PostgreSQL 데이터베이스를 설정합니다.

## Triggers

- "데이터베이스 설정", "db 설정", "drizzle", "postgresql"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | Next.js 프로젝트 경로 |
| `provider` | ❌ | DB 제공자 (neon, supabase, vercel) |

---

## 설치

```bash
# Drizzle ORM
npm install drizzle-orm
npm install -D drizzle-kit

# PostgreSQL 드라이버 (Neon 권장)
npm install @neondatabase/serverless

# 또는 다른 드라이버
npm install postgres              # node-postgres
npm install @vercel/postgres      # Vercel Postgres
```

---

## 디렉토리 구조

```
src/lib/db/
├── index.ts                  # DB 클라이언트
├── schema/
│   ├── index.ts              # 전체 스키마 export
│   ├── users.ts              # 사용자 테이블
│   ├── posts.ts              # 게시물 테이블
│   └── relations.ts          # 관계 정의
└── migrations/               # 마이그레이션 파일
    └── 0000_xxx.sql
```

---

## 설정 파일

### drizzle.config.ts

```typescript
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  schema: './src/lib/db/schema/index.ts',
  out: './src/lib/db/migrations',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
  verbose: true,
  strict: true,
});
```

---

## DB 클라이언트

### Neon (Serverless) - 권장

```typescript
// lib/db/index.ts
import { neon } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';
import * as schema from './schema';

const sql = neon(process.env.DATABASE_URL!);

export const db = drizzle(sql, { schema });
```

### Vercel Postgres

```typescript
// lib/db/index.ts
import { sql } from '@vercel/postgres';
import { drizzle } from 'drizzle-orm/vercel-postgres';
import * as schema from './schema';

export const db = drizzle(sql, { schema });
```

---

## 스키마 정의

### 사용자 테이블

```typescript
// lib/db/schema/users.ts
import {
  pgTable,
  text,
  varchar,
  boolean,
  timestamp,
} from 'drizzle-orm/pg-core';
import { createId } from '@paralleldrive/cuid2';

export const users = pgTable('users', {
  id: text('id')
    .primaryKey()
    .$defaultFn(() => createId()),
  email: varchar('email', { length: 255 }).notNull().unique(),
  name: varchar('name', { length: 100 }).notNull(),
  avatarUrl: text('avatar_url'),
  isVerified: boolean('is_verified').default(false),
  role: varchar('role', { length: 20 }).default('user'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at')
    .defaultNow()
    .notNull()
    .$onUpdate(() => new Date()),
});

// 타입 추론
export type User = typeof users.$inferSelect;
export type NewUser = typeof users.$inferInsert;
```

### 게시물 테이블

```typescript
// lib/db/schema/posts.ts
import {
  pgTable,
  text,
  varchar,
  timestamp,
  pgEnum,
} from 'drizzle-orm/pg-core';
import { createId } from '@paralleldrive/cuid2';
import { users } from './users';

export const postStatusEnum = pgEnum('post_status', [
  'draft',
  'published',
  'archived',
]);

export const posts = pgTable('posts', {
  id: text('id')
    .primaryKey()
    .$defaultFn(() => createId()),
  title: varchar('title', { length: 255 }).notNull(),
  slug: varchar('slug', { length: 255 }).notNull().unique(),
  content: text('content'),
  excerpt: varchar('excerpt', { length: 500 }),
  status: postStatusEnum('status').default('draft'),
  authorId: text('author_id')
    .notNull()
    .references(() => users.id, { onDelete: 'cascade' }),
  publishedAt: timestamp('published_at'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at')
    .defaultNow()
    .notNull()
    .$onUpdate(() => new Date()),
});

export type Post = typeof posts.$inferSelect;
export type NewPost = typeof posts.$inferInsert;
```

### 관계 정의

```typescript
// lib/db/schema/relations.ts
import { relations } from 'drizzle-orm';
import { users } from './users';
import { posts } from './posts';

export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
}));

export const postsRelations = relations(posts, ({ one }) => ({
  author: one(users, {
    fields: [posts.authorId],
    references: [users.id],
  }),
}));
```

### Index Export

```typescript
// lib/db/schema/index.ts
export * from './users';
export * from './posts';
export * from './relations';
```

---

## 마이그레이션

```bash
# 마이그레이션 파일 생성
npm run db:generate

# 마이그레이션 적용
npm run db:migrate

# 스키마 바로 적용 (개발용)
npm run db:push

# Drizzle Studio (DB 브라우저)
npm run db:studio
```

---

## 환경 변수

```bash
# .env.local
DATABASE_URL="postgresql://user:password@host:5432/database?sslmode=require"
```

---

## CUID2 설치 (ID 생성)

```bash
npm install @paralleldrive/cuid2
```

---

## 테스트 예제

### 스키마 테스트

```typescript
// lib/db/__tests__/schema.test.ts
import { describe, it, expect } from 'vitest';
import { users, posts, NewUser, NewPost } from '../schema';

describe('Users Schema', () => {
  it('has required columns', () => {
    expect(users.id).toBeDefined();
    expect(users.email).toBeDefined();
    expect(users.name).toBeDefined();
    expect(users.createdAt).toBeDefined();
  });

  it('infers correct NewUser type', () => {
    const validUser: NewUser = {
      email: 'test@example.com',
      name: 'Test User',
    };
    expect(validUser.email).toBe('test@example.com');
  });
});

describe('Posts Schema', () => {
  it('has foreign key to users', () => {
    expect(posts.authorId).toBeDefined();
  });

  it('has status enum with valid values', () => {
    const validPost: NewPost = {
      title: 'Test',
      slug: 'test',
      authorId: 'user-id',
      status: 'draft',
    };
    expect(['draft', 'published', 'archived']).toContain(validPost.status);
  });
});
```

### Repository 테스트 (통합)

```typescript
// features/user/__tests__/user.repository.integration.test.ts
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { db } from '@/lib/db';
import { users } from '@/lib/db/schema';
import { usersRepository } from '../api/user.repository';
import { eq } from 'drizzle-orm';

describe('UsersRepository (Integration)', () => {
  let testUserId: string;

  beforeEach(async () => {
    // 테스트 데이터 생성
    const [user] = await db.insert(users).values({
      email: 'test@example.com',
      name: 'Test User',
    }).returning();
    testUserId = user.id;
  });

  afterEach(async () => {
    // 테스트 데이터 정리
    await db.delete(users).where(eq(users.id, testUserId));
  });

  it('findById returns user', async () => {
    const user = await usersRepository.findById(testUserId);
    expect(user).not.toBeNull();
    expect(user?.email).toBe('test@example.com');
  });

  it('findById returns null for non-existent id', async () => {
    const user = await usersRepository.findById('non-existent');
    expect(user).toBeNull();
  });

  it('update modifies user', async () => {
    const updated = await usersRepository.update(testUserId, { name: 'Updated' });
    expect(updated.name).toBe('Updated');
  });
});
```

---

## 안티패턴 (❌ Bad → ✅ Good)

### 1. N+1 쿼리

```typescript
// ❌ Bad: N+1 쿼리 발생
async function getPostsWithAuthors() {
  const allPosts = await db.select().from(posts);

  // 각 post마다 author 조회 (N번 추가 쿼리)
  for (const post of allPosts) {
    post.author = await db.select().from(users).where(eq(users.id, post.authorId));
  }
  return allPosts;
}

// ✅ Good: Join 사용
async function getPostsWithAuthors() {
  return db.query.posts.findMany({
    with: {
      author: true,  // relations 정의 필요
    },
  });
}

// 또는 명시적 join
async function getPostsWithAuthors() {
  return db
    .select({
      post: posts,
      author: users,
    })
    .from(posts)
    .leftJoin(users, eq(posts.authorId, users.id));
}
```

### 2. 잘못된 타입 추론

```typescript
// ❌ Bad: any 타입 사용
async function createUser(data: any) {
  return db.insert(users).values(data).returning();
}

// ✅ Good: 스키마 기반 타입 사용
import { NewUser } from '@/lib/db/schema';

async function createUser(data: NewUser) {
  return db.insert(users).values(data).returning();
}
```

### 3. 트랜잭션 없는 복수 작업

```typescript
// ❌ Bad: 트랜잭션 없이 여러 작업 (실패 시 불일치 발생)
async function transferCredits(fromId: string, toId: string, amount: number) {
  await db.update(users).set({ credits: sql`credits - ${amount}` }).where(eq(users.id, fromId));
  await db.update(users).set({ credits: sql`credits + ${amount}` }).where(eq(users.id, toId));
}

// ✅ Good: 트랜잭션으로 원자성 보장
import { db } from '@/lib/db';

async function transferCredits(fromId: string, toId: string, amount: number) {
  await db.transaction(async (tx) => {
    await tx.update(users).set({ credits: sql`credits - ${amount}` }).where(eq(users.id, fromId));
    await tx.update(users).set({ credits: sql`credits + ${amount}` }).where(eq(users.id, toId));
  });
}
```

### 4. 마이그레이션 건너뛰기

```bash
# ❌ Bad: 프로덕션에서 db:push 사용
npm run db:push  # 데이터 손실 위험!

# ✅ Good: 마이그레이션 사용
npm run db:generate  # 마이그레이션 파일 생성
npm run db:migrate   # 마이그레이션 적용
```

---

## 에러 처리

### DB 연결 에러 처리

```typescript
// lib/db/index.ts
import { neon, NeonQueryFunction } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';
import * as schema from './schema';

let sql: NeonQueryFunction<false, false>;

try {
  if (!process.env.DATABASE_URL) {
    throw new Error('DATABASE_URL environment variable is not set');
  }
  sql = neon(process.env.DATABASE_URL);
} catch (error) {
  console.error('Failed to initialize database connection:', error);
  throw error;
}

export const db = drizzle(sql, { schema });
```

### 쿼리 에러 처리

```typescript
// features/user/api/user.repository.ts
import { DatabaseError } from 'pg';

async function createUser(data: NewUser) {
  try {
    const [user] = await db.insert(users).values(data).returning();
    return user;
  } catch (error) {
    if (error instanceof DatabaseError) {
      // 중복 키 에러 (unique constraint violation)
      if (error.code === '23505') {
        throw new ConflictError('User with this email already exists');
      }
      // 외래 키 에러
      if (error.code === '23503') {
        throw new BadRequestError('Referenced resource does not exist');
      }
    }
    throw error;
  }
}
```

---

## 성능 고려사항

### 인덱스 추가

```typescript
// lib/db/schema/users.ts
import { pgTable, text, varchar, index } from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: text('id').primaryKey(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  name: varchar('name', { length: 100 }).notNull(),
  role: varchar('role', { length: 20 }),
}, (table) => ({
  // 복합 인덱스
  emailRoleIdx: index('email_role_idx').on(table.email, table.role),
  // 부분 인덱스
  activeUsersIdx: index('active_users_idx')
    .on(table.role)
    .where(sql`role = 'admin'`),
}));
```

### 쿼리 최적화

```typescript
// 필요한 컬럼만 선택
const userSummaries = await db
  .select({ id: users.id, name: users.name })
  .from(users)
  .limit(100);

// 커서 기반 페이지네이션 (대용량 데이터)
const nextPage = await db
  .select()
  .from(posts)
  .where(gt(posts.id, lastSeenId))
  .orderBy(asc(posts.id))
  .limit(20);
```

---

## 보안 고려사항

### SQL Injection 방지

```typescript
// ❌ Bad: 문자열 연결 (위험!)
const results = await db.execute(
  `SELECT * FROM users WHERE email = '${userInput}'`  // 절대 금지!
);

// ✅ Good: Drizzle ORM 사용 (자동 파라미터화)
const results = await db
  .select()
  .from(users)
  .where(eq(users.email, userInput));  // 안전

// 동적 쿼리 필요 시 sql 템플릿 사용
import { sql } from 'drizzle-orm';
const results = await db.execute(
  sql`SELECT * FROM users WHERE email = ${userInput}`
);
```

### 민감 데이터 제외

```typescript
// 비밀번호 해시 등 민감 정보 제외
export const safeUserSelect = {
  id: users.id,
  email: users.email,
  name: users.name,
  role: users.role,
  createdAt: users.createdAt,
  // password: users.password,  // 제외!
};

const safeUsers = await db.select(safeUserSelect).from(users);
```

---

## References

- `_references/DATABASE-PATTERN.md` - Drizzle DAO 패턴 상세
- `_references/ARCHITECTURE-PATTERN.md` - Repository 계층 구조
