# Craft Harness Adapter: Codex

This project uses Craft Harness for reusable agents, skills, commands, and
worktree orchestration.

## Conventions

- Read `README.md`, `ROADMAP.md`, and relevant files under `skills/` before
  changing harness behavior.
- Keep changes scoped to the requested pack or command.
- Run `./craft validate` after editing skills, agents, commands, or adapters.
- Run `./craft catalog --format json --output /tmp/craft-catalog.json` after
  changing skills.
- Run `./craft orchestrate examples/plan.json --dry-run` after changing the
  orchestrator.

## Public Repo Rules

- Do not add local settings, logs, memory, sessions, checkpoints, private
  workspaces, or secrets.
- New skills need YAML frontmatter with `name` and `description`.
- Public output should be concise and evidence-based.
