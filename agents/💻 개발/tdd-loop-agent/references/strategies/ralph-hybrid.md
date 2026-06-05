# Strategy: Ralph Hybrid (TDD)

> **Version**: 1.0.0 | Score-based exit with coverage targets

---

## Overview

| Property | Value |
|----------|-------|
| Model | Opus |
| Verification | Test pass + Coverage threshold |
| Max Iterations | 30 |
| Target | 100% pass AND coverage >= target |
| Exit Condition | Score threshold met |
| Use Case | Quantitative quality gates |

---

## Philosophy

```
┌─────────────────────────────────────────────────────────────────┐
│                    HYBRID TDD: MEASURABLE QUALITY                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Pure Strengths:              + Quantitative Gates:            │
│   ─────────────────            ─────────────────────            │
│   • File-based memory          • Coverage threshold             │
│   • Self-referential loop      • Pass rate tracking             │
│   • Iterative improvement      • Numeric exit condition         │
│                                                                  │
│   ═══════════════════════════════════════════════════════════   │
│                                                                  │
│   HYBRID = Ralph Loop + Coverage Target + Score-based Exit      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Exit Conditions

Both conditions must be met:

1. **All tests pass** (0 failures)
2. **Coverage >= target** (default: 80%)

```
EXIT = (failures == 0) AND (coverage >= target)
```

---

## Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    HYBRID TDD ITERATION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. READ STATE                                                 │
│      └─ work-log.md                                             │
│      └─ test-results.json                                       │
│      └─ coverage.json (REQUIRED for Hybrid)                     │
│                                                                  │
│   2. RUN TESTS WITH COVERAGE                                    │
│      └─ flutter test --coverage                                 │
│      └─ Parse test results                                      │
│      └─ Parse coverage report (lcov)                            │
│                                                                  │
│   3. CALCULATE SCORE                                            │
│      └─ Pass rate: passed / total                               │
│      └─ Coverage: lines covered / total lines                   │
│      └─ Combined score for tracking                             │
│                                                                  │
│   4. CHECK EXIT CONDITIONS                                      │
│      └─ failures == 0? ✓                                        │
│      └─ coverage >= target? ✓                                   │
│      └─ Both true? → EXIT                                       │
│                                                                  │
│   5. IF NOT EXIT: PRIORITIZE FIXES                              │
│      └─ If failures > 0: Fix failing tests first                │
│      └─ If coverage low: Add missing tests                      │
│                                                                  │
│   6. APPLY & VERIFY                                             │
│      └─ Apply fix (respecting L1/L2/L3 levels)                  │
│      └─ Update state files                                      │
│      └─ Continue loop                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## State Files (Hybrid-Specific)

### coverage.json

```json
{
  "timestamp": "2025-01-28T10:00:00Z",
  "target": 80,
  "current": 72.5,
  "breakdown": {
    "lib/auth/": 85.2,
    "lib/api/": 62.1,
    "lib/utils/": 78.9
  },
  "uncoveredFiles": [
    "lib/api/error_handler.dart",
    "lib/api/retry_logic.dart"
  ]
}
```

---

## Coverage Commands by Framework

### Flutter

```bash
# Run with coverage
flutter test --coverage

# Generate HTML report (optional)
genhtml coverage/lcov.info -o coverage/html

# Parse lcov.info for percentage
lcov --summary coverage/lcov.info
```

---

## Scoring System

### Pass Rate Score (50%)

```
pass_score = (passed_tests / total_tests) * 50
```

### Coverage Score (50%)

```
coverage_score = (current_coverage / target_coverage) * 50
# Capped at 50 (no bonus for exceeding target)
```

### Combined Score

```
total_score = pass_score + coverage_score
# Max: 100
```

### Exit Threshold

```
EXIT when:
  - pass_score == 50 (all tests pass)
  - coverage_score >= 50 * (target / 100)

Example with 80% target:
  - Need: pass_score == 50 AND coverage >= 80%
```

---

## Work Log Example (Hybrid)

```markdown
# TDD Work Log (Hybrid Strategy)

## Goal
Achieve 80% coverage with all tests passing

## Configuration
- Target Coverage: 80%
- Max Iterations: 30

---

### Iteration 1
- **Timestamp:** 2025-01-28T10:00:00Z
- **Command:** `flutter test --coverage`
- **Test Result:** FAIL (8 passed, 2 failed)
- **Coverage:** 65.2%
- **Score:** Pass: 40/50, Coverage: 40.75/50 = 80.75/100
- **Gap Analysis:**
  - Need to fix 2 failing tests
  - Need +14.8% coverage
- **Priority:** Fix failing tests first
- **Next Action:** Fix api_client_test.dart failures

---

### Iteration 2
- **Timestamp:** 2025-01-28T10:05:00Z
- **Action:** Fixed mock setup in api_client_test.dart
- **Command:** `flutter test --coverage`
- **Test Result:** PASS (10 passed, 0 failed)
- **Coverage:** 65.2%
- **Score:** Pass: 50/50, Coverage: 40.75/50 = 90.75/100
- **Gap Analysis:**
  - Tests all pass ✓
  - Still need +14.8% coverage
- **Priority:** Add tests for uncovered files
- **Uncovered:**
  - lib/api/error_handler.dart (0%)
  - lib/api/retry_logic.dart (45%)

---

### Iteration 3
- **Timestamp:** 2025-01-28T10:10:00Z
- **Action:** Added tests for error_handler.dart
- **Command:** `flutter test --coverage`
- **Test Result:** PASS (15 passed, 0 failed)
- **Coverage:** 78.5%
- **Score:** Pass: 50/50, Coverage: 49.06/50 = 99.06/100
- **Gap Analysis:**
  - Tests all pass ✓
  - Need +1.5% coverage

---

### Iteration 4
- **Timestamp:** 2025-01-28T10:15:00Z
- **Action:** Added edge case tests for retry_logic.dart
- **Command:** `flutter test --coverage`
- **Test Result:** PASS (18 passed, 0 failed)
- **Coverage:** 82.3%
- **Score:** Pass: 50/50, Coverage: 50/50 = 100/100

## Exit Conditions Met
- All tests pass: ✓
- Coverage >= 80%: ✓ (82.3%)

TDD_RALPH_COMPLETE
```

---

## When to Use Hybrid

- You need measurable quality gates
- Coverage percentage is a requirement
- Want to ensure comprehensive test coverage
- CI/CD pipeline requires coverage thresholds

---

## Limitations

- Slower due to coverage analysis each iteration
- Coverage doesn't guarantee test quality
- May add low-value tests just to hit coverage target
- Requires coverage tooling support
