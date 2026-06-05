---
name: verification-loop
description: |
  6단계 검증 루프 — 빌드, 타입체크, 린트, 테스트, 보안, 변경 리뷰를 순차 실행.
  커밋 전, PR 전, 또는 수동으로 코드 품질을 종합 검증할 때 사용.
argument-hint: "[--fix] [--scope=changed|all] [path...]"
metadata:
  category: "standalone"
  version: "1.0.0"
  tags: "quality, verification, lint, test, security, ci"
  author: "woogi"
---

# Verification Loop

커밋 또는 PR 전에 6단계 품질 검증을 순차 실행하는 스킬.

## 6단계 검증

### Phase 1: Build
프로젝트가 빌드되는지 확인.
- Python: `python -m py_compile` 또는 프로젝트별 빌드 커맨드
- TypeScript: `npx tsc --noEmit`
- Flutter: `flutter build --no-pub`
- 실패 시 중단 (후속 단계 의미 없음)

### Phase 2: Type Check
정적 타입 검사.
- Python: `mypy` (설정 있으면)
- TypeScript: Phase 1에서 커버
- 경고는 보고, 에러만 중단

### Phase 3: Lint
코드 스타일 및 잠재적 문제 검출.
- Python: `ruff check {files}`
- TypeScript: `npx biome check {files}` 또는 `npx eslint {files}`
- Shell: `shellcheck {files}`
- `--fix` 옵션 시 자동 수정 시도

### Phase 4: Test
관련 테스트 실행.
- `--scope=changed` (기본): 변경된 파일과 관련된 테스트만 실행
- `--scope=all`: 전체 테스트 실행
- Python: `pytest {test_files} -v`
- TypeScript: `npx vitest run {test_files}` 또는 `npx jest {test_files}`

### Phase 5: Security
보안 취약점 스캔.
- 하드코딩된 시크릿 검출: API 키, 패스워드, 토큰 패턴 grep
- Python: `pip-audit` (있으면)
- Node.js: `npm audit --audit-level=high` (있으면)
- 패턴: `(?i)(api[_-]?key|secret|password|token)\s*[=:]\s*["'][^"']+["']`

### Phase 6: Diff Review
변경 내용 최종 리뷰.
- `git diff --staged` (커밋 전) 또는 `git diff main...HEAD` (PR 전)
- 의도하지 않은 변경 감지
- 디버그 코드 잔재 (console.log, print, debugger, TODO/FIXME)
- 대용량 파일 추가 경고 (>1MB)

## 실행 방식

```
# 기본: 변경된 파일만 검증
/verify

# 자동 수정 포함
/verify --fix

# 전체 검증
/verify --scope=all

# 특정 경로
/verify tools/clinic-consult/
```

## 출력 형식

```
=== Verification Loop ===

[1/6] Build .............. ✅ PASS
[2/6] Type Check ......... ✅ PASS
[3/6] Lint ............... ⚠️  3 warnings (auto-fixed)
[4/6] Test ............... ✅ 12 passed, 0 failed
[5/6] Security ........... ✅ No issues
[6/6] Diff Review ........ ⚠️  1 TODO comment found

=== Result: PASS (2 warnings) ===
```

## 판정 기준

| 결과 | 조건 |
|------|------|
| ✅ PASS | 모든 단계 통과 |
| ⚠️ PASS (warnings) | 경고만 있고 에러 없음 |
| ❌ FAIL | Phase 1-4 중 에러 발생 |
| 🔒 BLOCKED | Phase 5 보안 이슈 발견 |

## 프로젝트 자동 감지

스킬은 프로젝트 루트의 설정 파일로 스택을 자동 감지:
- `pyproject.toml` / `setup.py` → Python
- `package.json` → Node.js/TypeScript
- `pubspec.yaml` → Flutter/Dart
- `go.mod` → Go
- `Cargo.toml` → Rust

여러 스택이 공존하면 모두 실행.

## 연동

- `/commit` 전에 자동 실행 권장
- `/review` 시 Phase 6 결과 활용
- quality-gate hook과 보완적 (hook은 파일 단위, 이 스킬은 프로젝트 단위)
