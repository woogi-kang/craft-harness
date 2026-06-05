# Auto-Fix Levels (Shared)

> **Version**: 3.2.0 | **Type**: Shared Reference
> L1-L4 classification for automatic fixes

---

## Level Classification

| Level | Description | Auto-Fix | Approval |
|-------|-------------|----------|----------|
| **L1** | Simple value changes | Yes | None |
| **L2** | Property additions | Yes | None |
| **L3** | Component restructuring | Partial | Required |
| **L4** | Layout algorithm change | No | Manual |

---

## L1: Simple Value Changes

**Auto-fix without approval**

```tsx
// Font size adjustment
text-sm → text-base

// Padding adjustment
p-4 → p-6

// Color adjustment
text-gray-800 → text-gray-900

// Border radius
rounded → rounded-lg

// Font weight
font-normal → font-medium
```

---

## L2: Property Additions

**Auto-fix without approval**

```tsx
// Add letter spacing
<p className="text-base">
→ <p className="text-base tracking-wide">

// Add shadow
<div className="bg-white">
→ <div className="bg-white shadow-lg">

// Add border radius
<div>
→ <div className="rounded-xl">
```

---

## L3: Component Restructuring

**Requires approval before applying**

```tsx
// Flex to Grid conversion
<div className="flex flex-col">
→ <div className="grid grid-cols-2">

// Wrapper addition
<span>Text</span>
→ <div className="flex-1"><span>Text</span></div>

// Component extraction
<div>complex content</div>
→ <MyComponent />

// Layout direction change
<div className="flex-row">
→ <div className="flex-col">
```

---

## L4: Layout Algorithm Change

**Manual intervention required**

```tsx
// Grid to CSS Grid with custom areas
<div className="grid grid-cols-3">
→ <div style={{ gridTemplateAreas: '...' }}>

// Complex responsive restructuring
// Requires human review and approval

// Adding CSS modules or styled-components
// Major architectural changes
```

---

## Decision Tree

```
┌─────────────────────────────────────────────┐
│           Fix Classification                 │
├─────────────────────────────────────────────┤
│                                              │
│  Is it a Tailwind class change only?        │
│  ├─ YES → L1 (Auto-fix)                     │
│  └─ NO ↓                                    │
│                                              │
│  Is it adding classes/props?                │
│  ├─ YES → L2 (Auto-fix)                     │
│  └─ NO ↓                                    │
│                                              │
│  Is it component restructuring?             │
│  ├─ YES → L3 (Approval needed)              │
│  └─ NO ↓                                    │
│                                              │
│  Is it layout algorithm change?             │
│  └─ YES → L4 (Manual)                       │
│                                              │
└─────────────────────────────────────────────┘
```
