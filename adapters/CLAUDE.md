# Craft Harness Adapter: Claude

Use Craft Harness assets from this repository:

- agents: `agents/`
- skills: `skills/`
- commands: `commands/`
- templates: `templates/`

## Operating Rules

- Prefer the most specific skill or agent pack for the task.
- Use `craft doctor` before debugging installation issues.
- Use `craft validate` before publishing changes.
- For multi-agent work, create or review a `plan.json` and run
  `craft orchestrate PLAN --dry-run` before execution.
- Treat `success_criteria` as the contract for completion.

## Output Style

Default to `output-styles/concise-engineer.md`: direct summary, changed files,
verification, and next action.
