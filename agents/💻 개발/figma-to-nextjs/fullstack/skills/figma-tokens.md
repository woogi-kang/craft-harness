---
name: "Figma Tokens"
description: "Figma design token extraction and CSS variable conversion"
---

# Skill: Figma Tokens

> Figma 디자인 토큰 추출 및 변환 스킬

---

## 개요

이 스킬은 Figma의 디자인 토큰(Variables)을 추출하여 CSS 변수와 Tailwind 설정으로 변환합니다.

---

## 토큰 타입

| Type | Figma | CSS Variable | Tailwind |
|------|-------|--------------|----------|
| COLOR | `#3B82F6` | `--color-primary` | `colors.primary` |
| FLOAT | `16` | `--spacing-4` | `spacing.4` |
| STRING | `Inter` | `--font-sans` | `fontFamily.sans` |
| BOOLEAN | `true` | - | - |
| ALIAS | `{colors.primary}` | `var(--color-primary)` | 참조 |

---

## 추출 워크플로우

### Step 1: 변수 정의 가져오기

```typescript
// MCP 호출
get_variable_defs({
  fileKey: "ABC123"
})
```

### Step 2: 토큰 분류

```typescript
interface TokenCollection {
  colors: ColorToken[];
  spacing: SpacingToken[];
  typography: TypographyToken[];
  radius: RadiusToken[];
  shadows: ShadowToken[];
}
```

### Step 3: CSS 변수 생성

```css
/* src/styles/variables.css */
:root {
  /* Colors */
  --color-primary: #3B82F6;
  --color-primary-foreground: #FFFFFF;
  --color-secondary: #6B7280;
  --color-background: #FFFFFF;
  --color-foreground: #1F2937;
  --color-muted: #F3F4F6;
  --color-muted-foreground: #6B7280;
  --color-border: #E5E7EB;

  /* Spacing */
  --spacing-1: 0.25rem;
  --spacing-2: 0.5rem;
  --spacing-3: 0.75rem;
  --spacing-4: 1rem;
  --spacing-5: 1.25rem;
  --spacing-6: 1.5rem;
  --spacing-8: 2rem;
  --spacing-10: 2.5rem;
  --spacing-12: 3rem;
  --spacing-14: 3.5rem;
  --spacing-16: 4rem;
  --spacing-20: 5rem;
  --spacing-24: 6rem;

  /* Typography */
  --font-sans: 'Inter', sans-serif;
  --font-mono: 'Fira Code', monospace;

  /* Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
}
```

### Step 4: Tailwind 설정 업데이트

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss';

const config: Config = {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: 'var(--color-primary)',
          foreground: 'var(--color-primary-foreground)',
        },
        secondary: {
          DEFAULT: 'var(--color-secondary)',
          foreground: 'var(--color-secondary-foreground)',
        },
        background: 'var(--color-background)',
        foreground: 'var(--color-foreground)',
        muted: {
          DEFAULT: 'var(--color-muted)',
          foreground: 'var(--color-muted-foreground)',
        },
        border: 'var(--color-border)',
      },
      fontFamily: {
        sans: ['var(--font-sans)'],
        mono: ['var(--font-mono)'],
      },
      borderRadius: {
        sm: 'var(--radius-sm)',
        md: 'var(--radius-md)',
        lg: 'var(--radius-lg)',
        xl: 'var(--radius-xl)',
      },
    },
  },
};

export default config;
```

---

## 색상 모드 지원

### Light/Dark 테마

```css
:root {
  --color-background: #FFFFFF;
  --color-foreground: #1F2937;
}

.dark {
  --color-background: #1F2937;
  --color-foreground: #F9FAFB;
}
```

### Figma 컬렉션 매핑

```
Figma Collection: "Light Mode" → :root
Figma Collection: "Dark Mode" → .dark
```

---

## 토큰 네이밍 컨벤션

### Figma → CSS 변환

| Figma Name | CSS Variable |
|------------|--------------|
| `colors/primary` | `--color-primary` |
| `colors/primary/foreground` | `--color-primary-foreground` |
| `spacing/4` | `--spacing-4` |
| `typography/heading/1` | `--font-heading-1` |
| `radius/lg` | `--radius-lg` |

### 규칙

1. `/` → `-` 변환
2. 카멜케이스 → 케밥케이스
3. 숫자 유지
4. 접두사 추가 (`--color-`, `--spacing-` 등)

---

## 에러 처리

### 누락된 토큰

```typescript
// 기본값 제공
const defaultTokens = {
  'color-primary': '#3B82F6',
  'color-background': '#FFFFFF',
  'spacing-4': '1rem',
};

function getToken(name: string, figmaValue?: string): string {
  return figmaValue ?? defaultTokens[name] ?? 'inherit';
}
```

### 타입 불일치

```typescript
// 타입 검증
function validateColorToken(value: string): boolean {
  return /^#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?$/.test(value) ||  // 6 or 8 char hex
         /^rgba?\(/.test(value) ||
         /^hsla?\(/.test(value) ||
         /^oklch\(/.test(value) ||
         /^var\(--/.test(value);
}
```

---

## 출력 파일

```
src/
├── styles/
│   ├── variables.css     # CSS 변수 정의
│   └── tokens.json       # 원본 토큰 (참조용)
│
└── tailwind.config.ts    # Tailwind 설정 업데이트
```
