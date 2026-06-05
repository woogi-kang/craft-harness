# TDD-Ralph: MUST Rules

> **Version**: 1.0.0 | Common rules for all TDD-Ralph strategies

---

## Core Rules (All Strategies)

### 1. State Management

```
[HARD] Initialize tdd-state/ directory at start
[HARD] Read ALL state files before each iteration
[HARD] Update work-log.md after EVERY action
[HARD] Never delete state files during execution
```

### 2. Test Execution

```
[HARD] Always run tests via framework command (never mock results)
[HARD] Capture full stdout/stderr output
[HARD] Parse results into structured format (pass/fail/skip counts)
[HARD] Store raw output for debugging
```

### 3. Error Handling

```
[HARD] Generate error signature for circuit breaker
[HARD] Track consecutive same-error count
[HARD] Stop after 3 consecutive identical errors
[HARD] Generate circuit breaker report on stop
```

### 4. Fix Application

```
[HARD] Classify fix level (L1/L2/L3) before applying
[HARD] L3 fixes require documentation, not auto-apply
[HARD] Log all changes in work-log.md with diff format
[HARD] Verify build succeeds after fix
```

### 5. Exit Conditions

```
[HARD] Exit ONLY when: 100% tests pass OR circuit breaker OR user cancel
[HARD] Output appropriate exit tag (TDD_RALPH_COMPLETE or TDD_RALPH_STOPPED)
[HARD] Generate final summary report
```

---

## State Directory Structure

```
tdd-state/
├── work-log.md           # [REQUIRED] Iteration history
├── test-results.json     # [REQUIRED] Latest parsed results
├── error-history.json    # [REQUIRED] Circuit breaker data
├── plan.md               # [REQUIRED] Original goal
└── coverage.json         # [OPTIONAL] For Hybrid strategy
```

### work-log.md Format

```markdown
# TDD Work Log

## Goal
<User's original request>

---

### Iteration N
- **Timestamp:** <ISO 8601>
- **Hypothesis:** <What we expect to happen>
- **Action:** <Code diff or command>
- **Command:** <Test command executed>
- **Result:** <PASS/FAIL with counts>
- **Failures:** <List of failing tests if any>
- **Analysis:** <What we learned>
- **Next Action:** <What to do next>
```

### test-results.json Format

```json
{
  "timestamp": "2025-01-28T10:00:00Z",
  "command": "flutter test",
  "exitCode": 1,
  "summary": {
    "total": 10,
    "passed": 7,
    "failed": 3,
    "skipped": 0
  },
  "failures": [
    {
      "file": "test/auth_test.dart",
      "name": "AuthService login should return user",
      "error": "Expected: User, Actual: null",
      "stackTrace": "..."
    }
  ]
}
```

### error-history.json Format

```json
{
  "history": [
    {
      "iteration": 1,
      "signature": "abc123...",
      "message": "Expected: User, Actual: null"
    }
  ],
  "consecutiveSameError": 0,
  "lastSignature": null
}
```

---

## Circuit Breaker Algorithm

```
FUNCTION check_circuit_breaker(current_error, error_history):
    signature = generate_signature(current_error)

    IF signature == error_history.last_signature THEN
        error_history.consecutive_count += 1
    ELSE
        error_history.consecutive_count = 1
        error_history.last_signature = signature
    END IF

    IF error_history.consecutive_count >= 3 THEN
        RETURN TRIP_CIRCUIT_BREAKER
    END IF

    RETURN CONTINUE
END FUNCTION
```

### Signature Generation

1. Extract error message
2. Remove volatile parts (paths, line numbers, timestamps)
3. Extract function names from stack trace (top 5)
4. Concatenate and hash: `SHA256(message + functions)`

---

## Fix Level Classification

| Factor | L1 (1 point) | L2 (2 points) | L3 (3 points) |
|--------|--------------|---------------|---------------|
| Lines changed | 1-5 | 6-25 | 25+ |
| Files affected | 1 | 1-2 | 3+ |
| Construct | Variable/Import | Function body | Class/Architecture |
| Usages | 0-2 | 3-10 | 10+ |

**Classification:**
- Score 1-4: L1 (Auto-apply)
- Score 5-7: L2 (Apply with caution)
- Score 8+: L3 (Document only)

---

## Prohibited Actions

```
[FORBIDDEN] Deleting test files to make tests "pass"
[FORBIDDEN] Modifying test assertions to match wrong output
[FORBIDDEN] Skipping tests without explicit user permission
[FORBIDDEN] Continuing after circuit breaker trips
[FORBIDDEN] Exiting before 100% pass (unless circuit breaker)
```

---

## Recovery Procedures

### If state files corrupted

1. Backup corrupted files to `tdd-state/backup/`
2. Re-initialize from scratch
3. Log incident in work-log.md

### If build fails after fix

1. Revert the change
2. Log the failed attempt
3. Try alternative approach
4. If 3 alternatives fail, escalate to L3

### If test framework crashes

1. Check framework installation
2. Run `flutter doctor` (for Flutter)
3. Log diagnostic output
4. Attempt recovery or report to user
