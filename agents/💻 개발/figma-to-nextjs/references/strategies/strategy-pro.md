# Strategy: Pro

> **Version**: 3.2.0 | **Type**: Strategy Reference
> Dual-agent parallel verification for production-quality output

---

## Overview

| Property | Value |
|----------|-------|
| Model | Opus |
| Verification | Dual Agent (Parallel) |
| Max Iterations | 10 (5 per agent) |
| Target Accuracy | 95%+ |
| Exit Condition | Score threshold |
| Use Case | Complex pages, production |

---

## Dual Agent Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PARALLEL VERIFICATION                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌───────────────┐    ┌───────────────┐                        │
│   │ AGENT A       │    │ AGENT B       │                        │
│   │ Conservative  │    │ Experimental  │                        │
│   │ (shadcn/ui)   │    │ (Custom)      │                        │
│   └───────┬───────┘    └───────┬───────┘                        │
│           │                    │                                 │
│           ▼                    ▼                                 │
│   ┌───────────────┐    ┌───────────────┐                        │
│   │ 5 Iterations  │    │ 5 Iterations  │                        │
│   │ Safe fixes    │    │ Bold fixes    │                        │
│   └───────┬───────┘    └───────┬───────┘                        │
│           │                    │                                 │
│           └────────┬───────────┘                                 │
│                    ▼                                             │
│           ┌───────────────┐                                      │
│           │ RESULT SELECTOR│                                     │
│           │ Pick best of 2 │                                     │
│           └───────────────┘                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Agent Strategies

### Agent A: Conservative
- Prefer shadcn/ui components
- Apply only L1-L2 fixes automatically
- L3 fixes require approval
- Prioritize stability

### Agent B: Experimental
- Try custom Tailwind components
- Try L1-L3 fixes automatically
- Explore alternative structures
- Prioritize accuracy

---

## Result Selection Criteria

```yaml
selection_criteria:
  - Higher overall score wins
  - If scores within 1%, prefer Conservative
  - If Experimental is 2%+ higher, select Experimental
  - Build success is mandatory for both
```

---

## Verification Method

- Playwright screenshot comparison
- Multi-viewport (mobile, tablet, desktop)
- Automated diff calculation
