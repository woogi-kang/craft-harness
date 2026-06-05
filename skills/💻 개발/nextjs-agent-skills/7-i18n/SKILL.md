---
name: i18n
description: |
  next-intl을 사용하여 다국어 지원을 설정합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Internationalization (i18n) Skill

next-intl을 사용하여 다국어 지원을 설정합니다.

## Triggers

- "다국어", "i18n", "국제화", "next-intl", "번역"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | Next.js 프로젝트 경로 |
| `locales` | ❌ | 지원 언어 목록 (기본: ko, en) |
| `defaultLocale` | ❌ | 기본 언어 (기본: ko) |

---

## 설치

```bash
npm install next-intl@^4.12.0
```

> **Note**: next-intl 4.x는 Next.js 16 App Router와 React 19 기준으로 사용합니다. Proxy 파일은 `proxy.ts`로 작성합니다.

---

## 디렉토리 구조

```
src/
├── app/
│   └── [locale]/              # 동적 로케일 세그먼트
│       ├── layout.tsx
│       ├── page.tsx
│       └── (dashboard)/
│           └── page.tsx
│
├── i18n/
│   ├── routing.ts             # 라우팅 설정
│   ├── request.ts             # 요청 설정
│   └── navigation.ts          # 네비게이션 헬퍼
│
└── messages/                  # 번역 파일
    ├── ko.json
    └── en.json
```

---

## 설정 파일

### 라우팅 설정

```typescript
// i18n/routing.ts
import { defineRouting } from 'next-intl/routing';

export const routing = defineRouting({
  locales: ['ko', 'en'],
  defaultLocale: 'ko',
  localePrefix: 'as-needed', // 기본 로케일은 URL에서 생략
});

export type Locale = (typeof routing.locales)[number];
```

### 요청 설정

```typescript
// i18n/request.ts
import { getRequestConfig } from 'next-intl/server';
import { routing } from './routing';

export default getRequestConfig(async ({ requestLocale }) => {
  let locale = await requestLocale;

  // 유효한 로케일인지 확인
  if (!locale || !routing.locales.includes(locale as any)) {
    locale = routing.defaultLocale;
  }

  // 메시지 로딩 에러 처리
  let messages;
  try {
    messages = (await import(`../messages/${locale}.json`)).default;
  } catch (error) {
    console.error(`Failed to load messages for locale: ${locale}`, error);
    // Fallback to default locale
    messages = (await import(`../messages/${routing.defaultLocale}.json`)).default;
  }

  return {
    locale,
    messages,
  };
});
```

### 네비게이션 헬퍼

```typescript
// i18n/navigation.ts
import { createNavigation } from 'next-intl/navigation';
import { routing } from './routing';

export const { Link, redirect, usePathname, useRouter } =
  createNavigation(routing);
```

---

## Proxy

```typescript
// proxy.ts
import createMiddleware from 'next-intl/middleware';
import type { NextRequest } from 'next/server';
import { routing } from './i18n/routing';

const intlMiddleware = createMiddleware(routing);

export function proxy(request: NextRequest) {
  return intlMiddleware(request);
}

export const config = {
  matcher: ['/', '/(ko|en)/:path*'],
};
```

---

## 레이아웃

```tsx
// app/[locale]/layout.tsx
import { NextIntlClientProvider } from 'next-intl';
import { getMessages, setRequestLocale } from 'next-intl/server';
import { routing } from '@/i18n/routing';
import { notFound } from 'next/navigation';

interface Props {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

export default async function LocaleLayout({ children, params }: Props) {
  const { locale } = await params;

  // 유효한 로케일인지 확인
  if (!routing.locales.includes(locale as any)) {
    notFound();
  }

  // Static rendering 활성화
  setRequestLocale(locale);

  const messages = await getMessages();

  return (
    <html lang={locale}>
      <body>
        <NextIntlClientProvider messages={messages}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
```

---

## 번역 파일

### messages/ko.json

```json
{
  "Common": {
    "loading": "로딩 중...",
    "error": "오류가 발생했습니다",
    "save": "저장",
    "cancel": "취소",
    "delete": "삭제",
    "edit": "수정",
    "confirm": "확인"
  },
  "Navigation": {
    "home": "홈",
    "dashboard": "대시보드",
    "settings": "설정",
    "profile": "프로필"
  },
  "Auth": {
    "login": "로그인",
    "logout": "로그아웃",
    "register": "회원가입",
    "email": "이메일",
    "password": "비밀번호",
    "forgotPassword": "비밀번호 찾기"
  },
  "Validation": {
    "required": "필수 입력 항목입니다",
    "email": "유효한 이메일을 입력하세요",
    "minLength": "{count}자 이상 입력하세요",
    "maxLength": "{count}자 이하로 입력하세요"
  },
  "HomePage": {
    "title": "환영합니다",
    "description": "Next.js로 만든 앱입니다"
  }
}
```

### messages/en.json

```json
{
  "Common": {
    "loading": "Loading...",
    "error": "An error occurred",
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "edit": "Edit",
    "confirm": "Confirm"
  },
  "Navigation": {
    "home": "Home",
    "dashboard": "Dashboard",
    "settings": "Settings",
    "profile": "Profile"
  },
  "Auth": {
    "login": "Login",
    "logout": "Logout",
    "register": "Register",
    "email": "Email",
    "password": "Password",
    "forgotPassword": "Forgot Password"
  },
  "Validation": {
    "required": "This field is required",
    "email": "Please enter a valid email",
    "minLength": "Must be at least {count} characters",
    "maxLength": "Must be {count} characters or less"
  },
  "HomePage": {
    "title": "Welcome",
    "description": "An app built with Next.js"
  }
}
```

---

## 사용 방법

### 서버 컴포넌트

```tsx
// app/[locale]/page.tsx
import { getTranslations, setRequestLocale } from 'next-intl/server';

interface Props {
  params: Promise<{ locale: string }>;
}

export default async function HomePage({ params }: Props) {
  const { locale } = await params;
  setRequestLocale(locale);

  const t = await getTranslations('HomePage');

  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('description')}</p>
    </div>
  );
}

// 메타데이터
export async function generateMetadata({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'HomePage' });

  return {
    title: t('title'),
    description: t('description'),
  };
}
```

### 클라이언트 컴포넌트

```tsx
// components/login-form.tsx
'use client';

import { useTranslations } from 'next-intl';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export function LoginForm() {
  const t = useTranslations('Auth');
  const tValidation = useTranslations('Validation');

  return (
    <form>
      <Input
        type="email"
        placeholder={t('email')}
      />
      <Input
        type="password"
        placeholder={t('password')}
      />
      <Button type="submit">{t('login')}</Button>
    </form>
  );
}
```

### 변수 사용

```tsx
// 번역 파일
// "greeting": "안녕하세요, {name}님!"
// "itemCount": "{count, plural, =0 {항목 없음} one {# 항목} other {# 항목}}"

const t = useTranslations();

t('greeting', { name: '홍길동' });
// → "안녕하세요, 홍길동님!"

t('itemCount', { count: 5 });
// → "5 항목"
```

### 네비게이션

```tsx
// components/nav-link.tsx
'use client';

import { Link, usePathname } from '@/i18n/navigation';

export function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  const pathname = usePathname();
  const isActive = pathname === href;

  return (
    <Link href={href} className={isActive ? 'font-bold' : ''}>
      {children}
    </Link>
  );
}
```

---

## 언어 전환기

```tsx
// components/locale-switcher.tsx
'use client';

import { useLocale } from 'next-intl';
import { usePathname, useRouter } from '@/i18n/navigation';
import { routing } from '@/i18n/routing';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

const localeNames: Record<string, string> = {
  ko: '한국어',
  en: 'English',
};

export function LocaleSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const handleChange = (newLocale: string) => {
    router.replace(pathname, { locale: newLocale });
  };

  return (
    <Select value={locale} onValueChange={handleChange}>
      <SelectTrigger className="w-[120px]">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {routing.locales.map((loc) => (
          <SelectItem key={loc} value={loc}>
            {localeNames[loc]}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
```

---

## TypeScript 타입 안전성

```typescript
// global.d.ts
import ko from './messages/ko.json';

type Messages = typeof ko;

declare global {
  interface IntlMessages extends Messages {}
}
```

이렇게 하면 `t('NonExistent.key')`처럼 존재하지 않는 키 사용 시 타입 에러가 발생합니다.

---

## 베스트 프랙티스

1. **네임스페이스 활용** - 페이지/기능별로 번역 키 분리
2. **Static Rendering** - `setRequestLocale()` 호출로 성능 최적화
3. **타입 안전성** - `IntlMessages` 타입 정의
4. **일관된 키 네이밍** - PascalCase 네임스페이스, camelCase 키

---

## 테스트 예제

### 번역 키 테스트

```typescript
// tests/i18n/messages.test.ts
import { describe, it, expect } from 'vitest';
import ko from '@/messages/ko.json';
import en from '@/messages/en.json';

describe('Translation Messages', () => {
  it('has matching keys between locales', () => {
    const koKeys = getNestedKeys(ko);
    const enKeys = getNestedKeys(en);

    // 모든 한국어 키가 영어에도 있는지 확인
    koKeys.forEach((key) => {
      expect(enKeys, `Missing English key: ${key}`).toContain(key);
    });

    // 모든 영어 키가 한국어에도 있는지 확인
    enKeys.forEach((key) => {
      expect(koKeys, `Missing Korean key: ${key}`).toContain(key);
    });
  });

  it('has no empty values', () => {
    const checkEmpty = (obj: Record<string, any>, path = ''): void => {
      Object.entries(obj).forEach(([key, value]) => {
        const fullPath = path ? `${path}.${key}` : key;
        if (typeof value === 'string') {
          expect(value.trim(), `Empty value at ${fullPath}`).not.toBe('');
        } else if (typeof value === 'object') {
          checkEmpty(value, fullPath);
        }
      });
    };

    checkEmpty(ko);
    checkEmpty(en);
  });

  it('has valid ICU message format', () => {
    const checkFormat = (obj: Record<string, any>): void => {
      Object.values(obj).forEach((value) => {
        if (typeof value === 'string') {
          // 중괄호 짝이 맞는지 확인
          const open = (value.match(/{/g) || []).length;
          const close = (value.match(/}/g) || []).length;
          expect(open, `Unbalanced braces: ${value}`).toBe(close);
        } else if (typeof value === 'object') {
          checkFormat(value);
        }
      });
    };

    checkFormat(ko);
    checkFormat(en);
  });
});

function getNestedKeys(obj: Record<string, any>, prefix = ''): string[] {
  return Object.entries(obj).flatMap(([key, value]) => {
    const path = prefix ? `${prefix}.${key}` : key;
    if (typeof value === 'object' && value !== null) {
      return getNestedKeys(value, path);
    }
    return [path];
  });
}
```

### 컴포넌트 렌더링 테스트

```typescript
// components/__tests__/locale-switcher.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { LocaleSwitcher } from '../locale-switcher';
import { NextIntlClientProvider } from 'next-intl';

// next-intl 모킹
vi.mock('next-intl', async () => {
  const actual = await vi.importActual('next-intl');
  return {
    ...actual,
    useLocale: () => 'ko',
  };
});

vi.mock('@/i18n/navigation', () => ({
  useRouter: () => ({ replace: vi.fn() }),
  usePathname: () => '/',
}));

describe('LocaleSwitcher', () => {
  it('renders current locale', () => {
    render(
      <NextIntlClientProvider locale="ko" messages={{}}>
        <LocaleSwitcher />
      </NextIntlClientProvider>
    );

    expect(screen.getByRole('combobox')).toHaveTextContent('한국어');
  });

  it('shows all available locales', async () => {
    render(
      <NextIntlClientProvider locale="ko" messages={{}}>
        <LocaleSwitcher />
      </NextIntlClientProvider>
    );

    fireEvent.click(screen.getByRole('combobox'));

    expect(await screen.findByText('English')).toBeInTheDocument();
    expect(screen.getByText('한국어')).toBeInTheDocument();
  });
});
```

### E2E 테스트

```typescript
// tests/e2e/i18n.spec.ts (Playwright)
import { test, expect } from '@playwright/test';

test.describe('Internationalization', () => {
  test('default locale is Korean', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL('/');  // /ko 없이
    await expect(page.locator('html')).toHaveAttribute('lang', 'ko');
  });

  test('English locale works', async ({ page }) => {
    await page.goto('/en');
    await expect(page.locator('html')).toHaveAttribute('lang', 'en');
  });

  test('locale switcher changes language', async ({ page }) => {
    await page.goto('/');

    await page.getByRole('combobox').click();
    await page.getByRole('option', { name: 'English' }).click();

    await expect(page).toHaveURL('/en');
    await expect(page.locator('html')).toHaveAttribute('lang', 'en');
  });

  test('preserves locale on navigation', async ({ page }) => {
    await page.goto('/en');
    await page.getByRole('link', { name: 'Dashboard' }).click();

    await expect(page).toHaveURL('/en/dashboard');
  });
});
```

---

## 안티패턴 (❌ Bad → ✅ Good)

### 1. 하드코딩된 문자열

```tsx
// ❌ Bad: 직접 문자열 사용
export function Header() {
  return <h1>환영합니다</h1>;
}

// ✅ Good: 번역 키 사용
import { useTranslations } from 'next-intl';

export function Header() {
  const t = useTranslations('Common');
  return <h1>{t('welcome')}</h1>;
}
```

### 2. setRequestLocale 누락

```tsx
// ❌ Bad: Static Rendering 불가능
export default async function Page({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations('Page');
  // setRequestLocale 없이 사용
  return <div>{t('title')}</div>;
}

// ✅ Good: Static Rendering 활성화
export default async function Page({ params }: Props) {
  const { locale } = await params;
  setRequestLocale(locale);  // 반드시 호출

  const t = await getTranslations('Page');
  return <div>{t('title')}</div>;
}
```

### 3. 중복 번역 키

```json
// ❌ Bad: 같은 문구 중복
{
  "HomePage": { "save": "저장" },
  "ProfilePage": { "save": "저장" },
  "SettingsPage": { "save": "저장" }
}

// ✅ Good: 공통 네임스페이스 활용
{
  "Common": { "save": "저장" },
  "HomePage": { /* 페이지 특화 키 */ },
  "ProfilePage": { /* 페이지 특화 키 */ }
}
```

### 4. 동적 키 사용

```tsx
// ❌ Bad: 타입 안전하지 않음
const t = useTranslations();
const key = `Status.${status}`;
return <span>{t(key)}</span>;  // 타입 체크 안 됨

// ✅ Good: 명시적 매핑
const t = useTranslations('Status');
const statusMessages = {
  pending: t('pending'),
  approved: t('approved'),
  rejected: t('rejected'),
} as const;
return <span>{statusMessages[status]}</span>;
```

### 5. 날짜/숫자 직접 포맷

```tsx
// ❌ Bad: 로케일 무시
<span>{new Date().toLocaleDateString()}</span>
<span>{price.toFixed(2)}원</span>

// ✅ Good: next-intl 포맷터 사용
import { useFormatter } from 'next-intl';

function Price({ value }: { value: number }) {
  const format = useFormatter();
  return <span>{format.number(value, { style: 'currency', currency: 'KRW' })}</span>;
}

function Date({ value }: { value: Date }) {
  const format = useFormatter();
  return <span>{format.dateTime(value, { dateStyle: 'long' })}</span>;
}
```

---

## 에러 처리

### 누락된 번역 키 처리

```typescript
// i18n/request.ts
export default getRequestConfig(async ({ requestLocale }) => {
  let locale = await requestLocale;

  if (!locale || !routing.locales.includes(locale as any)) {
    locale = routing.defaultLocale;
  }

  let messages;
  try {
    messages = (await import(`../messages/${locale}.json`)).default;
  } catch (error) {
    console.error(`[i18n] Failed to load messages for ${locale}:`, error);
    // Fallback to default locale
    messages = (await import(`../messages/${routing.defaultLocale}.json`)).default;
  }

  return {
    locale,
    messages,
    // 누락된 키 처리
    onError(error) {
      if (error.code === 'MISSING_MESSAGE') {
        console.warn(`[i18n] Missing translation: ${error.key}`);
        return;  // 기본 fallback 사용
      }
      throw error;
    },
    getMessageFallback({ key, namespace }) {
      // 개발환경: 키 표시, 프로덕션: 빈 문자열 또는 기본값
      if (process.env.NODE_ENV === 'development') {
        return `[Missing: ${namespace}.${key}]`;
      }
      return key.split('.').pop() ?? key;
    },
  };
});
```

### 잘못된 로케일 처리

```typescript
// app/[locale]/layout.tsx
export default async function LocaleLayout({ children, params }: Props) {
  const { locale } = await params;

  // 지원하지 않는 로케일 처리
  if (!routing.locales.includes(locale as any)) {
    notFound();
  }

  setRequestLocale(locale);
  const messages = await getMessages();

  return (
    <html lang={locale} suppressHydrationWarning>
      <body>
        <NextIntlClientProvider messages={messages}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
```

---

## 성능 고려사항

### 메시지 분할 로딩

```typescript
// 대규모 번역 파일 분할
// i18n/request.ts
export default getRequestConfig(async ({ requestLocale }) => {
  const locale = await requestLocale ?? routing.defaultLocale;

  // 공통 메시지만 초기 로드
  const common = (await import(`../messages/${locale}/common.json`)).default;

  return {
    locale,
    messages: common,
  };
});

// 페이지별 메시지 동적 로드
export default async function DashboardPage({ params }: Props) {
  const { locale } = await params;

  // 페이지 특화 메시지 로드
  const dashboardMessages = (
    await import(`@/messages/${locale}/dashboard.json`)
  ).default;

  return (
    <NextIntlClientProvider messages={dashboardMessages}>
      <DashboardContent />
    </NextIntlClientProvider>
  );
}
```

### Static Generation

```typescript
// 모든 로케일 정적 생성
export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

// 페이지에서 setRequestLocale 필수
export default async function Page({ params }: Props) {
  const { locale } = await params;
  setRequestLocale(locale);  // Static 렌더링 활성화
  // ...
}
```

---

## 보안 고려사항

### XSS 방지

```tsx
// ❌ Bad: dangerouslySetInnerHTML 사용
const t = useTranslations();
return <div dangerouslySetInnerHTML={{ __html: t('htmlContent') }} />;

// ✅ Good: Rich Text 사용
// messages/ko.json: "terms": "이용약관에 <link>동의</link>합니다"

const t = useTranslations();
return (
  <p>
    {t.rich('terms', {
      link: (chunks) => <Link href="/terms">{chunks}</Link>,
    })}
  </p>
);
```

### 사용자 입력 검증

```typescript
// 로케일 변경 시 검증
'use client';

export function LocaleSwitcher() {
  const router = useRouter();
  const pathname = usePathname();

  const handleChange = (newLocale: string) => {
    // 허용된 로케일만 처리
    if (!routing.locales.includes(newLocale as any)) {
      console.error('Invalid locale:', newLocale);
      return;
    }
    router.replace(pathname, { locale: newLocale });
  };

  return (/* ... */);
}
```

---

## References

- `_references/ARCHITECTURE-PATTERN.md` - Clean Architecture 가이드
- `_references/TEST-PATTERN.md` - 테스트 패턴
