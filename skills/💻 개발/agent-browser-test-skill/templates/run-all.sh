#!/bin/bash
# agent-browser E2E Test Runner
# 모든 테스트 스크립트 실행

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="$SCRIPT_DIR/../test-results"

# 결과 디렉토리 생성
mkdir -p "$RESULTS_DIR"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  agent-browser E2E Test Suite"
echo "=========================================="
echo ""

# 테스트 카운터
PASSED=0
FAILED=0
TOTAL=0

# 테스트 실행 함수
run_test() {
    local test_file=$1
    local test_name=$(basename "$test_file" .sh)

    echo -n "Running: $test_name... "
    TOTAL=$((TOTAL + 1))

    if bash "$test_file" > "$RESULTS_DIR/${test_name}.log" 2>&1; then
        echo -e "${GREEN}PASSED${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}FAILED${NC}"
        FAILED=$((FAILED + 1))
        echo "  See: $RESULTS_DIR/${test_name}.log"
    fi
}

# agent-browser 설치 확인
if ! command -v agent-browser &> /dev/null; then
    echo -e "${RED}Error: agent-browser is not installed${NC}"
    echo "Install with: npm install -g agent-browser"
    exit 1
fi

# 테스트 디렉토리 순회
for category_dir in "$SCRIPT_DIR"/*/; do
    if [ -d "$category_dir" ] && [ "$(basename "$category_dir")" != "templates" ]; then
        category=$(basename "$category_dir")
        echo ""
        echo -e "${YELLOW}Category: $category${NC}"
        echo "----------------------------------------"

        for test_file in "$category_dir"*.sh; do
            if [ -f "$test_file" ]; then
                run_test "$test_file"
            fi
        done
    fi
done

# 결과 요약
echo ""
echo "=========================================="
echo "  Test Results Summary"
echo "=========================================="
echo -e "Total:  $TOTAL"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
else
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi
