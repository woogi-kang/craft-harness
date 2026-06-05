---
name: verify
description: 6단계 검증 루프 실행 (빌드→타입→린트→테스트→보안→리뷰)
allowed-tools: ["Bash", "Read", "Glob", "Grep", "Edit"]
---

$ARGUMENTS

Verification Loop 스킬을 실행합니다.

## 절차

1. 프로젝트 스택 자동 감지 (pyproject.toml, package.json, pubspec.yaml 등)
2. `$ARGUMENTS`에서 옵션 파싱:
   - `--fix`: 자동 수정 활성화
   - `--scope=changed` (기본) 또는 `--scope=all`
   - 경로 지정 시 해당 경로만 검증
3. 6단계 순차 실행 (Build → Type Check → Lint → Test → Security → Diff Review)
4. 각 단계 결과를 즉시 출력
5. Phase 1-4 실패 시 중단하고 수정 안내
6. 최종 판정 출력

스킬 상세: `.claude/skills/verification-loop/SKILL.md` 참조
