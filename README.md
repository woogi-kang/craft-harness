# Craft Harness

Craft Harness is a multi-runtime agent harness for teams that use several coding
agents at once. It packages reusable agents, skills, commands, worktree
orchestration, output styles, and verification contracts for Claude, Codex,
Gemini, OpenCode, and OpenHands-style workflows.

This repository is intentionally split from `claude-craft`. It starts as a clean
open-source staging repo with only the Core and Dev packs.

## Why This Exists

Most agent tools optimize for one runtime. Craft Harness focuses on the layer
above them:

- reusable agent and skill packs
- runtime adapters for common agent guidance files
- worktree-based DAG execution
- success criteria and QA contracts
- concise human output plus machine-readable sidecars
- public validation and install checks

## Current Packs

| Pack | Contents |
| --- | --- |
| Core | CLI, adapters, orchestration scripts, output styles, validation |
| Dev | FastAPI, Next.js, Flutter, browser test, TDD, build repair, live QA |
| Design QA | `design-harness`, styling, design-system, visual QA guidance |
| Review | code, architecture, security, design, content review agents |

Optional Korea, legal, finance, marketing, planning, and content packs are not
included in this initial public scope.

## Quick Start

```bash
git clone https://github.com/woogi-kang/craft-harness.git
cd craft-harness
python3 -m pip install -e .
craft doctor
craft validate
craft catalog --format md --output docs/skill-catalog.md
craft orchestrate examples/plan.json --dry-run
```

You can also run the local wrapper without installing:

```bash
./craft doctor
./craft catalog --format json
```

## Runtime Adapters

```bash
craft install --target claude --mode copy
craft install --target codex --dest /path/to/project
craft install --target gemini --dest /path/to/project
craft install --target opencode --dest /path/to/project
```

Claude installation copies `agents/`, `skills/`, and `commands/` into
`~/.claude`. Codex, Gemini, and OpenCode targets install adapter guidance files
into the destination project.

## Orchestration

Craft Harness uses isolated git worktrees and tmux windows for parallel workers.

```bash
craft orchestrate examples/plan.json --dry-run
craft orchestrate examples/plan.json --execute
craft orchestrate examples/plan.json --watch
```

The public plan format supports:

- `session`
- `base_ref`
- `workers[].name`
- `workers[].task`
- `workers[].depends_on`
- `workers[].success_criteria`
- `workers[].eval_type`

## Output Styles

Output styles live in `output-styles/` and define concise, predictable final
responses for common work modes:

- `concise-engineer`
- `research-brief`
- `qa-report`
- `executive-summary`

The principle is human-readable Markdown first, machine-readable run artifacts
second.

## Validation

```bash
craft doctor
craft validate
```

Validation checks skill frontmatter, public file exclusions, and high-confidence
secret patterns. CI also checks catalog generation and local Markdown links.

## License

Apache-2.0. Contributions are accepted under the Developer Certificate of Origin
as described in `CONTRIBUTING.md`.
