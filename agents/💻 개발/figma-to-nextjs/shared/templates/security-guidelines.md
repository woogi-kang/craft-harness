---
name: "Security Guidelines"
description: "Security best practices for generated code"
---

# Security Guidelines

> Security best practices for Figma-to-Next.js code generation

---

## XSS Prevention

### CRITICAL: Never Render Raw HTML from Figma

Figma text content may contain user-input that could include malicious scripts.

```tsx
// ❌ DANGEROUS - Never do this
<div dangerouslySetInnerHTML={{ __html: figmaTextContent }} />

// ❌ DANGEROUS - Template literals with HTML
const html = `<p>${figmaTextContent}</p>`;
document.innerHTML = html;
```

### Safe Text Rendering

```tsx
// ✅ SAFE - React automatically escapes text content
<p>{figmaTextContent}</p>

// ✅ SAFE - Text in attributes
<button aria-label={figmaButtonLabel}>Click</button>

// ✅ SAFE - Conditional rendering
{figmaText && <span>{figmaText}</span>}
```

### When HTML is Absolutely Required

If you must render HTML (e.g., rich text from Figma), always sanitize first:

```tsx
// ✅ SAFE - Sanitized HTML
import DOMPurify from 'dompurify';

interface RichTextProps {
  htmlContent: string;
}

export function RichText({ htmlContent }: RichTextProps) {
  const sanitizedContent = DOMPurify.sanitize(htmlContent, {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'u', 'a'],
    ALLOWED_ATTR: ['href', 'target', 'rel'],
  });

  return (
    <div
      dangerouslySetInnerHTML={{ __html: sanitizedContent }}
      className="rich-text"
    />
  );
}
```

### Sanitization Configuration

```typescript
// lib/sanitize.ts
import DOMPurify from 'dompurify';

// Strict configuration for Figma content
export const sanitizeConfig = {
  ALLOWED_TAGS: [
    'p', 'br', 'span', 'div',
    'strong', 'b', 'em', 'i', 'u',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li',
    'a',
  ],
  ALLOWED_ATTR: [
    'href', 'target', 'rel',
    'class', 'id',
  ],
  ALLOW_DATA_ATTR: false,
  ADD_ATTR: ['target'],
  FORBID_TAGS: ['script', 'style', 'iframe', 'form', 'input'],
  FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover'],
};

export function sanitizeFigmaContent(content: string): string {
  return DOMPurify.sanitize(content, sanitizeConfig);
}
```

---

## URL Validation

### Validate All URLs from Figma

URLs in Figma designs (buttons, links, images) should be validated:

```typescript
// lib/url-validator.ts

const ALLOWED_PROTOCOLS = ['https:', 'http:', 'mailto:', 'tel:'];
const BLOCKED_PROTOCOLS = ['javascript:', 'data:', 'vbscript:'];

export function isValidUrl(url: string): boolean {
  try {
    const parsed = new URL(url, 'https://example.com');

    // Block dangerous protocols
    if (BLOCKED_PROTOCOLS.includes(parsed.protocol)) {
      console.warn(`Blocked dangerous URL protocol: ${parsed.protocol}`);
      return false;
    }

    // Allow only safe protocols
    if (!ALLOWED_PROTOCOLS.includes(parsed.protocol)) {
      console.warn(`Unknown URL protocol: ${parsed.protocol}`);
      return false;
    }

    return true;
  } catch {
    return false;
  }
}

export function sanitizeUrl(url: string, fallback: string = '#'): string {
  if (!url) return fallback;

  // Handle relative URLs
  if (url.startsWith('/') || url.startsWith('#')) {
    return url;
  }

  // Validate absolute URLs
  return isValidUrl(url) ? url : fallback;
}
```

### Safe Link Component

```tsx
// components/safe-link.tsx
import Link from 'next/link';
import { sanitizeUrl } from '@/lib/url-validator';

interface SafeLinkProps {
  href: string;
  children: React.ReactNode;
  className?: string;
  external?: boolean;
}

export function SafeLink({
  href,
  children,
  className,
  external = false,
}: SafeLinkProps) {
  const safeHref = sanitizeUrl(href);

  // External links
  if (external || safeHref.startsWith('http')) {
    return (
      <a
        href={safeHref}
        className={className}
        target="_blank"
        rel="noopener noreferrer"  // Important for security
      >
        {children}
      </a>
    );
  }

  // Internal links
  return (
    <Link href={safeHref} className={className}>
      {children}
    </Link>
  );
}
```

---

## Image Security

### Validate Image Sources

```typescript
// lib/image-validator.ts

const ALLOWED_IMAGE_DOMAINS = [
  'figma.com',
  's3-alpha.figma.com',
  // Add your CDN domains
];

export function isAllowedImageDomain(src: string): boolean {
  try {
    const url = new URL(src);
    return ALLOWED_IMAGE_DOMAINS.some(domain =>
      url.hostname === domain || url.hostname.endsWith(`.${domain}`)
    );
  } catch {
    return false;
  }
}

// next.config.js
module.exports = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'figma.com',
      },
      {
        protocol: 'https',
        hostname: '*.figma.com',
      },
      // Add other allowed domains
    ],
  },
};
```

### Safe Image Component

```tsx
// components/safe-image.tsx
import Image from 'next/image';
import { isAllowedImageDomain } from '@/lib/image-validator';

interface SafeImageProps {
  src: string;
  alt: string;
  width: number;
  height: number;
  className?: string;
  priority?: boolean;
}

export function SafeImage({
  src,
  alt,
  width,
  height,
  className,
  priority = false,
}: SafeImageProps) {
  // Validate external images
  if (src.startsWith('http') && !isAllowedImageDomain(src)) {
    console.warn(`Blocked image from untrusted domain: ${src}`);
    return (
      <div
        className={`bg-muted flex items-center justify-center ${className}`}
        style={{ width, height }}
        role="img"
        aria-label={alt}
      >
        <span className="text-muted-foreground text-sm">Image unavailable</span>
      </div>
    );
  }

  return (
    <Image
      src={src}
      alt={alt}
      width={width}
      height={height}
      className={className}
      priority={priority}
    />
  );
}
```

---

## Input Validation

### Form Inputs Generated from Figma

```tsx
// components/safe-input.tsx
import { Input } from '@/components/ui/input';
import { forwardRef } from 'react';

interface SafeInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  maxLength?: number;
}

export const SafeInput = forwardRef<HTMLInputElement, SafeInputProps>(
  ({ maxLength = 255, ...props }, ref) => {
    return (
      <Input
        ref={ref}
        maxLength={maxLength}  // Prevent excessive input
        autoComplete="off"     // Disable autocomplete for sensitive fields if needed
        {...props}
      />
    );
  }
);

SafeInput.displayName = 'SafeInput';
```

### Form Submission Security

```tsx
// CSRF protection with Server Actions (Next.js 15+)
'use server';

import { headers } from 'next/headers';

export async function submitForm(formData: FormData) {
  // Validate origin
  const headersList = headers();
  const origin = headersList.get('origin');
  const host = headersList.get('host');

  if (origin && !origin.includes(host!)) {
    throw new Error('Invalid origin');
  }

  // Validate and sanitize form data
  const email = formData.get('email') as string;
  const message = formData.get('message') as string;

  // Input validation
  if (!email || !email.includes('@')) {
    return { error: 'Invalid email' };
  }

  if (!message || message.length > 1000) {
    return { error: 'Invalid message' };
  }

  // Process form...
}
```

---

## Content Security Policy

### Recommended CSP for Generated Sites

```typescript
// next.config.js
const ContentSecurityPolicy = `
  default-src 'self';
  script-src 'self' 'unsafe-eval' 'unsafe-inline';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https://figma.com https://*.figma.com;
  font-src 'self';
  connect-src 'self';
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
`;

const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: ContentSecurityPolicy.replace(/\s{2,}/g, ' ').trim(),
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY',
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff',
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin',
  },
  {
    key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=()',
  },
];

module.exports = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: securityHeaders,
      },
    ];
  },
};
```

---

## Security Checklist

### Before Code Generation

- [ ] Figma file source is trusted
- [ ] No user-generated content in design
- [ ] Image sources are from known domains

### During Code Generation

- [ ] Text content uses React's automatic escaping
- [ ] No `dangerouslySetInnerHTML` without sanitization
- [ ] URLs are validated before use
- [ ] External links have `rel="noopener noreferrer"`

### After Code Generation

- [ ] Review generated code for security issues
- [ ] Verify CSP headers are configured
- [ ] Test with security linting tools (eslint-plugin-security)
- [ ] Run OWASP ZAP or similar security scanner

### Code Review Flags

Look for these patterns in generated code:

```typescript
// 🚨 SECURITY REVIEW REQUIRED
const flaggedPatterns = [
  'dangerouslySetInnerHTML',
  'innerHTML',
  'eval(',
  'new Function(',
  'javascript:',
  'data:text/html',
];
```

---

## Dependencies

### Recommended Security Packages

```json
{
  "dependencies": {
    "dompurify": "^3.0.0"
  },
  "devDependencies": {
    "eslint-plugin-security": "^2.1.0",
    "@typescript-eslint/eslint-plugin": "^7.0.0"
  }
}
```

### ESLint Security Configuration

```javascript
// .eslintrc.js
module.exports = {
  plugins: ['security'],
  extends: ['plugin:security/recommended'],
  rules: {
    'security/detect-object-injection': 'warn',
    'security/detect-non-literal-fs-filename': 'warn',
    'security/detect-unsafe-regex': 'error',
    'security/detect-buffer-noassert': 'error',
    'security/detect-eval-with-expression': 'error',
    'security/detect-no-csrf-before-method-override': 'error',
    'security/detect-possible-timing-attacks': 'warn',
  },
};
```
