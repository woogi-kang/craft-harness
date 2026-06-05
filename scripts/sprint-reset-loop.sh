#!/bin/bash
# Sprint-Reset Loop — Context reset for long-running sequential tasks.
#
# Each sprint runs in a fresh Claude instance (full context reset).
# Previous sprint output is passed as structured handoff file.
#
# Usage:
#   bash scripts/sprint-reset-loop.sh --session jwt-auth --input initial-prompt.md
#   bash scripts/sprint-reset-loop.sh --session jwt-auth --input initial-prompt.md --max-sprints 8
#   bash scripts/sprint-reset-loop.sh --session jwt-auth --status
#
# Options:
#   --session NAME      Session name (required)
#   --input FILE        Initial input file (required for first run)
#   --max-sprints N     Maximum sprint count (default: 5)
#   --status            Show sprint progress
#   --resume            Resume from last completed sprint

set -euo pipefail

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------

SESSION=""
INITIAL_INPUT=""
MAX_SPRINTS=5
MODE="run"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --session)    SESSION="$2"; shift 2 ;;
        --input)      INITIAL_INPUT="$2"; shift 2 ;;
        --max-sprints) MAX_SPRINTS="$2"; shift 2 ;;
        --status)     MODE="status"; shift ;;
        --resume)     MODE="resume"; shift ;;
        *)            echo "Unknown option: $1"; exit 1 ;;
    esac
done

if [[ -z "$SESSION" ]]; then
    echo "Error: --session is required"
    echo "Usage: bash scripts/sprint-reset-loop.sh --session NAME --input FILE"
    exit 1
fi

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
WORK_DIR="$REPO_ROOT/.orchestration/$SESSION/sprints"
LOG_FILE="$WORK_DIR/sprint-log.jsonl"

# ---------------------------------------------------------------------------
# Status mode
# ---------------------------------------------------------------------------

if [[ "$MODE" == "status" ]]; then
    if [[ ! -d "$WORK_DIR" ]]; then
        echo "No sprints found for session: $SESSION"
        exit 0
    fi

    echo ""
    echo "=== Sprint-Reset Loop: $SESSION ==="
    echo ""

    total=$(ls "$WORK_DIR"/sprint-*-output.md 2>/dev/null | wc -l | tr -d ' ')
    echo "  Completed sprints: $total"
    echo ""

    if [[ -f "$LOG_FILE" ]]; then
        echo "  Sprint Log:"
        while IFS= read -r line; do
            sprint=$(echo "$line" | jq -r '.sprint')
            status=$(echo "$line" | jq -r '.status')
            timestamp=$(echo "$line" | jq -r '.timestamp')
            duration=$(echo "$line" | jq -r '.duration_seconds // "?"')
            if [[ "$status" == "completed" ]]; then
                echo "    Sprint $sprint: ✅ completed (${duration}s) at $timestamp"
            elif [[ "$status" == "early_exit" ]]; then
                echo "    Sprint $sprint: 🏁 early exit (all done) at $timestamp"
            else
                echo "    Sprint $sprint: ❌ $status at $timestamp"
            fi
        done < "$LOG_FILE"
    fi

    echo ""
    exit 0
fi

# ---------------------------------------------------------------------------
# Resume mode — find last completed sprint
# ---------------------------------------------------------------------------

START_SPRINT=1

if [[ "$MODE" == "resume" ]]; then
    if [[ ! -d "$WORK_DIR" ]]; then
        echo "Error: No sprints found for session: $SESSION"
        exit 1
    fi
    # Find last completed sprint output
    LAST=$(ls "$WORK_DIR"/sprint-*-output.md 2>/dev/null | sort -V | tail -1)
    if [[ -z "$LAST" ]]; then
        echo "Error: No completed sprints found"
        exit 1
    fi
    LAST_NUM=$(basename "$LAST" | sed 's/sprint-\([0-9]*\)-output.md/\1/')
    START_SPRINT=$((LAST_NUM + 1))
    echo "Resuming from sprint $START_SPRINT (last completed: $LAST_NUM)"
fi

# ---------------------------------------------------------------------------
# Run mode
# ---------------------------------------------------------------------------

if [[ "$MODE" == "run" ]]; then
    if [[ -z "$INITIAL_INPUT" ]]; then
        echo "Error: --input is required for initial run"
        exit 1
    fi
    if [[ ! -f "$INITIAL_INPUT" ]]; then
        echo "Error: Input file not found: $INITIAL_INPUT"
        exit 1
    fi
fi

mkdir -p "$WORK_DIR"

# Seed sprint 0 from initial input (only on fresh run)
if [[ "$MODE" == "run" && "$START_SPRINT" -eq 1 ]]; then
    cp "$INITIAL_INPUT" "$WORK_DIR/sprint-0-output.md"
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) Initialized from: $INITIAL_INPUT" > "$WORK_DIR/session-info.txt"
fi

echo ""
echo "=== Sprint-Reset Loop: $SESSION ==="
echo "  Max sprints: $MAX_SPRINTS"
echo "  Work dir: $WORK_DIR"
echo ""

for i in $(seq "$START_SPRINT" "$MAX_SPRINTS"); do
    PREV_OUTPUT="$WORK_DIR/sprint-$((i-1))-output.md"
    CURRENT_OUTPUT="$WORK_DIR/sprint-${i}-output.md"
    SPRINT_START=$(date +%s)

    if [[ ! -f "$PREV_OUTPUT" ]]; then
        echo "Error: Previous sprint output not found: $PREV_OUTPUT"
        exit 1
    fi

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Sprint ${i}/${MAX_SPRINTS}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Build sprint prompt
    PREV_CONTENT=$(cat "$PREV_OUTPUT")

    PROMPT=$(cat <<SPRINT_EOF
이전 스프린트 결과를 이어받아 작업합니다.
현재 작업 디렉토리: $REPO_ROOT

## 이전 스프린트 결과
$PREV_CONTENT

## 이번 스프린트 지시
Sprint ${i}/${MAX_SPRINTS}을 수행하세요.
이전 스프린트에서 완료하지 못한 작업을 이어서 진행합니다.

## 출력 형식 (반드시 이 형식을 따르세요)

### 완료된 작업
(이번 스프린트에서 완료한 작업 목록)

### 생성/수정된 파일
(파일 경로와 변경 내용)

### 다음 스프린트 입력
(다음 스프린트가 알아야 할 모든 컨텍스트 — 결정 사항, 현재 상태, 제약 조건)

### 남은 작업
(아직 완료하지 못한 것. 모두 완료했으면 "없음"이라고 명시)
SPRINT_EOF
    )

    # Run sprint in fresh Claude instance (context reset)
    if claude -p "$PROMPT" --output-file "$CURRENT_OUTPUT" 2>/dev/null; then
        SPRINT_END=$(date +%s)
        DURATION=$((SPRINT_END - SPRINT_START))

        # Check if all work is done (early exit)
        if grep -qi '남은 작업.*없음\|남은 작업.*완료\|모든 작업.*완료\|all.*completed' "$CURRENT_OUTPUT" 2>/dev/null; then
            echo ""
            echo "🏁 All work completed at Sprint ${i}!"
            # Log
            jq -n \
                --arg sprint "$i" \
                --arg status "early_exit" \
                --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
                --arg dur "$DURATION" \
                '{sprint:$sprint, status:$status, timestamp:$ts, duration_seconds:($dur|tonumber)}' \
                >> "$LOG_FILE"
            break
        fi

        echo ""
        echo "  ✅ Sprint ${i} completed (${DURATION}s)"

        # Log
        jq -n \
            --arg sprint "$i" \
            --arg status "completed" \
            --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
            --arg dur "$DURATION" \
            '{sprint:$sprint, status:$status, timestamp:$ts, duration_seconds:($dur|tonumber)}' \
            >> "$LOG_FILE"
    else
        SPRINT_END=$(date +%s)
        DURATION=$((SPRINT_END - SPRINT_START))
        echo ""
        echo "  ❌ Sprint ${i} failed"

        jq -n \
            --arg sprint "$i" \
            --arg status "failed" \
            --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
            --arg dur "$DURATION" \
            '{sprint:$sprint, status:$status, timestamp:$ts, duration_seconds:($dur|tonumber)}' \
            >> "$LOG_FILE"

        echo "  Check $WORK_DIR for details."
        exit 1
    fi

    echo ""
done

echo ""
echo "=== Sprint-Reset Loop Complete ==="
echo "  Session: $SESSION"
echo "  Output: $WORK_DIR/"
echo "  Status: bash scripts/sprint-reset-loop.sh --session $SESSION --status"
echo ""
