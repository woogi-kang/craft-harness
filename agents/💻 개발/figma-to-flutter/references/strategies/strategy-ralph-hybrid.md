# Strategy: Ralph Hybrid

> **Version**: 3.2.0 | **Type**: Strategy Reference
> Self-referential loop with dual verification (Code + Visual)

---

## Overview

| Property | Value |
|----------|-------|
| Model | Opus |
| Verification | Dual (Code + Visual via Playwright) |
| Max Iterations | 30 (unlimited spirit) |
| Target Accuracy | 99%+ (98% hard minimum) |
| Exit Condition | Score threshold |
| Use Case | Pixel-perfect requirements |

---

## Core Philosophy

```
┌─────────────────────────────────────────────────────────────────┐
│                    RALPH HYBRID: BEST OF BOTH WORLDS             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Ralph Strengths:              Original System Strengths:       │
│   ─────────────────             ─────────────────────────        │
│   • File-based infinite context • Code verification (numeric)   │
│   • Self-referential learning   • Visual verification (Playwright)│
│   • Stop Hook for auto-repeat   • Weighted scoring system       │
│   • Git history utilization     • Auto-fix levels (L1-L4)       │
│                                                                  │
│   ═══════════════════════════════════════════════════════════   │
│                                                                  │
│   HYBRID = Ralph Loop + Dual Verification + Score-based Exit    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    ITERATION N                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. Read State Files                                           │
│      └─ ./ralph-state/verification-report.json                  │
│      └─ ./ralph-state/iteration-history.json                    │
│      └─ ./ralph-state/current-score.json                        │
│                                                                  │
│   2. Analyze Gaps                                               │
│      └─ Compare Figma screenshot vs Flutter web                 │
│      └─ Calculate category scores                               │
│      └─ Identify specific fixes needed                          │
│                                                                  │
│   3. Apply Fixes                                                │
│      └─ L1-L2: Auto-apply                                       │
│      └─ L3: Apply with caution                                  │
│      └─ L4: Skip, document for manual                           │
│                                                                  │
│   4. Verify & Score                                             │
│      └─ Run flutter build web                                   │
│      └─ Take Playwright screenshot                              │
│      └─ Calculate new scores                                    │
│                                                                  │
│   5. Decision                                                   │
│      └─ Score >= 98%? → EXIT                                    │
│      └─ Score < 98%? → Continue loop                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## State Files

```
ralph-state/
├── verification-report.json   # Latest verification results
├── iteration-history.json     # All iterations with scores
├── current-score.json         # Current score breakdown
├── fix-attempts.json          # What was tried
└── blockers.json              # Known blockers
```

---

## Playwright Integration

```typescript
// Take Flutter web screenshot
await mcp__playwright__browser_navigate({ url: "http://localhost:PORT" });
await mcp__playwright__browser_take_screenshot({ path: "flutter-output.png" });

// Compare with Figma screenshot
// Calculate pixel difference
```
