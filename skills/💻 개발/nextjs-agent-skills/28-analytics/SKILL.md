---
name: analytics
description: |
  Google Analytics 4와 Vercel Analytics를 설정합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Analytics Skill

Google Analytics 4와 Vercel Analytics를 설정합니다.

## Triggers

- "애널리틱스", "analytics", "ga4", "vercel analytics", "추적"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `provider` | ✅ | ga4, vercel, both |
| `events` | ❌ | 커스텀 이벤트 목록 |

---

## Vercel Analytics (권장)

### 설치

```bash
npm install @vercel/analytics @vercel/speed-insights
```

### 설정

```tsx
// app/layout.tsx
import { Analytics } from '@vercel/analytics/react';
import { SpeedInsights } from '@vercel/speed-insights/next';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>
        {children}
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}
```

### 커스텀 이벤트

```typescript
// lib/analytics.ts
import { track } from '@vercel/analytics';

export const analytics = {
  // 페이지뷰는 자동 추적됨

  // 커스텀 이벤트
  trackSignUp: (method: 'email' | 'google' | 'github') => {
    track('sign_up', { method });
  },

  trackPurchase: (data: { productId: string; price: number; currency: string }) => {
    track('purchase', data);
  },

  trackSearch: (query: string, resultsCount: number) => {
    track('search', { query, results_count: resultsCount });
  },

  trackButtonClick: (buttonName: string, location: string) => {
    track('button_click', { button_name: buttonName, location });
  },

  trackError: (errorType: string, message: string) => {
    track('error', { error_type: errorType, message });
  },
};
```

### 사용 예시

```tsx
'use client';

import { analytics } from '@/lib/analytics';

export function SignUpButton() {
  const handleClick = () => {
    analytics.trackButtonClick('sign_up', 'hero_section');
    // ... 회원가입 로직
  };

  return <button onClick={handleClick}>회원가입</button>;
}
```

---

## Google Analytics 4

### 설치

```bash
npm install @next/third-parties
```

### 설정

```tsx
// app/layout.tsx
import { GoogleAnalytics } from '@next/third-parties/google';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>
        {children}
        <GoogleAnalytics gaId="G-XXXXXXXXXX" />
      </body>
    </html>
  );
}
```

### 이벤트 추적

```typescript
// lib/gtag.ts
export const GA_TRACKING_ID = process.env.NEXT_PUBLIC_GA_ID!;

// 타입 정의
type GtagCommand = 'config' | 'event' | 'consent' | 'set' | 'js';

interface GtagEventParams {
  event_category?: string;
  event_label?: string;
  value?: number;
  page_path?: string;
  page_title?: string;
  [key: string]: unknown;
}

interface ConsentParams {
  ad_storage?: 'granted' | 'denied';
  analytics_storage?: 'granted' | 'denied';
  functionality_storage?: 'granted' | 'denied';
  personalization_storage?: 'granted' | 'denied';
  security_storage?: 'granted' | 'denied';
  wait_for_update?: number;
}

declare global {
  interface Window {
    gtag: {
      (command: 'js', date: Date): void;
      (command: 'config', targetId: string, params?: GtagEventParams): void;
      (command: 'event', eventName: string, params?: GtagEventParams): void;
      (command: 'consent', consentArg: 'default' | 'update', params: ConsentParams): void;
      (command: 'set', params: Record<string, unknown>): void;
    };
    dataLayer: unknown[];
  }
}

// 페이지뷰
export const pageview = (url: string, title?: string) => {
  if (typeof window.gtag === 'undefined') return;

  window.gtag('config', GA_TRACKING_ID, {
    page_path: url,
    page_title: title,
  });
};

// 이벤트
export const event = (action: string, params: GtagEventParams = {}) => {
  if (typeof window.gtag === 'undefined') return;

  window.gtag('event', action, params);
};

// Consent Mode 설정
export const setConsent = (params: ConsentParams) => {
  if (typeof window.gtag === 'undefined') return;

  window.gtag('consent', 'update', params);
};
```

### Consent Mode 초기화

```tsx
// components/analytics/consent-banner.tsx
'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { setConsent } from '@/lib/gtag';

const CONSENT_KEY = 'cookie-consent';

type ConsentStatus = 'pending' | 'accepted' | 'declined';

export function ConsentBanner() {
  const [status, setStatus] = useState<ConsentStatus>('pending');

  useEffect(() => {
    const saved = localStorage.getItem(CONSENT_KEY);
    if (saved === 'accepted' || saved === 'declined') {
      setStatus(saved);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem(CONSENT_KEY, 'accepted');
    setStatus('accepted');
    setConsent({
      analytics_storage: 'granted',
      ad_storage: 'granted',
    });
  };

  const handleDecline = () => {
    localStorage.setItem(CONSENT_KEY, 'declined');
    setStatus('declined');
    setConsent({
      analytics_storage: 'denied',
      ad_storage: 'denied',
    });
  };

  if (status !== 'pending') return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-background border-t p-4">
      <div className="container flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-muted-foreground">
          이 웹사이트는 사용자 경험 향상을 위해 쿠키를 사용합니다.
        </p>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleDecline}>
            거부
          </Button>
          <Button size="sm" onClick={handleAccept}>
            동의
          </Button>
        </div>
      </div>
    </div>
  );
}
```

### GA4 스크립트 (Consent Mode 지원)

```tsx
// components/analytics/google-analytics.tsx
import Script from 'next/script';
import { GA_TRACKING_ID } from '@/lib/gtag';

export function GoogleAnalytics() {
  if (!GA_TRACKING_ID) return null;

  return (
    <>
      <Script
        strategy="afterInteractive"
        src={`https://www.googletagmanager.com/gtag/js?id=${GA_TRACKING_ID}`}
      />
      <Script
        id="gtag-init"
        strategy="afterInteractive"
        dangerouslySetInnerHTML={{
          __html: `
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}

            // Consent Mode 기본값 (EU 사용자 대응)
            gtag('consent', 'default', {
              'analytics_storage': 'denied',
              'ad_storage': 'denied',
              'wait_for_update': 500
            });

            gtag('js', new Date());
            gtag('config', '${GA_TRACKING_ID}', {
              page_path: window.location.pathname,
            });
          `,
        }}
      />
    </>
  );
}
```

### GA4 이벤트 헬퍼

```typescript
// lib/ga-events.ts
import { event } from './gtag';

export const gaEvents = {
  // 전자상거래
  viewItem: (item: { id: string; name: string; price: number }) => {
    event('view_item', {
      currency: 'KRW',
      value: item.price,
      items: [{ item_id: item.id, item_name: item.name, price: item.price }],
    });
  },

  addToCart: (item: { id: string; name: string; price: number; quantity: number }) => {
    event('add_to_cart', {
      currency: 'KRW',
      value: item.price * item.quantity,
      items: [{ item_id: item.id, item_name: item.name, price: item.price, quantity: item.quantity }],
    });
  },

  beginCheckout: (items: Array<{ id: string; name: string; price: number; quantity: number }>) => {
    const value = items.reduce((sum, item) => sum + item.price * item.quantity, 0);
    event('begin_checkout', {
      currency: 'KRW',
      value,
      items: items.map((item) => ({
        item_id: item.id,
        item_name: item.name,
        price: item.price,
        quantity: item.quantity,
      })),
    });
  },

  purchase: (transactionId: string, value: number, items: Array<{ id: string; name: string; price: number; quantity: number }>) => {
    event('purchase', {
      transaction_id: transactionId,
      currency: 'KRW',
      value,
      items: items.map((item) => ({
        item_id: item.id,
        item_name: item.name,
        price: item.price,
        quantity: item.quantity,
      })),
    });
  },

  // 사용자 행동
  signUp: (method: string) => {
    event('sign_up', { method });
  },

  login: (method: string) => {
    event('login', { method });
  },

  search: (searchTerm: string) => {
    event('search', { search_term: searchTerm });
  },

  share: (contentType: string, itemId: string) => {
    event('share', { content_type: contentType, item_id: itemId });
  },
};
```

---

## 라우트 변경 추적

```tsx
// components/analytics-provider.tsx
'use client';

import { usePathname, useSearchParams } from 'next/navigation';
import { useEffect, Suspense } from 'react';
import { pageview } from '@/lib/gtag';

function AnalyticsTrackerInner() {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    const url = pathname + (searchParams.toString() ? `?${searchParams.toString()}` : '');
    pageview(url);
  }, [pathname, searchParams]);

  return null;
}

export function AnalyticsTracker() {
  return (
    <Suspense fallback={null}>
      <AnalyticsTrackerInner />
    </Suspense>
  );
}
```

---

## 서버 사이드 이벤트 (Measurement Protocol)

```typescript
// lib/server-analytics.ts
const GA_MEASUREMENT_ID = process.env.GA_MEASUREMENT_ID;
const GA_API_SECRET = process.env.GA_API_SECRET;

export async function trackServerEvent(
  clientId: string,
  eventName: string,
  params: Record<string, unknown>
) {
  if (!GA_MEASUREMENT_ID || !GA_API_SECRET) return;

  await fetch(
    `https://www.google-analytics.com/mp/collect?measurement_id=${GA_MEASUREMENT_ID}&api_secret=${GA_API_SECRET}`,
    {
      method: 'POST',
      body: JSON.stringify({
        client_id: clientId,
        events: [{ name: eventName, params }],
      }),
    }
  );
}

// Server Action에서 사용
export async function purchaseAction(data: PurchaseData) {
  // ... 결제 처리

  await trackServerEvent(data.userId, 'purchase', {
    transaction_id: data.transactionId,
    value: data.total,
    currency: 'KRW',
  });
}
```

---

## A/B 테스트 (Vercel Edge Config)

```typescript
// proxy.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { get } from '@vercel/edge-config';

export async function proxy(request: NextRequest) {
  const variant = await get<'control' | 'variant'>('homepage_experiment');

  const response = NextResponse.next();
  response.cookies.set('ab-variant', variant || 'control');

  return response;
}
```

```tsx
// app/page.tsx
import { cookies } from 'next/headers';

export default async function HomePage() {
  const cookieStore = await cookies();
  const variant = cookieStore.get('ab-variant')?.value || 'control';

  if (variant === 'variant') {
    return <NewHomePage />;
  }

  return <OriginalHomePage />;
}
```

---

## 환경 변수

```env
# .env.local
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
GA_MEASUREMENT_ID=G-XXXXXXXXXX
GA_API_SECRET=xxxxxxxxxxxxx
```

---

## 테스트 예제

### Analytics 훅 테스트

```typescript
// lib/__tests__/analytics.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { analytics } from '../analytics';

describe('analytics', () => {
  beforeEach(() => {
    vi.stubGlobal('window', {
      gtag: vi.fn(),
    });
  });

  it('trackSignUp이 올바른 이벤트를 전송한다', () => {
    analytics.trackSignUp('email');

    expect(window.gtag).toHaveBeenCalledWith(
      'event',
      'sign_up',
      expect.objectContaining({ method: 'email' })
    );
  });

  it('trackPurchase가 구매 데이터를 포함한다', () => {
    analytics.trackPurchase({
      productId: 'prod_123',
      price: 10000,
      currency: 'KRW',
    });

    expect(window.gtag).toHaveBeenCalledWith(
      'event',
      'purchase',
      expect.objectContaining({
        productId: 'prod_123',
        price: 10000,
      })
    );
  });
});
```

### Consent Banner 테스트

```tsx
// components/__tests__/consent-banner.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ConsentBanner } from '../consent-banner';

describe('ConsentBanner', () => {
  it('동의하면 localStorage에 저장한다', async () => {
    const user = userEvent.setup();
    render(<ConsentBanner />);

    await user.click(screen.getByText('동의'));

    expect(localStorage.getItem('cookie-consent')).toBe('accepted');
  });

  it('거부하면 배너가 사라진다', async () => {
    const user = userEvent.setup();
    const { container } = render(<ConsentBanner />);

    await user.click(screen.getByText('거부'));

    expect(container).toBeEmptyDOMElement();
  });
});
```

---

## 안티패턴

### 1. 개인정보 무단 수집

```typescript
// ❌ Bad: 동의 없이 추적
window.gtag('config', GA_ID);

// ✅ Good: Consent Mode 적용
window.gtag('consent', 'default', {
  analytics_storage: 'denied',
  ad_storage: 'denied',
});
```

### 2. 과도한 이벤트 추적

```typescript
// ❌ Bad: 모든 클릭 추적
document.addEventListener('click', (e) => {
  analytics.track('click', { target: e.target });
});

// ✅ Good: 의미있는 이벤트만 추적
const handlePurchase = () => {
  analytics.trackPurchase(purchaseData);
};
```

### 3. 민감 정보 포함

```typescript
// ❌ Bad: 민감 정보 이벤트에 포함
analytics.track('user_profile', { password: '***', ssn: '***' });

// ✅ Good: 비식별 정보만 전송
analytics.track('user_profile', { userType: 'premium' });
```

### 4. 서버 이벤트 누락

```typescript
// ❌ Bad: 클라이언트만 의존
// 결제 성공 시 클라이언트에서만 추적 → 누락 가능

// ✅ Good: 서버 사이드 이벤트 (Measurement Protocol)
await trackServerEvent(userId, 'purchase', { value: 10000 });
```

---

## 에러 처리

### Analytics 에러 처리

```typescript
// lib/analytics-safe.ts
export function safeTrack(eventName: string, params: Record<string, unknown>) {
  try {
    if (typeof window === 'undefined' || !window.gtag) {
      return;
    }

    window.gtag('event', eventName, params);
  } catch (error) {
    // Analytics 실패가 앱 기능에 영향 주지 않도록
    console.warn('Analytics tracking failed:', error);
  }
}
```

### Consent 상태 복구

```typescript
// lib/consent.ts
export function initializeConsent() {
  try {
    const saved = localStorage.getItem('cookie-consent');

    if (saved === 'accepted') {
      window.gtag?.('consent', 'update', {
        analytics_storage: 'granted',
        ad_storage: 'granted',
      });
    }
  } catch {
    // localStorage 접근 실패 시 기본값 유지
  }
}
```

---

## 성능 고려사항

### 1. 지연 로딩

```tsx
// afterInteractive 전략으로 페이지 로드 방해 최소화
<Script
  strategy="afterInteractive"
  src="https://www.googletagmanager.com/gtag/js"
/>
```

### 2. 이벤트 배치 처리

```typescript
// lib/analytics-batch.ts
const eventQueue: Array<{ name: string; params: unknown }> = [];
let flushTimeout: ReturnType<typeof setTimeout>;

export function queueEvent(name: string, params: unknown) {
  eventQueue.push({ name, params });

  clearTimeout(flushTimeout);
  flushTimeout = setTimeout(flushEvents, 1000);
}

function flushEvents() {
  eventQueue.forEach(({ name, params }) => {
    window.gtag?.('event', name, params);
  });
  eventQueue.length = 0;
}
```

### 3. 조건부 로딩

```tsx
// 프로덕션에서만 Analytics 로드
{process.env.NODE_ENV === 'production' && <GoogleAnalytics gaId={GA_ID} />}
```

---

## 보안 고려사항

### 1. PII 필터링

```typescript
// lib/analytics-filter.ts
const PII_PATTERNS = [
  /\b[\w.-]+@[\w.-]+\.\w{2,}\b/, // 이메일
  /\b\d{3}-\d{4}-\d{4}\b/, // 전화번호
  /\b\d{6}-\d{7}\b/, // 주민번호
];

export function sanitizeEventData(data: Record<string, unknown>) {
  const sanitized = { ...data };

  Object.entries(sanitized).forEach(([key, value]) => {
    if (typeof value === 'string') {
      PII_PATTERNS.forEach((pattern) => {
        if (pattern.test(value)) {
          sanitized[key] = '[REDACTED]';
        }
      });
    }
  });

  return sanitized;
}
```

### 2. 서버 사이드 검증

```typescript
// Server Action에서 Analytics 호출 시 검증
export async function trackServerEvent(userId: string, eventName: string, params: Record<string, unknown>) {
  // 허용된 이벤트만 전송
  const allowedEvents = ['purchase', 'subscription_created', 'subscription_canceled'];

  if (!allowedEvents.includes(eventName)) {
    console.warn(`Blocked unauthorized event: ${eventName}`);
    return;
  }

  await fetch(GA_MEASUREMENT_URL, { /* ... */ });
}
```

### 3. CSP 설정

```typescript
// proxy.ts - Analytics 도메인 허용
const csp = `
  script-src 'self' https://www.googletagmanager.com https://www.google-analytics.com;
  connect-src 'self' https://www.google-analytics.com https://analytics.google.com;
`;
```

---

## References

- `_references/ARCHITECTURE-PATTERN.md`
- `_references/TEST-PATTERN.md`

