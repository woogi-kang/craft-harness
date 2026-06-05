---
name: "Phase 1: Design Scan"
phase_id: 1
phase_name: "Design Scan"
description: "Scan Figma design structure and create layer map with 80% token reduction"

dependencies:
  - phase_id: 0
    artifacts: [project_analysis.json]
    validation: project_is_nextjs

inputs:
  required: [figma_url, project_analysis]
  optional: [specific_node_ids]

outputs:
  artifacts: [design_scan.json, node_map.json, conversion_plan.json]
  state_updates: [figma.file_key, figma.node_ids]

validation:
  success_criteria:
    - Figma file accessible
    - Layer structure documented
    - Conversion targets identified
  quality_gates:
    - MCP call budget not exceeded

rollback:
  on_failure: log_error_and_retry
  cleanup: [design_scan.json]
  can_resume: true

mcp_calls:
  estimated: 2
  tools: [get_metadata, get_screenshot]
---

# Phase 1: Design Scan

> 대규모 디자인 최적화 스캔 (토큰 80% 절감)

---

## 실행 조건

- Phase 0 완료 후
- Figma 링크 또는 nodeId 확보

---

## 스캔 전략 결정

```
┌─────────────────────────────────────────────────────────────┐
│  디자인 규모에 따른 전략 선택                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  단일 컴포넌트 (1-5 레이어)                                   │
│  → get_design_context 직접 호출                              │
│                                                             │
│  중규모 페이지 (5-50 레이어)                                  │
│  → get_metadata → 선별 → get_design_context                 │
│                                                             │
│  대규모 디자인 (50+ 레이어)                                   │
│  → get_metadata 필수 → 배치 처리                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 1-1: URL에서 정보 추출

```typescript
// Figma URL 파싱
// https://www.figma.com/design/ABC123/Project-Name?node-id=123-456

const url = "https://www.figma.com/design/ABC123/Project?node-id=123-456";

// 추출 정보
fileKey: "ABC123"
nodeId: "123-456" → "123:456" (API 형식으로 변환)
```

### NodeId 형식 변환

```
URL 형식:  123-456  (하이픈)
API 형식:  123:456  (콜론)
```

---

## Step 1-2: 경량 메타데이터 스캔

```typescript
// MCP 호출
get_metadata({
  fileKey: "ABC123",  // 원격 서버 시 필수
  nodeId: "123:456"
})
```

### 반환 예시

```xml
<layer id="123:456" name="Hero Section" type="FRAME">
  <layer id="123:457" name="Title" type="TEXT" x="0" y="0" width="400" height="48"/>
  <layer id="123:458" name="Subtitle" type="TEXT" x="0" y="56" width="400" height="24"/>
  <layer id="123:459" name="CTA Button" type="COMPONENT" x="0" y="96" width="200" height="48"/>
  <layer id="123:460" name="Hero Image" type="RECTANGLE" x="420" y="0" width="600" height="400"/>
</layer>
```

---

## Step 1-3: 타겟 노드 선별

### 변환 대상 분류

| 타입 | 처리 방식 |
|------|----------|
| FRAME | 컨테이너 → div |
| TEXT | 텍스트 → p, h1-h6, span |
| COMPONENT | 재사용 컴포넌트 확인 |
| INSTANCE | 컴포넌트 인스턴스 |
| RECTANGLE | 이미지/배경 |
| VECTOR | SVG 아이콘 |

### 선별 기준

```markdown
## 우선순위 높음 (즉시 변환)
- [ ] FRAME: 주요 섹션 컨테이너
- [ ] TEXT: 제목, 본문
- [ ] COMPONENT: 버튼, 카드 등

## 우선순위 중간 (필요시 변환)
- [ ] INSTANCE: 컴포넌트 인스턴스
- [ ] GROUP: 그룹화된 요소

## 별도 처리 (에셋으로)
- [ ] RECTANGLE: 이미지 → Phase 5
- [ ] VECTOR: 아이콘 → Phase 5
```

---

## Step 1-4: 레이어 구조 문서화

```markdown
## Design Structure

### Hero Section (123:456)
```
Hero Section
├── Title (TEXT)
├── Subtitle (TEXT)
├── CTA Button (COMPONENT) → Button 재사용
└── Hero Image (RECTANGLE) → 에셋 처리
```

### Features Section (123:470)
```
Features Section
├── Section Title (TEXT)
└── Feature Cards (FRAME)
    ├── Card 1 (COMPONENT) → Card 재사용
    ├── Card 2 (COMPONENT)
    └── Card 3 (COMPONENT)
```
```

---

## Step 1-5: 변환 계획 수립

```markdown
## Conversion Plan

### Components to Create
| 컴포넌트 | nodeId | 우선순위 |
|---------|--------|---------|
| HeroSection | 123:456 | 1 |
| FeatureCard | 123:471 | 2 |
| CTAButton | 123:459 | 3 |

### Components to Reuse
| Figma | Code | 매핑 |
|-------|------|------|
| CTA Button | `@/components/ui/button` | Phase 3 |
| Card | `@/components/ui/card` | Phase 3 |

### Assets to Extract
| 에셋 | nodeId | 타입 |
|------|--------|------|
| Hero Image | 123:460 | PNG |
| Icon Set | 123:480 | SVG |
```

---

## Rate Limit 최적화

```
┌─────────────────────────────────────────────────────────────┐
│  Starter Plan (6 calls/month) 최적화                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ❌ 비효율적: 모든 레이어에 get_design_context (10+ calls)   │
│                                                             │
│  ✅ 효율적:                                                  │
│     1. get_metadata (1 call) - 전체 구조 파악               │
│     2. get_design_context (2-3 calls) - 핵심 섹션만         │
│     3. get_variable_defs (1 call) - 토큰 추출               │
│                                                             │
│  총 4-5 calls로 전체 페이지 변환 가능                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 산출물

```markdown
# Design Scan Report

## Summary
- Total Layers: 47
- Conversion Targets: 12
- Asset Targets: 5
- Reusable Components: 3

## Layer Structure
[구조 다이어그램]

## Conversion Plan
[변환 계획 테이블]

## Estimated MCP Calls
- get_metadata: 1
- get_design_context: 4
- get_variable_defs: 1
- get_screenshot: 2
- **Total: 8 calls**
```

---

## 다음 단계

Phase 1 완료 후 → **Phase 2: Token Extract** 진행
