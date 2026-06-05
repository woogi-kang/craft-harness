---
name: "Tailwind Mapping"
description: "Figma properties to Tailwind CSS classes mapping"
---

# Skill: Tailwind Mapping

> Figma 속성을 Tailwind CSS 클래스로 정확하게 매핑

---

## 개요

이 스킬은 Figma 디자인 속성을 Tailwind CSS 유틸리티 클래스로 1:1 변환합니다.
Pixel-Perfect 변환을 위한 정확한 매핑 테이블을 제공합니다.

---

## 간격 매핑 (Spacing)

### Padding & Margin

| Figma (px) | Tailwind | rem | 사용 예 |
|------------|----------|-----|---------|
| 0 | 0 | 0 | `p-0`, `m-0` |
| 1 | px | 1px | `p-px` |
| 2 | 0.5 | 0.125rem | `p-0.5` |
| 4 | 1 | 0.25rem | `p-1`, `m-1` |
| 6 | 1.5 | 0.375rem | `p-1.5` |
| 8 | 2 | 0.5rem | `p-2`, `m-2` |
| 10 | 2.5 | 0.625rem | `p-2.5` |
| 12 | 3 | 0.75rem | `p-3`, `m-3` |
| 14 | 3.5 | 0.875rem | `p-3.5` |
| 16 | 4 | 1rem | `p-4`, `m-4` |
| 20 | 5 | 1.25rem | `p-5`, `m-5` |
| 24 | 6 | 1.5rem | `p-6`, `m-6` |
| 28 | 7 | 1.75rem | `p-7` |
| 32 | 8 | 2rem | `p-8`, `m-8` |
| 36 | 9 | 2.25rem | `p-9` |
| 40 | 10 | 2.5rem | `p-10` |
| 44 | 11 | 2.75rem | `p-11` |
| 48 | 12 | 3rem | `p-12` |
| 56 | 14 | 3.5rem | `p-14` |
| 64 | 16 | 4rem | `p-16` |
| 80 | 20 | 5rem | `p-20` |
| 96 | 24 | 6rem | `p-24` |
| 112 | 28 | 7rem | `p-28` |
| 128 | 32 | 8rem | `p-32` |

### Gap

| Figma (px) | Tailwind |
|------------|----------|
| 4 | `gap-1` |
| 8 | `gap-2` |
| 12 | `gap-3` |
| 16 | `gap-4` |
| 24 | `gap-6` |
| 32 | `gap-8` |
| 48 | `gap-12` |
| 64 | `gap-16` |

---

## 타이포그래피 매핑

### Font Size

| Figma (px) | Tailwind | rem | Line Height |
|------------|----------|-----|-------------|
| 12 | text-xs | 0.75rem | 1rem |
| 14 | text-sm | 0.875rem | 1.25rem |
| 16 | text-base | 1rem | 1.5rem |
| 18 | text-lg | 1.125rem | 1.75rem |
| 20 | text-xl | 1.25rem | 1.75rem |
| 24 | text-2xl | 1.5rem | 2rem |
| 30 | text-3xl | 1.875rem | 2.25rem |
| 36 | text-4xl | 2.25rem | 2.5rem |
| 48 | text-5xl | 3rem | 1 |
| 60 | text-6xl | 3.75rem | 1 |
| 72 | text-7xl | 4.5rem | 1 |
| 96 | text-8xl | 6rem | 1 |
| 128 | text-9xl | 8rem | 1 |

### Font Weight

| Figma | Tailwind |
|-------|----------|
| Thin (100) | font-thin |
| Extra Light (200) | font-extralight |
| Light (300) | font-light |
| Regular (400) | font-normal |
| Medium (500) | font-medium |
| Semi Bold (600) | font-semibold |
| Bold (700) | font-bold |
| Extra Bold (800) | font-extrabold |
| Black (900) | font-black |

### Line Height

| Figma | Tailwind | 값 |
|-------|----------|-----|
| Auto | leading-normal | 1.5 |
| 100% | leading-none | 1 |
| 125% | leading-tight | 1.25 |
| 137.5% | leading-snug | 1.375 |
| 150% | leading-normal | 1.5 |
| 162.5% | leading-relaxed | 1.625 |
| 200% | leading-loose | 2 |

### Letter Spacing

| Figma | Tailwind | 값 |
|-------|----------|-----|
| -0.05em | tracking-tighter | -0.05em |
| -0.025em | tracking-tight | -0.025em |
| 0 | tracking-normal | 0 |
| 0.025em | tracking-wide | 0.025em |
| 0.05em | tracking-wider | 0.05em |
| 0.1em | tracking-widest | 0.1em |

---

## 색상 매핑

### Figma → Tailwind 변환

```typescript
// 변환 함수
function figmaColorToTailwind(hex: string): string {
  const colorMap: Record<string, string> = {
    '#FFFFFF': 'white',
    '#000000': 'black',
    '#F9FAFB': 'gray-50',
    '#F3F4F6': 'gray-100',
    '#E5E7EB': 'gray-200',
    '#D1D5DB': 'gray-300',
    '#9CA3AF': 'gray-400',
    '#6B7280': 'gray-500',
    '#4B5563': 'gray-600',
    '#374151': 'gray-700',
    '#1F2937': 'gray-800',
    '#111827': 'gray-900',
    '#3B82F6': 'blue-500',
    '#2563EB': 'blue-600',
    '#EF4444': 'red-500',
    '#22C55E': 'green-500',
    '#F59E0B': 'amber-500',
  };

  return colorMap[hex.toUpperCase()] || `[${hex}]`;
}
```

### 권장: CSS 변수 사용

```tsx
// 하드코딩 대신
<div className="bg-[#3B82F6]">  // ❌ 비권장

// CSS 변수 사용
<div className="bg-primary">    // ✅ 권장
```

---

## Border & Shadow 매핑

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

### Border Width

| Figma (px) | Tailwind |
|------------|----------|
| 0 | border-0 |
| 1 | border |
| 2 | border-2 |
| 4 | border-4 |
| 8 | border-8 |

### Box Shadow

| Figma Effect | Tailwind |
|--------------|----------|
| 0 1px 2px rgba(0,0,0,0.05) | shadow-sm |
| 0 1px 3px rgba(0,0,0,0.1) | shadow |
| 0 4px 6px rgba(0,0,0,0.1) | shadow-md |
| 0 10px 15px rgba(0,0,0,0.1) | shadow-lg |
| 0 20px 25px rgba(0,0,0,0.1) | shadow-xl |
| 0 25px 50px rgba(0,0,0,0.25) | shadow-2xl |
| inset 0 2px 4px rgba(0,0,0,0.05) | shadow-inner |
| none | shadow-none |

---

## 레이아웃 매핑

### Flexbox

| Figma Auto Layout | Tailwind |
|-------------------|----------|
| Horizontal | flex flex-row |
| Vertical | flex flex-col |
| Wrap | flex flex-wrap |
| Space Between | justify-between |
| Center | justify-center items-center |
| Start | justify-start items-start |
| End | justify-end items-end |

### Grid

| Figma 패턴 | Tailwind |
|------------|----------|
| 2열 | grid grid-cols-2 |
| 3열 | grid grid-cols-3 |
| 4열 | grid grid-cols-4 |
| 반응형 | grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 |

### Size

| Figma | Tailwind |
|-------|----------|
| Fill (100%) | w-full, h-full |
| Hug | w-fit, h-fit |
| Fixed (px) | w-[{n}px], h-[{n}px] |
| Min | min-w-{size}, min-h-{size} |
| Max | max-w-{size}, max-h-{size} |

---

## 매핑 함수

```typescript
// 완전한 변환 함수
function figmaToTailwind(figmaNode: FigmaNode): string {
  const classes: string[] = [];

  // Layout
  if (figmaNode.layoutMode === 'HORIZONTAL') {
    classes.push('flex', 'flex-row');
  } else if (figmaNode.layoutMode === 'VERTICAL') {
    classes.push('flex', 'flex-col');
  }

  // Gap
  if (figmaNode.itemSpacing) {
    classes.push(spacingToTailwind('gap', figmaNode.itemSpacing));
  }

  // Padding
  if (figmaNode.paddingTop) {
    classes.push(spacingToTailwind('pt', figmaNode.paddingTop));
  }
  if (figmaNode.paddingBottom) {
    classes.push(spacingToTailwind('pb', figmaNode.paddingBottom));
  }
  if (figmaNode.paddingLeft) {
    classes.push(spacingToTailwind('pl', figmaNode.paddingLeft));
  }
  if (figmaNode.paddingRight) {
    classes.push(spacingToTailwind('pr', figmaNode.paddingRight));
  }

  // Border Radius
  if (figmaNode.cornerRadius) {
    classes.push(radiusToTailwind(figmaNode.cornerRadius));
  }

  // Background
  if (figmaNode.backgroundColor) {
    classes.push(`bg-${colorToTailwind(figmaNode.backgroundColor)}`);
  }

  return classes.join(' ');
}

function spacingToTailwind(prefix: string, px: number): string {
  const map: Record<number, string> = {
    0: '0', 1: 'px', 2: '0.5', 4: '1', 6: '1.5', 8: '2',
    10: '2.5', 12: '3', 14: '3.5', 16: '4', 20: '5',
    24: '6', 28: '7', 32: '8', 36: '9', 40: '10',
    44: '11', 48: '12', 56: '14', 64: '16', 80: '20',
    96: '24', 112: '28', 128: '32', 144: '36', 160: '40',
    176: '44', 192: '48', 224: '56', 256: '64', 288: '72',
    320: '80', 384: '96',
  };
  return `${prefix}-${map[px] || `[${px}px]`}`;
}

function radiusToTailwind(px: number): string {
  const map: Record<number, string> = {
    0: 'rounded-none', 2: 'rounded-sm', 4: 'rounded',
    6: 'rounded-md', 8: 'rounded-lg', 12: 'rounded-xl',
    16: 'rounded-2xl', 24: 'rounded-3xl', 9999: 'rounded-full',
  };
  return map[px] || `rounded-[${px}px]`;
}
```

---

## 검증 체크리스트

```markdown
## Tailwind Mapping Verification

### Spacing
- [ ] 모든 padding 값 정확히 변환
- [ ] 모든 margin 값 정확히 변환
- [ ] gap 값 정확히 변환

### Typography
- [ ] font-size 매핑 확인
- [ ] font-weight 매핑 확인
- [ ] line-height 매핑 확인

### Colors
- [ ] 배경색 CSS 변수 사용
- [ ] 텍스트색 CSS 변수 사용
- [ ] 하드코딩 색상 없음

### Layout
- [ ] Flexbox 방향 정확
- [ ] 정렬 속성 정확
- [ ] Grid 컬럼 수 정확

### Border
- [ ] radius 값 정확
- [ ] width 값 정확
- [ ] color CSS 변수 사용
```
