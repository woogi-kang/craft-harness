#!/usr/bin/env python3
"""orchestrate-worktrees.py — tmux worktree orchestration for parallel Claude Code instances.

Creates git worktrees and tmux panes so multiple Claude instances can work on
independent tasks simultaneously, with optional dependency ordering (DAG).

Usage:
    python3 scripts/orchestrate-worktrees.py plan.json              # dry-run
    python3 scripts/orchestrate-worktrees.py plan.json --execute    # run
    python3 scripts/orchestrate-worktrees.py plan.json --status     # check
    python3 scripts/orchestrate-worktrees.py plan.json --watch      # auto-spawn on dep completion
    python3 scripts/orchestrate-worktrees.py plan.json --cleanup    # teardown
"""

import argparse
import json
import re
import shlex
import shutil
import subprocess
import sys
import textwrap
import time
import unicodedata
from pathlib import Path

SAFE_NAME_RE = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9 _-]{0,63}$')


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

KNOWN_STATES = frozenset({"not_started", "waiting", "running", "completed", "failed"})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slugify(text: str, fallback_index: int = 0) -> str:
    """Convert text to a filesystem/branch-safe slug.

    ASCII text is lowercased and cleaned.  Non-ASCII (e.g. Korean) is dropped;
    if the result is empty we fall back to ``w{fallback_index}``.
    """
    # Normalize unicode, strip accents
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_only = nfkd.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_only.lower()).strip("-")
    return slug if slug else f"w{fallback_index}"


def run(cmd: list[str], *, check: bool = True, capture: bool = True, **kw) -> subprocess.CompletedProcess:
    """Run a subprocess with sensible defaults."""
    return subprocess.run(
        cmd,
        check=check,
        capture_output=capture,
        text=True,
        **kw,
    )


def git(*args: str, **kw) -> subprocess.CompletedProcess:
    return run(["git", *args], **kw)


def tmux(*args: str, **kw) -> subprocess.CompletedProcess:
    return run(["tmux", *args], **kw)


def ensure_command(name: str) -> None:
    if shutil.which(name) is None:
        die(f"'{name}' is not installed or not in PATH.")


def die(msg: str, code: int = 1) -> None:
    print(f"\033[31mError:\033[0m {msg}", file=sys.stderr)
    sys.exit(code)


def info(msg: str) -> None:
    print(f"\033[36m▸\033[0m {msg}")


def success(msg: str) -> None:
    print(f"\033[32m✓\033[0m {msg}")


def warn(msg: str) -> None:
    print(f"\033[33m!\033[0m {msg}")


# ---------------------------------------------------------------------------
# Status file helpers
# ---------------------------------------------------------------------------

def read_worker_state(worker) -> str:
    """Read worker state from status.md. Handles JSON and legacy text."""
    if not worker.status_file.exists():
        return "unknown"
    text = worker.status_file.read_text(encoding="utf-8").strip()
    if not text:
        return "unknown"
    # Try JSON first (forward compat)
    try:
        data = json.loads(text)
        state = data.get("state", "unknown")
    except (json.JSONDecodeError, AttributeError):
        # Legacy plain-text format
        state = text
    return state if state in KNOWN_STATES else "unknown"


def write_state(path: Path, state: str) -> None:
    """Write status as plain text (backward compatible)."""
    path.write_text(f"{state}\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# DAG validation & ordering
# ---------------------------------------------------------------------------

def validate_dag(workers: list) -> None:
    """Validate dependency references exist and detect cycles."""
    names = {w.name for w in workers}

    # Check references
    for w in workers:
        for dep in w.depends_on:
            if dep not in names:
                die(f"Worker '{w.name}' depends on unknown worker '{dep}'")

    # Cycle detection via DFS coloring
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {w.name: WHITE for w in workers}
    dep_map = {w.name: w.depends_on for w in workers}

    def dfs(name: str) -> None:
        color[name] = GRAY
        for dep in dep_map[name]:
            if color[dep] == GRAY:
                die(f"Dependency cycle detected: '{name}' → '{dep}'")
            if color[dep] == WHITE:
                dfs(dep)
        color[name] = BLACK

    for w in workers:
        if color[w.name] == WHITE:
            dfs(w.name)


def topological_sort(workers: list) -> list:
    """Return workers in dependency order (dependencies first)."""
    name_to_worker = {w.name: w for w in workers}
    visited: set[str] = set()
    order: list = []

    def visit(name: str) -> None:
        if name in visited:
            return
        visited.add(name)
        for dep in name_to_worker[name].depends_on:
            visit(dep)
        order.append(name_to_worker[name])

    for w in workers:
        visit(w.name)
    return order


def partition_workers(workers: list) -> tuple[list, list]:
    """Partition not-yet-started workers into (ready, blocked).

    Ready = no deps or all deps completed.
    Blocked = has unmet deps (including failed deps → mark as failed).
    Already running/completed/failed workers are excluded.
    """
    states = {w.name: read_worker_state(w) for w in workers}
    ready, blocked = [], []

    for w in workers:
        state = states[w.name]
        if state in ("running", "completed", "failed", "unknown"):
            continue  # already handled or unresolvable

        # Check if any dependency failed → propagate failure
        failed_deps = [d for d in w.depends_on if states.get(d) == "failed"]
        if failed_deps:
            write_state(w.status_file, "failed")
            warn(f"Worker '{w.name}' marked failed: dependency {', '.join(failed_deps)} failed")
            continue

        if not w.depends_on:
            ready.append(w)
        elif all(states.get(d) == "completed" for d in w.depends_on):
            ready.append(w)
        else:
            blocked.append(w)
    return ready, blocked


def has_dag(workers: list) -> bool:
    """Check if any worker has dependencies."""
    return any(w.depends_on for w in workers)


# ---------------------------------------------------------------------------
# Plan loading & validation
# ---------------------------------------------------------------------------

def load_plan(path: str) -> dict:
    plan_path = Path(path)
    if not plan_path.is_file():
        die(f"Plan file not found: {path}")
    try:
        with open(plan_path, encoding="utf-8") as f:
            plan = json.load(f)
    except json.JSONDecodeError as exc:
        die(f"Invalid JSON in {path}: {exc}")

    # Required fields
    for key in ("session", "workers"):
        if key not in plan:
            die(f"Plan is missing required key: '{key}'")

    if not isinstance(plan["workers"], list) or len(plan["workers"]) == 0:
        die("Plan must have at least one worker.")

    # Validate session name
    if not SAFE_NAME_RE.match(plan["session"]):
        die(f"Invalid session name: '{plan['session']}'. Use alphanumeric, hyphen, underscore only.")

    # Validate workers
    seen_names: set[str] = set()
    for i, w in enumerate(plan["workers"]):
        if "name" not in w or "task" not in w:
            die(f"Worker #{i} is missing 'name' or 'task'.")
        if w["name"] in seen_names:
            die(f"Duplicate worker name: '{w['name']}'")
        seen_names.add(w["name"])
        # Normalize blocked_by → depends_on (TOML template compat)
        if "blocked_by" in w and "depends_on" not in w:
            w["depends_on"] = w.pop("blocked_by")

    # Defaults
    plan.setdefault("base_ref", "HEAD")
    plan.setdefault(
        "launcher",
        "cd {worktree} && cat {task_file} | claude -p -",
    )

    return plan


# ---------------------------------------------------------------------------
# Derived paths / names
# ---------------------------------------------------------------------------

class WorkerInfo:
    """Derived names and paths for a single worker."""

    def __init__(self, worker: dict, index: int, plan: dict, repo_root: Path):
        self.name: str = worker["name"]
        self.task: str = worker["task"]
        self.slug: str = slugify(self.name, fallback_index=index)
        self.session: str = plan["session"]
        self.tmux_session: str = f"orch-{self.session}"
        self.branch: str = f"orch-{self.session}-{self.slug}"
        self.repo_name: str = repo_root.name
        self.worktree_path: Path = repo_root.parent / f"{self.repo_name}-{self.session}-{self.slug}"
        self.coord_dir: Path = repo_root / ".orchestration" / self.session / self.slug
        self.task_file: Path = self.coord_dir / "task.md"
        self.handoff_file: Path = self.coord_dir / "handoff.md"
        self.status_file: Path = self.coord_dir / "status.md"
        self.base_ref: str = plan.get("base_ref", "HEAD")
        self.launcher_template: str = plan.get(
            "launcher",
            "cd {worktree} && cat {task_file} | claude -p -",
        )
        self.depends_on: list[str] = worker.get("depends_on", [])
        self.success_criteria: list[str] = worker.get("success_criteria", [])
        self.eval_type: str = worker.get("eval_type", "")

    def launcher_cmd(self) -> str:
        """Expand template variables in the launcher string with shell escaping."""
        return (
            self.launcher_template
            .replace("{worker}", shlex.quote(self.name))
            .replace("{session}", shlex.quote(self.session))
            .replace("{worktree}", shlex.quote(str(self.worktree_path)))
            .replace("{branch}", shlex.quote(self.branch))
            .replace("{task}", shlex.quote(self.task))
            .replace("{task_file}", shlex.quote(str(self.task_file)))
            .replace("{handoff_file}", shlex.quote(str(self.handoff_file)))
        )


def build_workers(plan: dict, repo_root: Path) -> list[WorkerInfo]:
    return [
        WorkerInfo(w, i, plan, repo_root)
        for i, w in enumerate(plan["workers"])
    ]


# ---------------------------------------------------------------------------
# Coordination files
# ---------------------------------------------------------------------------

TASK_TEMPLATE = textwrap.dedent("""\
    # Task: {worker_name}

    ## Session
    - Session: {session}
    - Worker: {worker_name}
    - Branch: {branch}
    - Worktree: {worktree_path}
    {dependency_section}{success_criteria_section}
    ## Objective
    {task_description}

    ## Coordination
    - Status: .orchestration/{session}/{worker_slug}/status.md
    - Handoff: .orchestration/{session}/{worker_slug}/handoff.md

    ## Instructions
    - Focus only on your assigned task
    - Do not modify files outside your scope
    - Write a summary of your work when done
""")

HANDOFF_TEMPLATE = textwrap.dedent("""\
    # Handoff: {worker_name}

    ## Summary
    _Pending_

    ## Files Changed
    _Pending_

    ## Tests/Verification
    _Pending_

    ## Follow-up Items
    _Pending_
""")


def write_coordination_files(worker: WorkerInfo) -> None:
    worker.coord_dir.mkdir(parents=True, exist_ok=True)

    # Build dependency section
    if worker.depends_on:
        deps = ", ".join(worker.depends_on)
        dependency_section = f"\n    ## Dependencies\n    Blocked by: {deps}\n"
    else:
        dependency_section = ""

    # Build success criteria section
    if worker.success_criteria:
        criteria_lines = "\n".join(f"    - [ ] {c}" for c in worker.success_criteria)
        success_criteria_section = f"\n    ## Success Criteria\n{criteria_lines}\n"
    else:
        success_criteria_section = ""

    worker.task_file.write_text(
        TASK_TEMPLATE.format(
            worker_name=worker.name,
            session=worker.session,
            branch=worker.branch,
            worktree_path=worker.worktree_path,
            task_description=worker.task,
            worker_slug=worker.slug,
            dependency_section=dependency_section,
            success_criteria_section=success_criteria_section,
        ),
        encoding="utf-8",
    )

    worker.handoff_file.write_text(
        HANDOFF_TEMPLATE.format(worker_name=worker.name),
        encoding="utf-8",
    )

    # Initial state: 'waiting' if has deps, 'not_started' otherwise
    initial = "waiting" if worker.depends_on else "not_started"
    write_state(worker.status_file, initial)


# ---------------------------------------------------------------------------
# Git worktree management
# ---------------------------------------------------------------------------

def create_worktree(worker: WorkerInfo) -> None:
    if worker.worktree_path.exists():
        warn(f"Worktree already exists: {worker.worktree_path}")
        return
    git(
        "worktree", "add",
        "-b", worker.branch,
        str(worker.worktree_path),
        worker.base_ref,
    )
    success(f"Worktree created: {worker.worktree_path}")


def remove_worktree(worker: WorkerInfo) -> None:
    if worker.worktree_path.exists():
        git("worktree", "remove", "--force", str(worker.worktree_path), check=False)
        info(f"Removed worktree: {worker.worktree_path}")
    else:
        info(f"Worktree already gone: {worker.worktree_path}")

    # Delete the branch if it still exists
    result = git("branch", "--list", worker.branch)
    if worker.branch in result.stdout:
        git("branch", "-D", worker.branch, check=False)
        info(f"Deleted branch: {worker.branch}")


# ---------------------------------------------------------------------------
# tmux management
# ---------------------------------------------------------------------------

def tmux_session_exists(name: str) -> bool:
    result = tmux("has-session", "-t", name, check=False)
    return result.returncode == 0


def create_tmux_session(workers: list[WorkerInfo], *, remain_on_exit: bool = False) -> None:
    """Create tmux session and launch given workers."""
    if not workers:
        return

    session_name = workers[0].tmux_session

    if tmux_session_exists(session_name):
        die(f"tmux session '{session_name}' already exists. Use --cleanup first or pick a different session name.")

    # Create session with the first worker
    first = workers[0]
    write_state(first.status_file, "running")
    tmux(
        "new-session",
        "-d",                        # detached
        "-s", session_name,          # session name
        "-n", first.slug,            # first window name
    )

    # Keep panes alive after process exit (for --watch pane death detection)
    if remain_on_exit:
        tmux("set-option", "-t", session_name, "remain-on-exit", "on")

    cmd = first.launcher_cmd()
    tmux("send-keys", "-t", f"{session_name}:{first.slug}", cmd, "Enter")
    success(f"Started worker: {first.name} ({first.slug})")

    # Additional windows
    for w in workers[1:]:
        add_worker_to_tmux(w)


def add_worker_to_tmux(worker: WorkerInfo) -> None:
    """Add a single worker as a new window in an existing tmux session."""
    session_name = worker.tmux_session
    if not tmux_session_exists(session_name):
        warn(f"tmux session '{session_name}' does not exist, cannot add worker.")
        return

    write_state(worker.status_file, "running")
    tmux("new-window", "-t", session_name, "-n", worker.slug)
    cmd = worker.launcher_cmd()
    tmux("send-keys", "-t", f"{session_name}:{worker.slug}", cmd, "Enter")
    success(f"Started worker: {worker.name} ({worker.slug})")


def kill_tmux_session(session_name: str) -> None:
    if tmux_session_exists(session_name):
        tmux("kill-session", "-t", session_name)
        info(f"Killed tmux session: {session_name}")
    else:
        info(f"tmux session not found: {session_name}")


def detect_completed_panes(session_name: str) -> dict[str, int]:
    """Return {window_name: exit_code} for panes whose process has exited."""
    if not tmux_session_exists(session_name):
        return {}

    result = tmux(
        "list-panes", "-s", "-t", session_name,
        "-F", "#{window_name} #{pane_dead} #{pane_dead_status}",
        check=False,
    )
    completed: dict[str, int] = {}
    if result.returncode == 0:
        for line in result.stdout.strip().splitlines():
            parts = line.split(None, 2)
            if len(parts) >= 2 and parts[1] == "1":
                exit_code = int(parts[2]) if len(parts) == 3 else 0
                completed[parts[0]] = exit_code
    return completed


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

STATE_COLORS = {
    "completed": "\033[32m",   # green
    "running": "\033[36m",     # cyan
    "waiting": "\033[33m",     # yellow
    "not_started": "\033[37m", # white
    "failed": "\033[31m",      # red
    "unknown": "\033[35m",     # magenta
}
RESET = "\033[0m"


# ---------------------------------------------------------------------------
# Modes
# ---------------------------------------------------------------------------

def mode_dry_run(plan: dict, workers: list[WorkerInfo]) -> None:
    """Print what would happen without executing anything."""
    session = plan["session"]
    tmux_name = f"orch-{session}"
    is_dag = has_dag(workers)

    print()
    print(f"{'='*60}")
    print(f"  Orchestration Plan: {session}")
    print(f"{'='*60}")
    print()
    print(f"  tmux session : {tmux_name}")
    print(f"  base ref     : {plan.get('base_ref', 'HEAD')}")
    print(f"  workers      : {len(workers)}")
    if is_dag:
        print(f"  dependencies : yes (use --watch for auto-spawn)")
    print(f"  launcher     : {plan.get('launcher', '(default)')}")
    print()

    if is_dag:
        print(f"  {'Worker':<16} {'Slug':<16} {'Depends On':<24} Worktree")
        print(f"  {'─'*15:<16} {'─'*15:<16} {'─'*23:<24} {'─'*40}")
        for w in workers:
            deps = ", ".join(w.depends_on) if w.depends_on else "—"
            print(f"  {w.name:<16} {w.slug:<16} {deps:<24} {w.worktree_path}")
        print()

        # DAG visualization
        print("  Execution Order:")
        sorted_workers = topological_sort(workers)
        for i, w in enumerate(sorted_workers):
            arrow = "→ " if w.depends_on else "  "
            deps_str = f" (after {', '.join(w.depends_on)})" if w.depends_on else " (immediate)"
            print(f"    {i+1}. {arrow}{w.name}{deps_str}")
    else:
        print(f"  {'Worker':<16} {'Slug':<16} {'Branch':<32} Worktree")
        print(f"  {'─'*15:<16} {'─'*15:<16} {'─'*31:<32} {'─'*40}")
        for w in workers:
            print(f"  {w.name:<16} {w.slug:<16} {w.branch:<32} {w.worktree_path}")

    print()
    print(f"  Coordination dir: .orchestration/{session}/")
    print()
    print("  Run with --execute to start, or --status / --cleanup for existing sessions.")
    if is_dag:
        print("  After --execute, run --watch in another terminal for auto dependency spawning.")
    print()


def mode_execute(plan: dict, workers: list[WorkerInfo], repo_root: Path) -> None:
    """Full execution: coordination files, worktrees, tmux session."""
    session = plan["session"]
    tmux_name = f"orch-{session}"
    is_dag = has_dag(workers)

    # Pre-flight checks
    if tmux_session_exists(tmux_name):
        die(f"Session '{tmux_name}' already running. Use --status to check or --cleanup first.")
    stale_worktrees = [w for w in workers if w.worktree_path.exists()]
    stale_worker_dirs = [w for w in workers if w.coord_dir.exists()]
    if stale_worker_dirs or stale_worktrees:
        die(f"Stale artifacts from previous '{session}' run. Run --cleanup first or use a different session name.")

    info(f"Starting orchestration: {session}")
    print()

    # 1. Coordination files (all workers)
    info("Creating coordination files...")
    for w in workers:
        write_coordination_files(w)
    success(f"Coordination directory: .orchestration/{session}/")
    print()

    # 2. Git worktrees (all workers — need them ready for when deps are met)
    info("Creating git worktrees...")
    for w in workers:
        create_worktree(w)
    git("worktree", "prune")
    print()

    # 3. Copy coordination files into each worktree
    info("Syncing coordination files to worktrees...")
    for w in workers:
        dst = w.worktree_path / ".orchestration" / session / w.slug
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copy2(w.task_file, dst / "task.md")
        shutil.copy2(w.handoff_file, dst / "handoff.md")
        shutil.copy2(w.status_file, dst / "status.md")
    print()

    # 4. tmux — DAG-aware: only spawn ready workers
    session_created = False
    if is_dag:
        ready, blocked = partition_workers(workers)
        info(f"DAG mode: {len(ready)} ready, {len(blocked)} blocked")
        if ready:
            info("Creating tmux session with ready workers...")
            create_tmux_session(ready, remain_on_exit=True)
            session_created = True
        else:
            die("DAG deadlock: all workers are blocked with no initially-ready worker.")
        if blocked:
            print()
            info("Blocked workers (waiting for dependencies):")
            for w in blocked:
                deps = ", ".join(w.depends_on)
                info(f"  {w.name} ← waiting for: {deps}")
    else:
        info("Creating tmux session...")
        create_tmux_session(workers)
        session_created = True
    print()

    if session_created:
        success("Orchestration running!")
        print()
        print(f"  Attach:  tmux attach -t {tmux_name}")
        print(f"  Status:  python3 scripts/orchestrate-worktrees.py {sys.argv[1]} --status")
        if is_dag:
            print(f"  Watch:   python3 scripts/orchestrate-worktrees.py {sys.argv[1]} --watch")
        print(f"  Cleanup: python3 scripts/orchestrate-worktrees.py {sys.argv[1]} --cleanup")
        print()


def mode_status(plan: dict, workers: list[WorkerInfo]) -> None:
    """Show status of a running session (read-only — does not mutate status files)."""
    session = plan["session"]
    tmux_name = f"orch-{session}"
    is_dag = has_dag(workers)

    print()
    print(f"=== Session: {session} ===")
    print()

    # Check tmux session
    session_alive = tmux_session_exists(tmux_name)
    if not session_alive:
        warn(f"tmux session '{tmux_name}' is not running.")
        warn("States below are from status files and may be stale.")
        print()

    # Pane info
    pane_map: dict[str, str] = {}
    if session_alive:
        result = tmux(
            "list-windows", "-t", tmux_name,
            "-F", "#{window_name} #{pane_id}",
            check=False,
        )
        if result.returncode == 0:
            for line in result.stdout.strip().splitlines():
                parts = line.split(None, 1)
                if len(parts) == 2:
                    pane_map[parts[0]] = parts[1]

    # Detect completed panes (read-only — for display only, no writes)
    dead_panes = detect_completed_panes(tmux_name) if session_alive else {}

    # Collect states (display only — no file writes)
    states: dict[str, str] = {}
    for w in workers:
        state = read_worker_state(w)
        # Infer state from tmux info (display only)
        if state == "running" and w.slug in dead_panes:
            exit_code = dead_panes[w.slug]
            state = "completed" if exit_code == 0 else "failed"
        elif state == "running" and not session_alive:
            state = "unknown"
        states[w.name] = state

    if is_dag:
        # DAG visualization
        print("  DAG Status:")
        print()
        sorted_workers = topological_sort(workers)
        for w in sorted_workers:
            state = states.get(w.name, "unknown")
            color = STATE_COLORS.get(state, "")
            pane = pane_map.get(w.slug, "—")

            # Build dependency arrows
            if w.depends_on:
                arrow = " ← " + ", ".join(w.depends_on)
            else:
                arrow = ""

            print(f"  {color}{w.name:<16} [{state:<10}]{RESET}  pane:{pane:<8}{arrow}")

        print()

        # Summary
        total = len(workers)
        counts: dict[str, int] = {}
        for s in states.values():
            counts[s] = counts.get(s, 0) + 1

        parts = []
        for label in ("completed", "running", "waiting", "not_started", "failed", "unknown"):
            if label in counts:
                parts.append(f"{counts[label]} {label}")
        print(f"  Tasks: {total} total | {' | '.join(parts)}")
    else:
        # Flat table with colors
        print(f"  {'Worker':<16} {'Branch':<32} {'Status':<14} Pane")
        print(f"  {'─'*15:<16} {'─'*31:<32} {'─'*13:<14} {'─'*8}")
        for w in workers:
            state = states.get(w.name, "unknown")
            color = STATE_COLORS.get(state, "")
            pane = pane_map.get(w.slug, "—")
            print(f"  {w.name:<16} {w.branch:<32} {color}{state:<14}{RESET} {pane}")

    print()
    print(f"  Coordination: .orchestration/{session}/")
    if session_alive:
        print(f"  Attach: tmux attach -t {tmux_name}")
    print()


def mode_watch(plan: dict, workers: list[WorkerInfo], repo_root: Path) -> None:
    """Monitor running session and auto-spawn blocked workers when deps complete."""
    session = plan["session"]
    tmux_name = f"orch-{session}"
    name_to_worker = {w.name: w for w in workers}

    if not has_dag(workers):
        info("No dependencies in plan — nothing to watch.")
        return

    if not tmux_session_exists(tmux_name):
        die(f"tmux session '{tmux_name}' not found. Run --execute first.")

    info(f"Watching session: {session} (Ctrl+C to stop)")
    print()

    try:
        while True:
            # 0. Check tmux session is still alive
            if not tmux_session_exists(tmux_name):
                warn(f"tmux session '{tmux_name}' died.")
                for w in workers:
                    if read_worker_state(w) == "running":
                        write_state(w.status_file, "failed")
                        warn(f"Worker marked failed (session lost): {w.name}")
                die("Watch aborted: tmux session no longer exists.")

            # 1. Detect completed panes and update status files (with exit codes)
            dead_panes = detect_completed_panes(tmux_name)
            for w in workers:
                state = read_worker_state(w)
                if state == "running" and w.slug in dead_panes:
                    exit_code = dead_panes[w.slug]
                    new_state = "completed" if exit_code == 0 else "failed"
                    write_state(w.status_file, new_state)
                    if exit_code == 0:
                        success(f"Worker completed: {w.name}")
                    else:
                        warn(f"Worker FAILED (exit {exit_code}): {w.name}")

            # 2. Check for newly ready workers (also propagates failure)
            try:
                ready, blocked = partition_workers(workers)
            except SystemExit:
                break  # die() was called inside partition_workers

            for w in ready:
                # Mark running BEFORE spawn to prevent double-spawn
                write_state(w.status_file, "running")
                info(f"Dependencies met — spawning: {w.name}")
                # Sync coordination files to worktree
                dst = w.worktree_path / ".orchestration" / session / w.slug
                dst.mkdir(parents=True, exist_ok=True)
                shutil.copy2(w.task_file, dst / "task.md")
                shutil.copy2(w.handoff_file, dst / "handoff.md")
                write_state(dst / "status.md", "running")
                # Sync upstream handoff files (prefer worktree copy where worker actually wrote)
                for dep_name in w.depends_on:
                    dep_w = name_to_worker[dep_name]
                    dep_dst = w.worktree_path / ".orchestration" / session / dep_w.slug
                    dep_dst.mkdir(parents=True, exist_ok=True)
                    # Worker writes handoff in its own worktree, so read from there first
                    wt_handoff = dep_w.worktree_path / ".orchestration" / session / dep_w.slug / "handoff.md"
                    if wt_handoff.exists():
                        shutil.copy2(wt_handoff, dep_dst / "handoff.md")
                    elif dep_w.handoff_file.exists():
                        shutil.copy2(dep_w.handoff_file, dep_dst / "handoff.md")
                try:
                    add_worker_to_tmux(w)
                except subprocess.CalledProcessError as e:
                    write_state(w.status_file, "failed")
                    warn(f"Failed to spawn worker '{w.name}': {e}")

            # 3. Check exit condition
            all_states = {w.name: read_worker_state(w) for w in workers}
            running = [n for n, s in all_states.items() if s == "running"]
            pending = [n for n, s in all_states.items() if s in ("not_started", "waiting")]
            failed = [n for n, s in all_states.items() if s == "failed"]

            if not running and not pending:
                print()
                if failed:
                    warn(f"Session finished with {len(failed)} failed: {', '.join(failed)}")
                else:
                    success("All workers completed!")
                break

            time.sleep(5)

    except KeyboardInterrupt:
        print()
        info("Watch stopped.")
        print()


def mode_cleanup(plan: dict, workers: list[WorkerInfo], repo_root: Path, *, force: bool = False) -> None:
    """Kill session, remove worktrees and branches, optionally remove coordination dir."""
    session = plan["session"]
    tmux_name = f"orch-{session}"

    info(f"Cleaning up session: {session}")
    print()

    # 1. Kill tmux
    kill_tmux_session(tmux_name)

    # 2. Remove worktrees and branches
    for w in workers:
        remove_worktree(w)
    git("worktree", "prune", check=False)
    print()

    # 3. Coordination directory
    coord_root = repo_root / ".orchestration" / session
    if coord_root.exists():
        if force:
            shutil.rmtree(coord_root)
            info(f"Removed coordination directory: {coord_root}")
        else:
            info(f"Coordination directory kept: {coord_root}")
            info("Use --force to also remove it.")

    # Clean up empty .orchestration parent
    orch_root = repo_root / ".orchestration"
    if orch_root.exists() and not any(orch_root.iterdir()):
        orch_root.rmdir()

    print()
    success("Cleanup complete.")
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def get_repo_root() -> Path:
    try:
        result = git("rev-parse", "--show-toplevel")
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        die("Not inside a git repository.")
        return Path()  # unreachable, satisfies type checker


def main() -> None:
    parser = argparse.ArgumentParser(
        description="tmux worktree orchestration for parallel Claude Code instances.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            examples:
              %(prog)s plan.json              # dry-run — show plan
              %(prog)s plan.json --execute    # create worktrees & tmux session
              %(prog)s plan.json --status     # check running session
              %(prog)s plan.json --watch      # auto-spawn blocked workers on dep completion
              %(prog)s plan.json --cleanup    # teardown everything
        """),
    )
    parser.add_argument("plan", help="Path to plan JSON file")

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--execute", action="store_true", help="Execute the plan (create worktrees & tmux)")
    mode.add_argument("--status", action="store_true", help="Show status of running session")
    mode.add_argument("--watch", action="store_true", help="Monitor and auto-spawn workers when deps complete")
    mode.add_argument("--cleanup", action="store_true", help="Kill session and remove worktrees")

    parser.add_argument("--force", action="store_true", help="With --cleanup, also remove .orchestration dir")

    args = parser.parse_args()

    # Validate environment
    ensure_command("git")
    repo_root = get_repo_root()
    plan = load_plan(args.plan)
    workers = build_workers(plan, repo_root)

    # Validate DAG if dependencies exist
    if has_dag(workers):
        validate_dag(workers)

    # tmux is only required for modes that interact with it
    needs_tmux = args.execute or args.status or args.cleanup or args.watch
    if needs_tmux:
        ensure_command("tmux")

    if args.execute:
        mode_execute(plan, workers, repo_root)
    elif args.status:
        mode_status(plan, workers)
    elif args.watch:
        mode_watch(plan, workers, repo_root)
    elif args.cleanup:
        mode_cleanup(plan, workers, repo_root, force=args.force)
    else:
        mode_dry_run(plan, workers)


if __name__ == "__main__":
    main()
