---
name: payment
description: |
  Stripe를 사용하여 결제 기능을 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Payment Skill

Stripe를 사용하여 결제 기능을 구현합니다.

## Triggers

- "결제", "payment", "stripe", "구독", "subscription"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `type` | ✅ | one-time, subscription |
| `products` | ❌ | 상품 목록 |

---

## 설치

```bash
npm install stripe @stripe/stripe-js @stripe/react-stripe-js
```

---

## Stripe 설정

### 서버 클라이언트

```typescript
// lib/stripe/server.ts
import Stripe from 'stripe';

// API 버전은 환경변수로 관리하거나 최신 안정 버전 사용
// Stripe Dashboard에서 API 버전 확인: https://dashboard.stripe.com/developers
export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-12-18.acacia', // Stripe Dashboard 설정과 일치시킬 것
  typescript: true,
  httpClient: Stripe.createFetchHttpClient(), // Edge Runtime 호환
  timeout: 30000, // 30초 타임아웃
});
```

> ⚠️ **API 버전 관리**: Stripe API 버전은 Dashboard 설정과 일치해야 합니다.
> 버전 업그레이드 시 [Migration Guide](https://stripe.com/docs/upgrades) 참조

### 클라이언트

```typescript
// lib/stripe/client.ts
import { loadStripe } from '@stripe/stripe-js';

let stripePromise: Promise<Stripe | null>;

export const getStripe = () => {
  if (!stripePromise) {
    stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);
  }
  return stripePromise;
};
```

---

## 일회성 결제 (Checkout Session)

### Server Action

```typescript
// features/checkout/actions/create-checkout.action.ts
'use server';

import { authActionClient } from '@/lib/actions/safe-action';
import { stripe } from '@/lib/stripe/server';
import { z } from 'zod';

const checkoutSchema = z.object({
  items: z.array(
    z.object({
      priceId: z.string(),
      quantity: z.number().min(1),
    })
  ),
});

export const createCheckoutAction = authActionClient
  .schema(checkoutSchema)
  .action(async ({ parsedInput, ctx }) => {
    const session = await stripe.checkout.sessions.create({
      customer_email: ctx.user.email,
      mode: 'payment',
      line_items: parsedInput.items.map((item) => ({
        price: item.priceId,
        quantity: item.quantity,
      })),
      success_url: `${process.env.NEXT_PUBLIC_APP_URL}/checkout/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/checkout/cancel`,
      metadata: {
        userId: ctx.user.id,
      },
    });

    return { url: session.url };
  });
```

### Checkout 버튼

```tsx
// features/checkout/components/checkout-button.tsx
'use client';

import { useAction } from 'next-safe-action/hooks';
import { createCheckoutAction } from '../actions/create-checkout.action';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';

interface CheckoutButtonProps {
  items: Array<{ priceId: string; quantity: number }>;
}

export function CheckoutButton({ items }: CheckoutButtonProps) {
  const { execute, isPending } = useAction(createCheckoutAction, {
    onSuccess: ({ data }) => {
      if (data?.url) {
        window.location.href = data.url;
      }
    },
  });

  return (
    <Button onClick={() => execute({ items })} disabled={isPending}>
      {isPending ? (
        <>
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          처리 중...
        </>
      ) : (
        '결제하기'
      )}
    </Button>
  );
}
```

---

## 구독 결제

### 가격 정책 페이지

```tsx
// app/pricing/page.tsx
import { stripe } from '@/lib/stripe/server';
import { PricingCard } from '@/features/billing/components/pricing-card';

export default async function PricingPage() {
  const { data: prices } = await stripe.prices.list({
    active: true,
    expand: ['data.product'],
    type: 'recurring',
  });

  const plans = prices.map((price) => ({
    id: price.id,
    name: (price.product as Stripe.Product).name,
    description: (price.product as Stripe.Product).description,
    price: price.unit_amount! / 100,
    interval: price.recurring?.interval,
    features: (price.product as Stripe.Product).metadata.features?.split(',') || [],
  }));

  return (
    <div className="grid gap-8 md:grid-cols-3">
      {plans.map((plan) => (
        <PricingCard key={plan.id} plan={plan} />
      ))}
    </div>
  );
}
```

### 구독 생성

```typescript
// features/billing/actions/create-subscription.action.ts
'use server';

import { authActionClient } from '@/lib/actions/safe-action';
import { stripe } from '@/lib/stripe/server';
import { z } from 'zod';
import { db } from '@/lib/db';
import { users } from '@/lib/db/schema';
import { eq } from 'drizzle-orm';

const subscriptionSchema = z.object({
  priceId: z.string(),
});

export const createSubscriptionAction = authActionClient
  .schema(subscriptionSchema)
  .action(async ({ parsedInput, ctx }) => {
    // 기존 Stripe 고객 확인 또는 생성
    let customerId = ctx.user.stripeCustomerId;

    if (!customerId) {
      const customer = await stripe.customers.create({
        email: ctx.user.email,
        name: ctx.user.name,
        metadata: { userId: ctx.user.id },
      });
      customerId = customer.id;

      await db
        .update(users)
        .set({ stripeCustomerId: customerId })
        .where(eq(users.id, ctx.user.id));
    }

    // Checkout Session 생성
    const session = await stripe.checkout.sessions.create({
      customer: customerId,
      mode: 'subscription',
      line_items: [{ price: parsedInput.priceId, quantity: 1 }],
      success_url: `${process.env.NEXT_PUBLIC_APP_URL}/billing?success=true`,
      cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/pricing`,
    });

    return { url: session.url };
  });
```

---

## Idempotency Key 패턴

```typescript
// lib/stripe/idempotency.ts
import { v4 as uuidv4 } from 'uuid';
import { cookies } from 'next/headers';

const IDEMPOTENCY_COOKIE = 'stripe-idempotency';

// 결제 요청별 고유 Idempotency Key 생성
export async function getIdempotencyKey(operation: string): Promise<string> {
  const cookieStore = await cookies();
  const existingKey = cookieStore.get(`${IDEMPOTENCY_COOKIE}-${operation}`)?.value;

  if (existingKey) {
    return existingKey;
  }

  const newKey = `${operation}-${uuidv4()}`;
  cookieStore.set(`${IDEMPOTENCY_COOKIE}-${operation}`, newKey, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 60 * 60, // 1시간
  });

  return newKey;
}

// Idempotency Key 삭제 (결제 완료 후)
export async function clearIdempotencyKey(operation: string): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.delete(`${IDEMPOTENCY_COOKIE}-${operation}`);
}
```

### Idempotent Checkout 생성

```typescript
// features/checkout/actions/create-checkout.action.ts
'use server';

import { authActionClient } from '@/lib/actions/safe-action';
import { stripe } from '@/lib/stripe/server';
import { getIdempotencyKey, clearIdempotencyKey } from '@/lib/stripe/idempotency';
import { z } from 'zod';

const checkoutSchema = z.object({
  items: z.array(
    z.object({
      priceId: z.string(),
      quantity: z.number().min(1),
    })
  ),
});

export const createCheckoutAction = authActionClient
  .schema(checkoutSchema)
  .action(async ({ parsedInput, ctx }) => {
    // Idempotency Key로 중복 결제 방지
    const idempotencyKey = await getIdempotencyKey(`checkout-${ctx.user.id}`);

    try {
      const session = await stripe.checkout.sessions.create(
        {
          customer_email: ctx.user.email,
          mode: 'payment',
          line_items: parsedInput.items.map((item) => ({
            price: item.priceId,
            quantity: item.quantity,
          })),
          success_url: `${process.env.NEXT_PUBLIC_APP_URL}/checkout/success?session_id={CHECKOUT_SESSION_ID}`,
          cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/checkout/cancel`,
          metadata: {
            userId: ctx.user.id,
          },
        },
        {
          idempotencyKey, // Stripe Idempotency Key
        }
      );

      return { url: session.url };
    } catch (error) {
      // 이미 처리된 요청인 경우 기존 세션 반환
      if (error instanceof Error && error.message.includes('idempotent')) {
        // 기존 세션 조회 로직
        throw new Error('이미 처리 중인 결제입니다. 잠시 후 다시 시도해주세요.');
      }
      throw error;
    }
  });
```

---

## 환불 처리

```typescript
// features/billing/actions/refund.action.ts
'use server';

import { adminActionClient } from '@/lib/actions/safe-action';
import { stripe } from '@/lib/stripe/server';
import { db } from '@/lib/db';
import { orders } from '@/lib/db/schema';
import { eq } from 'drizzle-orm';
import { z } from 'zod';

const refundSchema = z.object({
  orderId: z.string(),
  amount: z.number().min(0).optional(), // 부분 환불 금액 (없으면 전액 환불)
  reason: z.enum(['duplicate', 'fraudulent', 'requested_by_customer']),
});

export const refundOrderAction = adminActionClient
  .schema(refundSchema)
  .action(async ({ parsedInput }) => {
    const { orderId, amount, reason } = parsedInput;

    // 주문 조회
    const order = await db.query.orders.findFirst({
      where: eq(orders.id, orderId),
    });

    if (!order) throw new Error('주문을 찾을 수 없습니다');
    if (!order.paymentIntentId) throw new Error('결제 정보가 없습니다');
    if (order.status === 'refunded') throw new Error('이미 환불된 주문입니다');

    // Stripe 환불 처리
    const refund = await stripe.refunds.create({
      payment_intent: order.paymentIntentId,
      amount: amount ? amount * 100 : undefined, // 부분 환불 (센트 단위)
      reason,
    });

    // DB 업데이트
    await db
      .update(orders)
      .set({
        status: amount && amount < order.total ? 'partially_refunded' : 'refunded',
        refundedAmount: amount ?? order.total,
        refundedAt: new Date(),
      })
      .where(eq(orders.id, orderId));

    return { success: true, refundId: refund.id };
  });
```

---

## Webhook 처리

```typescript
// app/api/webhooks/stripe/route.ts
import { headers } from 'next/headers';
import { NextResponse } from 'next/server';
import { stripe } from '@/lib/stripe/server';
import { db } from '@/lib/db';
import { subscriptions, orders } from '@/lib/db/schema';
import { eq } from 'drizzle-orm';
import type Stripe from 'stripe';

const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET!;

export async function POST(request: Request) {
  const body = await request.text();
  const headersList = await headers();
  const signature = headersList.get('stripe-signature')!;

  let event: Stripe.Event;

  try {
    event = stripe.webhooks.constructEvent(body, signature, webhookSecret);
  } catch (err) {
    // 더 구체적인 에러 타입 처리
    if (err instanceof Stripe.errors.StripeSignatureVerificationError) {
      console.error('Webhook signature verification failed:', err.message);
      return NextResponse.json({ error: 'Invalid signature' }, { status: 401 });
    }
    console.error('Webhook error:', err);
    return NextResponse.json({ error: 'Webhook error' }, { status: 400 });
  }

  try {
    switch (event.type) {
      case 'checkout.session.completed': {
        const session = event.data.object as Stripe.Checkout.Session;
        await handleCheckoutComplete(session);
        break;
      }

      case 'customer.subscription.created':
      case 'customer.subscription.updated': {
        const subscription = event.data.object as Stripe.Subscription;
        await handleSubscriptionChange(subscription);
        break;
      }

      case 'customer.subscription.deleted': {
        const subscription = event.data.object as Stripe.Subscription;
        await handleSubscriptionCanceled(subscription);
        break;
      }

      case 'invoice.payment_failed': {
        const invoice = event.data.object as Stripe.Invoice;
        await handlePaymentFailed(invoice);
        break;
      }
    }

    return NextResponse.json({ received: true });
  } catch (error) {
    console.error('Webhook handler failed:', error);
    return NextResponse.json({ error: 'Webhook handler failed' }, { status: 500 });
  }
}

async function handleCheckoutComplete(session: Stripe.Checkout.Session) {
  if (session.mode === 'subscription') {
    // 구독 정보는 subscription.created에서 처리
    return;
  }

  // 일회성 결제 처리
  const userId = session.metadata?.userId;
  if (userId) {
    // 주문 생성, 상품 전달 등
  }
}

async function handleSubscriptionChange(subscription: Stripe.Subscription) {
  const customerId = subscription.customer as string;
  const customer = await stripe.customers.retrieve(customerId);

  if (customer.deleted) return;

  const userId = customer.metadata.userId;

  await db
    .insert(subscriptions)
    .values({
      id: subscription.id,
      userId,
      status: subscription.status,
      priceId: subscription.items.data[0].price.id,
      currentPeriodStart: new Date(subscription.current_period_start * 1000),
      currentPeriodEnd: new Date(subscription.current_period_end * 1000),
      cancelAtPeriodEnd: subscription.cancel_at_period_end,
    })
    .onConflictDoUpdate({
      target: subscriptions.id,
      set: {
        status: subscription.status,
        priceId: subscription.items.data[0].price.id,
        currentPeriodEnd: new Date(subscription.current_period_end * 1000),
        cancelAtPeriodEnd: subscription.cancel_at_period_end,
      },
    });
}

async function handleSubscriptionCanceled(subscription: Stripe.Subscription) {
  await db
    .update(subscriptions)
    .set({ status: 'canceled' })
    .where(eq(subscriptions.id, subscription.id));
}

async function handlePaymentFailed(invoice: Stripe.Invoice) {
  // 결제 실패 알림 이메일 발송
  const customerId = invoice.customer as string;
  const customer = await stripe.customers.retrieve(customerId);

  if (!customer.deleted && customer.email) {
    // await emailService.sendPaymentFailed(customer.email, { ... });
  }
}
```

---

## Customer Portal (구독 관리)

```typescript
// features/billing/actions/create-portal.action.ts
'use server';

import { authActionClient } from '@/lib/actions/safe-action';
import { stripe } from '@/lib/stripe/server';

export const createPortalAction = authActionClient.action(async ({ ctx }) => {
  if (!ctx.user.stripeCustomerId) {
    throw new Error('No Stripe customer');
  }

  const session = await stripe.billingPortal.sessions.create({
    customer: ctx.user.stripeCustomerId,
    return_url: `${process.env.NEXT_PUBLIC_APP_URL}/billing`,
  });

  return { url: session.url };
});
```

```tsx
// features/billing/components/manage-subscription-button.tsx
'use client';

import { useAction } from 'next-safe-action/hooks';
import { createPortalAction } from '../actions/create-portal.action';
import { Button } from '@/components/ui/button';

export function ManageSubscriptionButton() {
  const { execute, isPending } = useAction(createPortalAction, {
    onSuccess: ({ data }) => {
      if (data?.url) {
        window.location.href = data.url;
      }
    },
  });

  return (
    <Button variant="outline" onClick={() => execute()} disabled={isPending}>
      구독 관리
    </Button>
  );
}
```

---

## 환경 변수

```env
# .env.local
STRIPE_SECRET_KEY=sk_test_xxxxx
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

---

## 테스트 예제

### Checkout Action 테스트

```typescript
// features/checkout/__tests__/create-checkout.test.ts
import { describe, it, expect, vi } from 'vitest';
import { createCheckoutAction } from '../actions/create-checkout.action';
import { stripe } from '@/lib/stripe/server';

vi.mock('@/lib/stripe/server', () => ({
  stripe: {
    checkout: {
      sessions: {
        create: vi.fn(),
      },
    },
  },
}));

describe('createCheckoutAction', () => {
  it('Checkout 세션을 생성한다', async () => {
    vi.mocked(stripe.checkout.sessions.create).mockResolvedValue({
      url: 'https://checkout.stripe.com/session_123',
    } as any);

    const result = await createCheckoutAction({
      items: [{ priceId: 'price_123', quantity: 1 }],
    });

    expect(result.url).toContain('checkout.stripe.com');
    expect(stripe.checkout.sessions.create).toHaveBeenCalledWith(
      expect.objectContaining({
        mode: 'payment',
        line_items: [{ price: 'price_123', quantity: 1 }],
      })
    );
  });
});
```

### Webhook 테스트

```typescript
// app/api/webhooks/stripe/__tests__/route.test.ts
import { describe, it, expect, vi } from 'vitest';
import { POST } from '../route';
import { stripe } from '@/lib/stripe/server';

vi.mock('@/lib/stripe/server');

describe('Stripe Webhook', () => {
  it('유효한 서명을 검증한다', async () => {
    vi.mocked(stripe.webhooks.constructEvent).mockReturnValue({
      type: 'checkout.session.completed',
      data: { object: { id: 'cs_123' } },
    } as any);

    const request = new Request('http://localhost/api/webhooks/stripe', {
      method: 'POST',
      body: JSON.stringify({}),
      headers: { 'stripe-signature': 'sig_123' },
    });

    const response = await POST(request);

    expect(response.status).toBe(200);
  });

  it('잘못된 서명은 401을 반환한다', async () => {
    vi.mocked(stripe.webhooks.constructEvent).mockImplementation(() => {
      throw new Error('Invalid signature');
    });

    const request = new Request('http://localhost/api/webhooks/stripe', {
      method: 'POST',
      body: '{}',
      headers: { 'stripe-signature': 'invalid' },
    });

    const response = await POST(request);

    expect(response.status).toBe(401);
  });
});
```

---

## 안티패턴

### 1. Secret Key 노출

```typescript
// ❌ Bad: 클라이언트에 노출
const stripe = new Stripe(process.env.NEXT_PUBLIC_STRIPE_SECRET_KEY!);

// ✅ Good: 서버에서만 사용
// lib/stripe/server.ts
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);
```

### 2. Webhook 검증 누락

```typescript
// ❌ Bad: 서명 검증 없이 처리
export async function POST(request: Request) {
  const event = await request.json();
  // 바로 처리 → 위조 요청 가능
}

// ✅ Good: 서명 검증
export async function POST(request: Request) {
  const body = await request.text();
  const headersList = await headers();
  const signature = headersList.get('stripe-signature')!;

  const event = stripe.webhooks.constructEvent(body, signature, webhookSecret);
}
```

### 3. 중복 결제 미방지

```typescript
// ❌ Bad: Idempotency Key 없이 호출
await stripe.checkout.sessions.create({ ... });

// ✅ Good: Idempotency Key 사용
await stripe.checkout.sessions.create(
  { ... },
  { idempotencyKey: `checkout-${userId}-${Date.now()}` }
);
```

### 4. 금액 클라이언트 신뢰

```typescript
// ❌ Bad: 클라이언트에서 받은 금액 사용
const session = await stripe.checkout.sessions.create({
  line_items: [{ price_data: { unit_amount: clientAmount } }],
});

// ✅ Good: 서버에서 가격 조회
const price = await stripe.prices.retrieve(priceId);
const session = await stripe.checkout.sessions.create({
  line_items: [{ price: priceId }], // Stripe가 관리하는 가격 사용
});
```

---

## 에러 처리

### Payment 에러 타입

```typescript
// lib/stripe/errors.ts
import Stripe from 'stripe';

export class PaymentError extends Error {
  constructor(
    message: string,
    public code: 'CARD_DECLINED' | 'INSUFFICIENT_FUNDS' | 'EXPIRED_CARD' | 'PROCESSING_ERROR',
    public declineCode?: string
  ) {
    super(message);
    this.name = 'PaymentError';
  }
}

export function handleStripeError(error: unknown): PaymentError {
  if (error instanceof Stripe.errors.StripeCardError) {
    return new PaymentError(
      error.message,
      'CARD_DECLINED',
      error.decline_code
    );
  }

  if (error instanceof Stripe.errors.StripeInvalidRequestError) {
    return new PaymentError(error.message, 'PROCESSING_ERROR');
  }

  return new PaymentError('결제 처리 중 오류가 발생했습니다', 'PROCESSING_ERROR');
}
```

### 사용자 친화적 에러 메시지

```typescript
// lib/stripe/error-messages.ts
const declineCodeMessages: Record<string, string> = {
  insufficient_funds: '잔액이 부족합니다',
  lost_card: '분실 신고된 카드입니다',
  stolen_card: '도난 신고된 카드입니다',
  expired_card: '만료된 카드입니다',
  incorrect_cvc: 'CVC가 올바르지 않습니다',
  card_declined: '카드가 거부되었습니다',
};

export function getErrorMessage(declineCode?: string): string {
  return declineCode
    ? declineCodeMessages[declineCode] || '카드가 거부되었습니다'
    : '결제 처리 중 오류가 발생했습니다';
}
```

---

## 성능 고려사항

### 1. Webhook 비동기 처리

```typescript
// 복잡한 작업은 큐로 분리
export async function POST(request: Request) {
  // ... 검증

  // 빠르게 200 응답
  switch (event.type) {
    case 'checkout.session.completed':
      // 큐에 추가하고 즉시 응답
      await orderQueue.add('process-order', event.data.object);
      break;
  }

  return NextResponse.json({ received: true });
}
```

### 2. 가격 정보 캐싱

```typescript
// lib/stripe/cache.ts
import { unstable_cache } from 'next/cache';

export const getCachedPrices = unstable_cache(
  async () => {
    const { data: prices } = await stripe.prices.list({
      active: true,
      expand: ['data.product'],
    });
    return prices;
  },
  ['stripe-prices'],
  { revalidate: 3600 } // 1시간 캐싱
);
```

### 3. Customer Portal 재사용

```typescript
// 기존 포털 세션이 있으면 재사용
const existingSession = await stripe.billingPortal.sessions.list({
  customer: customerId,
  limit: 1,
});

if (existingSession.data[0]?.url) {
  return { url: existingSession.data[0].url };
}
```

---

## 보안 고려사항

### 1. Webhook 엔드포인트 보호

```typescript
// proxy.ts
export function proxy(request: NextRequest) {
  if (request.nextUrl.pathname.startsWith('/api/webhooks/stripe')) {
    // Stripe IP만 허용 (선택적)
    const stripeIps = ['3.18.12.63', ...]; // Stripe 공식 IP 목록

    if (!stripeIps.includes(request.ip || '')) {
      return new NextResponse('Forbidden', { status: 403 });
    }
  }
}
```

### 2. 민감 데이터 로깅 방지

```typescript
// lib/stripe/logging.ts
export function logPaymentEvent(event: string, data: Record<string, unknown>) {
  // 민감 정보 제거
  const sanitized = { ...data };
  delete sanitized.card_number;
  delete sanitized.cvc;

  console.log(`[Payment] ${event}:`, sanitized);
}
```

### 3. 금액 검증

```typescript
// Server Action에서 금액 검증
export const processPaymentAction = authActionClient
  .schema(paymentSchema)
  .action(async ({ parsedInput }) => {
    // DB에서 실제 가격 조회
    const product = await db.query.products.findFirst({
      where: eq(products.id, parsedInput.productId),
    });

    if (!product || product.price !== parsedInput.amount) {
      throw new Error('Invalid amount');
    }

    // Stripe 결제 진행
  });
```

### 4. 테스트 모드 분리

```typescript
// lib/stripe/server.ts
const isTestMode = process.env.STRIPE_SECRET_KEY?.startsWith('sk_test_');

if (process.env.NODE_ENV === 'production' && isTestMode) {
  console.warn('⚠️ Stripe is running in TEST mode in production!');
}
```

---

## References

- `_references/SERVER-ACTION-PATTERN.md`
- `_references/DATABASE-PATTERN.md`
- `_references/TEST-PATTERN.md`
