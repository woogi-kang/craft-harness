#!/bin/bash
# Logout Test - agent-browser
# 로그아웃 플로우 E2E 테스트

set -e

BASE_URL="${BASE_URL:-http://localhost:3000}"
SESSION="auth-logout-$$"
RESULTS_DIR="${RESULTS_DIR:-./test-results}"

echo "Testing: Logout Flow"

# 1. 먼저 로그인 수행
agent-browser --session $SESSION open "$BASE_URL/login"
agent-browser --session $SESSION wait network-idle
agent-browser --session $SESSION snapshot -i

agent-browser --session $SESSION fill @email "test@example.com"
agent-browser --session $SESSION fill @password "password123"
agent-browser --session $SESSION click @submit
agent-browser --session $SESSION wait network-idle

# 2. 로그아웃 버튼 찾기
agent-browser --session $SESSION snapshot -i

# 3. 로그아웃 클릭
agent-browser --session $SESSION click @logout
agent-browser --session $SESSION wait network-idle

# 4. 결과 검증
CURRENT_URL=$(agent-browser --session $SESSION get url)
if [[ "$CURRENT_URL" == *"/login"* ]] || [[ "$CURRENT_URL" == *"/"* ]]; then
    echo "✅ Logout successful - redirected to: $CURRENT_URL"
    agent-browser --session $SESSION screenshot "$RESULTS_DIR/logout-result.png"
    exit 0
else
    echo "❌ Logout failed - current URL: $CURRENT_URL"
    exit 1
fi
