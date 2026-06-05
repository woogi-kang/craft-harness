#!/bin/bash
# Login Test - agent-browser
# 로그인 플로우 E2E 테스트

set -e

BASE_URL="${BASE_URL:-http://localhost:3000}"
SESSION="auth-login-$$"
RESULTS_DIR="${RESULTS_DIR:-./test-results}"

echo "Testing: Login Flow"
echo "URL: $BASE_URL/login"

# 1. 로그인 페이지 열기
agent-browser --session $SESSION open "$BASE_URL/login"
agent-browser --session $SESSION wait network-idle

# 2. 스냅샷으로 요소 확인
echo "Capturing elements..."
agent-browser --session $SESSION snapshot -i

# 3. 이메일 입력
# 참고: @email, @password, @submit은 실제 Refs로 교체 필요
# 스냅샷 출력에서 확인: textbox "이메일" [ref=e2]
agent-browser --session $SESSION fill @email "test@example.com"

# 4. 비밀번호 입력
agent-browser --session $SESSION fill @password "password123"

# 5. 로그인 버튼 클릭
agent-browser --session $SESSION click @submit
agent-browser --session $SESSION wait network-idle

# 6. 결과 검증
echo "Verifying result..."
agent-browser --session $SESSION snapshot -i

# 7. 스크린샷 저장
mkdir -p "$RESULTS_DIR"
agent-browser --session $SESSION screenshot "$RESULTS_DIR/login-result.png"

# 8. URL 확인 (대시보드로 리다이렉트 여부)
CURRENT_URL=$(agent-browser --session $SESSION get url)
if [[ "$CURRENT_URL" == *"/dashboard"* ]] || [[ "$CURRENT_URL" == *"/home"* ]]; then
    echo "✅ Login successful - redirected to: $CURRENT_URL"
    exit 0
else
    echo "❌ Login failed - current URL: $CURRENT_URL"
    exit 1
fi
