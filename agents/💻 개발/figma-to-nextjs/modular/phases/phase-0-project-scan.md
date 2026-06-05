---
name: "Phase 0: Project Scan"
phase_id: 0
phase_name: "Project Scan"
description: "Analyze Next.js project structure and identify reusable components"

dependencies: []

inputs:
  required: [project_path]
  optional: [existing_config]

outputs:
  artifacts: [project_analysis.json, reusable_components.json]
  state_updates: [project.framework, project.ui_library, project.styling]

validation:
  success_criteria:
    - package.json exists and contains Next.js
    - Project type identified (App Router / Pages Router)
    - Styling system identified
  quality_gates:
    - TypeScript strict mode recommended

rollback:
  on_failure: abort_conversion
  cleanup: []
  can_resume: false

mcp_calls:
  estimated: 0
  tools: []
---

# Phase 0: Project Scan

> Next.js 프로젝트 구조 분석 및 재사용 가능 컴포넌트 식별

---

## 실행 조건

- Figma 작업 **전** 반드시 수행
- 프로젝트 루트에서 실행

---

## Step 0-1: Next.js 프로젝트 타입 확인

```bash
# package.json에서 Next.js 버전 확인
Grep: '"next"' path:"package.json"

# App Router vs Pages Router 확인
Glob: "**/app/**/page.tsx"     # App Router
Glob: "**/pages/**/*.tsx"       # Pages Router
```

### 결과 템플릿

```markdown
| 항목 | 값 |
|------|-----|
| Next.js Version | 14.x / 15.x |
| Router Type | App Router / Pages Router |
| TypeScript | Yes / No |
```

---

## Step 0-2: 스타일링 방식 확인

```bash
# Tailwind CSS
Glob: "**/tailwind.config.*"
Grep: "tailwindcss" path:"package.json"

# CSS Modules
Glob: "**/*.module.css"
Glob: "**/*.module.scss"

# Styled Components
Grep: "styled-components" path:"package.json"

# CSS-in-JS
Grep: "@emotion" path:"package.json"
```

### 결과 템플릿

```markdown
| 스타일링 | 사용 여부 |
|---------|----------|
| Tailwind CSS | ✅ / ❌ |
| CSS Modules | ✅ / ❌ |
| Styled Components | ✅ / ❌ |
| Emotion | ✅ / ❌ |
```

---

## Step 0-3: UI 라이브러리 확인

```bash
# shadcn/ui
Glob: "**/components/ui/*.tsx"
Grep: "@radix-ui" path:"package.json"

# 기타 UI 라이브러리
Grep: "@chakra-ui" path:"package.json"
Grep: "@mui/material" path:"package.json"
Grep: "antd" path:"package.json"
```

### shadcn/ui 컴포넌트 목록 (있는 경우)

```bash
# 설치된 shadcn/ui 컴포넌트 확인
ls src/components/ui/ 또는 components/ui/
```

---

## Step 0-4: 기존 컴포넌트 분석

```bash
# 모든 컴포넌트 파일
Glob: "**/components/**/*.tsx"

# 레이아웃 컴포넌트
Glob: "**/components/**/layout*.tsx"
Glob: "**/components/**/header*.tsx"
Glob: "**/components/**/footer*.tsx"

# 공통 컴포넌트
Glob: "**/components/common/*.tsx"
Glob: "**/components/shared/*.tsx"
```

---

## Step 0-5: 유틸리티 함수 확인

```bash
# cn 함수 (Tailwind 병합)
Grep: "export function cn" path:"."
Grep: "clsx" path:"package.json"
Grep: "tailwind-merge" path:"package.json"

# 기타 유틸리티
Glob: "**/lib/*.ts"
Glob: "**/utils/*.ts"
```

---

## Step 0-6: 에셋 구조 확인

```bash
# public 폴더 구조
ls public/
ls public/images/
ls public/icons/

# 기존 이미지 사용 패턴
Grep: "Image from 'next/image'" path:"."
Grep: "<img" path:"**/*.tsx"
```

---

## 최종 산출물

```markdown
# Project Analysis Report

## Environment
| 항목 | 값 |
|------|-----|
| Next.js | 14.2.x |
| Router | App Router |
| TypeScript | Yes (strict) |
| Node.js | 20.x |

## Styling
| 방식 | 상태 |
|------|------|
| Tailwind CSS | ✅ Primary |
| CSS Modules | ❌ |
| PostCSS | ✅ |

## UI Library
| 라이브러리 | 상태 |
|-----------|------|
| shadcn/ui | ✅ |
| Radix UI | ✅ (via shadcn) |

## Reusable Components

### UI Components (shadcn/ui)
| 컴포넌트 | 경로 | 재사용 |
|---------|------|--------|
| Button | `@/components/ui/button` | ✅ |
| Card | `@/components/ui/card` | ✅ |
| Input | `@/components/ui/input` | ✅ |
| Dialog | `@/components/ui/dialog` | ✅ |

### Custom Components
| 컴포넌트 | 경로 | 용도 |
|---------|------|------|
| Header | `@/components/layout/header` | 공통 헤더 |
| Footer | `@/components/layout/footer` | 공통 푸터 |

## Utilities
| 유틸리티 | 경로 |
|---------|------|
| cn() | `@/lib/utils` |
| formatDate() | `@/lib/date` |

## Asset Structure
```
public/
├── images/
├── icons/
└── fonts/
```

## Recommendations
1. shadcn/ui Button 재사용 권장
2. cn() 함수로 클래스 병합
3. public/images/에 에셋 저장
```

---

## 다음 단계

Phase 0 완료 후 → **Phase 1: Design Scan** 진행
