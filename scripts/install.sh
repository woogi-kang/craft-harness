#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

python3 -m pip install -e .
craft doctor

cat <<'EOF'
Craft Harness installed.

Useful commands:
  craft doctor
  craft validate
  craft catalog --format md --output docs/skill-catalog.md
  craft install --target claude --mode copy
EOF
