---
description: "멀티-LLM 리뷰 - Claude, Gemini, Codex가 함께 리뷰하고 합의된 피드백 생성"
argument-hint: "<file_path>"
type: utility
allowed-tools: AskUserQuestion, Bash, Read, Write, Glob, Grep, Task
model: opus
---

# /review - 멀티-LLM 리뷰 커맨드

## Purpose

여러 LLM(Claude, Gemini, Codex)이 콘텐츠를 병렬로 리뷰하고, 합의 기반의 통합 피드백 리포트를 생성합니다.

Version: 2.0.0

## Usage

```bash
/review <file_path>           # 특정 파일 리뷰
/review . --domain content    # 도메인 명시적 지정
```

---

## Execution Flow

```
/review "{target}"
       │
       ├─ Phase 0: LLM 가용성 체크
       ├─ Phase 1: 대상 분석 & 도메인 분류
       ├─ Phase 2: 구조화된 프롬프트 생성 (LLM별 역할 포함)
       ├─ Phase 3: 병렬 LLM 리뷰 수집
       ├─ Phase 4: 응답 검증 & 정규화
       ├─ Phase 5: 합의 도출 (가중치 투표)
       └─ Phase 6: 리포트 생성
```

---

## Phase 0: LLM 가용성 체크

```bash
claude --version  # 필수
gemini --version  # 선택
codex --version   # 선택
```

### 가용성에 따른 동작

| 상황 | 동작 |
|------|------|
| 모든 LLM 가용 | 3개 LLM 병렬 리뷰 → 합의 도출 |
| 일부 LLM 가용 | 가용한 LLM만 리뷰 → 가능한 합의 도출 |
| Claude만 가용 | 사용자에게 선택지 제공 (설치 or 단독 진행) |

---

## Phase 2: 구조화된 프롬프트 생성

### LLM별 역할 분담

| LLM | 역할 | 전문 분야 |
|-----|------|----------|
| **Claude** | 시니어 테크니컬 라이터 | 가독성, 논리 구조, UX |
| **Gemini** | 풀스택 아키텍트 | 실용성, 확장성, 일관성 |
| **Codex** | 보안 전문가 겸 QA | 정확성, 보안, 엣지케이스 |

### 프롬프트 구조

```markdown
## 시스템 정보
- 프레임워크: MoAI-ADK
- 리뷰 시스템: 멀티-LLM 앙상블

## 당신의 역할
{role_description}  # LLM별 차별화

## 리뷰 컨텍스트
- 리뷰 대상: {content_type}
- 파일 경로: {file_path}
- 리뷰 목적: {purpose}
- 대상 독자: {target_audience}

## 리뷰 기준 (가중치)
| 기준 | 설명 | 가중치 |
|------|------|--------|
| clarity | 명확하고 이해하기 쉬운가 | 25% |
| completeness | 필요한 정보가 모두 포함되었는가 | 25% |
| practicality | 실제로 구현/사용 가능한가 | 25% |
| consistency | 일관된 스타일과 용어를 사용하는가 | 25% |

## 리뷰 대상 내용
{content}

## 출력 규칙 [중요]
1. 반드시 JSON 형식으로만 응답
2. 최대 7개 피드백 항목
3. 모든 필드 필수
```

---

## Phase 3: 병렬 LLM 호출

### Claude CLI
```bash
claude -p "{full_prompt}" --output-format json --max-turns 1
```

### Gemini CLI
```bash
gemini "{full_prompt}" --yolo
# 또는 stdin 사용
cat {file} | gemini "{prompt}" --yolo
```

### Codex CLI
```bash
codex exec "{full_prompt}"
```

### 긴 프롬프트 처리

```bash
# 임시 파일 사용
cat > /tmp/review-prompt.txt << 'EOF'
{full_prompt}
EOF

cat /tmp/review-prompt.txt | gemini --yolo
```

---

## 강제 응답 JSON 스키마

모든 LLM은 반드시 이 형식으로 응답:

```json
{
  "$schema": "review-response-v2",
  "reviewer": "claude|gemini|codex",

  "findings": [
    {
      "id": "F001",
      "severity": "critical|major|minor|suggestion",
      "category": "clarity|completeness|practicality|consistency|security|accuracy",
      "location": {
        "section": "섹션명",
        "line_range": "42-45",
        "snippet": "문제 원본 텍스트"
      },
      "issue": "문제 설명",
      "suggestion": "개선안",
      "rationale": "근거",
      "confidence": 0.85
    }
  ],

  "scores": {
    "clarity": 8,
    "completeness": 7,
    "practicality": 6,
    "consistency": 8
  },

  "overall_score": 7.25,

  "summary": {
    "strengths": ["강점 1", "강점 2"],
    "improvements": ["개선점 1", "개선점 2"]
  },

  "expert_insight": "고유 통찰 (투표 제외)"
}
```

---

## Phase 5: 합의 도출

### 가중치 투표

```yaml
voting_weights:
  claude:
    clarity: 1.5
    completeness: 1.3
  gemini:
    practicality: 1.5
    consistency: 1.3
  codex:
    security: 1.5
    accuracy: 1.5
```

### 신뢰도 필터링

- `confidence < 0.5`: 투표 제외
- `confidence >= 0.8`: 가중치 1.2배
- 근거 없는 고신뢰: 감점

### 합의 판정

| 합의율 | 처리 |
|--------|------|
| 100% (3/3) | ✅ 자동 채택 |
| 67% (2/3) | ✅ 자동 채택 |
| 33% (1/3) | ⚠️ 메타-판단 |

---

## Phase 6: 리포트 생성

### 저장 경로
```
.moai/reports/reviews/review-{YYYYMMDD-HHmmss}.md
```

### 리포트 구조

```markdown
# 📋 멀티-LLM 리뷰 리포트

**참여 LLM**: Claude ✅ | Gemini ✅ | Codex ✅

## 🎯 Executive Summary
| 기준 | Claude | Gemini | Codex | 평균 | 합의도 |
|------|--------|--------|-------|------|--------|

## 🗳️ LLM 합의 매트릭스
| ID | 이슈 | Claude | Gemini | Codex | 합의 | 채택 |

## 📊 상세 피드백 (합의된 항목)

## 💡 Expert Insights (투표 제외)

## ✅ 권장 조치 (우선순위순)

## 📎 부록: 개별 LLM 원본 응답
```

---

## Output

```
✅ 멀티-LLM 리뷰 완료

📊 결과 요약:
- 참여 LLM: 3/3 (Claude, Gemini, Codex)
- 발견 항목: Critical 1, Major 3, Minor 5
- 합의율: 85%
- 종합 점수: 7.5/10

📄 리포트:
.moai/reports/reviews/review-20260116-143052.md
```

---

## Error Handling

| 에러 | 처리 |
|------|------|
| 파일 없음 | 에러 메시지 |
| LLM 타임아웃 (60초) | 해당 LLM 스킵 |
| JSON 파싱 실패 | expert_insight로만 활용, 투표 제외 |
| 스키마 검증 실패 | 투표 제외, 부록에 원본 포함 |

---

## Related

- Agent: `review-orchestrator` - 리뷰 오케스트레이션
- Agent: `review-content` - 콘텐츠 리뷰 전문성
- Reports: `.moai/reports/reviews/` - 생성된 리포트
