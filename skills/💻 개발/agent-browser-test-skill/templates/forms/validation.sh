#!/bin/bash
# Form Validation Test - agent-browser
# 폼 검증 E2E 테스트

set -e

BASE_URL="${BASE_URL:-http://localhost:3000}"
SESSION="form-validation-$$"
RESULTS_DIR="${RESULTS_DIR:-./test-results}"

echo "Testing: Form Validation"
echo "URL: $BASE_URL/register"

# 1. 회원가입 페이지 열기
agent-browser --session $SESSION open "$BASE_URL/register"
agent-browser --session $SESSION wait network-idle
agent-browser --session $SESSION snapshot -i

# 2. 빈 폼 제출 테스트
echo "Test 1: Empty form submission"
agent-browser --session $SESSION click @submit
agent-browser --session $SESSION snapshot -i
agent-browser --session $SESSION screenshot "$RESULTS_DIR/form-empty-error.png"

# 3. 잘못된 이메일 형식 테스트
echo "Test 2: Invalid email format"
agent-browser --session $SESSION fill @email "invalid-email"
agent-browser --session $SESSION click @submit
agent-browser --session $SESSION snapshot -i

ERROR_MSG=$(agent-browser --session $SESSION get text @email-error 2>/dev/null || echo "")
if [ -n "$ERROR_MSG" ]; then
    echo "Email error message: $ERROR_MSG"
fi

# 4. 비밀번호 불일치 테스트
echo "Test 3: Password mismatch"
agent-browser --session $SESSION clear @email
agent-browser --session $SESSION fill @email "valid@email.com"
agent-browser --session $SESSION fill @password "password123"
agent-browser --session $SESSION fill @confirm-password "different456"
agent-browser --session $SESSION click @submit
agent-browser --session $SESSION snapshot -i

ERROR_MSG=$(agent-browser --session $SESSION get text @password-error 2>/dev/null || echo "")
if [ -n "$ERROR_MSG" ]; then
    echo "Password error message: $ERROR_MSG"
fi

# 5. 최종 스크린샷
agent-browser --session $SESSION screenshot "$RESULTS_DIR/form-validation-result.png"

echo "✅ Form validation tests completed"
exit 0
