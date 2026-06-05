---
name: "Phase 7: Responsive Validation"
phase_id: 7
phase_name: "Responsive Validation"
description: "Verify responsive behavior across breakpoints and generate final report"

dependencies:
  - phase_id: 6
    artifacts: [verification_report.json]
    validation: verification_complete

inputs:
  required: [components, breakpoints]
  optional: [figma_responsive_variants]

outputs:
  artifacts: [responsive_report.json, final_report.md, breakpoint_screenshots/*]
  state_updates: [artifacts.phase_7.responsive_report, pipeline.phase_status.completed]

validation:
  success_criteria:
    - All breakpoints tested
    - No layout breaks
    - Final report generated
  quality_gates:
    - Touch targets >= 44px on mobile
    - Text readable at all sizes
    - No horizontal scroll

rollback:
  on_failure: generate_partial_report
  cleanup: [breakpoint_screenshots/*]
  can_resume: true

mcp_calls:
  estimated: 0
  tools: []
---

# Phase 7: Responsive Validation

> 브레이크포인트별 반응형 검증

---

## 실행 조건

- Phase 6 (Pixel-Perfect) 완료
- 데스크톱 버전 검증 완료

---

## Step 7-1: Tailwind 브레이크포인트

### 기본 브레이크포인트

| Prefix | Width | 용도 |
|--------|-------|------|
| `sm` | 640px | Mobile landscape |
| `md` | 768px | Tablet |
| `lg` | 1024px | Desktop |
| `xl` | 1280px | Large desktop |
| `2xl` | 1536px | Extra large |

### 모바일 퍼스트 전략

```tsx
// Tailwind은 모바일 퍼스트
// 기본 = 모바일, 브레이크포인트 = 더 큰 화면

<div className="
  flex flex-col          // 모바일: 세로 배치
  md:flex-row            // 태블릿+: 가로 배치
  gap-4                  // 모바일: gap-4
  lg:gap-8               // 데스크톱: gap-8
">
```

---

## Step 7-2: 반응형 패턴

### Grid 레이아웃

```tsx
// 1 → 2 → 3 컬럼
<div className="
  grid
  grid-cols-1           // 모바일: 1열
  md:grid-cols-2        // 태블릿: 2열
  lg:grid-cols-3        // 데스크톱: 3열
  gap-6
">
```

### Flexbox 레이아웃

```tsx
// 세로 → 가로
<div className="
  flex
  flex-col              // 모바일: 세로
  lg:flex-row           // 데스크톱: 가로
  items-center
  gap-8
">
```

### 숨김/표시

```tsx
// 모바일에서 숨김
<div className="hidden md:block">Desktop only</div>

// 데스크톱에서 숨김
<div className="md:hidden">Mobile only</div>
```

### 텍스트 크기

```tsx
<h1 className="
  text-3xl              // 모바일: 30px
  md:text-4xl           // 태블릿: 36px
  lg:text-5xl           // 데스크톱: 48px
  font-bold
">
```

### 간격

```tsx
<section className="
  px-4                  // 모바일: 16px
  md:px-8               // 태블릿: 32px
  lg:px-16              // 데스크톱: 64px
  py-12                 // 모바일: 48px
  lg:py-24              // 데스크톱: 96px
">
```

---

## Step 7-3: 검증 체크리스트

### Mobile (< 640px)

```markdown
## Mobile Checklist

### Layout
- [ ] 단일 컬럼 레이아웃
- [ ] 전체 너비 사용
- [ ] 적절한 좌우 패딩 (16-20px)

### Typography
- [ ] 제목 크기 적절 (24-32px)
- [ ] 본문 가독성 (16px+)
- [ ] 줄 간격 충분

### Navigation
- [ ] 햄버거 메뉴 표시
- [ ] 터치 영역 44px 이상
- [ ] 메뉴 전체 화면 or 슬라이드

### Images
- [ ] 가로 스크롤 없음
- [ ] 적절한 aspect ratio
- [ ] 로딩 최적화

### Forms
- [ ] 입력 필드 전체 너비
- [ ] 키보드 접근성
- [ ] 적절한 폰트 크기 (16px+)

### Interactions
- [ ] 터치 타겟 44x44px 이상
- [ ] 호버 상태 제거/대체
- [ ] 스와이프 제스처
```

### Tablet (768px - 1023px)

```markdown
## Tablet Checklist

### Layout
- [ ] 2컬럼 그리드 적용
- [ ] 사이드바 접힘/열림
- [ ] 적절한 좌우 패딩

### Navigation
- [ ] 상단 네비게이션 유지
- [ ] 드롭다운 동작

### Content
- [ ] 카드 2열 배치
- [ ] 이미지 적절한 크기
- [ ] 텍스트 줄바꿈 확인
```

### Desktop (1024px+)

```markdown
## Desktop Checklist

### Layout
- [ ] 3-4컬럼 그리드
- [ ] 최대 너비 제한
- [ ] 중앙 정렬

### Navigation
- [ ] 전체 메뉴 표시
- [ ] 드롭다운 호버 동작

### Interactions
- [ ] 호버 상태 표시
- [ ] 커서 변경
- [ ] 애니메이션 동작
```

---

## Step 7-4: 일반적인 반응형 이슈

### 이슈 1: 가로 스크롤

```tsx
// ❌ 문제
<div className="w-[500px]">Fixed width</div>

// ✅ 해결
<div className="w-full max-w-[500px]">Responsive</div>
```

### 이슈 2: 이미지 오버플로우

```tsx
// ❌ 문제
<img src="..." width="800" />

// ✅ 해결
<Image
  src="..."
  width={800}
  height={600}
  className="w-full h-auto"
/>
```

### 이슈 3: 텍스트 줄바꿈

```tsx
// ❌ 문제
<h1 className="whitespace-nowrap">Very Long Title Here</h1>

// ✅ 해결
<h1 className="break-words">Very Long Title Here</h1>
```

### 이슈 4: 버튼 크기

```tsx
// ❌ 문제 (터치 타겟 너무 작음)
<button className="px-2 py-1 text-sm">Click</button>

// ✅ 해결 (최소 44x44px)
<button className="px-4 py-3 text-base min-h-[44px]">Click</button>
```

---

## Step 7-5: 테스트 도구

### 브라우저 DevTools

```
Chrome DevTools:
1. F12 → Toggle Device Toolbar (Ctrl+Shift+M)
2. 프리셋 디바이스 선택 또는 커스텀 크기

테스트 뷰포트:
- iPhone SE: 375 x 667
- iPhone 12 Pro: 390 x 844
- iPad: 768 x 1024
- Desktop: 1440 x 900
```

### Tailwind 디버그

```tsx
// 현재 브레이크포인트 표시 (개발용)
<div className="fixed bottom-4 right-4 bg-black text-white px-2 py-1 text-xs rounded z-50">
  <span className="sm:hidden">XS</span>
  <span className="hidden sm:inline md:hidden">SM</span>
  <span className="hidden md:inline lg:hidden">MD</span>
  <span className="hidden lg:inline xl:hidden">LG</span>
  <span className="hidden xl:inline 2xl:hidden">XL</span>
  <span className="hidden 2xl:inline">2XL</span>
</div>
```

---

## Step 7-6: 컴포넌트별 반응형 패턴

### Hero Section

```tsx
<section className="
  px-4 py-16
  md:px-8 md:py-24
  lg:px-16 lg:py-32
">
  <div className="
    flex flex-col
    lg:flex-row lg:items-center lg:gap-16
    max-w-7xl mx-auto
  ">
    <div className="
      flex-1
      text-center lg:text-left
      mb-8 lg:mb-0
    ">
      <h1 className="
        text-3xl md:text-4xl lg:text-5xl
        font-bold mb-4
      ">
        Title
      </h1>
    </div>
    <div className="flex-1">
      {/* Image */}
    </div>
  </div>
</section>
```

### Feature Grid

```tsx
<div className="
  grid
  grid-cols-1
  md:grid-cols-2
  lg:grid-cols-3
  gap-4 md:gap-6 lg:gap-8
">
  {features.map((feature) => (
    <FeatureCard key={feature.id} {...feature} />
  ))}
</div>
```

### Navigation

```tsx
<nav className="flex items-center justify-between px-4 py-3">
  <Logo />

  {/* Desktop Menu */}
  <div className="hidden lg:flex items-center gap-8">
    {navItems.map((item) => (
      <NavLink key={item.href} {...item} />
    ))}
  </div>

  {/* Mobile Menu Button */}
  <button className="lg:hidden">
    <Menu className="w-6 h-6" />
  </button>
</nav>
```

---

## 산출물

```markdown
# Responsive Validation Report

## Test Summary
| Breakpoint | Status | Issues |
|------------|--------|--------|
| Mobile (375px) | ✅ Pass | 0 |
| Mobile (414px) | ✅ Pass | 0 |
| Tablet (768px) | ✅ Pass | 1 minor |
| Desktop (1024px) | ✅ Pass | 0 |
| Desktop (1440px) | ✅ Pass | 0 |

## Component Results

### HeroSection
- Mobile: ✅
- Tablet: ✅
- Desktop: ✅

### FeatureGrid
- Mobile: ✅ (1 column)
- Tablet: ✅ (2 columns)
- Desktop: ✅ (3 columns)

### Navigation
- Mobile: ✅ (hamburger menu)
- Tablet: ✅ (hamburger menu)
- Desktop: ✅ (full menu)

## Issues Found
1. Tablet: Card text overflow at 768px
   - **Fix**: Added `break-words` class

## Final Status: APPROVED ✅
```

---

## 완료

모든 Phase 완료!

```markdown
## Conversion Complete

### Summary
- Total Phases: 8 (0-7)
- Components Created: 8
- Assets Processed: 12
- Pixel-Perfect Score: 97.5%
- Responsive Score: 100%

### Files Created
- 8 component files
- 1 tailwind.config.ts update
- 1 globals.css update
- 12 asset files

### Next Steps
1. Code review
2. Accessibility audit
3. Performance testing
4. Deploy to staging
```
