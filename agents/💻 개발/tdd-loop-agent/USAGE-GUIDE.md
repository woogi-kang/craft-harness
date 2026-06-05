---
name: "TDD-Loop-Agent Usage Guide"
description: "Self-referential TDD loop until 100% test pass"
---

# TDD-Loop-Agent 사용 가이드

> **v1.0.0** - Ralph Wiggum 방법론 기반 TDD 자동화

---

## 개요

TDD-Loop-Agent는 **테스트가 100% 통과할 때까지 자동으로 반복**하는 에이전트입니다.

```
┌─────────────────────────────────────────────┐
│         TDD-RALPH CORE LOOP                 │
├─────────────────────────────────────────────┤
│                                             │
│   1. 테스트 실행                            │
│   2. 실패 분석                              │
│   3. 코드 수정                              │
│   4. 다시 테스트                            │
│   5. 100% 통과? → 종료 / 아니면 → 반복      │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Quick Start

### 기본 사용

```bash
# 모든 테스트가 통과할 때까지 반복
@tdd-loop-agent

# 전략 지정
@tdd-loop-agent --strategy pure      # Promise 기반 (권장)
@tdd-loop-agent --strategy hybrid    # 커버리지 기반
```

### 특정 테스트 파일 대상

```bash
# 특정 파일만 대상
@tdd-loop-agent --target test/auth_test.dart

# 특정 디렉토리
@tdd-loop-agent --target test/features/auth/
```

### 커버리지 목표 (Hybrid 전략)

```bash
# 80% 커버리지 + 100% 통과 목표
@tdd-loop-agent --strategy hybrid --coverage 80
```

---

## 전략 비교

| 특성 | Ralph Pure | Ralph Hybrid |
|------|------------|--------------|
| 종료 조건 | 모든 테스트 통과 | 통과 + 커버리지 목표 |
| 최대 반복 | 50회 | 30회 |
| 복잡도 | 낮음 | 중간 |
| 권장 상황 | 빠른 수정 | 품질 게이트 필요시 |

### 언제 어떤 전략을?

- **Pure**: 테스트 통과만 중요할 때
- **Hybrid**: CI/CD에서 커버리지 체크가 필요할 때

---

## 사전 준비

### 1. Flutter 프로젝트 확인

```bash
# Flutter 설치 확인
flutter doctor

# 테스트 의존성 확인
flutter pub get
```

### 2. 테스트 파일 존재 확인

```bash
# 테스트 파일이 있어야 함
ls test/
```

### 3. 기존 테스트 실행 확인

```bash
# 최소한 테스트가 실행되는지 확인
flutter test
```

---

## 동작 원리

### 상태 파일

에이전트는 `tdd-state/` 디렉토리에 상태를 저장합니다:

```
tdd-state/
├── work-log.md           # 반복 기록 (핵심!)
├── test-results.json     # 최신 테스트 결과
├── error-history.json    # 서킷 브레이커용
├── plan.md               # 원래 목표
└── coverage.json         # (Hybrid 전략시)
```

### Work Log 예시

```markdown
### Iteration 1
- **Command:** `flutter test`
- **Result:** FAIL (5 passed, 3 failed)
- **Failures:**
  - auth_test.dart: login should return user
- **Analysis:** Mock 설정 누락
- **Next Action:** Mock 추가
```

---

## 자동 수정 레벨

| 레벨 | 설명 | 처리 |
|------|------|------|
| **L1** | 단순 (typo, import) | 자동 적용 |
| **L2** | 중간 (로직 수정) | 적용 + 로깅 |
| **L3** | 복잡 (아키텍처) | 문서화만 |

---

## 서킷 브레이커

**무한 루프 방지**를 위해 다음 조건에서 중단:

1. 동일 에러 3회 연속 발생
2. 최대 반복 횟수 도달 (Pure: 50, Hybrid: 30)

### 중단 시 출력

```markdown
## Circuit Breaker Report

**Stopped at:** Iteration 15
**Reason:** Same error 3 consecutive times

**Unresolved Error:**
- Test: api_test.dart
- Error: Expected 404, Actual 500

**Recommendation:** 수동 개입 필요
```

---

## 종료 태그

### 성공

```
TDD_RALPH_COMPLETE
```

### 서킷 브레이커

```
TDD_RALPH_STOPPED: <reason>
```

---

## 예제 시나리오

### 시나리오 1: 새 기능 TDD

```bash
# 사용자: "로그인 기능 TDD로 구현해줘"

# 1. 테스트 먼저 작성 (Red)
# 2. @tdd-loop-agent 실행
# 3. 에이전트가 코드 구현 (Green)
# 4. 100% 통과 시 자동 종료
```

### 시나리오 2: 실패하는 테스트 수정

```bash
# 현재 상태: 10개 중 3개 실패

@tdd-loop-agent

# 에이전트가:
# 1. flutter test 실행
# 2. 3개 실패 원인 분석
# 3. 하나씩 수정
# 4. 10/10 통과 시 종료
```

### 시나리오 3: 커버리지 목표 달성

```bash
# 현재: 테스트 통과, 커버리지 60%
# 목표: 커버리지 80%

@tdd-loop-agent --strategy hybrid --coverage 80

# 에이전트가:
# 1. 커버리지 낮은 파일 식별
# 2. 테스트 추가
# 3. 80% 달성 시 종료
```

---

## 문제 해결

### Q: 에이전트가 같은 수정을 반복해요

서킷 브레이커가 작동해야 합니다. 만약 작동하지 않으면:
- `tdd-state/error-history.json` 확인
- 수동으로 중단 후 문제 분석

### Q: 커버리지가 올라가지 않아요

- 생성된 파일(`*.g.dart`, `*.freezed.dart`)이 제외되었는지 확인
- `lcov.info` 파일 생성 확인

### Q: 테스트가 실행되지 않아요

```bash
# Flutter 환경 확인
flutter doctor -v

# 의존성 재설치
flutter clean && flutter pub get
```

---

## 지원 프레임워크

현재 지원:
- **Flutter** (3.24+)

다른 프레임워크 추가 시 `frameworks/{name}/config.md` 생성

---

## 참고 문서

- `references/shared/must-rules.md` - 필수 규칙
- `references/strategies/ralph-pure.md` - Pure 전략 상세
- `references/strategies/ralph-hybrid.md` - Hybrid 전략 상세
- `frameworks/flutter/config.md` - Flutter 설정

---

Version: 1.0.0
Last Updated: 2025-01-28
