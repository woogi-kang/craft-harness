# Database Pattern Reference

Drizzle ORM 데이터베이스 패턴 및 샘플 코드 레퍼런스입니다.

## 개요

```
┌─────────────────────────────────────────────────────────────┐
│                      Drizzle ORM                             │
│  • TypeScript-first ORM                                      │
│  • SQL-like 쿼리 빌더                                        │
│  • Edge Runtime 호환 (7kb)                                   │
│  • 코드 생성 불필요 (타입 추론)                               │
├─────────────────────────────────────────────────────────────┤
│  지원 데이터베이스                                           │
│  • PostgreSQL (Neon, Supabase, Vercel Postgres)             │
│  • MySQL (PlanetScale)                                       │
│  • SQLite (Turso, Cloudflare D1)                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 설정

### 설치

```bash
npm install drizzle-orm
npm install -D drizzle-kit

# PostgreSQL 드라이버
npm install @neondatabase/serverless  # Neon
npm install postgres                   # node-postgres
npm install @vercel/postgres          # Vercel Postgres
```

### 디렉토리 구조

```
src/lib/db/
├── index.ts              # DB 클라이언트 export
├── schema/
│   ├── index.ts          # 모든 스키마 export
│   ├── users.ts          # 사용자 테이블
│   ├── posts.ts          # 게시물 테이블
│   └── relations.ts      # 관계 정의
└── migrations/           # 마이그레이션 파일
    └── 0000_xxx.sql
```

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

## 스키마 정의

### 기본 테이블

```typescript
// lib/db/schema/users.ts
import {
  pgTable,
  text,
  timestamp,
  boolean,
  varchar,
  integer,
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

### Enum 사용

```typescript
// lib/db/schema/posts.ts
import {
  pgTable,
  text,
  timestamp,
  pgEnum,
} from 'drizzle-orm/pg-core';
import { users } from './users';

// Enum 정의
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
  content: text('content'),
  status: postStatusEnum('status').default('draft'),
  authorId: text('author_id')
    .notNull()
    .references(() => users.id, { onDelete: 'cascade' }),
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
import { comments } from './comments';

export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
  comments: many(comments),
}));

export const postsRelations = relations(posts, ({ one, many }) => ({
  author: one(users, {
    fields: [posts.authorId],
    references: [users.id],
  }),
  comments: many(comments),
}));

export const commentsRelations = relations(comments, ({ one }) => ({
  author: one(users, {
    fields: [comments.authorId],
    references: [users.id],
  }),
  post: one(posts, {
    fields: [comments.postId],
    references: [posts.id],
  }),
}));
```

---

## 데이터베이스 클라이언트

### Neon (Serverless PostgreSQL)

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

### Connection Pool (node-postgres)

```typescript
// lib/db/index.ts
import { Pool } from 'pg';
import { drizzle } from 'drizzle-orm/node-postgres';
import * as schema from './schema';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 10,
});

export const db = drizzle(pool, { schema });
```

---

## 쿼리 패턴

### 기본 CRUD

```typescript
// features/users/api/users.repository.ts
import { db } from '@/lib/db';
import { users, type User, type NewUser } from '@/lib/db/schema/users';
import { eq, and, like, desc, asc } from 'drizzle-orm';

export const usersRepository = {
  // Create
  async create(data: NewUser): Promise<User> {
    const [user] = await db.insert(users).values(data).returning();
    return user;
  },

  // Read - 단일
  async findById(id: string): Promise<User | null> {
    const [user] = await db
      .select()
      .from(users)
      .where(eq(users.id, id))
      .limit(1);
    return user ?? null;
  },

  // Read - 목록
  async findAll(): Promise<User[]> {
    return db.select().from(users).orderBy(desc(users.createdAt));
  },

  // Update
  async update(id: string, data: Partial<NewUser>): Promise<User> {
    const [user] = await db
      .update(users)
      .set(data)
      .where(eq(users.id, id))
      .returning();
    return user;
  },

  // Delete
  async delete(id: string): Promise<void> {
    await db.delete(users).where(eq(users.id, id));
  },
};
```

### 필터링 & 검색

```typescript
// features/users/api/users.repository.ts
import { eq, and, or, like, gte, lte, ilike, sql } from 'drizzle-orm';

interface FindUsersParams {
  search?: string;
  role?: string;
  isVerified?: boolean;
  createdAfter?: Date;
  createdBefore?: Date;
}

export const usersRepository = {
  async findMany(params: FindUsersParams): Promise<User[]> {
    const conditions = [];

    if (params.search) {
      conditions.push(
        or(
          ilike(users.name, `%${params.search}%`),
          ilike(users.email, `%${params.search}%`)
        )
      );
    }

    if (params.role) {
      conditions.push(eq(users.role, params.role));
    }

    if (params.isVerified !== undefined) {
      conditions.push(eq(users.isVerified, params.isVerified));
    }

    if (params.createdAfter) {
      conditions.push(gte(users.createdAt, params.createdAfter));
    }

    if (params.createdBefore) {
      conditions.push(lte(users.createdAt, params.createdBefore));
    }

    return db
      .select()
      .from(users)
      .where(conditions.length > 0 ? and(...conditions) : undefined)
      .orderBy(desc(users.createdAt));
  },
};
```

### 페이지네이션

```typescript
// lib/db/utils/pagination.ts
export interface PaginationParams {
  page?: number;
  limit?: number;
}

export interface PaginatedResult<T> {
  data: T[];
  meta: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

// features/users/api/users.repository.ts
import { count, sql } from 'drizzle-orm';

export const usersRepository = {
  async findPaginated(
    params: PaginationParams & FindUsersParams
  ): Promise<PaginatedResult<User>> {
    const page = params.page ?? 1;
    const limit = params.limit ?? 10;
    const offset = (page - 1) * limit;

    // 조건 생성 (위와 동일)
    const conditions = [];
    // ...

    // 병렬로 데이터와 카운트 조회
    const [data, [{ total }]] = await Promise.all([
      db
        .select()
        .from(users)
        .where(conditions.length > 0 ? and(...conditions) : undefined)
        .orderBy(desc(users.createdAt))
        .limit(limit)
        .offset(offset),
      db
        .select({ total: count() })
        .from(users)
        .where(conditions.length > 0 ? and(...conditions) : undefined),
    ]);

    const totalPages = Math.ceil(total / limit);

    return {
      data,
      meta: {
        page,
        limit,
        total,
        totalPages,
        hasNext: page < totalPages,
        hasPrev: page > 1,
      },
    };
  },
};
```

### 관계 쿼리 (with)

```typescript
// features/posts/api/posts.repository.ts
import { db } from '@/lib/db';
import { posts } from '@/lib/db/schema/posts';
import { eq } from 'drizzle-orm';

export const postsRepository = {
  // 작성자 정보와 함께 조회
  async findByIdWithAuthor(id: string) {
    return db.query.posts.findFirst({
      where: eq(posts.id, id),
      with: {
        author: true,
      },
    });
  },

  // 작성자와 댓글까지 조회
  async findByIdWithDetails(id: string) {
    return db.query.posts.findFirst({
      where: eq(posts.id, id),
      with: {
        author: {
          columns: {
            id: true,
            name: true,
            avatarUrl: true,
          },
        },
        comments: {
          with: {
            author: {
              columns: {
                id: true,
                name: true,
                avatarUrl: true,
              },
            },
          },
          orderBy: (comments, { desc }) => [desc(comments.createdAt)],
        },
      },
    });
  },

  // 전체 목록 (작성자 포함)
  async findAllWithAuthor() {
    return db.query.posts.findMany({
      with: {
        author: {
          columns: {
            id: true,
            name: true,
            avatarUrl: true,
          },
        },
      },
      orderBy: (posts, { desc }) => [desc(posts.createdAt)],
    });
  },
};
```

### 집계 함수

```typescript
// features/analytics/api/analytics.repository.ts
import { db } from '@/lib/db';
import { users } from '@/lib/db/schema/users';
import { posts } from '@/lib/db/schema/posts';
import { count, countDistinct, sum, avg, sql } from 'drizzle-orm';

export const analyticsRepository = {
  // 기본 집계
  async getUserStats() {
    const [result] = await db
      .select({
        totalUsers: count(),
        verifiedUsers: count(sql`CASE WHEN ${users.isVerified} THEN 1 END`),
      })
      .from(users);

    return result;
  },

  // 그룹별 집계
  async getPostsByStatus() {
    return db
      .select({
        status: posts.status,
        count: count(),
      })
      .from(posts)
      .groupBy(posts.status);
  },

  // 날짜별 집계
  async getDailySignups(days: number = 30) {
    return db
      .select({
        date: sql<string>`DATE(${users.createdAt})`,
        count: count(),
      })
      .from(users)
      .where(
        sql`${users.createdAt} >= NOW() - INTERVAL '${sql.raw(String(days))} days'`
      )
      .groupBy(sql`DATE(${users.createdAt})`)
      .orderBy(sql`DATE(${users.createdAt})`);
  },
};
```

---

## 트랜잭션

```typescript
// features/orders/api/orders.repository.ts
import { db } from '@/lib/db';
import { orders, orderItems } from '@/lib/db/schema';

export const ordersRepository = {
  async createOrder(orderData: NewOrder, items: NewOrderItem[]) {
    return db.transaction(async (tx) => {
      // 1. 주문 생성
      const [order] = await tx
        .insert(orders)
        .values(orderData)
        .returning();

      // 2. 주문 항목 생성
      const insertedItems = await tx
        .insert(orderItems)
        .values(items.map((item) => ({ ...item, orderId: order.id })))
        .returning();

      // 3. 재고 감소 (예시)
      for (const item of insertedItems) {
        await tx
          .update(products)
          .set({
            stock: sql`${products.stock} - ${item.quantity}`,
          })
          .where(eq(products.id, item.productId));
      }

      return { order, items: insertedItems };
    });
  },
};
```

---

## 마이그레이션

### 명령어

```bash
# 스키마 변경사항 확인
npx drizzle-kit generate

# 마이그레이션 적용
npx drizzle-kit migrate

# 스키마 푸시 (개발용, 마이그레이션 파일 없이)
npx drizzle-kit push

# Drizzle Studio (DB 브라우저)
npx drizzle-kit studio
```

### 마이그레이션 파일

```sql
-- 0000_xxx_create_users.sql
CREATE TABLE IF NOT EXISTS "users" (
  "id" text PRIMARY KEY NOT NULL,
  "email" varchar(255) NOT NULL,
  "name" varchar(100) NOT NULL,
  "avatar_url" text,
  "is_verified" boolean DEFAULT false,
  "role" varchar(20) DEFAULT 'user',
  "created_at" timestamp DEFAULT now() NOT NULL,
  "updated_at" timestamp DEFAULT now() NOT NULL,
  CONSTRAINT "users_email_unique" UNIQUE("email")
);
```

---

## 시드 데이터

```typescript
// lib/db/seed.ts
import { db } from './index';
import { users, posts } from './schema';
import { createId } from '@paralleldrive/cuid2';

async function seed() {
  console.log('Seeding database...');

  // 사용자 생성
  const [admin] = await db
    .insert(users)
    .values({
      id: createId(),
      email: 'admin@example.com',
      name: 'Admin User',
      role: 'admin',
      isVerified: true,
    })
    .returning();

  // 게시물 생성
  await db.insert(posts).values([
    {
      id: createId(),
      title: 'First Post',
      content: 'This is the first post.',
      status: 'published',
      authorId: admin.id,
    },
    {
      id: createId(),
      title: 'Second Post',
      content: 'This is the second post.',
      status: 'draft',
      authorId: admin.id,
    },
  ]);

  console.log('Seeding completed!');
}

seed().catch(console.error);
```

### 실행

```bash
npx tsx lib/db/seed.ts
```

---

## 베스트 프랙티스

### 1. 스키마 Export 구조

```typescript
// lib/db/schema/index.ts
export * from './users';
export * from './posts';
export * from './comments';
export * from './relations';
```

### 2. Repository 패턴

```typescript
// 각 엔티티별 Repository 분리
features/
├── users/
│   └── api/
│       └── users.repository.ts
├── posts/
│   └── api/
│       └── posts.repository.ts
```

### 3. 타입 안전성

```typescript
// 항상 타입 추론 활용
type User = typeof users.$inferSelect;
type NewUser = typeof users.$inferInsert;

// 관계 포함 타입
type PostWithAuthor = Awaited<
  ReturnType<typeof postsRepository.findByIdWithAuthor>
>;
```

### 4. 에러 처리

```typescript
try {
  await db.insert(users).values(data);
} catch (error) {
  if (error.code === '23505') {
    // PostgreSQL unique violation
    throw new Error('Email already exists');
  }
  throw error;
}
```
