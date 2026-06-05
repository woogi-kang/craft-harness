---
name: monorepo
description: |
  Turborepo를 사용하여 모노레포를 설정합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Monorepo Skill

Turborepo를 사용하여 모노레포를 설정합니다.

## Triggers

- "모노레포", "monorepo", "turborepo", "workspace"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `apps` | ✅ | 애플리케이션 목록 |
| `packages` | ❌ | 공유 패키지 목록 |

---

## 디렉토리 구조

```
monorepo/
├── apps/
│   ├── web/                    # Next.js 메인 앱
│   │   ├── app/
│   │   ├── package.json
│   │   └── next.config.ts
│   ├── admin/                  # Next.js 어드민 앱
│   │   ├── app/
│   │   ├── package.json
│   │   └── next.config.ts
│   └── docs/                   # 문서 사이트
│       └── package.json
├── packages/
│   ├── ui/                     # 공유 UI 컴포넌트
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   ├── database/               # Drizzle 스키마 및 클라이언트
│   │   ├── src/
│   │   └── package.json
│   ├── config-eslint/          # 공유 ESLint 설정
│   │   └── package.json
│   ├── config-typescript/      # 공유 TypeScript 설정
│   │   └── package.json
│   └── utils/                  # 공유 유틸리티
│       ├── src/
│       └── package.json
├── turbo.json
├── package.json
└── pnpm-workspace.yaml
```

---

## 설정 파일

### pnpm-workspace.yaml

```yaml
# pnpm-workspace.yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

### 루트 package.json

```json
{
  "name": "monorepo",
  "private": true,
  "scripts": {
    "dev": "turbo dev",
    "build": "turbo build",
    "lint": "turbo lint",
    "typecheck": "turbo typecheck",
    "test": "turbo test",
    "format": "prettier --write \"**/*.{ts,tsx,md}\"",
    "clean": "turbo clean && rm -rf node_modules"
  },
  "devDependencies": {
    "prettier": "^3.4.2",
    "turbo": "^2.3.3"
  },
  "packageManager": "pnpm@9.14.4"
}
```

### turbo.json

```json
{
  "$schema": "https://turbo.build/schema.json",
  "ui": "tui",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**", "dist/**"],
      "env": ["DATABASE_URL", "NEXT_PUBLIC_*"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {
      "dependsOn": ["^build"]
    },
    "typecheck": {
      "dependsOn": ["^build"]
    },
    "test": {
      "dependsOn": ["^build"]
    },
    "clean": {
      "cache": false
    }
  }
}
```

---

## 공유 패키지

### packages/ui

```json
// packages/ui/package.json
{
  "name": "@repo/ui",
  "version": "0.0.0",
  "private": true,
  "sideEffects": false,
  "exports": {
    "./button": "./src/button.tsx",
    "./card": "./src/card.tsx",
    "./input": "./src/input.tsx",
    "./globals.css": "./src/globals.css"
  },
  "devDependencies": {
    "@repo/config-typescript": "workspace:*",
    "typescript": "^5.7.2"
  },
  "peerDependencies": {
    "react": "^19.0.0"
  }
}
```

```tsx
// packages/ui/src/button.tsx
import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from './lib/utils';

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground shadow hover:bg-primary/90',
        destructive: 'bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90',
        outline: 'border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground',
        secondary: 'bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'text-primary underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-9 px-4 py-2',
        sm: 'h-8 rounded-md px-3 text-xs',
        lg: 'h-10 rounded-md px-8',
        icon: 'h-9 w-9',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button';
    return (
      <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />
    );
  }
);
Button.displayName = 'Button';

export { Button, buttonVariants };
```

### packages/database

```json
// packages/database/package.json
{
  "name": "@repo/database",
  "version": "0.0.0",
  "private": true,
  "exports": {
    ".": "./src/index.ts",
    "./schema": "./src/schema/index.ts",
    "./client": "./src/client.ts"
  },
  "scripts": {
    "db:generate": "drizzle-kit generate",
    "db:migrate": "drizzle-kit migrate",
    "db:push": "drizzle-kit push",
    "db:studio": "drizzle-kit studio"
  },
  "dependencies": {
    "@neondatabase/serverless": "^0.10.4",
    "drizzle-orm": "^0.36.4"
  },
  "devDependencies": {
    "@repo/config-typescript": "workspace:*",
    "drizzle-kit": "^0.28.1",
    "typescript": "^5.7.2"
  }
}
```

```typescript
// packages/database/src/client.ts
import { neon } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';
import * as schema from './schema';

const sql = neon(process.env.DATABASE_URL!);
export const db = drizzle(sql, { schema });
export type Database = typeof db;
```

```typescript
// packages/database/src/schema/index.ts
export * from './users';
export * from './posts';
```

### packages/config-typescript

```json
// packages/config-typescript/package.json
{
  "name": "@repo/config-typescript",
  "version": "0.0.0",
  "private": true,
  "exports": {
    "./base.json": "./base.json",
    "./nextjs.json": "./nextjs.json",
    "./react-library.json": "./react-library.json"
  }
}
```

```json
// packages/config-typescript/base.json
{
  "$schema": "https://json.schemastore.org/tsconfig",
  "display": "Base TypeScript Config",
  "compilerOptions": {
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "moduleResolution": "Bundler",
    "module": "ESNext",
    "moduleDetection": "force",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "incremental": true,
    "noUncheckedIndexedAccess": true,
    "noEmit": true,
    "verbatimModuleSyntax": true
  },
  "$note": "Node.js 20.19+ 권장. moduleResolution: Bundler는 Next.js 16 App Router 권장 설정"
}
```

```json
// packages/config-typescript/nextjs.json
{
  "$schema": "https://json.schemastore.org/tsconfig",
  "extends": "./base.json",
  "compilerOptions": {
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "jsx": "preserve",
    "plugins": [{ "name": "next" }]
  }
}
```

### packages/config-eslint

```json
// packages/config-eslint/package.json
{
  "name": "@repo/config-eslint",
  "version": "0.0.0",
  "private": true,
  "exports": {
    "./base": "./base.js",
    "./nextjs": "./nextjs.js"
  },
  "dependencies": {
    "eslint": "^10.4.0",
    "@eslint/js": "^10.0.1",
    "typescript-eslint": "^8.59.4",
    "eslint-config-next": "^16.2.6"
  },
  "peerDependencies": {
    "eslint": ">=9.0.0",
    "typescript": ">=5.9.3"
  }
}
```

```javascript
// packages/config-eslint/nextjs.js
import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
  {
    rules: {
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    },
  }
);
```

---

## 앱 설정

### apps/web

```json
// apps/web/package.json
{
  "name": "@repo/web",
  "version": "0.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev --port 3000",
    "dev:webpack": "next dev --webpack --port 3000",
    "build": "next build",
    "start": "next start",
    "lint": "eslint .",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "@repo/database": "workspace:*",
    "@repo/ui": "workspace:*",
    "next": "^16.2.6",
    "react": "^19.2.6",
    "react-dom": "^19.2.6"
  },
  "devDependencies": {
    "@repo/config-eslint": "workspace:*",
    "@repo/config-typescript": "workspace:*",
    "@types/node": "^20.19.41",
    "@types/react": "^19.2.15",
    "typescript": "^5.9.3"
  }
}
```

```json
// apps/web/tsconfig.json
{
  "extends": "@repo/config-typescript/nextjs.json",
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

```tsx
// apps/web/app/page.tsx
import { Button } from '@repo/ui/button';
import { db } from '@repo/database/client';

export default async function Home() {
  const users = await db.query.users.findMany();

  return (
    <div>
      <h1>Web App</h1>
      <Button>Shared Button</Button>
      <pre>{JSON.stringify(users, null, 2)}</pre>
    </div>
  );
}
```

---

## 명령어

```bash
# 전체 빌드
pnpm build

# 특정 앱만 빌드
pnpm build --filter=@repo/web

# 특정 앱 개발 서버
pnpm dev --filter=@repo/web

# 패키지 추가 (특정 workspace)
pnpm add lodash --filter=@repo/web

# 워크스페이스 패키지 추가
pnpm add @repo/ui --filter=@repo/web --workspace

# 전체 의존성 업데이트
pnpm update -r

# 캐시 정리
pnpm clean
```

---

## CI/CD

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - name: Build
        run: pnpm build
      - name: Lint
        run: pnpm lint
      - name: Typecheck
        run: pnpm typecheck
      - name: Test
        run: pnpm test
```

---

## 테스트 예제

### Turborepo 설정 테스트

```typescript
// scripts/__tests__/turbo-config.test.ts
import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';

describe('Turborepo Configuration', () => {
  it('turbo.json이 유효하다', () => {
    const config = JSON.parse(readFileSync('turbo.json', 'utf-8'));

    expect(config).toHaveProperty('tasks');
    expect(config.tasks).toHaveProperty('build');
    expect(config.tasks).toHaveProperty('lint');
  });

  it('build task가 올바른 의존성을 가진다', () => {
    const config = JSON.parse(readFileSync('turbo.json', 'utf-8'));

    expect(config.tasks.build.dependsOn).toContain('^build');
  });

  it('출력 폴더가 정의되어 있다', () => {
    const config = JSON.parse(readFileSync('turbo.json', 'utf-8'));

    expect(config.tasks.build.outputs).toContain('.next/**');
  });
});
```

### 공유 패키지 테스트

```typescript
// packages/ui/__tests__/button.test.tsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Button } from '../src/button';

describe('Button (shared UI)', () => {
  it('children을 렌더링한다', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('variant props를 적용한다', () => {
    render(<Button variant="destructive">Delete</Button>);
    expect(screen.getByRole('button')).toHaveClass('bg-destructive');
  });
});
```

---

## 안티패턴

### 1. 순환 의존성

```json
// ❌ Bad: 패키지 간 순환 의존성
// packages/ui → packages/utils → packages/ui

// ✅ Good: 단방향 의존성
// packages/ui → packages/utils (utils는 ui 미참조)
```

### 2. 중복 의존성

```json
// ❌ Bad: 모든 앱에서 동일 버전 중복 관리
// apps/web: "react": "^18.2.0"
// apps/docs: "react": "^18.3.0"

// ✅ Good: 루트에서 버전 통합 관리
// package.json (root)
{
  "pnpm": {
    "overrides": {
      "react": "^18.3.0"
    }
  }
}
```

### 3. 불필요한 빌드

```json
// ❌ Bad: 매번 전체 빌드
{ "scripts": { "build": "pnpm -r build" } }

// ✅ Good: Turborepo 캐싱 활용
{ "scripts": { "build": "turbo build" } }
```

### 4. Internal Package 미설정

```json
// ❌ Bad: 매번 빌드 필요
{ "main": "dist/index.js" }

// ✅ Good: 직접 참조
{
  "exports": { ".": { "default": "./src/index.ts" } }
}
// + next.config.ts에 transpilePackages 설정
```

---

## 에러 처리

### 패키지 의존성 검사

```typescript
// scripts/check-deps.ts
import { execSync } from 'child_process';

function checkCircularDeps(): void {
  try {
    execSync('pnpm ls --depth Infinity', { stdio: 'pipe' });
  } catch (error) {
    if (error.message.includes('circular')) {
      console.error('::error::Circular dependency detected');
      process.exit(1);
    }
  }
}
```

### Turborepo 에러 디버깅

```bash
# 상세 로그
turbo build --verbosity=2

# dry-run으로 확인
turbo build --filter=@repo/web --dry-run
```

---

## 성능 고려사항

### 1. 리모트 캐싱

```bash
npx turbo login
npx turbo link
```

### 2. 필터링된 빌드

```bash
# 변경된 파일 기반
turbo build --filter='...[origin/main]'

# 특정 앱과 의존성
turbo build --filter=@repo/web...
```

### 3. 병렬 실행 최적화

```json
// turbo.json
{
  "tasks": {
    "lint": { "dependsOn": [], "cache": true },
    "test": { "dependsOn": [], "cache": true }
  }
}
```

---

## 보안 고려사항

### 1. 환경 변수 격리

```json
// turbo.json
{
  "globalEnv": ["CI"],
  "tasks": {
    "build": { "env": ["DATABASE_URL", "NEXT_PUBLIC_*"] }
  }
}
```

### 2. Private 패키지

```json
{
  "private": true,
  "publishConfig": { "access": "restricted" }
}
```

### 3. 의존성 감사

```bash
pnpm audit --audit-level=high
```

---

## References

- `_references/ARCHITECTURE-PATTERN.md`
- `_references/TEST-PATTERN.md`
