---
description: "팀 오케스트레이션 — 자연어로 멀티 에이전트 팀을 구성하고 DAG 실행"
argument-hint: "[task description or --status/--cleanup session]"
allowed-tools: Bash, Read, Write, Glob, Grep, AskUserQuestion
model: opus
---

## Pre-execution Context

!git branch --show-current
!tmux ls 2>/dev/null || echo "No tmux sessions"
!ls .claude/templates/*.toml 2>/dev/null || echo "No templates"

---

# /team - Team Orchestration with DAG Dependencies

## Core Principle

사용자의 자연어 요청을 분석하여:
1. 필요한 도메인 에이전트를 식별 (agent-orchestration.md 라우팅 매트릭스 참조)
2. 작업 간 의존성(depends_on)을 자동 추론
3. plan.json 생성 → DAG 실행 → --watch로 자동 스폰

## Command Modes

```
/team "백엔드 API + 프론트 UI + 테스트를 구현해줘"  → 팀 자동 구성 + 실행
/team --status feature-auth                          → 세션 상태 확인
/team --cleanup feature-auth                         → 세션 정리
```

## Step 1: Parse Input

사용자 입력 형태:
- 자연어: "JWT 인증 시스템을 백엔드+프론트+테스트로 구현해줘"
- 구조화: "Backend: API, Frontend: UI, Tests: E2E (depends on both)"
- 상태 확인: "--status session-name"
- 정리: "--cleanup session-name"

## Step 2: Status/Cleanup (shortcut)

If `--status` or `--cleanup`:
```bash
# Find plan.json in .orchestration/{session}/
python3 scripts/orchestrate-worktrees.py .orchestration/{session}/plan.json --status
python3 scripts/orchestrate-worktrees.py .orchestration/{session}/plan.json --cleanup
```

## Step 3: Analyze & Decompose

사용자 요청을 분석하여 워커를 자동 구성:

### 3a. 도메인 에이전트 매칭

`.claude/rules/common/agent-orchestration.md`의 라우팅 매트릭스를 참조하여
각 워커에 적절한 도메인 에이전트의 전문성을 주입:

| 작업 유형 | 참조 에이전트 | 태스크에 포함할 지식 |
|-----------|--------------|---------------------|
| API/백엔드 | fastapi-agent | Clean Architecture, SQLAlchemy |
| 프론트엔드 | nextjs-agent | App Router, TanStack Query, shadcn/ui |
| Flutter | flutter-agent | Riverpod, GoRouter |
| 테스트 | tdd-loop-agent | TDD RED-GREEN-REFACTOR |
| 리뷰 | review-orchestrator | 멀티 관점 리뷰 |

### 3b. 의존성 자동 추론

일반적인 의존성 패턴:
- Tests → depends_on: [Backend, Frontend]
- Frontend → depends_on: [Backend] (API 인터페이스가 필요한 경우)
- Integration → depends_on: [all other workers]
- Review → depends_on: [all implementation workers]

사용자가 명시적으로 의존성을 언급하면 그것을 우선 사용.

## Step 4: Generate Plan

세션 이름을 자동 생성 (kebab-case, 작업 내용 요약):

```json
{
  "session": "jwt-auth-system",
  "base_ref": "HEAD",
  "workers": [
    {
      "name": "Backend",
      "task": "JWT 인증 API 구현.\n\n## 요구사항\n- POST /auth/login\n- POST /auth/refresh\n- JWT 토큰 발급/검증\n\n## 기술 스택\n- FastAPI + SQLAlchemy\n- Clean Architecture 패턴\n\n## 범위\n- src/auth/ 디렉토리만 수정"
    },
    {
      "name": "Frontend",
      "task": "로그인 UI 구현.\n\n## 요구사항\n- 로그인 폼 컴포넌트\n- JWT 토큰 저장/갱신\n\n## 기술 스택\n- Next.js App Router\n- TanStack Query\n- shadcn/ui\n\n## 범위\n- src/app/auth/ 디렉토리만 수정",
      "depends_on": ["Backend"]
    },
    {
      "name": "Tests",
      "task": "E2E 테스트 작성.\n\n## 요구사항\n- 로그인 성공/실패 시나리오\n- 토큰 갱신 테스트\n\n## 범위\n- tests/ 디렉토리만 수정",
      "depends_on": ["Backend", "Frontend"]
    }
  ]
}
```

**워커 태스크 작성 규칙:**
- 구체적인 요구사항을 Markdown으로 상세 기술
- 기술 스택과 패턴을 명시
- 파일 수정 범위를 제한 (겹침 방지)
- 각 워커가 독립적으로 작업 가능하도록 충분한 컨텍스트 제공

## Step 5: Save Plan & Dry Run

1. `mkdir -p .orchestration/{session}`
2. Write tool로 `.orchestration/{session}/plan.json`에 생성한 JSON 저장
3. Dry-run 실행:
```bash
python3 scripts/orchestrate-worktrees.py .orchestration/{session}/plan.json
```

## Step 6: User Confirmation

AskUserQuestion으로 확인:
- Question: "이 팀 구성으로 실행할까요?"
- Show: 워커 목록, 의존성 DAG, 예상 실행 순서
- Options:
  - "실행" — 워크트리 생성 및 팀 스폰
  - "수정" — plan.json 수정 후 재확인
  - "취소" — 중단

## Step 7: Execute & Watch

```bash
python3 scripts/orchestrate-worktrees.py .orchestration/{session}/plan.json --execute
```

If plan has dependencies, inform user:
```markdown
## Team Spawned

**Session**: {session}
**Workers**: {count} ({ready} ready, {blocked} blocked)

### Commands
- Attach:  `tmux attach -t orch-{session}`
- Status:  `/team --status {session}`
- Watch:   `python3 scripts/orchestrate-worktrees.py .orchestration/{session}/plan.json --watch`
- Cleanup: `/team --cleanup {session}`

### Next Step
Run `--watch` in another terminal to auto-spawn blocked workers when dependencies complete.
```

---

## EXECUTION DIRECTIVE

1. Parse user input to determine mode (team / status / cleanup)

2. IF status or cleanup mode:
   - Find plan.json in `.orchestration/{session}/`
   - Run appropriate command
   - Show results
   - STOP

3. IF team mode:
   - Read `.claude/rules/common/agent-orchestration.md` for agent routing matrix
   - Analyze user's task description
   - Identify domain agents and their expertise
   - Decompose into workers with:
     - Detailed task descriptions (Markdown, with requirements/stack/scope)
     - Non-overlapping file scopes
     - Appropriate depends_on relationships
   - Generate session name (kebab-case summary of the task)
   - Use Write tool to save plan.json to `.orchestration/{session}/plan.json`
   - Run dry-run: `python3 scripts/orchestrate-worktrees.py .orchestration/{session}/plan.json`
   - Ask user to confirm via AskUserQuestion
   - If confirmed, run `--execute` with the same path
   - Show post-execution guide

4. Key principles:
   - Worker names: English (for branch/slug generation)
   - Worker names: must be unique
   - Task descriptions: detailed Markdown (Korean OK)
   - Session names: kebab-case English
   - base_ref: defaults to HEAD
   - Always infer depends_on from task relationships
   - Each worker's task should be self-contained with full context

---

Version: 1.0.0
Last Updated: 2026-03-19
Core: Natural language → DAG orchestration
