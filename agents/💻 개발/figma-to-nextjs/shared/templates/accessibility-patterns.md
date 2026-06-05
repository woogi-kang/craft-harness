---
name: "Accessibility Patterns"
description: "WCAG 2.1 AA compliant patterns for code generation"
---

# Accessibility Patterns

> WCAG 2.1 AA compliant patterns for Figma-to-Next.js code generation

---

## Core Principles

### POUR Framework

| Principle | Requirement | Implementation |
|-----------|-------------|----------------|
| **Perceivable** | Content accessible to all senses | Alt text, captions, color contrast |
| **Operable** | All functionality via keyboard | Focus management, touch targets |
| **Understandable** | Clear and predictable | Consistent navigation, error messages |
| **Robust** | Works with assistive tech | Semantic HTML, ARIA labels |

---

## Semantic HTML Requirements

### Element Selection Guide

| Figma Pattern | HTML Element | Never Use |
|---------------|--------------|-----------|
| Page section | `<section aria-labelledby="...">` | `<div>` |
| Navigation | `<nav aria-label="...">` | `<div>` |
| Header area | `<header>` | `<div>` |
| Footer area | `<footer>` | `<div>` |
| Article/Card | `<article>` | `<div>` |
| Sidebar | `<aside>` | `<div>` |
| Main content | `<main>` | `<div>` |
| Heading | `<h1>` - `<h6>` | `<div class="heading">` |
| List | `<ul>`, `<ol>` | `<div>` with bullets |
| Button | `<button>` | `<div onClick>` |

### Correct Implementation

```tsx
// ✅ CORRECT - Semantic structure
<main>
  <section aria-labelledby="hero-heading">
    <h1 id="hero-heading">Welcome to Our Platform</h1>
    <p>Description text here</p>
  </section>

  <section aria-labelledby="features-heading">
    <h2 id="features-heading">Features</h2>
    <ul>
      <li>Feature one</li>
      <li>Feature two</li>
    </ul>
  </section>
</main>

// ❌ INCORRECT - Div soup
<div className="main">
  <div className="section">
    <div className="heading">Welcome to Our Platform</div>
    <div className="text">Description text here</div>
  </div>
</div>
```

---

## Focus Management

### Focus Visible States

All interactive elements MUST have visible focus states:

```tsx
// ✅ CORRECT - Visible focus ring
<Button className="focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
  Click me
</Button>

// ✅ CORRECT - Custom focus style
<a
  href="/about"
  className="focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
>
  About us
</a>

// ❌ INCORRECT - Removing focus without replacement
<button className="outline-none focus:outline-none">
  Inaccessible button
</button>
```

### Focus Order

Ensure logical tab order:

```tsx
// ✅ CORRECT - Natural focus order follows visual order
<nav>
  <a href="/">Home</a>      {/* Tab 1 */}
  <a href="/about">About</a> {/* Tab 2 */}
  <a href="/contact">Contact</a> {/* Tab 3 */}
</nav>

// ❌ INCORRECT - Don't use positive tabindex
<nav>
  <a href="/" tabIndex={3}>Home</a>
  <a href="/about" tabIndex={1}>About</a>  {/* Confusing order */}
  <a href="/contact" tabIndex={2}>Contact</a>
</nav>
```

### Skip Links

Add skip links for keyboard users:

```tsx
// components/skip-link.tsx
export function SkipLink() {
  return (
    <a
      href="#main-content"
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-background focus:text-foreground focus:ring-2"
    >
      Skip to main content
    </a>
  );
}

// app/layout.tsx
export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <SkipLink />
        <Header />
        <main id="main-content" tabIndex={-1}>
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}
```

---

## Interactive Elements

### Button Accessibility

```tsx
// components/accessible-button.tsx
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';

interface AccessibleButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  loading?: boolean;
  disabled?: boolean;
  ariaLabel?: string;
}

export function AccessibleButton({
  children,
  onClick,
  loading = false,
  disabled = false,
  ariaLabel,
}: AccessibleButtonProps) {
  return (
    <Button
      onClick={onClick}
      disabled={disabled || loading}
      aria-label={ariaLabel}
      aria-busy={loading}
      aria-disabled={disabled || loading}
      className="min-h-[44px] min-w-[44px] focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
    >
      {loading && (
        <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
      )}
      {loading ? 'Loading...' : children}
    </Button>
  );
}
```

### Icon Button

```tsx
// components/icon-button.tsx
import { Button } from '@/components/ui/button';
import { LucideIcon } from 'lucide-react';

interface IconButtonProps {
  icon: LucideIcon;
  label: string;  // Required for accessibility
  onClick?: () => void;
  variant?: 'default' | 'outline' | 'ghost';
}

export function IconButton({
  icon: Icon,
  label,
  onClick,
  variant = 'ghost',
}: IconButtonProps) {
  return (
    <Button
      variant={variant}
      size="icon"
      onClick={onClick}
      aria-label={label}  // Screen reader text
      className="min-h-[44px] min-w-[44px]"
    >
      <Icon className="h-5 w-5" aria-hidden="true" />
      <span className="sr-only">{label}</span>
    </Button>
  );
}

// Usage
<IconButton icon={Menu} label="Open menu" onClick={toggleMenu} />
<IconButton icon={X} label="Close menu" onClick={closeMenu} />
```

### Mobile Navigation

```tsx
// components/mobile-nav.tsx
'use client';

import { useState, useEffect, useRef } from 'react';
import { Menu, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function MobileNav({ items }) {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Close on Escape
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false);
        buttonRef.current?.focus();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen]);

  // Trap focus in menu
  useEffect(() => {
    if (isOpen && menuRef.current) {
      const focusableElements = menuRef.current.querySelectorAll(
        'a[href], button:not([disabled])'
      );
      const firstElement = focusableElements[0] as HTMLElement;
      firstElement?.focus();
    }
  }, [isOpen]);

  return (
    <>
      <Button
        ref={buttonRef}
        variant="ghost"
        size="icon"
        className="lg:hidden min-h-[44px] min-w-[44px]"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-controls="mobile-menu"
        aria-label={isOpen ? 'Close menu' : 'Open menu'}
      >
        {isOpen ? (
          <X className="h-6 w-6" aria-hidden="true" />
        ) : (
          <Menu className="h-6 w-6" aria-hidden="true" />
        )}
      </Button>

      {isOpen && (
        <div
          id="mobile-menu"
          ref={menuRef}
          role="dialog"
          aria-modal="true"
          aria-label="Navigation menu"
          className="fixed inset-0 z-50 bg-background lg:hidden"
        >
          <nav className="flex flex-col p-4" role="navigation">
            {items.map((item, index) => (
              <a
                key={item.href}
                href={item.href}
                className="py-3 text-lg focus-visible:ring-2 focus-visible:ring-ring"
                onClick={() => setIsOpen(false)}
              >
                {item.label}
              </a>
            ))}
          </nav>
        </div>
      )}
    </>
  );
}
```

---

## Touch Targets

### Minimum Size Requirements

All interactive elements must have minimum touch target of 44x44 pixels:

```tsx
// ✅ CORRECT - Adequate touch target
<button className="min-h-[44px] min-w-[44px] p-3">
  <Icon className="h-5 w-5" />
</button>

// ✅ CORRECT - Padding increases touch area
<a href="/link" className="inline-block py-3 px-4">
  Small text link
</a>

// ❌ INCORRECT - Too small for touch
<button className="p-1">
  <Icon className="h-4 w-4" />
</button>
```

### Touch Target Spacing

```tsx
// ✅ CORRECT - Adequate spacing between targets
<div className="flex gap-4">  {/* 16px gap */}
  <Button>Action 1</Button>
  <Button>Action 2</Button>
</div>

// ❌ INCORRECT - Targets too close
<div className="flex gap-1">  {/* Only 4px gap */}
  <Button>Action 1</Button>
  <Button>Action 2</Button>
</div>
```

---

## Color and Contrast

### Contrast Requirements

| Content Type | Minimum Ratio | Example |
|--------------|---------------|---------|
| Normal text (< 18px) | 4.5:1 | `text-foreground` on `bg-background` |
| Large text (>= 18px bold or 24px) | 3:1 | `text-muted-foreground` on `bg-background` |
| UI components | 3:1 | Button borders, form inputs |
| Non-text (icons, graphics) | 3:1 | Icon on background |

### Don't Rely on Color Alone

```tsx
// ✅ CORRECT - Multiple indicators
<div className="flex items-center gap-2">
  <span className="text-destructive">Error:</span>
  <AlertCircle className="h-4 w-4 text-destructive" aria-hidden="true" />
  <span>Please enter a valid email</span>
</div>

// ❌ INCORRECT - Color only
<span className="text-red-500">Invalid email</span>
```

### Form Validation

```tsx
// components/form-field.tsx
interface FormFieldProps {
  label: string;
  error?: string;
  children: React.ReactNode;
  required?: boolean;
}

export function FormField({ label, error, children, required }: FormFieldProps) {
  const id = useId();
  const errorId = `${id}-error`;

  return (
    <div className="space-y-2">
      <Label htmlFor={id}>
        {label}
        {required && <span className="text-destructive ml-1" aria-hidden="true">*</span>}
        {required && <span className="sr-only">(required)</span>}
      </Label>

      {/* Clone child to add aria attributes */}
      {React.cloneElement(children as React.ReactElement, {
        id,
        'aria-invalid': !!error,
        'aria-describedby': error ? errorId : undefined,
        'aria-required': required,
      })}

      {error && (
        <p id={errorId} className="text-sm text-destructive flex items-center gap-1" role="alert">
          <AlertCircle className="h-4 w-4" aria-hidden="true" />
          {error}
        </p>
      )}
    </div>
  );
}
```

---

## Motion and Animation

### Respect User Preferences

```tsx
// ✅ CORRECT - Motion-reduced alternative
<div className="transition-transform duration-300 motion-reduce:transition-none motion-reduce:transform-none hover:scale-105">
  Animated card
</div>

// ✅ CORRECT - Using CSS media query
// globals.css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Framer Motion with Reduced Motion

```tsx
import { motion, useReducedMotion } from 'framer-motion';

export function AnimatedComponent({ children }) {
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.div
      initial={{ opacity: 0, y: shouldReduceMotion ? 0 : 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: shouldReduceMotion ? 0 : 0.3 }}
    >
      {children}
    </motion.div>
  );
}
```

---

## Images and Media

### Alt Text Guidelines

```tsx
// ✅ Informative alt text
<Image
  src="/hero.jpg"
  alt="Team collaboration in modern office with glass walls and green plants"
/>

// ✅ Decorative images - empty alt
<Image
  src="/decorative-pattern.svg"
  alt=""
  aria-hidden="true"
/>

// ✅ Functional images (buttons, links)
<button>
  <Image src="/search-icon.svg" alt="Search" />
</button>

// ❌ INCORRECT - Redundant or unhelpful
<Image src="/hero.jpg" alt="image" />
<Image src="/hero.jpg" alt="hero-image-01.jpg" />
```

### Video Accessibility

```tsx
// components/accessible-video.tsx
interface VideoProps {
  src: string;
  poster: string;
  captions?: string;
}

export function AccessibleVideo({ src, poster, captions }: VideoProps) {
  return (
    <figure>
      <video
        controls
        poster={poster}
        preload="metadata"
        className="w-full rounded-lg"
      >
        <source src={src} type="video/mp4" />
        {captions && (
          <track
            kind="captions"
            src={captions}
            srcLang="en"
            label="English captions"
            default
          />
        )}
        Your browser does not support the video tag.
      </video>
      <figcaption className="sr-only">
        Video player with captions available
      </figcaption>
    </figure>
  );
}
```

---

## ARIA Patterns

### Common ARIA Usage

```tsx
// Live regions for dynamic content
<div aria-live="polite" aria-atomic="true">
  {statusMessage}
</div>

// Loading states
<Button aria-busy={isLoading} disabled={isLoading}>
  {isLoading ? 'Saving...' : 'Save'}
</Button>

// Expanded/collapsed
<Button
  aria-expanded={isOpen}
  aria-controls="panel-content"
  onClick={() => setIsOpen(!isOpen)}
>
  {isOpen ? 'Collapse' : 'Expand'}
</Button>
<div id="panel-content" hidden={!isOpen}>
  Panel content
</div>

// Current page in navigation
<nav>
  <a href="/" aria-current={isHome ? 'page' : undefined}>Home</a>
  <a href="/about" aria-current={isAbout ? 'page' : undefined}>About</a>
</nav>
```

---

## Testing Checklist

### Automated Testing

```bash
# axe-core with Jest
npm install --save-dev jest-axe @axe-core/react

# Playwright accessibility testing
npm install --save-dev @axe-core/playwright
```

```typescript
// __tests__/accessibility.test.tsx
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { HeroSection } from '@/components/sections/hero-section';

expect.extend(toHaveNoViolations);

describe('HeroSection Accessibility', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(
      <HeroSection
        title="Test Title"
        subtitle="Test subtitle"
        primaryCta={{ text: 'Click', href: '/' }}
      />
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

### Manual Testing Checklist

- [ ] Navigate entire page using only keyboard (Tab, Shift+Tab, Enter, Escape)
- [ ] Test with screen reader (VoiceOver, NVDA, or JAWS)
- [ ] Verify focus is always visible
- [ ] Check color contrast with browser tools
- [ ] Test at 200% zoom
- [ ] Test with reduced motion setting enabled
- [ ] Verify all images have appropriate alt text
- [ ] Confirm form errors are announced to screen readers
