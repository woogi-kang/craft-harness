---
name: routing
description: |
  Flutter 라우팅(GoRouter/Navigator)을 Next.js App Router로 변환합니다.
  동적 라우트, 중첩 레이아웃, 미들웨어를 설정합니다.
triggers:
  - "라우팅 변환"
  - "routing"
  - "페이지 변환"
---

# Routing Conversion Skill

Flutter 라우팅을 Next.js App Router로 변환합니다.

## 입력

- Flutter 라우팅 코드 (GoRouter/Navigator)
- 매핑 전략 (mapping-strategy.md)

## 출력

- App Router 디렉토리 구조
- 페이지 파일 (.tsx)
- 레이아웃 파일 (.tsx)
- 미들웨어 (필요시)

---

## 라우팅 변환 원칙

### 핵심 차이점

| Flutter | Next.js App Router |
|---------|-------------------|
| 선언적 라우트 설정 | 파일 기반 라우팅 |
| GoRoute/Navigator | 디렉토리 구조 |
| 런타임 라우트 매칭 | 빌드 타임 라우트 생성 |
| Widget 반환 | React Component 반환 |

### 변환 전략

1. GoRouter 라우트 → 디렉토리 구조
2. ShellRoute → Layout
3. redirect → Middleware
4. pathParameters → Dynamic segments `[param]`
5. queryParameters → `searchParams`

---

## GoRouter → App Router 변환

### 기본 라우트

```dart
// Flutter GoRouter
GoRouter(
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => HomeScreen(),
    ),
    GoRoute(
      path: '/about',
      builder: (context, state) => AboutScreen(),
    ),
  ],
)
```

```
// Next.js App Router 디렉토리
src/app/
├── page.tsx          # / → HomeScreen
├── about/
│   └── page.tsx      # /about → AboutScreen
└── layout.tsx
```

### 동적 라우트

```dart
// Flutter
GoRoute(
  path: '/user/:id',
  builder: (context, state) {
    final id = state.pathParameters['id']!;
    return UserScreen(id: id);
  },
),
GoRoute(
  path: '/product/:category/:id',
  builder: (context, state) {
    final category = state.pathParameters['category']!;
    final id = state.pathParameters['id']!;
    return ProductScreen(category: category, id: id);
  },
),
```

```
// Next.js
src/app/
├── user/
│   └── [id]/
│       └── page.tsx
└── product/
    └── [category]/
        └── [id]/
            └── page.tsx
```

```tsx
// src/app/user/[id]/page.tsx
interface UserPageProps {
  params: { id: string }
}

export default function UserPage({ params }: UserPageProps) {
  const { id } = params
  return <UserScreen id={id} />
}

// src/app/product/[category]/[id]/page.tsx
interface ProductPageProps {
  params: { category: string; id: string }
}

export default function ProductPage({ params }: ProductPageProps) {
  const { category, id } = params
  return <ProductScreen category={category} id={id} />
}
```

### 쿼리 파라미터

```dart
// Flutter
GoRoute(
  path: '/search',
  builder: (context, state) {
    final query = state.uri.queryParameters['q'];
    final page = state.uri.queryParameters['page'];
    return SearchScreen(query: query, page: page);
  },
),
```

```tsx
// Next.js
// src/app/search/page.tsx
interface SearchPageProps {
  searchParams: { q?: string; page?: string }
}

export default function SearchPage({ searchParams }: SearchPageProps) {
  const { q: query, page } = searchParams
  return <SearchScreen query={query} page={page} />
}
```

### 중첩 라우트 (ShellRoute)

```dart
// Flutter
ShellRoute(
  builder: (context, state, child) {
    return MainShell(child: child);
  },
  routes: [
    GoRoute(path: '/home', builder: (_, __) => HomeScreen()),
    GoRoute(path: '/profile', builder: (_, __) => ProfileScreen()),
    GoRoute(path: '/settings', builder: (_, __) => SettingsScreen()),
  ],
),
```

```
// Next.js - Route Groups
src/app/
├── (main)/                    # Route Group (URL에 영향 없음)
│   ├── layout.tsx             # MainShell
│   ├── home/
│   │   └── page.tsx
│   ├── profile/
│   │   └── page.tsx
│   └── settings/
│       └── page.tsx
└── layout.tsx                 # Root Layout
```

```tsx
// src/app/(main)/layout.tsx
export default function MainLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1">{children}</main>
      <BottomNav className="md:hidden" />
    </div>
  )
}
```

### 인증 라우트 그룹

```dart
// Flutter
GoRouter(
  redirect: (context, state) {
    final isLoggedIn = authService.isLoggedIn;
    final isAuthRoute = state.matchedLocation.startsWith('/auth');

    if (!isLoggedIn && !isAuthRoute) {
      return '/auth/login';
    }
    if (isLoggedIn && isAuthRoute) {
      return '/';
    }
    return null;
  },
  routes: [
    GoRoute(path: '/auth/login', builder: ...),
    GoRoute(path: '/auth/register', builder: ...),
    // Protected routes
    GoRoute(path: '/', builder: ...),
    GoRoute(path: '/profile', builder: ...),
  ],
)
```

```
// Next.js
src/app/
├── (auth)/                    # 인증 페이지 그룹
│   ├── layout.tsx             # 인증 레이아웃 (심플)
│   ├── login/
│   │   └── page.tsx
│   └── register/
│       └── page.tsx
├── (protected)/               # 보호된 페이지 그룹
│   ├── layout.tsx             # 인증 체크 + 메인 레이아웃
│   ├── page.tsx               # /
│   └── profile/
│       └── page.tsx
└── layout.tsx
```

```tsx
// src/app/(protected)/layout.tsx
import { redirect } from 'next/navigation'
import { auth } from '@/lib/auth'

export default async function ProtectedLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const session = await auth()

  if (!session) {
    redirect('/login')
  }

  return (
    <>
      <Header user={session.user} />
      <main>{children}</main>
    </>
  )
}
```

```typescript
// src/middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-token')
  const isAuthPage = request.nextUrl.pathname.startsWith('/login') ||
                     request.nextUrl.pathname.startsWith('/register')

  if (!token && !isAuthPage) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  if (token && isAuthPage) {
    return NextResponse.redirect(new URL('/', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}
```

---

## 네비게이션 변환

### 프로그래매틱 네비게이션

```dart
// Flutter
context.go('/user/123');
context.push('/user/123');
context.pop();
context.pushReplacement('/home');
```

```tsx
// Next.js
'use client'

import { useRouter } from 'next/navigation'

function MyComponent() {
  const router = useRouter()

  const handleNavigation = () => {
    router.push('/user/123')    // context.go / context.push
    router.back()               // context.pop
    router.replace('/home')     // context.pushReplacement
  }
}
```

### Link 컴포넌트

```dart
// Flutter
InkWell(
  onTap: () => context.go('/about'),
  child: Text('About'),
)
```

```tsx
// Next.js
import Link from 'next/link'

<Link href="/about">About</Link>

// 동적 경로
<Link href={`/user/${user.id}`}>View Profile</Link>

// 쿼리 파라미터
<Link href={{ pathname: '/search', query: { q: 'keyword' } }}>
  Search
</Link>
```

### 뒤로가기 방지 (WillPopScope)

```dart
// Flutter
WillPopScope(
  onWillPop: () async {
    final shouldPop = await showConfirmDialog();
    return shouldPop;
  },
  child: ...
)
```

```tsx
// Next.js
'use client'

import { useEffect } from 'react'

function FormPage() {
  const [hasChanges, setHasChanges] = useState(false)

  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasChanges) {
        e.preventDefault()
        e.returnValue = ''
      }
    }

    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => window.removeEventListener('beforeunload', handleBeforeUnload)
  }, [hasChanges])

  // 브라우저 네비게이션 차단은 제한적
  // 앱 내 네비게이션은 확인 모달로 처리
}
```

---

## 라우트 전환 애니메이션

```dart
// Flutter
GoRoute(
  path: '/details',
  pageBuilder: (context, state) {
    return CustomTransitionPage(
      child: DetailsScreen(),
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        return SlideTransition(
          position: Tween<Offset>(
            begin: const Offset(1, 0),
            end: Offset.zero,
          ).animate(animation),
          child: child,
        );
      },
    );
  },
)
```

```tsx
// Next.js + Framer Motion
// src/app/template.tsx (또는 layout.tsx)
'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { usePathname } from 'next/navigation'

export default function Template({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={pathname}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -20 }}
        transition={{ duration: 0.2 }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}
```

---

## 출력 파일 구조

```
src/app/
├── (auth)/
│   ├── layout.tsx
│   ├── login/
│   │   └── page.tsx
│   └── register/
│       └── page.tsx
│
├── (main)/
│   ├── layout.tsx
│   ├── page.tsx                 # /
│   ├── profile/
│   │   └── page.tsx             # /profile
│   ├── settings/
│   │   └── page.tsx             # /settings
│   └── [category]/
│       ├── page.tsx             # /[category]
│       └── [id]/
│           └── page.tsx         # /[category]/[id]
│
├── api/                         # API Routes (필요시)
│   └── ...
│
├── layout.tsx                   # Root Layout
├── loading.tsx                  # Global Loading UI
├── error.tsx                    # Global Error UI
└── not-found.tsx               # 404 페이지

middleware.ts                    # 인증 미들웨어
```

### 페이지 파일 템플릿

```tsx
// src/app/(main)/[category]/[id]/page.tsx

import { notFound } from 'next/navigation'
import { productApi } from '@/lib/api/product'

interface ProductPageProps {
  params: { category: string; id: string }
}

/**
 * 상품 상세 페이지
 *
 * @flutter ProductDetailScreen (lib/features/product/product_detail_screen.dart)
 * @route /product/:category/:id → /[category]/[id]
 */
export default async function ProductPage({ params }: ProductPageProps) {
  const { category, id } = params

  const product = await productApi.getProduct(id)

  if (!product) {
    notFound()
  }

  return <ProductDetail product={product} />
}

// Metadata
export async function generateMetadata({ params }: ProductPageProps) {
  const product = await productApi.getProduct(params.id)
  return {
    title: product?.name ?? 'Product',
    description: product?.description,
  }
}
```
