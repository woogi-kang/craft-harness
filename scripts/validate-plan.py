#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


SESSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _-]{0,63}$")
EVAL_TYPES = {"", "api", "ui", "fullstack", "content", "review", "custom"}


def fail(errors: list[str]) -> int:
    print("Plan validation failed:")
    for error in errors:
        print(f"  - {error}")
    return 1


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid JSON: {exc}"]

    if not isinstance(plan, dict):
        return ["plan must be a JSON object"]

    session = plan.get("session")
    if not isinstance(session, str) or not SESSION_RE.match(session):
        errors.append("session must match ^[A-Za-z0-9][A-Za-z0-9 _-]{0,63}$")

    workers = plan.get("workers")
    if not isinstance(workers, list) or not workers:
        errors.append("workers must be a non-empty array")
        return errors

    names: set[str] = set()
    for index, worker in enumerate(workers):
        prefix = f"workers[{index}]"
        if not isinstance(worker, dict):
            errors.append(f"{prefix} must be an object")
            continue
        name = worker.get("name")
        task = worker.get("task")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{prefix}.name is required")
        elif name in names:
            errors.append(f"{prefix}.name duplicates '{name}'")
        else:
            names.add(name)
        if not isinstance(task, str) or not task.strip():
            errors.append(f"{prefix}.task is required")
        for field in ("depends_on", "blocked_by", "success_criteria", "allowed_paths", "artifacts"):
            if field in worker and not isinstance(worker[field], list):
                errors.append(f"{prefix}.{field} must be an array")
        eval_type = worker.get("eval_type", "")
        if eval_type not in EVAL_TYPES:
            errors.append(f"{prefix}.eval_type must be one of {sorted(EVAL_TYPES)}")

    for index, worker in enumerate(workers):
        if not isinstance(worker, dict):
            continue
        deps = worker.get("depends_on", worker.get("blocked_by", []))
        if isinstance(deps, list):
            for dep in deps:
                if dep not in names:
                    errors.append(f"workers[{index}] depends on unknown worker '{dep}'")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate-plan.py PLAN.json", file=sys.stderr)
        return 2
    errors = validate(Path(sys.argv[1]))
    if errors:
        return fail(errors)
    print(f"Plan OK: {sys.argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
