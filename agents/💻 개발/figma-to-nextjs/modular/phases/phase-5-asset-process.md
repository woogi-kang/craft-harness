---
name: "Phase 5: Asset Process"
phase_id: 5
phase_name: "Asset Process"
description: "Extract, optimize, and integrate images and icons with next/image"

dependencies:
  - phase_id: 4
    artifacts: [components/*.tsx]
    validation: components_generated

inputs:
  required: [asset_list, component_asset_refs]
  optional: [optimization_settings]

outputs:
  artifacts: [public/images/*, public/icons/*, asset_manifest.json]
  state_updates: [artifacts.phase_5.assets]

validation:
  success_criteria:
    - All referenced assets downloaded (100% - no exceptions)
    - Images in correct formats
    - Asset paths match component imports
    - Zero placeholder/substitute assets used
  quality_gates:
    - Images optimized (WebP/AVIF)
    - SVGs cleaned and minified
    - next/image used for raster images
    - All assets sourced from Figma only

rollback:
  on_failure: halt_and_alert_user
  retry_policy:
    retryable_errors: [timeout, 429, 500, 502, 503, connection_reset]
    fatal_errors: [404, 403, invalid_node_id, file_deleted]
    max_retry: unlimited
    backoff: exponential
  cleanup: none
  can_resume: true
  user_action_required: true

mcp_calls:
  estimated: 2-4
  tools: [get_screenshot]
---

# Phase 5: Asset Process

> 이미지/아이콘 최적화 및 next/image 적용

---

## 실행 조건

- Phase 4 (Code Generate) 완료
- 에셋 목록 확정

---

## Step 5-1: 에셋 목록 추출

### Phase 1에서 식별된 에셋

```markdown
## Assets to Extract

| Asset | Type | nodeId | 용도 |
|-------|------|--------|------|
| Hero Image | PNG/JPG | 123:460 | 히어로 배경 |
| Logo | SVG | 123:401 | 헤더 로고 |
| Feature Icon 1 | SVG | 123:481 | 기능 아이콘 |
| Feature Icon 2 | SVG | 123:482 | 기능 아이콘 |
| CTA Background | PNG | 123:490 | CTA 섹션 배경 |
```

---

## Step 5-2: 에셋 다운로드 (Retry Until Success)

> **CRITICAL**: 모든 에셋이 다운로드될 때까지 진행 불가. 단 하나라도 누락 시 Phase 6 진입 금지.

### Retry Strategy

```typescript
async function downloadAssetWithRetry(nodeId: string, assetName: string) {
  const RETRYABLE_ERRORS = ['timeout', 'ECONNRESET', '429', '500', '502', '503'];
  const FATAL_ERRORS = ['404', '403', 'INVALID_NODE'];

  let attempt = 0;
  let delay = 2000; // Start with 2 seconds

  while (true) {
    attempt++;
    console.log(`[Attempt ${attempt}] Downloading: ${assetName} (${nodeId})`);

    try {
      const result = await get_screenshot({ nodeId });
      console.log(`✅ Success: ${assetName}`);
      return result;

    } catch (error) {
      const errorType = classifyError(error);

      // FATAL ERROR → Immediate HALT
      if (FATAL_ERRORS.includes(errorType)) {
        throw new AssetFatalError({
          type: 'HALT_WORKFLOW',
          asset: assetName,
          nodeId: nodeId,
          error: errorType,
          message: `Asset download failed with unrecoverable error.
                    Cannot substitute with placeholders or icon libraries.
                    User action required.`
        });
      }

      // RETRYABLE ERROR → Wait and retry
      console.log(`⚠️ Retryable error (${errorType}), waiting ${delay/1000}s...`);
      await sleep(delay);
      delay = Math.min(delay * 2, 60000); // Max 60 seconds
    }
  }
}
```

### 에러 유형별 처리

| Error Type | Action | Retry |
|------------|--------|-------|
| timeout | 대기 후 재시도 | ♾️ 무한 |
| 429 (rate limit) | 대기 후 재시도 | ♾️ 무한 |
| 500/502/503 | 대기 후 재시도 | ♾️ 무한 |
| connection reset | 대기 후 재시도 | ♾️ 무한 |
| **404 (not found)** | **즉시 중단** | ❌ |
| **403 (forbidden)** | **즉시 중단** | ❌ |
| **invalid nodeId** | **즉시 중단** | ❌ |

### MCP 호출

```typescript
// 이미지 스크린샷 추출
get_screenshot({ nodeId: "123:460" })
→ Base64 인코딩 이미지
```

### 저장 위치

```
public/
├── images/
│   ├── hero/
│   │   └── hero-bg.png
│   ├── cta/
│   │   └── cta-bg.png
│   └── team/
│       ├── member-1.jpg
│       └── member-2.jpg
│
├── icons/
│   ├── feature-1.svg
│   ├── feature-2.svg
│   └── feature-3.svg
│
└── logos/
    ├── logo.svg
    └── logo-dark.svg
```

---

## Step 5-3: 이미지 최적화

### next/image 사용

```tsx
import Image from 'next/image';

// 기본 사용
<Image
  src="/images/hero/hero-bg.png"
  alt="Hero background"
  width={1200}
  height={600}
  priority // LCP 이미지인 경우
/>

// Fill 모드 (부모 크기에 맞춤)
<div className="relative w-full aspect-video">
  <Image
    src="/images/hero/hero-bg.png"
    alt="Hero background"
    fill
    className="object-cover"
    sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
  />
</div>

// 배경 이미지처럼 사용
<div className="relative">
  <Image
    src="/images/cta/cta-bg.png"
    alt=""
    fill
    className="object-cover -z-10"
    aria-hidden="true"
  />
  <div className="relative z-10">
    {/* Content */}
  </div>
</div>
```

### sizes 속성 가이드

```tsx
// 반응형 sizes 설정
sizes="
  (max-width: 640px) 100vw,   // 모바일: 전체 너비
  (max-width: 1024px) 50vw,   // 태블릿: 절반
  33vw                         // 데스크톱: 1/3
"
```

---

## Step 5-4: SVG 아이콘 처리

### 방법 1: 컴포넌트로 변환

```tsx
// src/components/icons/feature-icon.tsx
export function FeatureIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="M12 2L2 7l10 5 10-5-10-5z" />
      <path d="M2 17l10 5 10-5" />
      <path d="M2 12l10 5 10-5" />
    </svg>
  );
}
```

### 방법 2: Figma SVG 직접 import (권장)

> ⚠️ **FORBIDDEN**: lucide-react, heroicons 등 아이콘 라이브러리 사용 금지
> 모든 아이콘은 반드시 Figma에서 다운로드해야 함

```tsx
// Figma에서 다운로드한 SVG를 직접 import
import FeatureIcon1 from '@/public/icons/feature-1.svg';
import FeatureIcon2 from '@/public/icons/feature-2.svg';
import FeatureIcon3 from '@/public/icons/feature-3.svg';

// 사용
<FeatureIcon1 className="w-6 h-6 text-primary" />
<FeatureIcon2 className="w-6 h-6 text-primary" />
<FeatureIcon3 className="w-6 h-6 text-primary" />
```

### 방법 3: @svgr/webpack (커스텀 SVG)

```tsx
// next.config.js
module.exports = {
  webpack(config) {
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack'],
    });
    return config;
  },
};

// 사용
import CustomIcon from '@/public/icons/custom.svg';

<CustomIcon className="w-6 h-6" />
```

---

## Step 5-5: 이미지 포맷 최적화

### 포맷 선택 가이드

| 용도 | 포맷 | 이유 |
|------|------|------|
| 사진 | WebP/AVIF | 압축률 우수 |
| 일러스트 | SVG | 벡터, 무손실 |
| 아이콘 | SVG | 크기 조절 가능 |
| 투명 배경 | PNG/WebP | 알파 채널 |
| 로고 | SVG | 선명도 유지 |

### Next.js 자동 최적화

```typescript
// next.config.js
module.exports = {
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
};
```

---

## Step 5-6: 에셋 사용 패턴

### Hero 이미지

```tsx
// src/components/sections/hero-section.tsx
import Image from 'next/image';

export function HeroSection() {
  return (
    <section className="relative min-h-screen">
      {/* Background Image */}
      <Image
        src="/images/hero/hero-bg.png"
        alt=""
        fill
        className="object-cover -z-10"
        priority
        sizes="100vw"
      />

      {/* Overlay */}
      <div className="absolute inset-0 bg-black/50 -z-10" />

      {/* Content */}
      <div className="relative z-10 container mx-auto px-4 py-24">
        <h1 className="text-5xl font-bold text-white">Title</h1>
      </div>
    </section>
  );
}
```

### 아바타/프로필 이미지

```tsx
import Image from 'next/image';

export function Avatar({ src, alt, size = 40 }) {
  return (
    <div
      className="relative rounded-full overflow-hidden"
      style={{ width: size, height: size }}
    >
      <Image
        src={src}
        alt={alt}
        fill
        className="object-cover"
        sizes={`${size}px`}
      />
    </div>
  );
}
```

### 로고

```tsx
import Image from 'next/image';
import Link from 'next/link';

export function Logo() {
  return (
    <Link href="/" className="flex items-center">
      <Image
        src="/logos/logo.svg"
        alt="Company Logo"
        width={120}
        height={40}
        priority
      />
    </Link>
  );
}
```

---

## 산출물

```markdown
# Asset Processing Report

## Asset Inventory Verification
| Expected | Downloaded | Status |
|----------|------------|--------|
| 12 | 12 | ✅ 100% |

## Assets Processed (All from Figma)
| Asset | Type | Size | Location | Source |
|-------|------|------|----------|--------|
| hero-bg.png | PNG | 245KB | public/images/hero/ | Figma ✅ |
| logo.svg | SVG | 2KB | public/logos/ | Figma ✅ |
| feature-1.svg | SVG | 1KB | public/icons/ | Figma ✅ |
| feature-2.svg | SVG | 1KB | public/icons/ | Figma ✅ |
| feature-3.svg | SVG | 1KB | public/icons/ | Figma ✅ |

## Optimization Results
- Original Total: 512KB
- Optimized Total: 198KB
- Reduction: 61%

## Usage Summary
- next/image: 5 instances
- SVG components (Figma): 8 icons
- Icon libraries used: 0 (FORBIDDEN)
- Placeholders used: 0 (FORBIDDEN)

## CRITICAL Checklist
- [x] All images in public/
- [x] next/image used
- [x] sizes attribute set
- [x] priority for LCP
- [x] Alt text provided
- [x] **100% assets from Figma (no substitutes)**
- [x] **Zero icon library usage**
- [x] **Zero placeholder images**
- [x] **Asset count matches inventory**
```

---

## FORBIDDEN Actions (Zero Tolerance)

다음 행동은 절대 허용되지 않음:

| Action | Why Forbidden |
|--------|---------------|
| `import { Icon } from 'lucide-react'` | 아이콘 라이브러리 사용 금지 |
| `import { Icon } from '@heroicons/react'` | 아이콘 라이브러리 사용 금지 |
| `<div className="bg-gray-200" />` (as image placeholder) | 플레이스홀더 금지 |
| "Similar icon used instead" | 대체 아이콘 금지 |
| "Will add asset later" | 에셋 스킵 금지 |

**위반 시**: 워크플로우 즉시 중단, Phase 6 진입 불가

---

## 다음 단계

Phase 5 완료 후 → **Phase 6: Pixel-Perfect Verification** 진행
