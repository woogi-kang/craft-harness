# Bold Strategy

대담하고 실험적인 디자인 전략입니다.
브랜드, 포트폴리오, 게임, 스타트업에 최적화되어 있습니다.

---

## 템플릿

### 1. Soft Maximalism
- **특징**: 대담하지만 통제된, 풍부한 레이어
- **폰트**: Clash Display, Sora
- **적용 분야**: 브랜드, 마케팅

```css
/* Layered Composition */
.maximalist-hero {
  position: relative;
}

.maximalist-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    135deg,
    oklch(70% 0.2 340) 0%,
    oklch(60% 0.25 280) 50%,
    oklch(50% 0.2 220) 100%
  );
  opacity: 0.8;
}
```

**디자인 원칙**:
- 풍부한 색상 그라데이션
- 오버랩 레이어
- 대담한 타이포그래피
- 그래픽 요소 적극 활용

### 2. Anti-Design Chaos
- **특징**: 규칙 파괴, 비정형, 예측 불가
- **폰트**: Basement Grotesque, Space Grotesk
- **적용 분야**: 포트폴리오, 크리에이티브 에이전시

```css
/* Chaotic Grid */
.chaos-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 0;
}

.chaos-item:nth-child(1) { grid-column: 1 / 5; grid-row: 1 / 3; }
.chaos-item:nth-child(2) { grid-column: 5 / 13; grid-row: 2 / 4; }
.chaos-item:nth-child(3) { grid-column: 2 / 8; grid-row: 4 / 5; }
```

**디자인 원칙**:
- 의도적인 불균형
- 오버랩과 충돌
- 비정형 그리드
- 커스텀 커서, 예상치 못한 인터랙션

### 3. Retro-Futuristic
- **특징**: 90s 복고 + 사이버펑크
- **폰트**: VT323, Orbitron, Press Start 2P
- **적용 분야**: 게임, 엔터테인먼트

```css
/* CRT Effect */
.crt-effect {
  animation: flicker 0.15s infinite;
  text-shadow:
    0 0 5px oklch(80% 0.3 160),
    0 0 10px oklch(80% 0.3 160),
    0 0 20px oklch(80% 0.3 160);
}

@keyframes flicker {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.95; }
}
```

**디자인 원칙**:
- 네온 색상
- 글리치 효과
- 픽셀 아트 요소
- Scanline, CRT 효과

### 4. Playful Rounded
- **특징**: 친근한, 둥근 형태, 밝은 색상
- **폰트**: Nunito, Quicksand, Varela Round
- **적용 분야**: 교육, 키즈, 커뮤니티

```css
/* Playful Shapes */
.playful-button {
  border-radius: 9999px;
  padding: 1rem 2rem;
  background: oklch(75% 0.2 280);
  box-shadow:
    0 4px 0 oklch(55% 0.2 280),
    0 6px 0 oklch(45% 0.15 280);
  transition: transform 0.1s, box-shadow 0.1s;
}

.playful-button:active {
  transform: translateY(4px);
  box-shadow: 0 0 0 oklch(55% 0.2 280);
}
```

**디자인 원칙**:
- 둥근 모서리 (pill, rounded)
- 밝은 파스텔 또는 비비드 색상
- 큰 버튼, 명확한 액션
- 친근한 일러스트레이션

### 5. Grade-School Bold
- **특징**: 기본 색상, 명확한 구분, 단순함
- **폰트**: Albert Sans, DM Sans
- **적용 분야**: 스타트업, 프로덕트

```css
/* Primary Colors */
:root {
  --red: oklch(60% 0.25 25);
  --blue: oklch(55% 0.2 250);
  --yellow: oklch(85% 0.2 95);
  --green: oklch(65% 0.2 145);
}
```

**디자인 원칙**:
- RGB 기본색 + 보조색
- 명확한 계층 구조
- 굵은 폰트 웨이트
- 단순하고 직관적

---

## Hero Section Patterns

### Overlapping Chaos
```tsx
<section className="min-h-screen relative overflow-hidden">
  <div className="absolute top-[10%] left-[5%] w-[60%] z-10">
    <h1 className="text-[15vw] font-black leading-none">
      BREAK
    </h1>
  </div>
  <div className="absolute top-[25%] right-[10%] w-[50%] z-20">
    <Image src="/chaos-1.jpg" alt="" className="rotate-[-5deg]" />
  </div>
  <div className="absolute bottom-[15%] left-[20%] z-30">
    <h2 className="text-[12vw] font-black leading-none text-stroke">
      RULES
    </h2>
  </div>
  <div className="absolute bottom-[5%] right-[5%] z-10">
    <Image src="/chaos-2.jpg" alt="" className="rotate-[8deg]" />
  </div>
</section>
```

### Neon Retro
```tsx
<section className="min-h-screen bg-black flex items-center justify-center relative">
  <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-20" />
  <div className="text-center z-10 space-y-8">
    <h1 className="text-8xl font-mono uppercase tracking-wider neon-text">
      GAME ON
    </h1>
    <p className="text-xl text-cyan-400 font-mono">
      [PRESS START TO BEGIN]
    </p>
    <Button className="bg-cyan-500 hover:bg-cyan-400 text-black font-mono uppercase">
      Enter the Grid
    </Button>
  </div>
</section>
```

### Playful Bento
```tsx
<section className="p-8 bg-gradient-to-br from-purple-100 to-pink-100">
  <div className="grid grid-cols-4 grid-rows-3 gap-4 h-[80vh]">
    <div className="col-span-2 row-span-2 bg-yellow-300 rounded-3xl p-8">
      <h1 className="text-5xl font-bold">Learn Anything.</h1>
    </div>
    <div className="bg-blue-400 rounded-3xl p-6 flex items-center justify-center">
      <Sparkles className="w-16 h-16 text-white" />
    </div>
    <div className="row-span-2 bg-green-400 rounded-3xl p-6">
      <p className="text-2xl font-bold text-white">500K+ Students</p>
    </div>
    <div className="bg-pink-400 rounded-3xl" />
    <div className="col-span-2 bg-purple-400 rounded-3xl p-6">
      <Button size="lg" className="bg-white text-purple-600 rounded-full">
        Start Free Trial
      </Button>
    </div>
  </div>
</section>
```

---

## Color Palettes

### Neon Cyber
```css
:root {
  --background: oklch(10% 0.02 280);
  --foreground: oklch(95% 0.02 280);
  --cyan: oklch(80% 0.2 200);
  --magenta: oklch(70% 0.25 330);
  --yellow: oklch(90% 0.2 100);
  --green: oklch(80% 0.25 160);
}
```

### Vibrant Playful
```css
:root {
  --background: oklch(98% 0.01 280);
  --foreground: oklch(25% 0.02 280);
  --primary: oklch(65% 0.25 280);
  --secondary: oklch(75% 0.2 180);
  --accent-1: oklch(80% 0.2 60);
  --accent-2: oklch(70% 0.22 340);
}
```

### Bold Startup
```css
:root {
  --background: oklch(99% 0 0);
  --foreground: oklch(15% 0.02 250);
  --primary: oklch(55% 0.25 250);
  --secondary: oklch(65% 0.2 160);
  --accent: oklch(70% 0.22 30);
  --highlight: oklch(90% 0.15 95);
}
```

---

## Motion Patterns

### Glitch Effect
```tsx
const glitchVariants = {
  initial: { x: 0, y: 0 },
  glitch: {
    x: [0, -5, 5, -3, 0],
    y: [0, 3, -3, 2, 0],
    transition: { duration: 0.3 }
  }
}
```

### Bounce Entrance
```tsx
const bounceIn = {
  initial: { scale: 0, rotate: -180 },
  animate: {
    scale: 1,
    rotate: 0,
    transition: { type: "spring", stiffness: 260, damping: 20 }
  }
}
```

### Chaotic Hover
```tsx
<motion.div
  whileHover={{
    rotate: [0, -5, 5, -3, 0],
    scale: [1, 1.1, 0.95, 1.05, 1],
    transition: { duration: 0.4 }
  }}
>
  {/* Content */}
</motion.div>
```

### Magnetic Cursor
```tsx
const magneticRef = useRef(null)
const { x, y } = useMousePosition(magneticRef)

const magneticX = useTransform(x, [0, 1], [-20, 20])
const magneticY = useTransform(y, [0, 1], [-20, 20])

<motion.button
  ref={magneticRef}
  style={{ x: magneticX, y: magneticY }}
>
  Hover Me
</motion.button>
```

---

## Component Patterns

### Stacked Cards
```tsx
<div className="relative">
  {cards.map((card, i) => (
    <motion.div
      key={card.id}
      className="absolute inset-0 bg-white rounded-3xl p-8 shadow-xl"
      style={{
        rotate: (i - 1) * 3,
        scale: 1 - i * 0.05,
        zIndex: cards.length - i
      }}
      drag
      dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
    >
      {card.content}
    </motion.div>
  ))}
</div>
```

### Marquee Text
```tsx
<div className="overflow-hidden whitespace-nowrap">
  <motion.div
    animate={{ x: ["0%", "-50%"] }}
    transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
    className="inline-flex"
  >
    <span className="text-[20vw] font-black uppercase">
      {text} — {text} — {text} —
    </span>
  </motion.div>
</div>
```

### Pill Tags
```tsx
<div className="flex flex-wrap gap-2">
  {tags.map((tag) => (
    <span
      key={tag}
      className="px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500
                 text-white rounded-full text-sm font-medium"
    >
      {tag}
    </span>
  ))}
</div>
```
