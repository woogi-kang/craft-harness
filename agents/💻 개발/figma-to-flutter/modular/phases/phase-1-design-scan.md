---
name: "Phase 1: Design Scan"
description: "Figma design analysis for Flutter conversion"
---

# Phase 1: Design Scan

> Figma 디자인 구조 분석

---

## 실행 조건

- Phase 0 완료
- Figma URL 제공됨
- Figma MCP 연결됨

---

## Step 1-1: URL 파싱

### Figma URL 구조

```
https://www.figma.com/design/[FILE_KEY]/[FILE_NAME]?node-id=[NODE_ID]

예시:
https://www.figma.com/design/ABC123/App-Design?node-id=123-456

파싱 결과:
- fileKey: ABC123
- nodeId: 123-456
```

---

## Step 1-2: 메타데이터 조회

### MCP 호출 (필수 첫 호출)

```typescript
// MUST: Always call get_metadata first
get_metadata({
  fileKey: "ABC123",
  nodeId: "123-456"  // optional
})
```

### 응답 구조

```json
{
  "name": "App Design",
  "lastModified": "2025-01-15T10:00:00Z",
  "nodes": [
    {
      "id": "123-456",
      "name": "Home Screen",
      "type": "FRAME",
      "children": [...]
    }
  ]
}
```

---

## Step 1-3: 노드 트리 분석

### 노드 타입별 분류

| Figma Type | Flutter Widget | 용도 |
|------------|----------------|------|
| FRAME | Container/Column/Row | 레이아웃 컨테이너 |
| GROUP | Stack | 그룹 레이어 |
| TEXT | Text | 텍스트 |
| RECTANGLE | Container | 사각형 |
| ELLIPSE | Container (circular) | 원형 |
| VECTOR | SvgPicture | 벡터 그래픽 |
| INSTANCE | Custom Widget | 컴포넌트 인스턴스 |
| COMPONENT | StatelessWidget | 재사용 컴포넌트 |

### Flutter 레이아웃 감지

```
Auto Layout (horizontal) → Row
Auto Layout (vertical) → Column
Auto Layout (wrap) → Wrap
Fixed position → Positioned (in Stack)
Grid → GridView
```

---

## Step 1-4: 디자인 컨텍스트 조회

### 선택적 MCP 호출

```typescript
// 필요한 노드만 조회 (Rate Limit 관리)
get_design_context({
  fileKey: "ABC123",
  nodeId: "123-456"
})
```

### 추출 데이터

```json
{
  "node": {
    "id": "123-456",
    "name": "Home Screen",
    "type": "FRAME",
    "width": 390,
    "height": 844,
    "fills": [...],
    "strokes": [...],
    "effects": [...],
    "layoutMode": "VERTICAL",
    "itemSpacing": 16,
    "paddingTop": 24,
    "paddingBottom": 24,
    "paddingLeft": 16,
    "paddingRight": 16
  }
}
```

---

## Step 1-5: 컴포넌트 식별

### 재사용 컴포넌트 감지

```markdown
## Detected Components

### Buttons
- [ ] PrimaryButton (12 instances)
- [ ] SecondaryButton (8 instances)
- [ ] IconButton (15 instances)

### Cards
- [ ] ProductCard (6 instances)
- [ ] FeatureCard (4 instances)

### Inputs
- [ ] TextField (8 instances)
- [ ] SearchField (2 instances)

### Navigation
- [ ] BottomNavBar (1 instance)
- [ ] AppBar (3 instances)
```

---

## Step 1-6: 화면 구조 매핑

### 화면별 분석

```markdown
## Screen: Home (390x844)

### Layout Structure
```
Column
├── AppBar (h: 56)
├── Expanded
│   └── SingleChildScrollView
│       └── Column
│           ├── HeroSection (h: 200)
│           ├── SizedBox (h: 24)
│           ├── FeatureGrid
│           │   └── GridView (2 columns)
│           ├── SizedBox (h: 24)
│           └── ProductList
│               └── ListView.builder
└── BottomNavBar (h: 80)
```

### Spacing Analysis
- Section gap: 24px
- Card gap: 16px
- Content padding: 16px
```

---

## 산출물

```markdown
# Design Scan Report

## File Info
- File: App Design
- Last Modified: 2025-01-15
- Target Node: Home Screen (123-456)

## Screen Dimensions
- Width: 390px (iPhone 14 Pro)
- Height: 844px

## Layout Analysis
- Root Layout: Column
- Scroll: SingleChildScrollView
- Has AppBar: Yes
- Has BottomNav: Yes

## Components Found
| Component | Type | Instances |
|-----------|------|-----------|
| PrimaryButton | Button | 12 |
| ProductCard | Card | 6 |
| TextField | Input | 8 |

## Color Usage
| Color | Hex | Usage |
|-------|-----|-------|
| Primary | #3B82F6 | Buttons, Links |
| Background | #FFFFFF | Screen BG |
| Text | #1F2937 | Body text |

## Typography
| Style | Size | Weight | Usage |
|-------|------|--------|-------|
| Heading1 | 32px | 700 | Page titles |
| Heading2 | 24px | 600 | Section titles |
| Body | 16px | 400 | Content |

## Next Phase
Phase 2: Token Extract 진행 가능
```
