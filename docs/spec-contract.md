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

Top-level required fields:

- `session`: short run name used for branches, tmux session, and coordination files.
- `workers`: one or more worker objects.

Top-level optional fields:

- `base_ref`: git ref used when creating worktrees. Defaults to `HEAD`.
- `launcher`: shell command template used to start each worker. Defaults to
  `cd {worktree} && cat {task_file} | claude -p -`.

Worker required fields:

- `name`: unique worker name.
- `task`: the concrete assignment written into the worker's `task.md`.

Worker optional fields:

- `depends_on`: worker names that must complete before this worker starts.
- `blocked_by`: template-friendly alias for `depends_on`.
- `success_criteria`: checklist copied into `task.md` and used by QA workers.
- `eval_type`: one of `api`, `ui`, `fullstack`, `content`, `review`, `custom`, or empty.
- `allowed_paths`: file or directory scopes copied into `task.md`.
- `artifacts`: expected output files copied into `task.md`.

The orchestrator writes each worker's criteria, allowed paths, and expected
artifacts into `task.md`. QA workers use those fields as the completion
contract.

Custom `launcher` values execute as shell inside tmux. Treat shared plans like
code: review the launcher before `--execute`.

## Schema

The public plan schema lives at `schemas/plan-v2.schema.json`.

Validate a plan with:

```bash
python3 scripts/validate-plan.py examples/plan.json
```
