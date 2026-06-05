#!/bin/bash
# CRUD Create Test - agent-browser
# 아이템 생성 E2E 테스트

set -e

BASE_URL="${BASE_URL:-http://localhost:3000}"
SESSION="crud-create-$$"
RESULTS_DIR="${RESULTS_DIR:-./test-results}"

echo "Testing: Create Item"

# 1. 로그인 (인증이 필요한 경우)
agent-browser --session $SESSION open "$BASE_URL/login"
agent-browser --session $SESSION wait network-idle
agent-browser --session $SESSION snapshot -i

agent-browser --session $SESSION fill @email "admin@test.com"
agent-browser --session $SESSION fill @password "admin123"
agent-browser --session $SESSION click @submit
agent-browser --session $SESSION wait network-idle

# 2. 아이템 목록으로 이동
agent-browser --session $SESSION open "$BASE_URL/items"
agent-browser --session $SESSION wait network-idle
agent-browser --session $SESSION snapshot -i

# 3. 새 아이템 생성 버튼 클릭
agent-browser --session $SESSION click @create-btn
agent-browser --session $SESSION wait network-idle
agent-browser --session $SESSION snapshot -i

# 4. 폼 작성
TIMESTAMP=$(date +%s)
agent-browser --session $SESSION fill @name "Test Item $TIMESTAMP"
agent-browser --session $SESSION fill @description "This is a test item created by agent-browser"
agent-browser --session $SESSION fill @price "99.99"

# 5. 저장
agent-browser --session $SESSION click @save-btn
agent-browser --session $SESSION wait network-idle

# 6. 결과 확인
agent-browser --session $SESSION snapshot -i

# 성공 메시지 확인
SUCCESS_MSG=$(agent-browser --session $SESSION get text @success-toast 2>/dev/null || echo "")
if [ -n "$SUCCESS_MSG" ]; then
    echo "✅ Item created successfully: $SUCCESS_MSG"
    agent-browser --session $SESSION screenshot "$RESULTS_DIR/create-item-success.png"
    exit 0
else
    echo "❌ Item creation may have failed"
    agent-browser --session $SESSION screenshot "$RESULTS_DIR/create-item-result.png"
    exit 1
fi
