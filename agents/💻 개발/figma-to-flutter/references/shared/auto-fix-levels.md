# Auto-Fix Levels (Shared)

> **Version**: 3.2.0 | **Type**: Shared Reference
> L1-L4 classification for automatic fixes

---

## Level Classification

| Level | Description | Auto-Fix | Approval |
|-------|-------------|----------|----------|
| **L1** | Simple value changes | Yes | None |
| **L2** | Property additions | Yes | None |
| **L3** | Widget restructuring | Partial | Required |
| **L4** | Layout algorithm change | No | Manual |

---

## L1: Simple Value Changes

**Auto-fix without approval**

```dart
// Font size adjustment
fontSize: 14 → fontSize: 16

// Padding adjustment
EdgeInsets.all(16) → EdgeInsets.all(24)

// Color adjustment
Color(0xFF000000) → Color(0xFF333333)

// Border radius
BorderRadius.circular(4) → BorderRadius.circular(8)

// Font weight
FontWeight.w400 → FontWeight.w500
```

---

## L2: Property Additions

**Auto-fix without approval**

```dart
// Add letter spacing
TextStyle(fontSize: 16)
→ TextStyle(fontSize: 16, letterSpacing: 0.5)

// Add shadow
Container(color: Colors.white)
→ Container(
    color: Colors.white,
    decoration: BoxDecoration(
      boxShadow: [BoxShadow(...)],
    ),
  )

// Add border radius
Container()
→ Container(
    decoration: BoxDecoration(
      borderRadius: BorderRadius.circular(8),
    ),
  )
```

---

## L3: Widget Restructuring

**Requires approval before applying**

```dart
// Row to Column conversion
Row(children: [...])
→ Column(children: [...])

// Container to DecoratedBox
Container(decoration: ...)
→ DecoratedBox(decoration: ...)

// Add Expanded wrapper
Text("Hello")
→ Expanded(child: Text("Hello"))

// Wrap with Padding
Widget()
→ Padding(padding: EdgeInsets.all(16), child: Widget())
```

---

## L4: Layout Algorithm Change

**Manual intervention required**

```dart
// ListView to CustomScrollView
ListView(children: [...])
→ CustomScrollView(slivers: [SliverList(...)])

// Wrap to Flow
Wrap(children: [...])
→ Flow(delegate: ..., children: [...])

// Add CustomMultiChildLayout
Column(children: [...])
→ CustomMultiChildLayout(delegate: ..., children: [...])

// Complete layout restructuring
// Requires human review and approval
```

---

## Decision Tree

```
┌─────────────────────────────────────────────┐
│           Fix Classification                 │
├─────────────────────────────────────────────┤
│                                              │
│  Is it a value change only?                 │
│  ├─ YES → L1 (Auto-fix)                     │
│  └─ NO ↓                                    │
│                                              │
│  Is it adding a property?                   │
│  ├─ YES → L2 (Auto-fix)                     │
│  └─ NO ↓                                    │
│                                              │
│  Is it widget restructuring?                │
│  ├─ YES → L3 (Approval needed)              │
│  └─ NO ↓                                    │
│                                              │
│  Is it layout algorithm change?             │
│  └─ YES → L4 (Manual)                       │
│                                              │
└─────────────────────────────────────────────┘
```
