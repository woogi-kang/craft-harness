#!/bin/bash
# Accessibility Test - agent-browser
# 접근성 트리 분석 테스트

set -e

BASE_URL="${BASE_URL:-http://localhost:3000}"
SESSION="a11y-test-$$"
RESULTS_DIR="${RESULTS_DIR:-./test-results}"

echo "Testing: Accessibility"
echo "URL: $BASE_URL"

mkdir -p "$RESULTS_DIR"

# 1. 홈페이지 접근성 트리 추출
echo "Analyzing: Home page"
agent-browser --session $SESSION open "$BASE_URL"
agent-browser --session $SESSION wait network-idle
agent-browser --session $SESSION snapshot --json > "$RESULTS_DIR/a11y-home.json"
agent-browser --session $SESSION screenshot "$RESULTS_DIR/a11y-home.png"

# 2. 로그인 페이지 접근성 트리 추출
echo "Analyzing: Login page"
agent-browser --session $SESSION open "$BASE_URL/login"
agent-browser --session $SESSION wait network-idle
agent-browser --session $SESSION snapshot --json > "$RESULTS_DIR/a11y-login.json"
agent-browser --session $SESSION screenshot "$RESULTS_DIR/a11y-login.png"

# 3. 대시보드 (인증 필요시 스킵)
echo "Analyzing: Dashboard (if accessible)"
agent-browser --session $SESSION open "$BASE_URL/dashboard" 2>/dev/null || true
agent-browser --session $SESSION wait network-idle 2>/dev/null || true
agent-browser --session $SESSION snapshot --json > "$RESULTS_DIR/a11y-dashboard.json" 2>/dev/null || true

# 4. 접근성 체크리스트 (AI 분석용)
cat << 'EOF' > "$RESULTS_DIR/a11y-checklist.md"
# Accessibility Checklist

접근성 트리 JSON 파일을 분석하여 다음을 확인하세요:

## 필수 체크 항목

### 1. 버튼
- [ ] 모든 버튼에 접근 가능한 이름 (텍스트 또는 aria-label)
- [ ] 아이콘만 있는 버튼에 aria-label

### 2. 폼 요소
- [ ] 모든 입력 필드에 label 연결
- [ ] 필수 필드에 required 표시
- [ ] 에러 메시지가 접근 가능

### 3. 이미지
- [ ] 의미있는 이미지에 alt 텍스트
- [ ] 장식용 이미지는 alt=""

### 4. 네비게이션
- [ ] 메인 네비게이션에 nav role
- [ ] 건너뛰기 링크 (Skip to content)

### 5. 헤딩 구조
- [ ] 논리적인 헤딩 레벨 (h1 → h2 → h3)
- [ ] 페이지당 하나의 h1

### 6. 포커스 관리
- [ ] 모든 인터랙티브 요소에 포커스 가능
- [ ] 포커스 순서가 논리적

## 분석 대상 파일

- a11y-home.json
- a11y-login.json
- a11y-dashboard.json
EOF

echo "✅ Accessibility analysis completed"
echo "Results saved to: $RESULTS_DIR"
echo ""
echo "Next steps:"
echo "1. Review JSON files for accessibility tree structure"
echo "2. Check a11y-checklist.md for manual verification items"
echo "3. Use AI to analyze JSON files against checklist"

exit 0
