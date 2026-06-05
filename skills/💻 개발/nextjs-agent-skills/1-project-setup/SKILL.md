---
name: project-setup
description: |
  Next.js 프로젝트 초기 설정 및 의존성 구성을 수행합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Project Setup Skill

Extends: `../../_shared/project-setup/SKILL.md` (공통 프로세스 참조)

Next.js 프로젝트 초기 설정 및 의존성 구성을 수행합니다.

## Triggers

- "프로젝트 생성", "프로젝트 설정", "nextjs init", "nextjs create"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectName` | ✅ | 프로젝트 이름 (kebab-case) |
| `features` | ❌ | 선택 기능 (auth, i18n, pwa 등) |

---

## Output

### package.json 핵심 의존성

```json
{
  "name": "{project-name}",
  "version": "0.1.0",
  "private": true,
  "engines": {
    "node": ">=20.19.0"
  },
  "scripts": {
    "dev": "next dev",
    "dev:webpack": "next dev --webpack",
    "build": "next build",
    "start": "next start",
    "lint": "eslint . --max-warnings=0",
    "lint:fix": "eslint . --fix",
    "typecheck": "next typegen && tsc --noEmit",
    "test": "vitest",
    "test:run": "vitest run",
    "test:coverage": "vitest run --coverage",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "db:generate": "drizzle-kit generate",
    "db:migrate": "drizzle-kit migrate",
    "db:push": "drizzle-kit push",
    "db:studio": "drizzle-kit studio"
  },
  "dependencies": {
    "next": "^16.2.6",
    "react": "^19.2.6",
    "react-dom": "^19.2.6",
    "next-themes": "^0.4.6",

    "@tanstack/react-query": "^5.100.14",
    "@tanstack/react-query-devtools": "^5.100.14",
    "zustand": "^5.0.13",
    "nuqs": "^2.8.9",

    "drizzle-orm": "^0.45.2",
    "@neondatabase/serverless": "^1.1.0",

    "zod": "^4.4.3",
    "react-hook-form": "^7.76.1",
    "@hookform/resolvers": "^5.4.0",
    "next-safe-action": "^8.5.3",

    "@radix-ui/react-slot": "^1.2.4",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "tailwind-merge": "^3.6.0",
    "lucide-react": "^1.16.0",
    "sonner": "^2.0.7",

    "framer-motion": "^12.40.0",
    "@t3-oss/env-nextjs": "^0.13.11"
  },
  "devDependencies": {
    "typescript": "^5.9.3",
    "@types/node": "^20.19.41",
    "@types/react": "^19.2.15",
    "@types/react-dom": "^19.2.3",

    "tailwindcss": "^4.3.0",
    "@tailwindcss/postcss": "^4.3.0",
    "postcss": "^8.5.15",
    "tw-animate-css": "^1.4.0",

    "drizzle-kit": "^0.31.10",

    "vitest": "^4.1.7",
    "@vitejs/plugin-react": "^6.0.2",
    "vite-tsconfig-paths": "^6.1.1",
    "@testing-library/react": "^16.3.2",
    "@testing-library/dom": "^10.4.1",
    "@testing-library/jest-dom": "^6.9.1",
    "jsdom": "^29.1.1",
    "msw": "^2.14.6",

    "@playwright/test": "^1.60.0",

    "eslint": "^10.4.0",
    "eslint-config-next": "^16.2.6",
    "@eslint/eslintrc": "^3.3.5",

    "prettier": "^3.8.3",
    "prettier-plugin-tailwindcss": "^0.8.0"
  }
}
```

### 프로젝트 생성 명령어

```bash
# Next.js 프로젝트 생성
npx create-next-app@latest {project-name} \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir \
  --import-alias "@/*"

cd {project-name}

# 핵심 의존성 설치
npm install @tanstack/react-query @tanstack/react-query-devtools zustand nuqs
npm install drizzle-orm @neondatabase/serverless
npm install zod react-hook-form @hookform/resolvers next-safe-action
npm install framer-motion sonner lucide-react
npm install @t3-oss/env-nextjs

# Dev 의존성
npm install -D drizzle-kit
npm install -D vitest @vitejs/plugin-react vite-tsconfig-paths
npm install -D @testing-library/react @testing-library/dom @testing-library/jest-dom jsdom
npm install -D msw @playwright/test
npm install -D tw-animate-css

# shadcn/ui 초기화
npx shadcn@latest init -d

# 기본 컴포넌트 추가
npx shadcn@latest add button card form input label
```

### 디렉토리 구조

```
{project-name}/
├── src/
│   ├── app/
│   │   ├── (auth)/              # Route Group: 인증
│   │   ├── (dashboard)/         # Route Group: 대시보드
│   │   ├── api/                 # API Routes
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── globals.css
│   │   └── providers.tsx
│   │
│   ├── components/
│   │   ├── ui/                  # shadcn/ui
│   │   ├── atoms/
│   │   ├── molecules/
│   │   ├── organisms/
│   │   └── templates/
│   │
│   ├── features/                # Feature 모듈
│   │
│   ├── lib/
│   │   ├── db/                  # Drizzle ORM
│   │   │   ├── schema/
│   │   │   ├── migrations/
│   │   │   └── index.ts
│   │   ├── auth/                # Auth.js
│   │   ├── api/                 # API 클라이언트
│   │   ├── actions/             # next-safe-action
│   │   └── utils/
│   │
│   ├── hooks/                   # 공통 훅
│   ├── stores/                  # 글로벌 스토어
│   ├── types/                   # 글로벌 타입
│   ├── env.ts                   # T3 Env
│   └── proxy.ts                 # Next.js 16 Proxy (기존 Middleware)
│
├── tests/
│   ├── setup.ts
│   ├── utils/
│   ├── mocks/
│   └── e2e/
│
├── public/
├── drizzle.config.ts
├── vitest.config.ts
├── playwright.config.ts
├── next.config.ts
├── tailwind.config.ts           # (Tailwind v4는 선택적)
├── tsconfig.json
├── .env.local
└── .env.example
```

### 설정 파일

#### next.config.ts

```typescript
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  typedRoutes: true,
  cacheComponents: true,
};

export default nextConfig;
```

#### vitest.config.ts

```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import tsconfigPaths from 'vite-tsconfig-paths';

export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
    },
  },
});
```

#### postcss.config.js (Tailwind v4 필수)

```javascript
export default {
  plugins: {
    '@tailwindcss/postcss': {},
  },
};
```

#### drizzle.config.ts

```typescript
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  schema: './src/lib/db/schema/index.ts',
  out: './src/lib/db/migrations',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
});
```

#### .env.example

```bash
# Database
DATABASE_URL="postgresql://user:password@host:5432/database?sslmode=require"

# Auth
AUTH_SECRET="your-auth-secret"

# App
NEXT_PUBLIC_APP_URL="http://localhost:3000"
```

---

## 테스트 설정

### tests/setup.ts

```typescript
// tests/setup.ts
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

// 각 테스트 후 클린업
afterEach(() => {
  cleanup();
});

// Next.js 환경 모킹
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    prefetch: vi.fn(),
  }),
  usePathname: () => '/',
  useSearchParams: () => new URLSearchParams(),
  useParams: () => ({}),
}));

// 환경 변수 모킹
vi.stubEnv('DATABASE_URL', 'postgresql://test:test@localhost:5432/test');
vi.stubEnv('NEXT_PUBLIC_APP_URL', 'http://localhost:3000');
```

---

## 테스트 예제

### 환경 설정 검증 테스트

```typescript
// tests/config.test.ts
import { describe, it, expect } from 'vitest';
import { env } from '@/env';

describe('Environment Configuration', () => {
  it('has required environment variables', () => {
    expect(env.DATABASE_URL).toBeDefined();
    expect(env.NEXT_PUBLIC_APP_URL).toBeDefined();
  });

  it('validates DATABASE_URL format', () => {
    expect(env.DATABASE_URL).toMatch(/^postgres(ql)?:\/\//);
  });

  it('validates NEXT_PUBLIC_APP_URL format', () => {
    expect(env.NEXT_PUBLIC_APP_URL).toMatch(/^https?:\/\//);
  });
});

describe('Package Dependencies', () => {
  it('has compatible React version for Next.js 16', async () => {
    const pkg = await import('../../package.json');
    const reactVersion = pkg.dependencies?.react || '';
    expect(reactVersion).toMatch(/\^19|^19/);
  });

  it('has required dev dependencies for testing', async () => {
    const pkg = await import('../../package.json');
    expect(pkg.devDependencies).toHaveProperty('vitest');
    expect(pkg.devDependencies).toHaveProperty('@testing-library/react');
  });
});
```

### 디렉토리 구조 검증 테스트

```typescript
// tests/structure.test.ts
import { describe, it, expect } from 'vitest';
import { existsSync } from 'fs';
import { join } from 'path';

describe('Project Structure', () => {
  const requiredDirs = [
    'src/app',
    'src/components',
    'src/features',
    'src/lib',
    'src/hooks',
    'tests',
  ];

  it.each(requiredDirs)('has required directory: %s', (dir) => {
    expect(existsSync(join(process.cwd(), dir))).toBe(true);
  });

  const requiredFiles = [
    'next.config.ts',
    'vitest.config.ts',
    'drizzle.config.ts',
    'src/env.ts',
    'tests/setup.ts',
  ];

  it.each(requiredFiles)('has required file: %s', (file) => {
    expect(existsSync(join(process.cwd(), file))).toBe(true);
  });
});
```

### Vitest 설정 테스트

```typescript
// tests/vitest-setup.test.ts
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

// 모킹이 제대로 동작하는지 확인
describe('Vitest Setup', () => {
  it('has jsdom environment configured', () => {
    expect(typeof window).toBe('object');
    expect(typeof document).toBe('object');
  });

  it('has jest-dom matchers available', () => {
    const div = document.createElement('div');
    div.textContent = 'test';
    document.body.appendChild(div);

    expect(div).toBeInTheDocument();
    expect(div).toHaveTextContent('test');
  });

  it('can mock modules', () => {
    const mockFn = vi.fn(() => 'mocked');
    expect(mockFn()).toBe('mocked');
    expect(mockFn).toHaveBeenCalledTimes(1);
  });

  it('has Next.js navigation mocked', async () => {
    const { useRouter } = await import('next/navigation');
    const router = useRouter();

    expect(router.push).toBeDefined();
    expect(router.replace).toBeDefined();
  });
});
```

---

## 안티패턴

### 1. 잘못된 디렉토리 구조

```
// ❌ Bad: 모든 파일을 src/에 평면적으로 배치
src/
├── UserService.ts
├── ProductService.ts
├── UserComponent.tsx
├── ProductComponent.tsx
├── userUtils.ts
└── ... (수백 개 파일)

// ✅ Good: Feature 기반 모듈화
src/
├── features/
│   ├── user/
│   │   ├── api/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── schemas/
│   └── product/
│       └── ...
├── lib/
└── components/
```

### 2. 버전 불일치

```json
// ❌ Bad: 호환되지 않는 버전 조합
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^18.0.0",  // ❌ Next.js 16 기준과 불일치
    "@tanstack/react-query": "^4.0.0"  // ❌ v5 권장
  }
}

// ✅ Good: 호환되는 최신 버전
{
  "dependencies": {
    "next": "^16.2.6",
    "react": "^19.2.6",
    "react-dom": "^19.2.6",
    "@tanstack/react-query": "^5.100.14"
  }
}
```

### 3. 환경 변수 직접 참조

```typescript
// ❌ Bad: process.env 직접 사용 (타입 안전하지 않음)
const dbUrl = process.env.DATABASE_URL;  // string | undefined
fetch(process.env.API_URL + '/users');   // 런타임 에러 가능

// ✅ Good: T3 Env로 타입 안전하게
// env.ts
import { createEnv } from '@t3-oss/env-nextjs';
import { z } from 'zod';

export const env = createEnv({
  server: {
    DATABASE_URL: z.string().url(),
  },
  client: {
    NEXT_PUBLIC_APP_URL: z.string().url(),
  },
  runtimeEnv: {
    DATABASE_URL: process.env.DATABASE_URL,
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL,
  },
});

// 사용
import { env } from '@/env';
const dbUrl = env.DATABASE_URL;  // string (validated!)
```

### 4. Tailwind CSS v4 설정 오류

```javascript
// ❌ Bad: Tailwind v4에서 잘못된 postcss 설정
// postcss.config.js
module.exports = {
  plugins: {
    tailwindcss: {},  // ❌ v4에서는 이 방식 사용 안 함
    autoprefixer: {},
  },
};

// ✅ Good: Tailwind v4 올바른 설정
// postcss.config.js
export default {
  plugins: {
    '@tailwindcss/postcss': {},
  },
};
```

### 5. Test 설정 누락

```typescript
// ❌ Bad: jsdom 환경 설정 없이 컴포넌트 테스트
// vitest.config.ts
export default defineConfig({
  test: {
    // environment 누락 → DOM API 에러
  },
});

// ✅ Good: 올바른 테스트 환경 설정
export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
  },
});
```

---

## 에러 처리

### 설치 오류 해결

```bash
# Peer dependency 충돌
npm install --legacy-peer-deps

# 캐시 문제
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

# Sharp 설치 문제 (macOS M1/M2)
npm install --platform=darwin --arch=arm64 sharp
```

### 빌드 에러 대응

```typescript
// next.config.ts - 일반적인 빌드 에러 해결
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // TypeScript 에러 무시 (임시)
  typescript: {
    ignoreBuildErrors: process.env.CI !== 'true',
  },

  // ESLint 에러 무시 (임시)
  eslint: {
    ignoreDuringBuilds: process.env.CI !== 'true',
  },

  // 외부 패키지 트랜스파일
  transpilePackages: ['some-package'],

  typedRoutes: true,
  cacheComponents: true,
};

export default nextConfig;
```

### 환경 변수 검증 실패

```typescript
// 앱 시작 시 환경 변수 검증
// env.ts
import { createEnv } from '@t3-oss/env-nextjs';
import { z } from 'zod';

export const env = createEnv({
  server: {
    DATABASE_URL: z.string().url().describe('PostgreSQL connection URL'),
    AUTH_SECRET: z.string().min(32).describe('Auth.js secret (32+ chars)'),
  },
  client: {
    NEXT_PUBLIC_APP_URL: z.string().url(),
  },
  runtimeEnv: {
    DATABASE_URL: process.env.DATABASE_URL,
    AUTH_SECRET: process.env.AUTH_SECRET,
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL,
  },
  // 빌드 시 검증 건너뛰기 (CI에서 유용)
  skipValidation: process.env.SKIP_ENV_VALIDATION === 'true',
  // 빈 문자열을 undefined로 처리
  emptyStringAsUndefined: true,
});
```

---

## 성능 고려사항

### Turbopack 활용

```bash
# 개발 서버 Turbopack 사용 (Next.js 16 기본값)
npm run dev

# Webpack으로 회귀가 필요한 경우만 명시
npm run dev:webpack

# 벤치마크
# Cold start: ~2.5초 (Turbopack) vs ~8초 (Webpack)
# HMR: ~50ms (Turbopack) vs ~300ms (Webpack)
```

### Bundle Size 최적화

```typescript
// next.config.ts
const nextConfig: NextConfig = {
  experimental: {
    optimizePackageImports: [
      'lucide-react',
      '@radix-ui/react-icons',
      'framer-motion',
    ],
  },
};
```

---

## 보안 고려사항

### 환경 변수 보안

```bash
# .env.local (Git에 포함하지 않음)
DATABASE_URL="postgresql://..."
AUTH_SECRET="your-super-secret-key-32-chars-min"

# .env.example (Git에 포함, 값은 비움)
DATABASE_URL=""
AUTH_SECRET=""
```

### .gitignore 필수 항목

```gitignore
# 환경 변수
.env
.env.local
.env.*.local

# 의존성
node_modules/

# 빌드 결과물
.next/
out/

# 테스트 커버리지
coverage/

# IDE
.idea/
.vscode/

# OS
.DS_Store
Thumbs.db

# 로그
*.log
npm-debug.log*
```

### 시크릿 생성

```bash
# AUTH_SECRET 생성 (32자 이상 권장)
openssl rand -base64 32

# 또는 Node.js로
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

---

## 실행 확인 체크리스트

```bash
# 1. 개발 서버 시작
npm run dev
# ✓ localhost:3000 접속 확인

# 2. 타입 체크
npx tsc --noEmit
# ✓ 에러 없음

# 3. Lint
npm run lint
# ✓ 에러 없음

# 4. 테스트
npm run test:run
# ✓ 모든 테스트 통과

# 5. 빌드
npm run build
# ✓ 빌드 성공

# 6. 프로덕션 서버
npm run start
# ✓ 빌드된 앱 실행 확인
```

---

## References

- `_references/ARCHITECTURE-PATTERN.md` - Clean Architecture 가이드
- `_references/TEST-PATTERN.md` - 테스트 설정 및 피라미드
