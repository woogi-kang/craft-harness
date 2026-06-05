---
name: "Phase 4: Code Generate"
phase_id: 4
phase_name: "Code Generate"
description: "Generate React/TSX components from Figma design context"

dependencies:
  - phase_id: 2
    artifacts: [tokens.json, tailwind.config.patch.ts]
    validation: tokens_extracted
  - phase_id: 3
    artifacts: [component_mapping.json, creation_plan.json]
    validation: mapping_complete

inputs:
  required: [tokens, component_mapping, creation_plan, figma_file_key]
  optional: [style_preferences, custom_templates]

outputs:
  artifacts: [components/*.tsx, types/generated.ts, index.ts]
  state_updates: [artifacts.phase_4.components, checkpoint]

validation:
  success_criteria:
    - All planned components generated
    - TypeScript compiles without errors
    - Imports resolve correctly
  quality_gates:
    - "'use client' only where needed"
    - Accessibility attributes present
    - No hardcoded values (use tokens)

rollback:
  on_failure: checkpoint_and_pause
  cleanup: [partially_generated_components]
  can_resume: true

mcp_calls:
  estimated: 3-5
  tools: [get_design_context]
---

# Phase 4: Code Generate

> React + Tailwind 코드 생성 및 Next.js 컴포넌트 변환

---

## 실행 조건

- Phase 3 (Component Mapping) 완료
- 생성할 컴포넌트 목록 확정

---

## Step 4-1: 디자인 컨텍스트 추출

```typescript
// MCP 호출
get_design_context({
  fileKey: "ABC123",
  nodeId: "123:456"
})
```

### 반환 예시 (React + Tailwind)

```jsx
<div className="flex flex-col items-center justify-center gap-8 px-6 py-16 bg-white">
  <div className="flex flex-col items-center gap-4 max-w-2xl">
    <h1 className="text-5xl font-bold text-gray-900 text-center">
      Build faster with AI
    </h1>
    <p className="text-xl text-gray-600 text-center">
      Transform your Figma designs into production-ready code instantly.
    </p>
  </div>
  <div className="flex gap-4">
    <button className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700">
      Get Started
    </button>
    <button className="px-6 py-3 bg-white text-gray-900 border border-gray-300 rounded-lg font-medium hover:bg-gray-50">
      Learn More
    </button>
  </div>
</div>
```

---

## Step 4-2: Next.js 컴포넌트 변환

### 변환 규칙

| Figma Output | Next.js Convention |
|--------------|-------------------|
| `<div>` | Semantic HTML (`section`, `article`) |
| `<button>` | shadcn `<Button>` 재사용 |
| `<img>` | `next/image` `<Image>` |
| `<a>` | `next/link` `<Link>` |
| Inline styles | Tailwind classes |
| Hard-coded colors | CSS variables / Tailwind |

### 변환 예시

```tsx
// src/components/sections/hero-section.tsx
'use client';

import Image from 'next/image';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface HeroSectionProps {
  title: string;
  subtitle: string;
  primaryCta: {
    text: string;
    href: string;
  };
  secondaryCta?: {
    text: string;
    href: string;
  };
  image?: {
    src: string;
    alt: string;
  };
  className?: string;
}

export function HeroSection({
  title,
  subtitle,
  primaryCta,
  secondaryCta,
  image,
  className,
}: HeroSectionProps) {
  return (
    <section
      className={cn(
        'flex flex-col items-center justify-center gap-8 px-6 py-16 bg-background',
        className
      )}
    >
      <div className="flex flex-col items-center gap-4 max-w-2xl text-center">
        <h1 className="text-5xl font-bold text-foreground">
          {title}
        </h1>
        <p className="text-xl text-muted-foreground">
          {subtitle}
        </p>
      </div>

      <div className="flex gap-4">
        <Button asChild size="lg">
          <Link href={primaryCta.href}>
            {primaryCta.text}
          </Link>
        </Button>

        {secondaryCta && (
          <Button asChild variant="outline" size="lg">
            <Link href={secondaryCta.href}>
              {secondaryCta.text}
            </Link>
          </Button>
        )}
      </div>

      {image && (
        <div className="relative w-full max-w-4xl aspect-video">
          <Image
            src={image.src}
            alt={image.alt}
            fill
            className="object-cover rounded-xl"
            priority
          />
        </div>
      )}
    </section>
  );
}
```

---

## Step 4-3: 컴포넌트 구조 패턴

### 기본 컴포넌트 템플릿

```tsx
// Component Template
'use client'; // 클라이언트 컴포넌트인 경우만

import { cn } from '@/lib/utils';

// 1. Props Interface
interface ComponentNameProps {
  // Required props
  title: string;
  // Optional props
  description?: string;
  className?: string;
  children?: React.ReactNode;
}

// 2. Component Definition
export function ComponentName({
  title,
  description,
  className,
  children,
}: ComponentNameProps) {
  return (
    <div className={cn('base-classes', className)}>
      {/* Content */}
    </div>
  );
}

// 3. Default Export (optional)
export default ComponentName;
```

### Server vs Client Component

```tsx
// Server Component (default) - 데이터 페칭, 정적 렌더링
// src/components/features/feature-list.tsx
import { getFeatures } from '@/lib/api';

export async function FeatureList() {
  const features = await getFeatures();

  return (
    <div className="grid grid-cols-3 gap-6">
      {features.map((feature) => (
        <FeatureCard key={feature.id} {...feature} />
      ))}
    </div>
  );
}

// Client Component - 상호작용, 상태 관리
// src/components/features/feature-card.tsx
'use client';

import { useState } from 'react';

export function FeatureCard({ title, description }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div onClick={() => setIsExpanded(!isExpanded)}>
      {/* Interactive content */}
    </div>
  );
}
```

---

## Step 4-4: 파일 구조

```
src/
├── components/
│   ├── ui/                      # shadcn/ui 컴포넌트
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── input.tsx
│   │
│   ├── layout/                  # 레이아웃 컴포넌트
│   │   ├── header.tsx
│   │   ├── footer.tsx
│   │   └── nav.tsx
│   │
│   ├── sections/                # 페이지 섹션 컴포넌트
│   │   ├── hero-section.tsx
│   │   ├── features-section.tsx
│   │   └── cta-section.tsx
│   │
│   ├── features/                # 기능별 컴포넌트
│   │   └── [feature-name]/
│   │       ├── index.tsx
│   │       └── components/
│   │
│   └── common/                  # 공통 컴포넌트
│       ├── logo.tsx
│       └── social-links.tsx
│
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── (routes)/
│
└── lib/
    ├── utils.ts                 # cn() 함수 등
    └── constants.ts
```

---

## Step 4-5: 코드 품질 체크

### TypeScript 체크리스트

```markdown
## TypeScript Quality

- [ ] `any` 타입 사용 금지
- [ ] Props interface 명시적 정의
- [ ] 필수/선택 props 구분 (`?:`)
- [ ] React.ReactNode 사용 (children)
- [ ] 이벤트 핸들러 타입 명시
```

### Tailwind 체크리스트

```markdown
## Tailwind Quality

- [ ] 하드코딩된 색상 없음 (#xxx → text-primary)
- [ ] 반복 클래스 추출 (cn() 활용)
- [ ] 반응형 클래스 적용 (sm:, md:, lg:)
- [ ] 다크 모드 고려 (dark:)
```

### Next.js 체크리스트

```markdown
## Next.js Quality

- [ ] 'use client' 필요한 경우만 사용
- [ ] Image 컴포넌트 사용 (next/image)
- [ ] Link 컴포넌트 사용 (next/link)
- [ ] Metadata 정의 (SEO)
- [ ] 적절한 파일 위치
```

---

## Step 4-6: 코드 생성 예시

### Feature Card 컴포넌트

```tsx
// src/components/features/feature-card.tsx
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface FeatureCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  className?: string;
}

export function FeatureCard({
  icon: Icon,
  title,
  description,
  className,
}: FeatureCardProps) {
  return (
    <Card className={cn('hover:shadow-lg transition-shadow', className)}>
      <CardHeader>
        <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
          <Icon className="w-6 h-6 text-primary" />
        </div>
        <CardTitle className="text-xl">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
}
```

---

## 산출물

```markdown
# Code Generation Report

## Generated Components
| Component | Path | Lines | Status |
|-----------|------|-------|--------|
| HeroSection | `sections/hero-section.tsx` | 67 | ✅ |
| FeatureCard | `features/feature-card.tsx` | 38 | ✅ |
| CTASection | `sections/cta-section.tsx` | 45 | ✅ |

## Quality Checks
- [ ] TypeScript strict: ✅
- [ ] No any types: ✅
- [ ] Tailwind only: ✅
- [ ] next/image used: ✅

## Dependencies Added
- None (using existing shadcn/ui)

## Files Modified
- None
```

---

## 다음 단계

Phase 4 완료 후 → **Phase 5: Asset Process** 진행
