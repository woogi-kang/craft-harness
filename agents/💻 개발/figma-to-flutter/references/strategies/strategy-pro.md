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
│   │ (Standard)    │    │ (Creative)    │                        │
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
- Apply only L1-L2 fixes automatically
- L3 fixes require approval
- Prioritize stability over speed
- Prefer existing widget patterns

### Agent B: Experimental
- Try L1-L3 fixes automatically
- Explore alternative widget structures
- Prioritize accuracy over stability
- May introduce new patterns

---

## Result Selection Criteria

```yaml
selection_criteria:
  - Higher overall score wins
  - If scores within 1%, prefer Conservative (more stable)
  - If Experimental is 2%+ higher, select Experimental
  - Build success is mandatory for both
```

---

## Verification Method

- Golden Test comparison
- Multi-device screenshots (iPhone, Android, Web)
- Automated diff calculation
