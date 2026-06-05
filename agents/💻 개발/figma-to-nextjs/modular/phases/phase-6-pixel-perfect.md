---
name: "Phase 6: Pixel-Perfect Verification"
phase_id: 6
phase_name: "Pixel-Perfect Verification"
description: "Compare rendered output with Figma design for visual accuracy"

dependencies:
  - phase_id: 4
    artifacts: [components/*.tsx]
    validation: components_generated
  - phase_id: 5
    artifacts: [asset_manifest.json]
    validation: assets_processed

inputs:
  required: [generated_components, figma_screenshots]
  optional: [diff_threshold]

outputs:
  artifacts: [verification_report.json, diff_images/*, fix_recommendations.md]
  state_updates: [artifacts.phase_6.verification_report]

validation:
  success_criteria:
    - All components rendered
    - Diff calculated for each component
    - Report generated
  quality_gates:
    - Visual diff under threshold (default 5%)
    - Critical elements match exactly

rollback:
  on_failure: generate_partial_report
  cleanup: [diff_images/*]
  can_resume: true

mcp_calls:
  estimated: 2-3
  tools: [get_screenshot]
---

# Phase 6: Pixel-Perfect Verification

> Figma 원본과 1:1 정확도 검증

---

## 실행 조건

- Phase 5 (Asset Process) 완료
- 모든 컴포넌트 생성 완료

---

## Step 6-1: 스크린샷 비교

### MCP 호출

```typescript
// Figma 원본 스크린샷
get_screenshot({ nodeId: "123:456" })
→ Base64 이미지
```

### 비교 방법

1. Figma 스크린샷 저장
2. 브라우저에서 동일 뷰포트 캡처
3. 오버레이 비교

---

## Step 6-2: 검증 항목

### Layout 검증

| 요소 | Figma | 코드 | 차이 | 상태 |
|------|-------|------|------|------|
| Container Width | 1200px | max-w-7xl (1280px) | +80px | ⚠️ |
| Section Padding | 64px | py-16 (64px) | 0 | ✅ |
| Content Gap | 32px | gap-8 (32px) | 0 | ✅ |
| Card Width | 380px | w-full md:w-1/3 | 반응형 | ✅ |

### Typography 검증

| 요소 | Figma | 코드 | 상태 |
|------|-------|------|------|
| H1 Size | 48px | text-5xl (48px) | ✅ |
| H1 Weight | Bold (700) | font-bold | ✅ |
| H1 Line Height | 56px | leading-tight (1.25) | ✅ |
| Body Size | 16px | text-base (16px) | ✅ |
| Body Line Height | 24px | leading-relaxed (1.625) | ⚠️ |

### Color 검증

| 요소 | Figma | 코드 | 상태 |
|------|-------|------|------|
| Background | #FFFFFF | bg-white | ✅ |
| Primary | #3B82F6 | bg-primary | ✅ |
| Text Primary | #1F2937 | text-gray-800 | ✅ |
| Text Secondary | #6B7280 | text-gray-500 | ✅ |
| Border | #E5E7EB | border-gray-200 | ✅ |

### Spacing 검증

| 요소 | Figma | 코드 | 상태 |
|------|-------|------|------|
| Section Top | 64px | pt-16 | ✅ |
| Section Bottom | 64px | pb-16 | ✅ |
| Card Padding | 24px | p-6 | ✅ |
| Button Padding X | 24px | px-6 | ✅ |
| Button Padding Y | 12px | py-3 | ✅ |
| Element Gap | 16px | gap-4 | ✅ |

### Border & Shadow 검증

| 요소 | Figma | 코드 | 상태 |
|------|-------|------|------|
| Card Radius | 12px | rounded-xl | ✅ |
| Button Radius | 8px | rounded-lg | ✅ |
| Input Radius | 6px | rounded-md | ✅ |
| Card Shadow | 0 4px 6px rgba(0,0,0,0.1) | shadow-md | ✅ |

---

## Step 6-3: Figma px → Tailwind 매핑

### 간격 (Spacing)

| Figma (px) | Tailwind | rem |
|------------|----------|-----|
| 4 | 1 | 0.25 |
| 8 | 2 | 0.5 |
| 12 | 3 | 0.75 |
| 16 | 4 | 1 |
| 20 | 5 | 1.25 |
| 24 | 6 | 1.5 |
| 32 | 8 | 2 |
| 40 | 10 | 2.5 |
| 48 | 12 | 3 |
| 64 | 16 | 4 |
| 80 | 20 | 5 |
| 96 | 24 | 6 |

### 폰트 크기

| Figma (px) | Tailwind | rem |
|------------|----------|-----|
| 12 | text-xs | 0.75 |
| 14 | text-sm | 0.875 |
| 16 | text-base | 1 |
| 18 | text-lg | 1.125 |
| 20 | text-xl | 1.25 |
| 24 | text-2xl | 1.5 |
| 30 | text-3xl | 1.875 |
| 36 | text-4xl | 2.25 |
| 48 | text-5xl | 3 |
| 60 | text-6xl | 3.75 |

### Border Radius

| Figma (px) | Tailwind |
|------------|----------|
| 0 | rounded-none |
| 2 | rounded-sm |
| 4 | rounded |
| 6 | rounded-md |
| 8 | rounded-lg |
| 12 | rounded-xl |
| 16 | rounded-2xl |
| 24 | rounded-3xl |
| 9999 | rounded-full |

---

## Step 6-4: 검증 리포트 템플릿

```markdown
# Pixel-Perfect Verification Report

## Component: HeroSection

### Screenshot Comparison
![Figma](./figma-hero.png) vs ![Code](./code-hero.png)

### Layout Score: 95%
| Element | Figma | Code | Status |
|---------|-------|------|--------|
| Width | 1200px | 1280px | ⚠️ |
| Padding | 64px | 64px | ✅ |
| Gap | 32px | 32px | ✅ |

### Typography Score: 100%
| Element | Figma | Code | Status |
|---------|-------|------|--------|
| H1 | 48px Bold | text-5xl font-bold | ✅ |
| Body | 16px Regular | text-base | ✅ |

### Color Score: 100%
| Element | Figma | Code | Status |
|---------|-------|------|--------|
| Background | #FFFFFF | bg-white | ✅ |
| Primary | #3B82F6 | bg-primary | ✅ |

### Spacing Score: 100%
| Element | Figma | Code | Status |
|---------|-------|------|--------|
| Section Padding | 64px | py-16 | ✅ |
| Content Gap | 32px | gap-8 | ✅ |

### Overall Score: 98.75%

### Issues Found
1. Container width difference (1200px vs 1280px)
   - **Impact**: Minor
   - **Fix**: Use `max-w-[1200px]` instead of `max-w-7xl`

### Recommendations
- [ ] Adjust container max-width
- [ ] Verify on multiple screen sizes
```

---

## Step 6-5: 자동 검증 체크리스트

```markdown
## Verification Checklist

### Structure
- [ ] All sections present
- [ ] Correct nesting hierarchy
- [ ] Semantic HTML used

### Typography
- [ ] Font family matches
- [ ] Font sizes match
- [ ] Font weights match
- [ ] Line heights match
- [ ] Letter spacing matches

### Colors
- [ ] Background colors match
- [ ] Text colors match
- [ ] Border colors match
- [ ] Accent colors match

### Spacing
- [ ] Margins match
- [ ] Paddings match
- [ ] Gaps match

### Components
- [ ] Button styles match
- [ ] Card styles match
- [ ] Input styles match

### Images
- [ ] Correct aspect ratios
- [ ] Proper sizing
- [ ] Alt text provided

### Responsive
- [ ] Mobile layout correct
- [ ] Tablet layout correct
- [ ] Desktop layout correct
```

---

## Step 6-6: 수정 사항 적용

### 우선순위 분류

| 우선순위 | 기준 | 액션 |
|---------|------|------|
| **Critical** | 레이아웃 깨짐 | 즉시 수정 |
| **High** | 5px 이상 차이 | 수정 권장 |
| **Medium** | 2-4px 차이 | 가능하면 수정 |
| **Low** | 1px 차이 | 무시 가능 |

### 수정 예시

```tsx
// Before: max-w-7xl (1280px)
<div className="max-w-7xl mx-auto">

// After: custom max-width (1200px)
<div className="max-w-[1200px] mx-auto">
```

---

## 산출물

```markdown
# Final Verification Report

## Summary
- Components Verified: 8
- Overall Score: 97.5%
- Critical Issues: 0
- Minor Issues: 3

## Component Scores
| Component | Score | Issues |
|-----------|-------|--------|
| HeroSection | 98% | 1 |
| FeatureCard | 100% | 0 |
| CTASection | 95% | 2 |
| Footer | 98% | 0 |

## Issues Summary
1. HeroSection: Container width (Minor)
2. CTASection: Button padding (Minor)
3. CTASection: Text line-height (Minor)

## Fixes Applied
- [x] Container width adjusted
- [x] Button padding fixed
- [ ] Line-height pending

## Final Status: APPROVED ✅
```

---

## 다음 단계

Phase 6 완료 후 → **Phase 7: Responsive Validation** 진행
