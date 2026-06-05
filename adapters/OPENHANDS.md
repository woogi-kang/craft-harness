# Craft Harness Adapter: OpenHands

Use Craft Harness as a skill and agent registry for OpenHands-style workflows.

## Registry Export Target

The public skill catalog is generated with:

```bash
./craft catalog --format json --output docs/skill-catalog.json
```

OpenHands integrations should consume the generated catalog plus individual
`SKILL.md` files by path.

## Execution Contract

For autonomous work, prefer `plan.json` with explicit workers, dependencies, and
success criteria. Store QA artifacts under `.craft/runs/` or the run-specific
artifact directory.
