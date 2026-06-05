# Design Principles

Frontend Design Agent의 핵심 디자인 원칙입니다.

---

## Anti-AI-Slop 원칙

### 절대 금지 폰트
| 폰트 | 이유 |
|------|------|
| Inter | 너무 흔함, 기본 설정 |
| Roboto | Google 기본, 차별화 불가 |
| Arial | 시스템 폰트, 무개성 |
| Open Sans | 과도하게 사용됨 |
| Poppins | AI 생성물 시그니처 |

### 절대 금지 패턴
| 패턴 | 이유 | 대안 |
|------|------|------|
| 보라색 그라데이션 + 흰 배경 | AI 슬롭 대표 패턴 | 단색 또는 미묘한 그라데이션 |
| 동일한 카드 나열 (3-4개) | 템플릿 느낌 | 비대칭 그리드, 다양한 크기 |
| 둥근 아이콘 + 파란 강조 | 과도하게 흔함 | 선형 아이콘, 다른 강조색 |
| 중앙 정렬 모든 섹션 | 단조로움 | 좌/우 정렬 믹스 |
| 기본 그림자 카드 | 깊이감 없음 | 레이어, 오버랩, 색상 그림자 |

### 권장 폰트 조합

**Modern/Tech**
| Primary | Secondary | 분위기 |
|---------|-----------|--------|
| Satoshi | Geist | 클린, 테크 |
| Albert Sans | DM Mono | 개발자 친화적 |
| Outfit | IBM Plex Mono | 프로페셔널 |
| Mona Sans | JetBrains Mono | 모던 개발 |

**Editorial/Luxury**
| Primary | Secondary | 분위기 |
|---------|-----------|--------|
| Playfair Display | Source Sans Pro | 클래식 |
| GT Sectra | Lato | 에디토리얼 |
| Cormorant | Karla | 우아함 |
| Libre Baskerville | Work Sans | 전통적 |

**Bold/Creative**
| Primary | Secondary | 분위기 |
|---------|-----------|--------|
| Clash Display | Sora | 대담함 |
| Basement Grotesque | Space Grotesk | 실험적 |
| Cabinet Grotesk | Manrope | 현대적 대담 |
| Unbounded | Work Sans | 유니크 |

---

## Context-Driven Aesthetics

### 분석 체크리스트
1. **프로젝트 목적**
   - B2B vs B2C
   - 정보 전달 vs 전환 유도
   - 브랜딩 vs 기능

2. **타겟 유저**
   - 연령대
   - 기술 친숙도
   - 문화적 배경

3. **브랜드 톤**
   - 공식적 vs 캐주얼
   - 혁신적 vs 신뢰할 수 있는
   - 럭셔리 vs 접근 가능한

### 컨텍스트 → 템플릿 매핑

| 컨텍스트 | 추천 템플릿 | 이유 |
|----------|------------|------|
| B2B SaaS | Barely-There Minimal | 전문성, 명확함 |
| 소비자 앱 | Liquid Glass | 친근함, 세련됨 |
| 미디어/블로그 | Editorial Magazine | 가독성, 몰입 |
| 크리에이티브 | Anti-Design Chaos | 독창성, 차별화 |
| 게임/엔터 | Retro-Futuristic | 재미, 흥미 |
| 웰니스 | Organic Natural | 평화, 자연 |
| 럭셔리 | Luxury Refined | 고급스러움 |
| 교육 | Playful Rounded | 친근함, 접근성 |
| 스타트업 | Grade-School Bold | 신뢰, 단순함 |
| 개발자 도구 | Tech Documentation | 명확함, 효율 |

---

## 접근성 필수 규칙

### Icon 버튼
```tsx
// ✅ Good
<button aria-label="메뉴 닫기">
  <X className="h-5 w-5" />
</button>

// ❌ Bad
<button>
  <X className="h-5 w-5" />
</button>
```

### 이미지
```tsx
// ✅ Good
<Image
  src="/product.jpg"
  alt="검은색 무선 이어폰 제품 이미지"
/>

// ❌ Bad
<Image src="/product.jpg" alt="" />
<Image src="/product.jpg" alt="image" />
```

### Focus 스타일
```tsx
// ✅ Good - focus-visible 포함
<button className="outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2">
  Click me
</button>

// ❌ Bad - outline-none만 사용
<button className="outline-none">
  Click me
</button>
```

### Form Elements
```tsx
// ✅ Good
<div>
  <label htmlFor="email" className="sr-only">이메일</label>
  <input id="email" type="email" placeholder="이메일 입력" />
</div>

// ❌ Bad
<input type="email" placeholder="이메일" />
```

### Color Contrast
- 일반 텍스트: 최소 4.5:1 대비율
- 큰 텍스트 (18px+ bold): 최소 3:1 대비율
- UI 컴포넌트: 최소 3:1 대비율

---

## 애니메이션 규칙

### prefers-reduced-motion 존중
```tsx
import { useReducedMotion } from 'framer-motion'

function AnimatedComponent() {
  const shouldReduce = useReducedMotion()

  return (
    <motion.div
      animate={{
        scale: shouldReduce ? 1 : 1.05,
        y: shouldReduce ? 0 : 10
      }}
      transition={{
        duration: shouldReduce ? 0 : 0.3
      }}
    />
  )
}
```

### GPU 가속 속성만 사용
```tsx
// ✅ Good: GPU 가속 (transform, opacity)
animate={{
  scale: 1.1,
  opacity: 1,
  x: 10,
  y: 10,
  rotate: 5
}}

// ❌ Bad: 레이아웃 재계산 유발
animate={{
  width: 200,
  height: 200,
  padding: 20,
  margin: 10
}}
```

### 애니메이션 성능 체크리스트
- [ ] `transform` 또는 `opacity`만 애니메이션
- [ ] `will-change` 과도하게 사용하지 않음
- [ ] 60fps 유지 확인
- [ ] `prefers-reduced-motion` 존중
- [ ] 무한 반복 애니메이션 최소화

---

## Anti-Patterns 체크리스트

| 패턴 | 문제 | 해결 |
|------|------|------|
| `outline-none` 단독 | 키보드 접근성 파괴 | `focus-visible:ring-2` 추가 |
| `div` + `onClick` | 의미론적 HTML 위반 | `button` 또는 `a` 사용 |
| 아이콘만 있는 버튼 | 스크린리더 접근 불가 | `aria-label` 추가 |
| `transition: all` | 성능 저하 | 특정 속성만 지정 |
| 50+ 리스트 아이템 | 렌더링 병목 | 가상화 또는 `content-visibility` |
| 이미지 alt="" | 접근성 위반 | 의미 있는 설명 추가 |
| z-index 남용 | 레이어 충돌 | 체계적인 z-index 스케일 |
| !important 남용 | 유지보수 어려움 | 명시도 관리 |

---

## 디자인 다양성 보장

### Template Rotation
매 요청 시 이전 3개 프로젝트와 다른 템플릿 선택

### Color Palette Shuffle
- 같은 템플릿이라도 accent color 변경
- Primary hue +/-30도 범위 변형
- Dark/Light mode 기본값 교대

### Layout Variation
```
Hero Section Options:
├── Centered Text
├── Split Layout (Left Text + Right Image)
├── Split Layout (Left Image + Right Text)
├── Full-Bleed Background
├── Asymmetric Grid
└── Bento Style
```

### Effect Combination Pool
| 요청 횟수 | 배경 효과 | 마이크로인터랙션 | 스크롤 효과 |
|-----------|----------|-----------------|------------|
| 1회 | Gradient Mesh | Scale on Hover | Fade In |
| 2회 | Noise Texture | Glow on Hover | Slide Up |
| 3회 | Glassmorphism | Lift on Hover | Parallax |
| 4회 | Geometric Pattern | Ripple on Click | Stagger |
