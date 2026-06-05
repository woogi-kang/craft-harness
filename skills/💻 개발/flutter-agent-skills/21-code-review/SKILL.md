---
name: code-review
description: |
  코드 리뷰 및 품질 검증을 수행합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Code Review Skill

코드 리뷰 및 품질 검증을 수행합니다.

## Triggers

- "코드 리뷰", "품질 검증", "QA"

---

## 리뷰 체크리스트

최신 SDK/패키지 기준은 `_references/RECENT-FLUTTER-CHANGES.md`를 먼저 확인한다.

### 1. 아키텍처

- [ ] Clean Architecture 레이어 준수
  - Domain Layer에 외부 의존성 없음
  - Data → Domain ← Presentation 의존성 방향
- [ ] 공식 Flutter MVVM 매핑 준수
  - View는 렌더링과 이벤트 전달만 담당
  - ViewModel/Notifier는 UI 상태와 사용자 액션 처리
  - Repository는 데이터의 단일 진실 공급원
- [ ] Feature 단위 모듈화
- [ ] 단일 책임 원칙 (SRP) 준수
- [ ] 의존성 주입 (DI) 사용

### 2. Atomic Design

- [ ] 컴포넌트 계층 적절성
  - Atoms: 더 이상 분해 불가
  - Molecules: 단일 책임
  - Organisms: 복합 기능
  - Templates: 레이아웃 구조
  - Pages: 데이터 연동
- [ ] 네이밍 규칙 준수
- [ ] 재사용 가능성
- [ ] 위젯 순수성
  - 재사용 위젯 내부 API/DB/Repository/Platform Channel 호출 없음
  - 하위 위젯은 값과 콜백으로 연결
  - Preview/Widget Test에서 독립 렌더링 가능

### 3. 상태 관리 (Riverpod)

- [ ] Provider 분리 적절성
- [ ] select 사용으로 리빌드 최소화
- [ ] 에러 상태 처리
- [ ] 메모리 누수 방지 (dispose)

### 4. 타입 안전성

- [ ] Freezed로 불변 데이터 클래스
- [ ] Either로 에러 처리
- [ ] null safety 준수
- [ ] Type-safe 라우팅

### 5. 테스트

- [ ] Unit Test 커버리지 60%+
- [ ] Widget Test 주요 UI
- [ ] Golden Test 시각적 회귀
- [ ] E2E Test 핵심 흐름

### 6. 성능

- [ ] ListView.builder 사용
- [ ] const 위젯 활용
- [ ] 이미지 최적화
- [ ] 불필요한 리빌드 제거
- [ ] Constraints 기반 반응형 레이아웃
  - 앱 전체 분기는 `MediaQuery.sizeOf`
  - 로컬 영역 분기는 `LayoutBuilder`
  - 기기 기준 고정 width/height 남용 없음

### 7. 코드 품질

- [ ] 린트 규칙 통과
- [ ] 중복 코드 없음
- [ ] 명확한 네이밍
- [ ] 적절한 주석 (필요한 경우만)
- [ ] DevTools Inspector/Performance 또는 MCP 기반으로 레이아웃/성능 문제 원인 확인

### 8. 보안

- [ ] 민감 정보 하드코딩 없음
- [ ] 안전한 토큰 저장 (SecureStorage)
- [ ] 입력 검증
- [ ] HTTPS 사용

---

## 리뷰 리포트 템플릿

```markdown
# Code Review Report

## 개요
- **프로젝트**: {project_name}
- **검토일**: {date}
- **검토자**: Flutter Expert Agent

## 요약
- 전체 파일 수: {count}
- 이슈 발견: {issues_count}
  - Critical: {critical}
  - Major: {major}
  - Minor: {minor}

## 발견된 이슈

### Critical (즉시 수정 필요)
| 위치 | 이슈 | 제안 |
|------|------|------|
| ... | ... | ... |

### Major (수정 권장)
| 위치 | 이슈 | 제안 |
|------|------|------|
| ... | ... | ... |

### Minor (개선 권장)
| 위치 | 이슈 | 제안 |
|------|------|------|
| ... | ... | ... |

## 긍정적인 점
- ...

## 개선 권장 사항
1. ...
2. ...

## 다음 단계
1. Critical 이슈 즉시 수정
2. Major 이슈 스프린트 내 수정
3. Minor 이슈 백로그 등록
```

---

## 자동화 검사

```bash
# 린트 검사
flutter analyze

# 포맷 검사
dart format --set-exit-if-changed .

# 테스트 실행
flutter test --coverage

# 커버리지 리포트
genhtml coverage/lcov.info -o coverage/html
```

---

## CI 설정

```yaml
# .github/workflows/review.yml
name: Code Review

on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.44.0'

      - name: Install dependencies
        run: flutter pub get

      - name: Analyze
        run: flutter analyze

      - name: Format check
        run: dart format --set-exit-if-changed .

      - name: Test with coverage
        run: flutter test --coverage

      - name: Check coverage threshold
        run: |
          COVERAGE=$(lcov --summary coverage/lcov.info | grep 'lines' | cut -d':' -f2 | cut -d'%' -f1 | tr -d ' ')
          if (( $(echo "$COVERAGE < 60" | bc -l) )); then
            echo "Coverage is below 60%: $COVERAGE%"
            exit 1
          fi
```

## References

- `_references/RECENT-FLUTTER-CHANGES.md`
- `_references/QUALITY-CODE-PATTERN.md`
- `_references/TEST-PATTERN.md`
