# Minimal Strategy

여백과 타이포그래피를 중심으로 한 미니멀 디자인 전략입니다.
미디어, 갤러리, 웰니스, 럭셔리 브랜드에 최적화되어 있습니다.

---

## 템플릿

### 1. Editorial Magazine
- **특징**: 매거진 스타일, 타이포그래피 중심
- **폰트**: GT Sectra, Playfair Display
- **적용 분야**: 미디어, 블로그, 콘텐츠

```css
/* Typography System */
.editorial-heading {
  font-family: 'GT Sectra', 'Playfair Display', serif;
  font-weight: 400;
  letter-spacing: -0.02em;
  line-height: 1.1;
}
```

**디자인 원칙**:
- Serif 폰트를 제목에 활용
- 대담한 타이포그래피 스케일
- 이미지와 텍스트의 긴장감
- 그리드 기반 레이아웃

### 2. Organic Natural
- **특징**: 자연스러움, 부드러운 곡선
- **폰트**: Cormorant, Lora
- **적용 분야**: 웰니스, 라이프스타일

```css
/* Organic Shapes */
.organic-blob {
  border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%;
  animation: morph 8s ease-in-out infinite;
}

@keyframes morph {
  0%, 100% { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; }
  50% { border-radius: 30% 60% 70% 40% / 50% 60% 30% 60%; }
}
```

**디자인 원칙**:
- Earth tones 색상
- 유기적인 형태
- 자연 이미지 활용
- 부드러운 전환

### 3. Brutalist Raw
- **특징**: 거친, 원시적, 의도적 불완전함
- **폰트**: Helvetica Now, Arial Black
- **적용 분야**: 갤러리, 아트, 실험적 프로젝트

```css
/* Brutalist Style */
.brutalist {
  border: 3px solid black;
  box-shadow: 8px 8px 0 black;
  background: white;
}
```

**디자인 원칙**:
- 강한 대비
- 의도적으로 "디자인되지 않은" 느낌
- Raw HTML 미학
- 흑백 + 단일 강조색

### 4. Luxury Refined
- **특징**: 고급스러움, 세련된 디테일
- **폰트**: Didot, Playfair Display
- **적용 분야**: 럭셔리 브랜드, 하이엔드 제품

```css
/* Luxury Accents */
.gold-accent {
  background: linear-gradient(
    135deg,
    oklch(75% 0.1 85) 0%,
    oklch(85% 0.12 90) 50%,
    oklch(70% 0.08 80) 100%
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

**디자인 원칙**:
- 여백의 미학
- 섬세한 타이포그래피
- 고급 소재 텍스처
- 절제된 색상

---

## Hero Section Patterns

### Full-Bleed Image
```tsx
<section className="relative min-h-screen">
  <Image
    src="/hero.jpg"
    alt="Hero image"
    fill
    className="object-cover"
  />
  <div className="absolute inset-0 bg-black/30" />
  <div className="relative z-10 min-h-screen flex items-end p-12">
    <div className="max-w-2xl text-white">
      <h1 className="font-serif text-6xl tracking-tight mb-6">
        The Art of Living
      </h1>
      <p className="text-xl text-white/80">
        Discover timeless elegance in every detail.
      </p>
    </div>
  </div>
</section>
```

### Editorial Split
```tsx
<section className="min-h-screen grid lg:grid-cols-12">
  <div className="lg:col-span-5 p-12 flex flex-col justify-center">
    <span className="text-sm tracking-widest uppercase text-muted-foreground mb-8">
      Volume 01
    </span>
    <h1 className="font-serif text-5xl tracking-tight leading-none mb-6">
      Stories That Matter
    </h1>
    <p className="text-lg text-muted-foreground mb-8 max-w-md">
      Exploring the intersection of culture, design, and human experience.
    </p>
    <Link href="/read" className="underline underline-offset-4">
      Start Reading
    </Link>
  </div>
  <div className="lg:col-span-7 relative">
    <Image src="/editorial.jpg" alt="" fill className="object-cover" />
  </div>
</section>
```

---

## Color Palettes

### Natural Tones
```css
:root {
  --background: oklch(97% 0.01 85);
  --foreground: oklch(25% 0.02 85);
  --card: oklch(99% 0.005 85);
  --muted: oklch(93% 0.015 85);
  --muted-foreground: oklch(50% 0.02 85);
  --border: oklch(88% 0.02 85);
  --primary: oklch(35% 0.04 150);
  --accent: oklch(60% 0.08 85);
}
```

### Monochrome
```css
:root {
  --background: oklch(98% 0 0);
  --foreground: oklch(10% 0 0);
  --card: oklch(100% 0 0);
  --muted: oklch(95% 0 0);
  --muted-foreground: oklch(40% 0 0);
  --border: oklch(90% 0 0);
  --primary: oklch(10% 0 0);
  --accent: oklch(10% 0 0);
}
```

### Luxury Dark
```css
:root {
  --background: oklch(12% 0.01 85);
  --foreground: oklch(95% 0.01 85);
  --card: oklch(15% 0.015 85);
  --muted: oklch(20% 0.02 85);
  --muted-foreground: oklch(60% 0.02 85);
  --border: oklch(25% 0.02 85);
  --gold: oklch(75% 0.1 85);
}
```

---

## Typography Scale

```css
/* Editorial Scale - Larger contrast */
--text-xs: 0.75rem;
--text-sm: 0.875rem;
--text-base: 1rem;
--text-lg: 1.125rem;
--text-xl: 1.375rem;
--text-2xl: 1.75rem;
--text-3xl: 2.25rem;
--text-4xl: 3rem;
--text-5xl: 4rem;
--text-6xl: 5.5rem;
--text-7xl: 7rem;

/* Serif + Sans combination */
.heading { font-family: 'GT Sectra', 'Playfair Display', serif; }
.body { font-family: 'Source Sans Pro', 'Lato', sans-serif; }
```

---

## Motion Patterns

### Reveal on Scroll
```tsx
const revealVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration: 0.8, ease: "easeOut" }
  }
}
```

### Image Parallax
```tsx
const { scrollYProgress } = useScroll({
  target: ref,
  offset: ["start end", "end start"]
})

const y = useTransform(scrollYProgress, [0, 1], ["-10%", "10%"])
```

### Text Mask Reveal
```tsx
<motion.div
  initial={{ clipPath: "inset(0 100% 0 0)" }}
  animate={{ clipPath: "inset(0 0% 0 0)" }}
  transition={{ duration: 1, ease: [0.77, 0, 0.175, 1] }}
>
  <h1>Revealed Text</h1>
</motion.div>
```

---

## Component Patterns

### Article Card
```tsx
<article className="group cursor-pointer">
  <div className="relative aspect-[4/3] overflow-hidden mb-4">
    <Image
      src={article.image}
      alt={article.title}
      fill
      className="object-cover transition-transform duration-700 group-hover:scale-105"
    />
  </div>
  <div className="space-y-2">
    <span className="text-xs tracking-widest uppercase text-muted-foreground">
      {article.category}
    </span>
    <h3 className="font-serif text-2xl tracking-tight group-hover:underline">
      {article.title}
    </h3>
    <p className="text-muted-foreground line-clamp-2">
      {article.excerpt}
    </p>
  </div>
</article>
```

### Quote Block
```tsx
<blockquote className="border-l-2 border-foreground pl-8 py-4">
  <p className="font-serif text-3xl leading-relaxed italic">
    "Design is not just what it looks like and feels like.
    Design is how it works."
  </p>
  <footer className="mt-4 text-sm text-muted-foreground">
    — Steve Jobs
  </footer>
</blockquote>
```

### Image Gallery Grid
```tsx
<div className="grid grid-cols-12 gap-4">
  <div className="col-span-8 aspect-[4/3] relative">
    <Image src="/large.jpg" alt="" fill className="object-cover" />
  </div>
  <div className="col-span-4 space-y-4">
    <div className="aspect-square relative">
      <Image src="/small-1.jpg" alt="" fill className="object-cover" />
    </div>
    <div className="aspect-square relative">
      <Image src="/small-2.jpg" alt="" fill className="object-cover" />
    </div>
  </div>
</div>
```
