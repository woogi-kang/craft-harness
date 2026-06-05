from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from craft_harness import __version__


ROOT_MARKERS = ("agents", "skills", "commands", "templates")
FORBIDDEN_PATH_PARTS = {
    ".codex",
    ".orchestration",
    "workspace",
    "work-social",
    "logs",
    "memory",
    "sessions",
    "checkpoints",
    "plans",
    "dist",
}
FORBIDDEN_NAME_PATTERNS = (
    re.compile(r"\.env($|\.)", re.I),
    re.compile(r"settings\.local", re.I),
    re.compile(r"backup", re.I),
    re.compile(r"secret", re.I),
)
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bghp_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
)


@dataclass
class SkillInfo:
    name: str
    description: str
    path: str
    category: str
    pack: str
    status: str
    compatibility: list[str]
    required_tools: list[str]
    tags: list[str]


def find_root(start: Path | None = None) -> Path:
    env_root = os.environ.get("CRAFT_HARNESS_ROOT")
    if env_root:
        candidate = Path(env_root).expanduser().resolve()
        if all((candidate / marker).exists() for marker in ROOT_MARKERS):
            return candidate

    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if all((candidate / marker).exists() for marker in ROOT_MARKERS):
            return candidate
    return current


def parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    block = text[4:end]
    return parse_simple_yaml(block)


def parse_simple_yaml(text: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        if not raw.strip() or raw.lstrip().startswith("#"):
            i += 1
            continue
        match = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", raw)
        if not match:
            i += 1
            continue
        key, value = match.group(1), match.group(2).strip()
        if value in {"", "|", ">"}:
            nested: dict[str, Any] = {}
            items: list[str] = []
            literal: list[str] = []
            i += 1
            while i < len(lines):
                child = lines[i]
                if child and not child.startswith("  "):
                    break
                stripped = child.strip()
                if not stripped:
                    i += 1
                    continue
                if value in {"|", ">"}:
                    literal.append(stripped)
                    i += 1
                    continue
                if stripped.startswith("- "):
                    items.append(unquote(stripped[2:].strip()))
                    i += 1
                    continue
                nested_match = re.match(r"^([\w-]+)\s*:\s*(.*)$", stripped)
                if nested_match:
                    nested[nested_match.group(1)] = unquote(nested_match.group(2).strip())
                i += 1
            if literal:
                result[key] = " ".join(literal)
            elif items:
                result[key] = items
            elif nested:
                result[key] = nested
            continue
        result[key] = unquote(value)
        i += 1
    return result


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def first_heading_or_dir(text: str, path: Path) -> str:
    match = re.search(r"^#\s+(.+)$", text, re.M)
    return match.group(1).strip() if match else path.parent.name


def listify(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return [str(value)]


def infer_pack(rel: Path) -> str:
    if not rel.parts:
        return "standalone"
    if rel.parts[0] == "💻 개발" and len(rel.parts) > 1:
        return rel.parts[1]
    return rel.parts[0]


def metadata_list(frontmatter: dict[str, Any], key: str) -> list[str]:
    metadata = frontmatter.get("metadata", {})
    values: list[str] = []
    values.extend(listify(frontmatter.get(key)))
    if isinstance(metadata, dict):
        values.extend(listify(metadata.get(key)))
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def collect_skills(root: Path) -> list[SkillInfo]:
    skills_root = root / "skills"
    skills: list[SkillInfo] = []
    for skill_file in sorted(skills_root.rglob("SKILL.md")):
        text = skill_file.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(text)
        rel = skill_file.parent.relative_to(skills_root)
        category = rel.parts[0] if rel.parts else "standalone"
        metadata = frontmatter.get("metadata", {})
        status = str(frontmatter.get("status") or "beta")
        if isinstance(metadata, dict):
            status = str(metadata.get("status") or status)
        compatibility = metadata_list(frontmatter, "compatibility")
        if not compatibility:
            compatibility = ["claude", "codex", "openhands"]
        skills.append(
            SkillInfo(
                name=str(frontmatter.get("name") or first_heading_or_dir(text, skill_file)),
                description=str(frontmatter.get("description") or "").strip(),
                path=str(rel),
                category=category,
                pack=infer_pack(rel),
                status=status,
                compatibility=compatibility,
                required_tools=metadata_list(frontmatter, "required_tools"),
                tags=metadata_list(frontmatter, "tags"),
            )
        )
    return skills


def catalog_json(skills: list[SkillInfo]) -> str:
    data = {
        "schema": "craft-harness.skill-catalog.v1",
        "generated_at": date.today().isoformat(),
        "total": len(skills),
        "skills": [skill.__dict__ for skill in skills],
    }
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def catalog_markdown(skills: list[SkillInfo]) -> str:
    by_category: dict[str, list[SkillInfo]] = {}
    for skill in skills:
        by_category.setdefault(skill.category, []).append(skill)
    lines = [
        "# Skill Catalog",
        "",
        "> Auto-generated by `craft catalog --format md`.",
        "",
        f"Total skills: **{len(skills)}**",
        "",
    ]
    for category in sorted(by_category):
        group = sorted(by_category[category], key=lambda item: item.name.lower())
        lines.extend([f"## {category} ({len(group)})", ""])
        lines.extend([
            "| Skill | Description | Status | Compatibility | Pack | Tools | Path |",
            "|---|---|---|---|---|---|---|",
        ])
        for skill in group:
            compat = ", ".join(skill.compatibility) or "-"
            tools = ", ".join(skill.required_tools) or "-"
            lines.append(
                "| "
                f"{escape_pipe(skill.name)} | "
                f"{escape_pipe(shorten(skill.description, 96) or '-')} | "
                f"{skill.status} | "
                f"{compat} | "
                f"{escape_pipe(skill.pack)} | "
                f"{escape_pipe(tools)} | "
                f"`{skill.path}` |"
            )
        lines.append("")
    return "\n".join(lines)


def escape_pipe(value: str) -> str:
    return value.replace("|", "\\|")


def shorten(value: str, limit: int) -> str:
    value = " ".join(value.split())
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def write_output(content: str, output: str | None) -> None:
    if output:
        Path(output).write_text(content, encoding="utf-8")
    else:
        print(content, end="")


def command_catalog(args: argparse.Namespace) -> int:
    root = find_root()
    skills = collect_skills(root)
    content = catalog_json(skills) if args.format == "json" else catalog_markdown(skills)
    write_output(content, args.output)
    return 0


def command_doctor(_args: argparse.Namespace) -> int:
    root = find_root()
    checks: list[tuple[str, bool, str]] = []
    checks.append(("repo root", root.exists(), str(root)))
    for dirname in ROOT_MARKERS:
        checks.append((dirname, (root / dirname).is_dir(), str(root / dirname)))
    checks.append(("git", shutil.which("git") is not None, shutil.which("git") or "missing"))
    checks.append(("python", sys.version_info >= (3, 11), sys.version.split()[0]))

    skills = collect_skills(root)
    checks.append(("skills", len(skills) > 0, str(len(skills))))
    checks.append(("agents", any((root / "agents").rglob("*.md")), "present"))
    checks.append(("commands", any((root / "commands").rglob("*.md")), "present"))

    ok = True
    print("Craft Harness Doctor")
    print("====================")
    for name, passed, detail in checks:
        ok = ok and passed
        mark = "OK" if passed else "FAIL"
        print(f"[{mark}] {name}: {detail}")
    return 0 if ok else 1


def validate_frontmatter(root: Path) -> list[str]:
    errors: list[str] = []
    for skill_file in sorted((root / "skills").rglob("SKILL.md")):
        text = skill_file.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(text)
        if not frontmatter:
            errors.append(f"{skill_file.relative_to(root)}: missing YAML frontmatter")
            continue
        if not frontmatter.get("name"):
            errors.append(f"{skill_file.relative_to(root)}: missing frontmatter field 'name'")
        if not frontmatter.get("description"):
            errors.append(f"{skill_file.relative_to(root)}: missing frontmatter field 'description'")
    return errors


def validate_forbidden_paths(root: Path) -> list[str]:
    errors: list[str] = []
    skip_dirs = {".git", ".ruff_cache", "__pycache__", ".pytest_cache"}
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if any(part in skip_dirs for part in rel.parts):
            continue
        if path.name.startswith(".env.example"):
            continue
        if any(part in FORBIDDEN_PATH_PARTS for part in rel.parts):
            errors.append(f"forbidden path present: {rel}")
        if any(pattern.search(path.name) for pattern in FORBIDDEN_NAME_PATTERNS):
            errors.append(f"forbidden file/dir name present: {rel}")
    return errors


def validate_secret_scan(root: Path) -> list[str]:
    errors: list[str] = []
    binary_suffixes = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip", ".lock"}
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if ".git" in rel.parts or path.is_dir() or path.suffix.lower() in binary_suffixes:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"possible secret in {rel}: {pattern.pattern}")
                break
    return errors


def command_validate(args: argparse.Namespace) -> int:
    root = find_root()
    errors = []
    errors.extend(validate_frontmatter(root))
    errors.extend(validate_forbidden_paths(root))
    if not args.skip_secret_scan:
        errors.extend(validate_secret_scan(root))

    print("Craft Harness Validation")
    print("========================")
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("OK: skills, public file set, and secret scan passed")
    return 0


def copy_or_link(src: Path, dest: Path, mode: str, *, force: bool = False, dry_run: bool = False) -> None:
    action = "link" if mode == "link" else "copy"
    if dest.exists() or dest.is_symlink():
        if dry_run:
            verb = "replace" if force else "refuse existing"
            print(f"Would {verb} {dest} with {action} from {src}")
            return
        if not force:
            print(f"Refusing to replace existing path: {dest}", file=sys.stderr)
            print("Rerun with --force to replace it, or choose a different --dest.", file=sys.stderr)
            raise SystemExit(1)
    elif dry_run:
        print(f"Would {action} {src} -> {dest}")
        return

    if dest.exists() or dest.is_symlink():
        if dest.is_dir() and not dest.is_symlink():
            shutil.rmtree(dest)
        else:
            dest.unlink()
    if mode == "link":
        dest.symlink_to(src)
    else:
        if src.is_dir():
            shutil.copytree(src, dest)
        else:
            shutil.copy2(src, dest)


def command_install(args: argparse.Namespace) -> int:
    root = find_root()
    target = args.target
    mode = args.mode
    force = args.force
    dry_run = args.dry_run
    if target == "claude":
        dest = Path(args.dest or Path.home() / ".claude")
        if dry_run:
            print(f"Would install Claude assets to {dest} ({mode})")
        else:
            dest.mkdir(parents=True, exist_ok=True)
        for name in ("agents", "skills", "commands"):
            copy_or_link(root / name, dest / name, mode, force=force, dry_run=dry_run)
        if not dry_run:
            print(f"Installed Claude assets to {dest} ({mode})")
        return 0

    dest = Path(args.dest or Path.cwd())
    if dry_run:
        print(f"Would install {target} adapter into {dest}")
    else:
        dest.mkdir(parents=True, exist_ok=True)
    if target == "openhands":
        adapter_file = root / "adapters" / "OPENHANDS.md"
        copy_or_link(adapter_file, dest / "AGENTS.md", "copy", force=force, dry_run=dry_run)
        skills_dest = dest / ".agents" / "skills"
        if not dry_run:
            skills_dest.parent.mkdir(parents=True, exist_ok=True)
        copy_or_link(root / "skills", skills_dest, mode, force=force, dry_run=dry_run)
        if not dry_run:
            print(f"Installed openhands adapter to {dest / 'AGENTS.md'}")
            print(f"Installed OpenHands skills to {skills_dest} ({mode})")
        return 0

    adapter_file = {
        "codex": root / "adapters" / "AGENTS.md",
        "gemini": root / "adapters" / "GEMINI.md",
        "opencode": root / "adapters" / "OPENCODE.md",
    }[target]
    if not adapter_file.exists():
        print(f"Missing adapter template: {adapter_file}", file=sys.stderr)
        return 1
    output_name = {
        "codex": "AGENTS.md",
        "gemini": "GEMINI.md",
        "opencode": "AGENTS.md",
    }[target]
    copy_or_link(adapter_file, dest / output_name, "copy", force=force, dry_run=dry_run)
    if not dry_run:
        print(f"Installed {target} adapter to {dest / output_name}")
    return 0


def command_orchestrate(args: argparse.Namespace) -> int:
    root = find_root()
    script = root / "scripts" / "orchestrate-worktrees.py"
    if not script.exists():
        print(f"Missing orchestrator script: {script}", file=sys.stderr)
        return 1

    caller_cwd = Path(os.environ.get("CRAFT_HARNESS_CALLER_CWD") or Path.cwd()).resolve()
    plan_path = Path(args.plan).expanduser()
    if plan_path.is_absolute():
        resolved_plan = plan_path
    elif (caller_cwd / plan_path).exists():
        resolved_plan = caller_cwd / plan_path
    elif (root / plan_path).exists():
        resolved_plan = root / plan_path
    else:
        resolved_plan = caller_cwd / plan_path

    cmd = [sys.executable, str(script), str(resolved_plan)]
    if args.execute:
        cmd.append("--execute")
    elif args.watch:
        cmd.append("--watch")
    elif args.status:
        cmd.append("--status")
    elif args.cleanup:
        cmd.append("--cleanup")
    if args.force:
        cmd.append("--force")
    return subprocess.call(cmd, cwd=caller_cwd)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="craft",
        description="Craft Harness CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  craft doctor
  craft catalog --format md --output docs/skill-catalog.md
  craft install --target openhands --dest /path/to/project
  craft orchestrate examples/plan.json --dry-run
""",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser(
        "doctor",
        help="Check local harness health",
        description="Check repo shape, Python version, git, and bundled asset directories.",
    )
    doctor.set_defaults(func=command_doctor)

    catalog = sub.add_parser(
        "catalog",
        help="Generate a skill catalog",
        description="Generate a human or machine readable catalog from skills/**/SKILL.md frontmatter.",
    )
    catalog.add_argument("--format", choices=("md", "json"), default="md", help="Output format")
    catalog.add_argument("--output", help="Write output to a file instead of stdout")
    catalog.set_defaults(func=command_catalog)

    validate = sub.add_parser(
        "validate",
        help="Validate public repo contents",
        description="Validate skill frontmatter, public file boundaries, and common secret patterns.",
    )
    validate.add_argument("--skip-secret-scan", action="store_true", help="Skip high-confidence secret scan")
    validate.set_defaults(func=command_validate)

    install = sub.add_parser(
        "install",
        help="Install adapters or runtime assets",
        description=(
            "Install runtime guidance. Claude and OpenHands receive skill assets; "
            "Codex, Gemini, and OpenCode receive adapter guidance files."
        ),
    )
    install.add_argument(
        "--target",
        choices=("claude", "codex", "gemini", "opencode", "openhands"),
        required=True,
        help="Runtime adapter to install",
    )
    install.add_argument(
        "--mode",
        choices=("copy", "link"),
        default="copy",
        help="Use copy for stable installs or link for local development (default: copy)",
    )
    install.add_argument(
        "--dest",
        help="Destination project or runtime config directory (default: current directory; Claude uses ~/.claude)",
    )
    install.add_argument("--dry-run", action="store_true", help="Show planned files without writing")
    install.add_argument("--force", action="store_true", help="Replace existing adapter/assets")
    install.set_defaults(func=command_install)

    orchestrate = sub.add_parser(
        "orchestrate",
        help="Run the worktree orchestrator",
        description="Preview, execute, watch, inspect, or clean up a worktree worker DAG.",
    )
    orchestrate.add_argument("plan", help="Path to a plan JSON file")
    orchestrate.add_argument("--dry-run", action="store_true", help="Default mode; kept for readability")
    orchestrate.add_argument("--execute", action="store_true")
    orchestrate.add_argument("--watch", action="store_true")
    orchestrate.add_argument("--status", action="store_true")
    orchestrate.add_argument("--cleanup", action="store_true")
    orchestrate.add_argument("--force", action="store_true", help="With --cleanup, allow destructive teardown")
    orchestrate.set_defaults(func=command_orchestrate)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
