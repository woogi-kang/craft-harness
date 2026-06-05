# Spec and Contract Notes

Craft Harness uses lightweight contracts before autonomous execution.

## Minimal Spec

```markdown
# SPEC-001: Feature Name

## Goal
What user or developer outcome should change?

## Constraints
Runtime, files, dependencies, and non-goals.

## Acceptance Criteria
- Criterion 1
- Criterion 2

## Verification
Commands, QA flow, screenshots, API checks, or review criteria.
```

## Plan Contract

`plan.json` workers should include:

- `name`
- `task`
- `depends_on`
- `success_criteria`
- `eval_type`

The orchestrator writes each worker's criteria into `task.md`. QA workers use
those criteria as the completion contract.

## Schema

The public plan schema lives at `schemas/plan-v2.schema.json`.

Validate a plan with:

```bash
python3 scripts/validate-plan.py examples/plan.json
```
