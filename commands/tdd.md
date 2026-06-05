---
name: tdd
description: TDD RED-GREEN-REFACTOR 사이클 드라이버
allowed-tools: ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "AskUserQuestion"]
---

$ARGUMENTS

Test-Driven Development 사이클을 엄격하게 실행합니다.

## 사이클

### Phase 1: RED — 실패하는 테스트 작성
1. 구현할 기능/수정할 버그를 명확히 정의
2. 테스트 파일 생성 또는 기존 파일에 추가
3. 테스트 실행 → **반드시 실패해야 함**
4. 실패하지 않으면 테스트가 잘못된 것 → 수정

### Phase 2: GREEN — 최소한의 코드로 통과
1. 테스트를 통과시키는 **가장 간단한** 코드 작성
2. 과도한 구현 금지 — 테스트가 요구하는 것만
3. 테스트 실행 → **반드시 통과해야 함**
4. 실패하면 코드 수정 (테스트 수정 아님)

### Phase 3: REFACTOR — 코드 정리
1. 중복 제거, 네이밍 개선, 구조 정리
2. 리팩토링 후 테스트 재실행 → **여전히 통과해야 함**
3. 기존 테스트가 깨지면 리팩토링 롤백

### Phase 4: REPEAT
다음 기능으로 Phase 1부터 반복.

## 프로젝트 자동 감지

| 파일 | 프레임워크 | 실행 명령 |
|------|-----------|----------|
| `pyproject.toml` | pytest | `python -m pytest {test} -v` |
| `package.json` + vitest | vitest | `npx vitest run {test}` |
| `package.json` + jest | jest | `npx jest {test}` |
| `pubspec.yaml` | flutter_test | `flutter test {test}` |

## 규칙
- 테스트 먼저, 코드 나중 — 예외 없음
- 각 사이클에서 테스트는 1개만 추가 (한 번에 하나)
- GREEN 단계에서 "미래를 위한" 코드 금지
- 커버리지 목표: 일반 80%, 핵심 로직 100%

## 사용 예시
```
/tdd UserService.create_user 기능 구현
/tdd --bug fix login timeout issue
```
