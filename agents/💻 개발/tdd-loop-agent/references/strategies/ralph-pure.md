# Strategy: Ralph Pure (TDD)

> **Version**: 1.0.0 | Maximum autonomy through self-referential learning

---

## Overview

| Property | Value |
|----------|-------|
| Model | Opus |
| Verification | Self-assessment |
| Max Iterations | 50 |
| Target | 100% test pass |
| Exit Condition | Promise tag (TDD_RALPH_COMPLETE) |
| Use Case | Maximum autonomy, trust agent judgment |

---

## Philosophy

```
┌─────────────────────────────────────────────────────────────────┐
│                    PURE RALPH FOR TDD                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   "Tests don't lie"                                             │
│   "Green means done"                                            │
│   "Every failure teaches"                                       │
│   "Persist until victory"                                       │
│                                                                  │
│   ═══════════════════════════════════════════════════════════   │
│                                                                  │
│   Exit when YOU judge all tests pass.                           │
│   No external score needed.                                     │
│   Trust the test output.                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## vs Hybrid Comparison

| Aspect | Ralph Pure | Ralph Hybrid |
|--------|------------|--------------|
| Exit Condition | "All tests pass" declaration | Coverage >= target% |
| Judgment | Qualitative (pass/fail) | Quantitative (%) |
| Max Iterations | 50 | 30 |
| Coverage Tracking | Optional | Required |
| Complexity | Low | Medium |

---

## Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    PURE TDD ITERATION                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. READ: Previous state                                       │
│      - work-log.md (history)                                    │
│      - test-results.json (last run)                             │
│      - plan.md (original goal)                                  │
│                                                                  │
│   2. RUN: Execute tests                                         │
│      - flutter test (or framework command)                      │
│      - Capture all output                                       │
│      - Parse pass/fail/skip counts                              │
│                                                                  │
│   3. ANALYZE: Check results                                     │
│      - All passed? → Prepare to exit                            │
│      - Failures? → Identify root cause                          │
│      - Same error 3x? → Circuit breaker                         │
│                                                                  │
│   4. FIX: Apply corrections                                     │
│      - Classify fix level (L1/L2/L3)                            │
│      - Apply fix                                                │
│      - Update work-log.md                                       │
│                                                                  │
│   5. VERIFY: Build check                                        │
│      - Ensure code compiles                                     │
│      - If build fails, revert and retry                         │
│                                                                  │
│   6. DECIDE: Continue or complete?                              │
│      - All tests pass? → Output TDD_RALPH_COMPLETE              │
│      - More failures? → Continue loop                           │
│      - Circuit breaker? → Output TDD_RALPH_STOPPED              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Exit Tag

When all tests pass, output:

```
TDD_RALPH_COMPLETE
```

This signals the loop to exit successfully.

---

## Work Log Example (Pure)

```markdown
# TDD Work Log (Pure Strategy)

## Goal
Fix all failing tests in auth module

---

### Iteration 1
- **Timestamp:** 2025-01-28T10:00:00Z
- **Hypothesis:** Run tests to identify current failures
- **Command:** `flutter test test/auth/`
- **Result:** FAIL (2 passed, 3 failed)
- **Failures:**
  - login_test.dart: "should return user on success"
  - login_test.dart: "should throw on invalid credentials"
  - logout_test.dart: "should clear session"
- **Analysis:** Mock setup incomplete for AuthRepository
- **Next Action:** Configure mock responses

---

### Iteration 2
- **Timestamp:** 2025-01-28T10:03:00Z
- **Hypothesis:** Proper mock setup will fix login tests
- **Action:**
  ```diff
  --- a/test/auth/login_test.dart
  +++ b/test/auth/login_test.dart
  @@ -15,6 +15,8 @@
   setUp(() {
     mockRepo = MockAuthRepository();
  +  when(mockRepo.login(any, any))
  +      .thenAnswer((_) async => Right(testUser));
   });
  ```
- **Command:** `flutter test test/auth/`
- **Result:** FAIL (4 passed, 1 failed)
- **Analysis:** Login tests now pass. Logout test remains.
- **Next Action:** Fix logout mock

---

### Iteration 3
- **Timestamp:** 2025-01-28T10:06:00Z
- **Hypothesis:** Adding logout mock will complete fixes
- **Action:**
  ```diff
  --- a/test/auth/logout_test.dart
  +++ b/test/auth/logout_test.dart
  @@ -12,6 +12,7 @@
   setUp(() {
     mockRepo = MockAuthRepository();
  +  when(mockRepo.logout()).thenAnswer((_) async => Right(unit));
   });
  ```
- **Command:** `flutter test test/auth/`
- **Result:** PASS (5 passed, 0 failed)
- **Analysis:** All tests now passing!

---

## Summary
- Total Iterations: 3
- Tests Fixed: 3
- Final Result: 5/5 passed

TDD_RALPH_COMPLETE
```

---

## When to Use Pure

- You trust the agent to judge completion
- Tests are the sole source of truth
- Coverage percentage is not a requirement
- You want maximum autonomy with minimal configuration

---

## Limitations

- No coverage enforcement (use Hybrid if needed)
- Relies on test quality (bad tests = bad judgment)
- May exit with low coverage if all existing tests pass
