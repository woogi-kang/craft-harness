---
name: email
description: |
  Resend와 React Email을 사용하여 이메일을 발송합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Email Skill

Resend와 React Email을 사용하여 이메일을 발송합니다.

## Triggers

- "이메일", "email", "resend", "react email", "메일 발송"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `provider` | ✅ | resend, nodemailer |
| `templates` | ❌ | 이메일 템플릿 목록 |

---

## 설치

```bash
# Resend SDK (2024.12 기준 권장 버전)
npm install resend@^4.0.1

# React Email 컴포넌트
npm install @react-email/components@^0.0.28

# 개발 도구 (이메일 미리보기)
npm install -D react-email@^3.0.4
```

---

## Resend 설정

```typescript
// lib/email/resend.ts
import { Resend } from 'resend';

export const resend = new Resend(process.env.RESEND_API_KEY);

export const emailConfig = {
  from: 'My App <noreply@myapp.com>',
  replyTo: 'support@myapp.com',
};
```

---

## React Email 템플릿

### 기본 레이아웃

```tsx
// emails/components/layout.tsx
import {
  Body,
  Container,
  Head,
  Html,
  Img,
  Preview,
  Section,
  Tailwind,
} from '@react-email/components';

interface EmailLayoutProps {
  preview: string;
  children: React.ReactNode;
}

export function EmailLayout({ preview, children }: EmailLayoutProps) {
  return (
    <Html>
      <Head />
      <Preview>{preview}</Preview>
      <Tailwind>
        <Body className="bg-gray-100 font-sans">
          <Container className="mx-auto max-w-[600px] bg-white p-8">
            <Section className="mb-8">
              <Img
                src="https://myapp.com/logo.png"
                width={120}
                height={40}
                alt="My App"
              />
            </Section>
            {children}
            <Section className="mt-8 border-t border-gray-200 pt-8 text-center text-sm text-gray-500">
              <p>© 2025 My App. All rights reserved.</p>
              <p>서울특별시 강남구 테헤란로 123</p>
            </Section>
          </Container>
        </Body>
      </Tailwind>
    </Html>
  );
}
```

### 환영 이메일

```tsx
// emails/welcome.tsx
import {
  Button,
  Heading,
  Hr,
  Link,
  Section,
  Text,
} from '@react-email/components';
import { EmailLayout } from './components/layout';

interface WelcomeEmailProps {
  username: string;
  loginUrl: string;
}

export function WelcomeEmail({ username, loginUrl }: WelcomeEmailProps) {
  return (
    <EmailLayout preview={`${username}님, 환영합니다!`}>
      <Heading className="text-2xl font-bold text-gray-900">
        환영합니다, {username}님!
      </Heading>

      <Text className="text-gray-600">
        My App에 가입해 주셔서 감사합니다. 이제 모든 기능을 사용하실 수 있습니다.
      </Text>

      <Section className="my-8 text-center">
        <Button
          href={loginUrl}
          className="rounded-md bg-blue-600 px-6 py-3 text-white"
        >
          시작하기
        </Button>
      </Section>

      <Hr className="border-gray-200" />

      <Text className="text-sm text-gray-500">
        도움이 필요하시면{' '}
        <Link href="mailto:support@myapp.com" className="text-blue-600">
          support@myapp.com
        </Link>
        으로 문의해 주세요.
      </Text>
    </EmailLayout>
  );
}

export default WelcomeEmail;
```

### 비밀번호 재설정

```tsx
// emails/reset-password.tsx
import {
  Button,
  Heading,
  Section,
  Text,
} from '@react-email/components';
import { EmailLayout } from './components/layout';

interface ResetPasswordEmailProps {
  username: string;
  resetUrl: string;
  expiresIn: string;
}

export function ResetPasswordEmail({
  username,
  resetUrl,
  expiresIn,
}: ResetPasswordEmailProps) {
  return (
    <EmailLayout preview="비밀번호 재설정 요청">
      <Heading className="text-2xl font-bold text-gray-900">
        비밀번호 재설정
      </Heading>

      <Text className="text-gray-600">
        {username}님, 비밀번호 재설정 요청이 접수되었습니다.
        아래 버튼을 클릭하여 새 비밀번호를 설정해 주세요.
      </Text>

      <Section className="my-8 text-center">
        <Button
          href={resetUrl}
          className="rounded-md bg-blue-600 px-6 py-3 text-white"
        >
          비밀번호 재설정
        </Button>
      </Section>

      <Text className="text-sm text-gray-500">
        이 링크는 {expiresIn} 후에 만료됩니다.
        본인이 요청하지 않은 경우 이 이메일을 무시해 주세요.
      </Text>
    </EmailLayout>
  );
}

export default ResetPasswordEmail;
```

### 주문 확인

```tsx
// emails/order-confirmation.tsx
import {
  Column,
  Heading,
  Img,
  Row,
  Section,
  Text,
} from '@react-email/components';
import { EmailLayout } from './components/layout';

interface OrderItem {
  name: string;
  quantity: number;
  price: number;
  image: string;
}

interface OrderConfirmationEmailProps {
  orderId: string;
  customerName: string;
  items: OrderItem[];
  subtotal: number;
  shipping: number;
  total: number;
  shippingAddress: string;
}

export function OrderConfirmationEmail({
  orderId,
  customerName,
  items,
  subtotal,
  shipping,
  total,
  shippingAddress,
}: OrderConfirmationEmailProps) {
  return (
    <EmailLayout preview={`주문 확인 #${orderId}`}>
      <Heading className="text-2xl font-bold text-gray-900">
        주문이 완료되었습니다
      </Heading>

      <Text className="text-gray-600">
        {customerName}님, 주문해 주셔서 감사합니다.
        주문 번호: <strong>#{orderId}</strong>
      </Text>

      <Section className="my-6">
        <Heading as="h2" className="text-lg font-semibold">
          주문 상품
        </Heading>
        {items.map((item, index) => (
          <Row key={index} className="border-b border-gray-100 py-4">
            <Column className="w-16">
              <Img src={item.image} width={64} height={64} alt={item.name} />
            </Column>
            <Column className="pl-4">
              <Text className="m-0 font-medium">{item.name}</Text>
              <Text className="m-0 text-sm text-gray-500">
                수량: {item.quantity}
              </Text>
            </Column>
            <Column className="text-right">
              <Text className="m-0">
                ₩{(item.price * item.quantity).toLocaleString()}
              </Text>
            </Column>
          </Row>
        ))}
      </Section>

      <Section className="rounded-lg bg-gray-50 p-4">
        <Row>
          <Column>소계</Column>
          <Column className="text-right">₩{subtotal.toLocaleString()}</Column>
        </Row>
        <Row>
          <Column>배송비</Column>
          <Column className="text-right">
            {shipping === 0 ? '무료' : `₩${shipping.toLocaleString()}`}
          </Column>
        </Row>
        <Row className="font-bold">
          <Column>합계</Column>
          <Column className="text-right">₩{total.toLocaleString()}</Column>
        </Row>
      </Section>

      <Section className="mt-6">
        <Heading as="h2" className="text-lg font-semibold">
          배송 주소
        </Heading>
        <Text className="text-gray-600">{shippingAddress}</Text>
      </Section>
    </EmailLayout>
  );
}

export default OrderConfirmationEmail;
```

---

## 이메일 발송 서비스

```typescript
// lib/email/send.ts
import { resend, emailConfig } from './resend';
import WelcomeEmail from '@/emails/welcome';
import ResetPasswordEmail from '@/emails/reset-password';
import OrderConfirmationEmail from '@/emails/order-confirmation';

export const emailService = {
  async sendWelcome(to: string, data: { username: string; loginUrl: string }) {
    return resend.emails.send({
      from: emailConfig.from,
      to,
      subject: `${data.username}님, 환영합니다!`,
      react: WelcomeEmail(data),
    });
  },

  async sendPasswordReset(
    to: string,
    data: { username: string; resetUrl: string; expiresIn: string }
  ) {
    return resend.emails.send({
      from: emailConfig.from,
      to,
      subject: '비밀번호 재설정',
      react: ResetPasswordEmail(data),
    });
  },

  async sendOrderConfirmation(
    to: string,
    data: Parameters<typeof OrderConfirmationEmail>[0]
  ) {
    return resend.emails.send({
      from: emailConfig.from,
      to,
      subject: `주문 확인 #${data.orderId}`,
      react: OrderConfirmationEmail(data),
    });
  },
};
```

---

## Server Action에서 사용

```typescript
// features/auth/actions/register.action.ts
'use server';

import { authActionClient } from '@/lib/actions/safe-action';
import { registerSchema } from '../schemas/auth.schema';
import { emailService } from '@/lib/email/send';

export const registerAction = authActionClient
  .schema(registerSchema)
  .action(async ({ parsedInput }) => {
    // 사용자 생성 로직...
    const user = await createUser(parsedInput);

    // 환영 이메일 발송
    await emailService.sendWelcome(user.email, {
      username: user.name,
      loginUrl: `${process.env.NEXT_PUBLIC_APP_URL}/login`,
    });

    return { success: true };
  });
```

---

## 이메일 미리보기 (개발용)

```json
// package.json
{
  "scripts": {
    "email:dev": "email dev --dir emails --port 3001"
  }
}
```

```bash
npm run email:dev
# http://localhost:3001 에서 이메일 미리보기
```

---

## 환경 변수

```env
# .env.local
RESEND_API_KEY=re_xxxxxxxxxxxxx
```

---

## 테스트 예제

### Email Service 테스트

```typescript
// lib/email/__tests__/send.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { emailService } from '../send';
import { resend } from '../resend';

vi.mock('../resend', () => ({
  resend: {
    emails: {
      send: vi.fn(),
    },
  },
}));

describe('emailService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('sendWelcome이 올바른 데이터로 호출된다', async () => {
    vi.mocked(resend.emails.send).mockResolvedValue({ id: 'email_123' });

    await emailService.sendWelcome('test@example.com', {
      username: 'Test User',
      loginUrl: 'https://app.com/login',
    });

    expect(resend.emails.send).toHaveBeenCalledWith(
      expect.objectContaining({
        to: 'test@example.com',
        subject: 'Test User님, 환영합니다!',
      })
    );
  });

  it('sendPasswordReset이 만료 시간을 포함한다', async () => {
    await emailService.sendPasswordReset('test@example.com', {
      username: 'Test',
      resetUrl: 'https://app.com/reset/token',
      expiresIn: '1시간',
    });

    expect(resend.emails.send).toHaveBeenCalledWith(
      expect.objectContaining({
        subject: '비밀번호 재설정',
      })
    );
  });
});
```

### React Email 템플릿 테스트

```tsx
// emails/__tests__/welcome.test.tsx
import { describe, it, expect } from 'vitest';
import { render } from '@react-email/render';
import WelcomeEmail from '../welcome';

describe('WelcomeEmail', () => {
  it('사용자 이름이 포함된다', async () => {
    const html = await render(
      <WelcomeEmail username="홍길동" loginUrl="https://app.com/login" />
    );

    expect(html).toContain('홍길동');
    expect(html).toContain('환영합니다');
  });

  it('로그인 URL이 버튼에 포함된다', async () => {
    const html = await render(
      <WelcomeEmail username="Test" loginUrl="https://app.com/login" />
    );

    expect(html).toContain('https://app.com/login');
  });
});
```

---

## 안티패턴

### 1. API 키 노출

```typescript
// ❌ Bad: 클라이언트에서 직접 호출
const resend = new Resend(process.env.NEXT_PUBLIC_RESEND_KEY);

// ✅ Good: 서버에서만 호출
// lib/email/resend.ts (서버 전용)
const resend = new Resend(process.env.RESEND_API_KEY);
```

### 2. 동기 전송으로 응답 지연

```typescript
// ❌ Bad: 이메일 전송 완료까지 대기
await emailService.sendWelcome(email, data);
return { success: true };

// ✅ Good: 비동기 처리 (큐 사용)
await emailQueue.add('welcome', { to: email, data });
return { success: true }; // 즉시 응답
```

### 3. 템플릿 하드코딩

```tsx
// ❌ Bad: 인라인 HTML
resend.emails.send({
  html: `<h1>환영합니다, ${name}님!</h1>`,
});

// ✅ Good: React Email 컴포넌트
resend.emails.send({
  react: WelcomeEmail({ username: name }),
});
```

### 4. 에러 무시

```typescript
// ❌ Bad: 에러 무시
try {
  await emailService.sendWelcome(email, data);
} catch {
  // 무시
}

// ✅ Good: 에러 로깅 및 재시도
try {
  await emailService.sendWelcome(email, data);
} catch (error) {
  console.error('Email failed:', error);
  await emailQueue.add('welcome', { to: email, data, retries: 3 });
}
```

---

## 에러 처리

### Email 에러 타입

```typescript
// lib/email/errors.ts
export class EmailError extends Error {
  constructor(
    message: string,
    public code: 'SEND_FAILED' | 'TEMPLATE_ERROR' | 'RATE_LIMITED' | 'INVALID_RECIPIENT',
    public retryable: boolean = false
  ) {
    super(message);
    this.name = 'EmailError';
  }
}
```

### 안전한 이메일 전송

```typescript
// lib/email/send-safe.ts
export async function sendEmailSafe(
  sendFn: () => Promise<unknown>,
  options?: { retries?: number; delay?: number }
): Promise<{ success: boolean; error?: string }> {
  const { retries = 3, delay = 1000 } = options || {};

  for (let attempt = 0; attempt < retries; attempt++) {
    try {
      await sendFn();
      return { success: true };
    } catch (error) {
      if (attempt === retries - 1) {
        console.error('Email send failed after retries:', error);
        return { success: false, error: 'Failed to send email' };
      }
      await new Promise((r) => setTimeout(r, delay * (attempt + 1)));
    }
  }

  return { success: false, error: 'Max retries exceeded' };
}
```

---

## 성능 고려사항

### 1. 비동기 큐 사용

```typescript
// 이메일 발송을 큐에 추가
import { Queue } from 'bullmq';

const emailQueue = new Queue('emails', { connection: redis });

export async function queueEmail(type: string, data: unknown) {
  await emailQueue.add(type, data, {
    attempts: 3,
    backoff: { type: 'exponential', delay: 1000 },
  });
}
```

### 2. 배치 전송

```typescript
// 여러 수신자에게 한 번에 전송
await resend.batch.send([
  { to: 'user1@example.com', ... },
  { to: 'user2@example.com', ... },
]);
```

### 3. 템플릿 캐싱

```typescript
// 자주 사용하는 템플릿 미리 렌더링
import { render } from '@react-email/render';
import WelcomeEmail from '@/emails/welcome';

const welcomeCache = new Map<string, string>();

export async function getWelcomeHtml(props: WelcomeEmailProps) {
  const cacheKey = JSON.stringify(props);

  if (!welcomeCache.has(cacheKey)) {
    const html = await render(<WelcomeEmail {...props} />);
    welcomeCache.set(cacheKey, html);
  }

  return welcomeCache.get(cacheKey)!;
}
```

---

## 보안 고려사항

### 1. 이메일 검증

```typescript
// lib/email/validate.ts
import { z } from 'zod';

const emailSchema = z.string().email().max(254);

export function validateEmail(email: string): boolean {
  return emailSchema.safeParse(email).success;
}
```

### 2. Rate Limiting

```typescript
// lib/email/rate-limit.ts
const emailRateLimit = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(10, '1 h'), // 시간당 10개
  prefix: 'email',
});

export async function canSendEmail(userId: string): Promise<boolean> {
  const { success } = await emailRateLimit.limit(userId);
  return success;
}
```

### 3. 토큰 보안

```typescript
// 비밀번호 재설정 토큰
import { randomBytes, createHash } from 'crypto';

export function generateResetToken() {
  const token = randomBytes(32).toString('hex');
  const hashedToken = createHash('sha256').update(token).digest('hex');

  return { token, hashedToken }; // token은 이메일로, hashedToken은 DB에
}
```

### 4. 링크 만료

```typescript
// 재설정 링크에 만료 시간 포함
const expiresAt = Date.now() + 60 * 60 * 1000; // 1시간
const resetUrl = `${baseUrl}/reset/${token}?expires=${expiresAt}`;
```

---

## References

- `_references/SERVER-ACTION-PATTERN.md`
- `_references/TEST-PATTERN.md`

