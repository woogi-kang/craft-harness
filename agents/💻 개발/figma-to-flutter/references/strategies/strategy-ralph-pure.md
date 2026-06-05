# Strategy: Ralph Pure

> **Version**: 3.2.0 | **Type**: Strategy Reference
> Maximum autonomy through self-referential file-based learning

---

## Overview

| Property | Value |
|----------|-------|
| Model | Opus |
| Verification | Self-assessment + Playwright |
| Max Iterations | 50 (unlimited spirit) |
| Target Accuracy | 99%+ |
| Exit Condition | Promise tag (subjective) |
| Use Case | Maximum autonomy, complex edge cases |

---

## Pure Ralph Philosophy

```
┌─────────────────────────────────────────────────────────────────┐
│                         PURE RALPH PHILOSOPHY                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   "Ralph is a Bash loop"                                        │
│   "Iteration > Perfection"                                      │
│   "Failures are Data"                                           │
│   "Persistence Wins"                                            │
│                                                                  │
│   ═══════════════════════════════════════════════════════════   │
│                                                                  │
│   Core Principles:                                               │
│   ─────────────                                                  │
│   1. Judge by "completion state" not score                      │
│   2. Files ARE memory (infinite context)                        │
│   3. Read previous attempts and self-improve                    │
│   4. Keep trying even after failures (never give up)            │
│   5. Promise is declared only when truly complete               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## vs Hybrid Comparison

| Aspect | Ralph Hybrid | Ralph Pure |
|--------|--------------|------------|
| Exit | Score >= 98% | "I'm done" promise |
| Judgment | Numeric | Qualitative |
| Iterations | 30 max | 50 max |
| Verification | Dual | Self-assessment |
| Complexity | Medium | Low |

---

## Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    PURE RALPH ITERATION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. READ: Previous work files                                  │
│      - ./work-log.md (what I did, what failed)                  │
│      - ./todo.md (what remains)                                 │
│      - lib/**/*.dart (generated code)                           │
│      - Git diff (what changed)                                  │
│                                                                  │
│   2. THINK: What needs improvement?                             │
│      - Compare Figma screenshot vs Flutter web                  │
│      - Identify visual differences                              │
│      - Check if previous fix worked                             │
│                                                                  │
│   3. ACT: Make improvements                                     │
│      - Fix identified issues                                    │
│      - Update work-log.md                                       │
│      - Update todo.md                                           │
│                                                                  │
│   4. VERIFY: Build and check                                    │
│      - flutter build web                                        │
│      - Take screenshot via Playwright                           │
│      - Self-assess: "Is this good enough?"                      │
│                                                                  │
│   5. DECIDE: Continue or complete?                              │
│      - More to fix? → Continue                                  │
│      - Perfect? → Declare promise tag                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Promise Tag

```markdown
<!-- When truly complete, output this tag -->
FLUTTER_CONVERSION_COMPLETE

<!-- This tag signals the Stop Hook to exit the loop -->
```

---

## Work Log Format

```markdown
# Work Log

## Iteration 1
- Started: 2024-01-15 10:00
- Actions: Created initial widget structure
- Issues: Button padding too large
- Next: Fix button padding

## Iteration 2
- Started: 2024-01-15 10:05
- Actions: Fixed button padding (EdgeInsets.all(16) → all(12))
- Issues: Card shadow not matching
- Next: Adjust BoxShadow parameters
```
