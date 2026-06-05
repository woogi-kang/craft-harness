#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def iter_markdown(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.md")
        if ".git" not in path.relative_to(root).parts
    )


def is_external(link: str) -> bool:
    return bool(re.match(r"^[a-z][a-z0-9+.-]*:", link, re.I))


def normalize_link(link: str) -> str:
    link = link.strip()
    if link.startswith("<") and link.endswith(">"):
        link = link[1:-1]
    return link.split("#", 1)[0]


def should_check(link: str) -> bool:
    if "${{" in link:
        return False
    if is_external(link) or link.startswith("mailto:"):
        return False
    target = normalize_link(link)
    if not target:
        return False
    if target.startswith((".", "/")):
        return True
    if "/" in target:
        return True
    return Path(target).suffix != ""


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    errors: list[str] = []
    for md in iter_markdown(root):
        text = md.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            raw_link = match.group(1)
            if not should_check(raw_link):
                continue
            target = normalize_link(raw_link)
            if target.startswith("/"):
                resolved = root / target.lstrip("/")
            else:
                resolved = md.parent / target
            if not resolved.exists() and not (resolved.with_suffix(".md")).exists():
                errors.append(f"{md.relative_to(root)}: broken link -> {raw_link}")
    if errors:
        print("Broken Markdown links:")
        for error in errors:
            print(f"  {error}")
        return 1
    print("Markdown links OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
