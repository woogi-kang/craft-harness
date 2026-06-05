---
name: "Phase 3: Component Mapping"
phase_id: 3
phase_name: "Component Mapping"
description: "Map Figma components to existing codebase components"

dependencies:
  - phase_id: 0
    artifacts: [reusable_components.json]
    validation: components_list_exists
  - phase_id: 1
    artifacts: [node_map.json]
    validation: node_map_exists

inputs:
  required: [node_map, reusable_components, figma_file_key]
  optional: [existing_code_connect_map]

outputs:
  artifacts: [component_mapping.json, dependency_graph.json, creation_plan.json]
  state_updates: [artifacts.phase_3.component_mapping]

validation:
  success_criteria:
    - All Figma components categorized (mapped/mappable/create)
    - Dependency graph complete
    - Creation order determined
  quality_gates:
    - shadcn/ui components prioritized for reuse
    - No circular dependencies

rollback:
  on_failure: log_and_continue_with_defaults
  cleanup: [component_mapping.json]
  can_resume: true

mcp_calls:
  estimated: 2
  tools: [get_code_connect_map, add_code_connect_map]
---

# Phase 3: Component Mapping

> Figma 컴포넌트 ↔ 코드베이스 컴포넌트 매핑

---

## 실행 조건

- Phase 0 (프로젝트 스캔) 완료
- Phase 1 (디자인 스캔) 완료
- 재사용 가능 컴포넌트 목록 확보

---

## Step 3-1: 기존 매핑 조회

```typescript
// MCP 호출
get_code_connect_map({
  fileKey: "ABC123",
  nodeId: "123:456"
})
```

### 반환 예시

```json
{
  "node-123:459": {
    "codeConnectSrc": "src/components/ui/button.tsx",
    "codeConnectName": "Button"
  },
  "node-123:471": {
    "codeConnectSrc": "src/components/ui/card.tsx",
    "codeConnectName": "Card"
  }
}
```

---

## Step 3-2: 매핑 분석

### 매핑 상태 분류

| 상태 | 설명 | 액션 |
|------|------|------|
| **Mapped** | 이미 매핑됨 | 재사용 |
| **Mappable** | 유사 컴포넌트 존재 | 매핑 등록 |
| **Create** | 새로 생성 필요 | Phase 4 |

### 분석 템플릿

```markdown
## Component Mapping Analysis

### Already Mapped ✅
| Figma Component | Code Component | nodeId |
|-----------------|----------------|--------|
| Primary Button | `Button` | 123:459 |
| Card Container | `Card` | 123:471 |

### Mappable (Need Registration) 🔄
| Figma Component | Suggested Code | Similarity |
|-----------------|----------------|------------|
| Secondary Button | `Button variant="secondary"` | 95% |
| Input Field | `Input` | 90% |

### Need Creation 🆕
| Figma Component | Suggested Name | Complexity |
|-----------------|---------------|------------|
| Hero Section | `HeroSection` | Medium |
| Feature Card | `FeatureCard` | Low |
```

---

## Step 3-3: 새 매핑 등록

```typescript
// MCP 호출
add_code_connect_map({
  nodeId: "123:480",
  source: "src/components/ui/input.tsx",
  componentName: "Input",
  clientLanguages: "typescript",
  clientFrameworks: "react"
})
```

### 등록 체크리스트

```markdown
## Mapping Registration

- [x] Secondary Button → `Button variant="secondary"`
- [x] Input Field → `Input`
- [x] Dialog Modal → `Dialog`
- [ ] Custom Component (Phase 4에서 생성 후 등록)
```

---

## Step 3-4: shadcn/ui 컴포넌트 매핑

### 자주 사용되는 매핑

| Figma Pattern | shadcn/ui Component | Props |
|---------------|---------------------|-------|
| Primary Button | `<Button>` | `variant="default"` |
| Secondary Button | `<Button>` | `variant="secondary"` |
| Outline Button | `<Button>` | `variant="outline"` |
| Ghost Button | `<Button>` | `variant="ghost"` |
| Link Button | `<Button>` | `variant="link"` |
| Card | `<Card>` | - |
| Input | `<Input>` | `type="text"` |
| Checkbox | `<Checkbox>` | - |
| Switch | `<Switch>` | - |
| Dialog | `<Dialog>` | - |
| Dropdown | `<DropdownMenu>` | - |
| Tabs | `<Tabs>` | - |
| Avatar | `<Avatar>` | - |
| Badge | `<Badge>` | `variant` |

### Variant 매핑

```markdown
## Button Variants

| Figma Style | shadcn Variant |
|-------------|----------------|
| Filled Primary | `variant="default"` |
| Filled Secondary | `variant="secondary"` |
| Outline | `variant="outline"` |
| Text Only | `variant="ghost"` |
| Destructive | `variant="destructive"` |

## Size Variants

| Figma Size | shadcn Size |
|------------|-------------|
| Small (32px) | `size="sm"` |
| Medium (40px) | `size="default"` |
| Large (48px) | `size="lg"` |
| Icon Only | `size="icon"` |
```

---

## Step 3-5: 커스텀 컴포넌트 계획

### 생성 필요 컴포넌트

```markdown
## Components to Create

### HeroSection
- **Path**: `src/components/sections/hero-section.tsx`
- **Dependencies**: Button, Image
- **Props**: title, subtitle, ctaText, ctaLink, image
- **Variants**: centered, left-aligned

### FeatureCard
- **Path**: `src/components/features/feature-card.tsx`
- **Dependencies**: Card, Icon
- **Props**: icon, title, description
- **Variants**: default, highlighted

### PricingTable
- **Path**: `src/components/pricing/pricing-table.tsx`
- **Dependencies**: Card, Button, Badge
- **Props**: plans, onSelect
- **Variants**: monthly, yearly
```

---

## Step 3-6: 컴포넌트 의존성 그래프

```
┌─────────────────────────────────────────────────────────────┐
│                    Component Dependency Graph                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  HeroSection                                                │
│  ├── Button (shadcn) ✅                                     │
│  ├── Image (next/image) ✅                                  │
│  └── Container (new)                                        │
│                                                             │
│  FeatureCard                                                │
│  ├── Card (shadcn) ✅                                       │
│  └── Icon (lucide-react) ✅                                 │
│                                                             │
│  PricingTable                                               │
│  ├── Card (shadcn) ✅                                       │
│  ├── Button (shadcn) ✅                                     │
│  ├── Badge (shadcn) ✅                                      │
│  └── Switch (shadcn) ✅                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 산출물

```markdown
# Component Mapping Report

## Summary
- Total Figma Components: 15
- Already Mapped: 5
- Newly Mapped: 4
- To Create: 6

## Mapping Table
| Figma | Code | Status |
|-------|------|--------|
| Primary Button | `Button` | ✅ Mapped |
| Card | `Card` | ✅ Mapped |
| Input | `Input` | 🔄 Registered |
| HeroSection | (new) | 🆕 Create |

## Dependencies
- shadcn/ui: Button, Card, Input, Dialog
- lucide-react: Icons
- next/image: Image optimization

## Next Actions
1. Create HeroSection component
2. Create FeatureCard component
3. Register new mappings after creation
```

---

## 다음 단계

Phase 3 완료 후 → **Phase 4: Code Generate** 진행
