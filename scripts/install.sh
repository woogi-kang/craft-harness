#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${CRAFT_HARNESS_REPO:-https://github.com/woogi-kang/craft-harness}"
REF="${CRAFT_HARNESS_REF:-main}"
PREFIX="${CRAFT_HARNESS_PREFIX:-$HOME/.local}"
INSTALL_DIR="${CRAFT_HARNESS_HOME:-$PREFIX/share/craft-harness}"
BIN_DIR="${CRAFT_HARNESS_BIN_DIR:-$PREFIX/bin}"
RUN_DOCTOR=1
LOCAL_SOURCE=""
FORCE=0
MARKER_FILE=".craft-harness-install"

usage() {
  cat <<'EOF'
Craft Harness installer

Usage:
  scripts/install.sh [options]
  curl -fsSL https://raw.githubusercontent.com/woogi-kang/craft-harness/main/scripts/install.sh | bash

Options:
  --prefix DIR       Install under DIR (default: ~/.local)
  --install-dir DIR  Install harness assets into DIR
  --bin-dir DIR      Link the craft executable into DIR
  --repo URL         GitHub repository URL
  --ref REF          Git branch or tag to install (default: main)
  --local DIR        Install from a local checkout instead of downloading
  --no-doctor        Skip the post-install doctor check
  --force            Replace an existing non-marked install directory
  -h, --help         Show this help

Environment:
  CRAFT_HARNESS_PREFIX
  CRAFT_HARNESS_HOME
  CRAFT_HARNESS_BIN_DIR
  CRAFT_HARNESS_REPO
  CRAFT_HARNESS_REF
  CRAFT_HARNESS_ARCHIVE_URL
EOF
}

log() {
  printf '==> %s\n' "$1" >&2
}

fail() {
  printf 'error: %s\n' "$1" >&2
  exit 1
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

default_local_source() {
  local script_path="${BASH_SOURCE[0]:-}"
  if [[ -n "$script_path" && -f "$script_path" ]]; then
    local script_dir
    script_dir="$(cd "$(dirname "$script_path")" && pwd)"
    local project_dir
    project_dir="$(dirname "$script_dir")"
    if [[ -d "$project_dir/agents" && -d "$project_dir/skills" && -d "$project_dir/commands" ]]; then
      printf '%s\n' "$project_dir"
    fi
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prefix)
      PREFIX="$2"
      INSTALL_DIR="$PREFIX/share/craft-harness"
      BIN_DIR="$PREFIX/bin"
      shift 2
      ;;
    --install-dir)
      INSTALL_DIR="$2"
      shift 2
      ;;
    --bin-dir)
      BIN_DIR="$2"
      shift 2
      ;;
    --repo)
      REPO_URL="$2"
      shift 2
      ;;
    --ref)
      REF="$2"
      shift 2
      ;;
    --local)
      LOCAL_SOURCE="$2"
      shift 2
      ;;
    --no-doctor)
      RUN_DOCTOR=0
      shift
      ;;
    --force)
      FORCE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "unknown option: $1"
      ;;
  esac
done

PREFIX="${PREFIX/#\~/$HOME}"
INSTALL_DIR="${INSTALL_DIR/#\~/$HOME}"
BIN_DIR="${BIN_DIR/#\~/$HOME}"
PREFIX="$(mkdir -p "$PREFIX" && cd "$PREFIX" && pwd)"
INSTALL_DIR="$(mkdir -p "$(dirname "$INSTALL_DIR")" && cd "$(dirname "$INSTALL_DIR")" && pwd)/$(basename "$INSTALL_DIR")"
BIN_DIR="$(mkdir -p "$BIN_DIR" && cd "$BIN_DIR" && pwd)"

assert_safe_install_dir() {
  local target="$1"
  [[ -n "$target" ]] || fail "install directory is empty"
  [[ "$target" != "/" ]] || fail "refusing to install into /"
  [[ "$target" != "$HOME" ]] || fail "refusing to replace HOME"
  [[ "$target" != "$PREFIX" ]] || fail "refusing to replace prefix root"
  [[ "$target" != "$BIN_DIR" ]] || fail "refusing to replace bin dir"
  [[ "$target" != "/usr" && "$target" != "/usr/local" && "$target" != "/opt" ]] || \
    fail "refusing to replace system directory: $target"
}

if [[ -z "$LOCAL_SOURCE" ]]; then
  LOCAL_SOURCE="$(default_local_source || true)"
fi

TMP_DIR="$(mktemp -d)"
cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

download_source() {
  command_exists curl || fail "curl is required for remote install"
  command_exists tar || fail "tar is required for remote install"

  local archive_url="${CRAFT_HARNESS_ARCHIVE_URL:-}"
  if [[ -z "$archive_url" ]]; then
    if [[ "$REF" =~ ^v?[0-9]+(\.[0-9]+)* ]]; then
      archive_url="$REPO_URL/archive/refs/tags/$REF.tar.gz"
    else
      archive_url="$REPO_URL/archive/refs/heads/$REF.tar.gz"
    fi
  fi

  log "Downloading Craft Harness from $archive_url"
  curl -fsSL "$archive_url" -o "$TMP_DIR/source.tar.gz"
  mkdir -p "$TMP_DIR/source"
  tar -xzf "$TMP_DIR/source.tar.gz" -C "$TMP_DIR/source" --strip-components=1
  printf '%s\n' "$TMP_DIR/source"
}

install_source() {
  local source_dir="$1"
  [[ -d "$source_dir/agents" ]] || fail "missing agents directory in $source_dir"
  [[ -d "$source_dir/skills" ]] || fail "missing skills directory in $source_dir"
  [[ -x "$source_dir/craft" ]] || fail "missing executable craft wrapper in $source_dir"

  local staging="$TMP_DIR/install"
  mkdir -p "$staging"

  assert_safe_install_dir "$INSTALL_DIR"
  if [[ -e "$INSTALL_DIR" && ! -f "$INSTALL_DIR/$MARKER_FILE" && "$FORCE" -ne 1 ]]; then
    fail "$INSTALL_DIR already exists and is not marked as a Craft Harness install. Rerun with --force to replace it."
  fi

  log "Copying harness assets to $INSTALL_DIR"
  tar \
    --exclude '.git' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude 'src/*.egg-info' \
    -C "$source_dir" -cf - . | tar -C "$staging" -xf -

  rm -rf "$INSTALL_DIR"
  mkdir -p "$(dirname "$INSTALL_DIR")"
  mv "$staging" "$INSTALL_DIR"
  printf 'installed_at=%s\nref=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$REF" > "$INSTALL_DIR/$MARKER_FILE"

  mkdir -p "$BIN_DIR"
  ln -sfn "$INSTALL_DIR/craft" "$BIN_DIR/craft"
}

if [[ -n "$LOCAL_SOURCE" ]]; then
  SOURCE_DIR="$(cd "$LOCAL_SOURCE" && pwd)"
  log "Installing Craft Harness from local checkout: $SOURCE_DIR"
else
  SOURCE_DIR="$(download_source)"
fi

install_source "$SOURCE_DIR"

if [[ "$RUN_DOCTOR" -eq 1 ]]; then
  log "Running doctor"
  "$BIN_DIR/craft" doctor
fi

case ":$PATH:" in
  *":$BIN_DIR:"*) PATH_NOTE="" ;;
  *) PATH_NOTE="Add $BIN_DIR to PATH if the craft command is not found." ;;
esac

cat <<'EOF'
Craft Harness installed.

Useful commands:
  craft doctor
  craft validate
EOF

printf '\nInstall root: %s\n' "$INSTALL_DIR"
printf 'Executable : %s/craft\n' "$BIN_DIR"
if [[ -n "$PATH_NOTE" ]]; then
  printf '\n%s\n' "$PATH_NOTE"
fi
