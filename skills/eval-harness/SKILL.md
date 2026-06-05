---
name: eval-harness
description: "Eval 기반 개발 프레임워크 — pass/fail 기준 정의와 pass@k 품질 측정"
metadata:
  category: "standalone"
  version: "1.0.0"
  tags: "eval, testing, metrics, quality, verification"
  author: "woogi"
---

# Eval-Driven Development (EDD)

구현 전에 평가 기준을 정의하고, 객관적 메트릭으로 품질을 측정하는 프레임워크.

## TDD와의 차이

| | TDD | EDD |
|---|---|---|
| 대상 | 코드 정확성 | 행동/결과 품질 |
| 기준 | 유닛 테스트 | Eval 함수 (다양한 입력) |
| 메트릭 | pass/fail | pass@k (k번 시도 중 성공률) |
| 범위 | 함수/모듈 | 기능/워크플로우 전체 |

## Eval 구조

```
.claude/evals/
├── {eval-name}/
│   ├── eval.md           # Eval 정의 (기준, 입력, 기대 출력)
│   ├── grader.sh         # 자동 채점 스크립트
│   ├── cases/            # 테스트 케이스
│   │   ├── case-1.json
│   │   └── case-2.json
│   └── results/          # 실행 결과
│       └── {timestamp}.json
```

## Eval 유형

### 1. Code-Based Grader (자동)
```bash
#!/bin/bash
# grader.sh — 결과를 자동 채점
INPUT="$1"
OUTPUT="$2"
# 조건 확인
if jq -e '.status == "success"' "$OUTPUT" > /dev/null 2>&1; then
  echo "PASS"
else
  echo "FAIL: status is not success"
fi
```

### 2. Model-Based Grader (LLM 판단)
```markdown
# eval.md
## 채점 기준
- 응답이 한국어로 작성되었는가
- 기술적으로 정확한가
- 톤이 전문적인가

## 채점 방법
Claude에게 결과와 기준을 제시하고 PASS/FAIL 판정 요청
```

### 3. Human Grader (수동)
결과를 사용자에게 보여주고 판정 요청.

## pass@k 메트릭

```
pass@k = 1 - C(n-c, k) / C(n, k)
```
- n = 총 시도 횟수
- c = 성공 횟수
- k = 필요한 성공 횟수

| pass@k | 의미 |
|--------|------|
| pass@1 > 90% | 프로덕션 준비 완료 |
| pass@1 > 70% | 안정적이지만 개선 여지 |
| pass@1 < 50% | 근본적 재설계 필요 |

## 워크플로우

1. **Eval 정의**: 기능 요구사항에서 평가 기준 도출
2. **케이스 작성**: 다양한 입력 시나리오 (정상, 에지, 에러)
3. **구현**: 코드 작성
4. **실행**: Eval 실행하여 pass@k 측정
5. **반복**: pass@k 목표 미달 시 구현 개선
6. **회귀 방지**: CI에 Eval 통합

## 사용 예시

```bash
# Eval 생성
mkdir -p .claude/evals/auth-login
# eval.md, grader.sh, cases/ 작성

# Eval 실행 (수동)
bash .claude/evals/auth-login/grader.sh input.json output.json

# 결과 기록
echo '{"timestamp":"...","pass":true,"notes":"..."}' >> .claude/evals/auth-login/results/latest.json
```

## 도메인별 Eval 프리셋

사전 정의된 평가 루브릭을 사용하여 도메인별 품질을 측정:

| 프리셋 | 파일 | 용도 |
|--------|------|------|
| UI/Design | `.claude/evals/presets/ui-design.md` | 4축 평가 (Design Quality, Originality, Craft, Functionality) |
| API Backend | `.claude/evals/presets/api-backend.md` | 4축 평가 (Correctness, Robustness, Security, Performance) |
| Content | `.claude/evals/presets/content-quality.md` | 4축 평가 (Clarity, Completeness, Accuracy, Engagement) |

프리셋은 `live-qa-agent`의 `eval_type` 파라미터와 연동됩니다.

## 기존 도구와 연동

- `/verify`: 코드 품질 검증 (린트, 테스트)
- `/tdd`: 단위 테스트 기반 개발
- `live-qa-agent`: Playwright 기반 라이브 QA (eval 프리셋 사용)
- **eval-harness**: 행동/결과 기반 검증 (보완적)
