# Tech Stack

Frontend Design Agent가 사용하는 기술 스택 상세 정보입니다.

---

## Core Stack

| 영역 | 기술 | 버전 | 용도 |
|------|------|------|------|
| **Framework** | Next.js (App Router) | 15+ | React 기반 풀스택 |
| **Styling** | Tailwind CSS | v4 | 유틸리티 기반 스타일링 |
| **Animation** | tw-animate-css | latest | Tailwind 애니메이션 유틸리티 |
| **Animation** | Framer Motion | 12+ | 선언적 애니메이션 |
| **Components** | shadcn/ui | latest | 재사용 가능한 컴포넌트 |
| **Components** | Motion Primitives | latest | 애니메이션 컴포넌트 |

---

## Design Tokens

### Color Space: oklch

```css
/* oklch(lightness chroma hue) */
/* 인간 지각에 기반한 균일한 색상 공간 */

:root {
  /* Primary */
  --primary: oklch(55% 0.15 250);
  --primary-foreground: oklch(98% 0 0);

  /* Background */
  --background: oklch(99% 0 0);
  --foreground: oklch(15% 0 0);

  /* Muted */
  --muted: oklch(96% 0.005 250);
  --muted-foreground: oklch(45% 0.01 250);

  /* Border */
  --border: oklch(92% 0.005 250);

  /* Accent */
  --accent: oklch(96% 0.01 250);
  --accent-foreground: oklch(15% 0.01 250);
}
```

### Typography: Variable Fonts

```css
/* Variable font axes */
/* wght: 100-900 */
/* wdth: 75-125 (some fonts) */

@font-face {
  font-family: 'Geist';
  src: url('/fonts/GeistVF.woff2') format('woff2');
  font-weight: 100 900;
  font-display: swap;
}

.heading {
  font-family: 'Geist', sans-serif;
  font-weight: 600;
  font-variation-settings: 'wght' 600;
}
```

### Spacing System

```css
/* 4px base, rem units */
:root {
  --spacing-0: 0;
  --spacing-1: 0.25rem;  /* 4px */
  --spacing-2: 0.5rem;   /* 8px */
  --spacing-3: 0.75rem;  /* 12px */
  --spacing-4: 1rem;     /* 16px */
  --spacing-5: 1.25rem;  /* 20px */
  --spacing-6: 1.5rem;   /* 24px */
  --spacing-8: 2rem;     /* 32px */
  --spacing-10: 2.5rem;  /* 40px */
  --spacing-12: 3rem;    /* 48px */
  --spacing-16: 4rem;    /* 64px */
  --spacing-20: 5rem;    /* 80px */
  --spacing-24: 6rem;    /* 96px */
}
```

---

## Tailwind v4 Configuration

### CSS-first Configuration
```css
/* app/globals.css */
@import "tailwindcss";

@theme {
  --color-primary: oklch(55% 0.15 250);
  --color-background: oklch(99% 0 0);
  --color-foreground: oklch(15% 0 0);

  --font-sans: 'Geist', ui-sans-serif, system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;

  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 1rem;
  --radius-xl: 1.5rem;
}
```

### Dark Mode
```css
@theme dark {
  --color-primary: oklch(75% 0.15 250);
  --color-background: oklch(12% 0.01 250);
  --color-foreground: oklch(98% 0 0);
}
```

---

## Animation Patterns

### Framer Motion Variants

```tsx
// Fade In Up
export const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] }
}

// Stagger Container
export const staggerContainer = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1
    }
  }
}

// Scale on Hover
export const scaleOnHover = {
  whileHover: { scale: 1.02 },
  whileTap: { scale: 0.98 },
  transition: { type: "spring", stiffness: 400, damping: 17 }
}
```

### Easing Functions

```tsx
// Custom easing curves
export const easings = {
  // Apple-like smooth
  smooth: [0.25, 0.46, 0.45, 0.94],

  // Sharp in, smooth out
  easeOut: [0, 0, 0.2, 1],

  // Smooth in, sharp out
  easeIn: [0.4, 0, 1, 1],

  // Bounce effect
  bounce: [0.68, -0.55, 0.265, 1.55],

  // Elastic
  elastic: [0.68, -0.6, 0.32, 1.6]
}
```

### tw-animate-css Classes

```html
<!-- Entrance animations -->
<div class="animate-fade-in">Fade In</div>
<div class="animate-slide-up">Slide Up</div>
<div class="animate-slide-down">Slide Down</div>
<div class="animate-scale-in">Scale In</div>

<!-- With delays -->
<div class="animate-fade-in animation-delay-100">Delayed 100ms</div>
<div class="animate-fade-in animation-delay-200">Delayed 200ms</div>

<!-- With duration -->
<div class="animate-fade-in animation-duration-500">500ms</div>
<div class="animate-fade-in animation-duration-700">700ms</div>
```

---

## shadcn/ui Integration

### Component Installation
```bash
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add input
npx shadcn@latest add dialog
```

### Custom Variants
```tsx
// components/ui/button.tsx
const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        outline: "border border-input bg-background hover:bg-accent",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        // Custom variants
        gradient: "bg-gradient-to-r from-purple-500 to-pink-500 text-white",
        glass: "bg-white/10 backdrop-blur-lg border border-white/20",
      },
      size: {
        sm: "h-9 px-3",
        default: "h-10 px-4 py-2",
        lg: "h-11 px-8",
        xl: "h-14 px-10 text-base",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)
```

---

## Performance Optimization

### Font Loading
```tsx
// app/layout.tsx
import { GeistSans } from 'geist/font/sans'
import { GeistMono } from 'geist/font/mono'

export default function RootLayout({ children }) {
  return (
    <html className={`${GeistSans.variable} ${GeistMono.variable}`}>
      <body>{children}</body>
    </html>
  )
}
```

### Image Optimization
```tsx
import Image from 'next/image'

<Image
  src="/hero.jpg"
  alt="Hero image"
  width={1920}
  height={1080}
  priority // LCP image
  placeholder="blur"
  blurDataURL="data:image/jpeg;base64,..."
/>
```

### Animation Performance
```tsx
// Use transform and opacity only
const goodAnimation = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 }
}

// Avoid layout-triggering properties
const badAnimation = {
  initial: { width: 0 },
  animate: { width: 200 } // Causes layout recalculation
}
```

### Code Splitting
```tsx
import dynamic from 'next/dynamic'

// Heavy components
const HeavyChart = dynamic(() => import('./Chart'), {
  loading: () => <Skeleton className="h-[400px]" />,
  ssr: false
})

// Modal components
const Dialog = dynamic(() => import('./Dialog'))
```

---

## Responsive Breakpoints

```css
/* Tailwind v4 default breakpoints */
--breakpoint-sm: 640px;
--breakpoint-md: 768px;
--breakpoint-lg: 1024px;
--breakpoint-xl: 1280px;
--breakpoint-2xl: 1536px;
```

### Mobile-First Pattern
```tsx
<div className="
  grid
  grid-cols-1
  md:grid-cols-2
  lg:grid-cols-3
  xl:grid-cols-4
  gap-4
  md:gap-6
  lg:gap-8
">
  {items.map(item => <Card key={item.id} {...item} />)}
</div>
```

### Container Queries
```tsx
<div className="@container">
  <div className="@md:flex @md:gap-8">
    <div className="@md:w-1/2">Content</div>
    <div className="@md:w-1/2">Sidebar</div>
  </div>
</div>
```

---

## Z-Index Scale

```css
:root {
  --z-base: 0;
  --z-dropdown: 10;
  --z-sticky: 20;
  --z-fixed: 30;
  --z-modal-backdrop: 40;
  --z-modal: 50;
  --z-popover: 60;
  --z-tooltip: 70;
  --z-toast: 80;
}
```

---

## Reference Documents

| 문서 | 설명 |
|------|------|
| `TYPOGRAPHY-RECIPES.md` | 50+ 폰트 조합, 금지 목록 |
| `COLOR-SYSTEM.md` | oklch 팔레트, 다크모드 |
| `MOTION-PATTERNS.md` | Framer Motion 레시피 30+ |
| `BACKGROUND-EFFECTS.md` | 그래디언트, 노이즈, 글래스 |
| `LAYOUT-TECHNIQUES.md` | 비대칭, 오버랩, Bento |
| `ANTI-PATTERNS.md` | AI Slop 체크리스트 |
| `ACCESSIBILITY-CHECKLIST.md` | WCAG 2.2, 신경다양성 |
