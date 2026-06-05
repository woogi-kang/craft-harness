---
name: test-coverage
description: 테스트 커버리지 분석 및 부족한 테스트 자동 생성
allowed-tools: ["Bash", "Read", "Write", "Edit", "Glob", "Grep"]
---

$ARGUMENTS

테스트 커버리지를 분석하고 부족한 테스트를 생성합니다.

## 절차

### 1. 프레임워크 감지 및 커버리지 실행
| 파일 | 명령 |
|------|------|
| `pyproject.toml` | `python -m pytest --cov --cov-report=term-missing -q` |
| `package.json` + vitest | `npx vitest run --coverage` |
| `package.json` + jest | `npx jest --coverage` |

특정 경로 지정 시 해당 경로만 분석: `$ARGUMENTS`

### 2. 갭 분석
- 전체 커버리지 퍼센트 확인
- 80% 미만인 파일 식별
- 미커버 라인/브랜치 추출

### 3. 테스트 생성 (우선순위순)
1. **Happy path** — 정상 동작 케이스
2. **Error handling** — 예외/에러 케이스
3. **Edge cases** — 경계값, null, 빈 값
4. **Branch coverage** — 미커버 조건문

### 4. 검증
- 생성된 테스트 실행
- 커버리지 재측정
- 개선된 수치 보고

## 출력 형식
```
=== Coverage Report ===
Overall: 72% → 85% (+13%)

File                    Before  After   Generated Tests
src/auth/service.py     45%     88%     3 tests
src/api/routes.py       60%     82%     2 tests
src/db/repository.py    90%     95%     1 test

Total tests generated: 6
```

## 사용 예시
```
/test-coverage                        # 전체 프로젝트
/test-coverage src/auth/              # 특정 경로
/test-coverage --target 90            # 목표 커버리지 지정
```
