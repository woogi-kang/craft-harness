# Modern Strategy

세련되고 기능 중심의 모던 디자인 전략입니다.
SaaS, AI 플랫폼, 개발자 도구에 최적화되어 있습니다.

---

## 템플릿

### 1. Barely-There Minimal
- **특징**: 극도의 절제, 여백 중심
- **폰트**: Satoshi, Geist
- **적용 분야**: SaaS, AI

```css
/* Color Palette */
--background: oklch(99% 0 0);
--foreground: oklch(15% 0 0);
--muted: oklch(96% 0 0);
--accent: oklch(55% 0.15 250);
```

**디자인 원칙**:
- 화면의 60% 이상 여백
- 단색 배경, 미니멀 그래픽
- 콘텐츠 밀도 최소화
- Monospace 폰트를 숫자/코드에 활용

### 2. Liquid Glass
- **특징**: Apple 스타일, Glassmorphism
- **폰트**: SF Pro, Mona Sans
- **적용 분야**: 앱, 소프트웨어

```css
/* Glassmorphism Effect */
.glass {
  background: oklch(100% 0 0 / 0.7);
  backdrop-filter: blur(20px);
  border: 1px solid oklch(100% 0 0 / 0.2);
  border-radius: 16px;
}
```

**디자인 원칙**:
- 반투명 레이어 활용
- 부드러운 그림자
- 미묘한 그라데이션
- 다크모드에서 더 효과적

### 3. Tech Documentation
- **특징**: 매뉴얼 스타일, 명확함
- **폰트**: JetBrains Mono, Geist
- **적용 분야**: 개발자 도구, API 문서

```css
/* Code Block Style */
.code-block {
  background: oklch(20% 0 0);
  border-radius: 8px;
  font-family: 'JetBrains Mono', monospace;
  padding: 1rem;
}
```

**디자인 원칙**:
- 계층 구조 명확히
- 코드 블록 강조
- 네비게이션 우선
- 다크 테마 기본

---

## Hero Section Patterns

### Centered Minimal
```tsx
<section className="min-h-screen flex items-center justify-center">
  <div className="max-w-2xl text-center space-y-6">
    <h1 className="text-5xl font-medium tracking-tight">
      Build faster with AI
    </h1>
    <p className="text-lg text-muted-foreground">
      Ship production-ready features in minutes.
    </p>
    <Button size="lg">Get Started</Button>
  </div>
</section>
```

### Split with Visual
```tsx
<section className="min-h-screen grid lg:grid-cols-2 gap-12 items-center">
  <div className="space-y-6">
    <Badge variant="secondary">New Release</Badge>
    <h1 className="text-5xl font-medium tracking-tight">
      The developer platform
    </h1>
    <p className="text-lg text-muted-foreground">
      Everything you need to build modern applications.
    </p>
    <div className="flex gap-4">
      <Button>Start Free</Button>
      <Button variant="outline">View Demo</Button>
    </div>
  </div>
  <div className="relative">
    <div className="glass p-8 rounded-2xl">
      {/* Product Screenshot */}
    </div>
  </div>
</section>
```

---

## Color Palettes

### Light Mode
```css
:root {
  --background: oklch(99% 0 0);
  --foreground: oklch(15% 0 0);
  --card: oklch(100% 0 0);
  --muted: oklch(96% 0.005 250);
  --muted-foreground: oklch(45% 0.01 250);
  --border: oklch(92% 0.005 250);
  --primary: oklch(25% 0.02 250);
  --primary-foreground: oklch(98% 0 0);
  --accent: oklch(55% 0.15 250);
}
```

### Dark Mode
```css
.dark {
  --background: oklch(12% 0.01 250);
  --foreground: oklch(98% 0 0);
  --card: oklch(15% 0.01 250);
  --muted: oklch(20% 0.01 250);
  --muted-foreground: oklch(65% 0.01 250);
  --border: oklch(25% 0.01 250);
  --primary: oklch(98% 0 0);
  --primary-foreground: oklch(12% 0.01 250);
  --accent: oklch(65% 0.15 250);
}
```

---

## Typography Scale

```css
/* Modern Scale */
--text-xs: clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem);
--text-sm: clamp(0.875rem, 0.8rem + 0.375vw, 1rem);
--text-base: clamp(1rem, 0.9rem + 0.5vw, 1.125rem);
--text-lg: clamp(1.125rem, 1rem + 0.625vw, 1.25rem);
--text-xl: clamp(1.25rem, 1.1rem + 0.75vw, 1.5rem);
--text-2xl: clamp(1.5rem, 1.3rem + 1vw, 2rem);
--text-3xl: clamp(1.875rem, 1.5rem + 1.875vw, 2.5rem);
--text-4xl: clamp(2.25rem, 1.75rem + 2.5vw, 3.5rem);
--text-5xl: clamp(3rem, 2rem + 5vw, 5rem);
```

---

## Motion Patterns

### Fade In Up
```tsx
const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] }
}
```

### Stagger Children
```tsx
const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1
    }
  }
}
```

### Scale on Hover
```tsx
<motion.div
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
  transition={{ type: "spring", stiffness: 400, damping: 17 }}
>
  {/* Card Content */}
</motion.div>
```

---

## Component Patterns

### Metric Card
```tsx
<Card className="p-6">
  <div className="flex items-center justify-between">
    <span className="text-sm text-muted-foreground">Total Revenue</span>
    <TrendingUp className="h-4 w-4 text-green-500" />
  </div>
  <div className="mt-2">
    <span className="text-3xl font-semibold">$45,231.89</span>
  </div>
  <p className="text-xs text-muted-foreground mt-1">
    +20.1% from last month
  </p>
</Card>
```

### Feature Grid
```tsx
<div className="grid md:grid-cols-3 gap-8">
  {features.map((feature) => (
    <div key={feature.title} className="space-y-3">
      <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
        <feature.icon className="w-5 h-5 text-primary" />
      </div>
      <h3 className="font-medium">{feature.title}</h3>
      <p className="text-sm text-muted-foreground">{feature.description}</p>
    </div>
  ))}
</div>
```
