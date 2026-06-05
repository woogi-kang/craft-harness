# Craft Harness Adapter: OpenHands

Use Craft Harness as a skill and agent registry for OpenHands-style workflows.

Install into an OpenHands project with:

```bash
craft install --target openhands --dest /path/to/project
```

This writes `AGENTS.md` and exports the public skill tree to `.agents/skills/`.

## Registry Export Target

The public skill catalog is generated with:

```bash
craft catalog --format json --output /tmp/craft-skill-catalog.json
```

OpenHands integrations should consume the generated catalog plus individual
`SKILL.md` files by path.

## Execution Contract

For autonomous work, prefer `plan.json` with explicit workers, dependencies, and
success criteria. Current orchestration artifacts live under
`.orchestration/{session}/`, including `events.jsonl`, worker task files,
handoffs, status files, and expected artifact paths declared by the plan.
