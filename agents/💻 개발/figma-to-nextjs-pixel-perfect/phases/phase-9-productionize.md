---
name: "Phase 9: Productionize Guard"
phase_id: 9
description: "Refactor after strict pass while preserving visual output"
---

# Phase 9: Productionize Guard

## Purpose

Make code maintainable only after exact render passes.

## Allowed Refactors

- Extract repeated components.
- Replace duplicated arbitrary values with CSS variables.
- Improve semantic HTML.
- Add accessibility attributes.
- Move frame-specific constants into typed config.

## Guard

After each refactor:

1. Run build/lint.
2. Re-run visual diff.
3. Re-run computed-style diff for touched elements.

If diff worsens, revert the refactor or keep the exact render implementation.

## Completion

Productionize mode must not change the verified visual output. If maintainability conflicts with fidelity, fidelity wins unless the user explicitly changes the goal.

