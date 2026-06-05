---
name: performance-shared
description: |
  애플리케이션 성능 최적화 공통 방법론 및 전략.
  FastAPI, Flutter, Next.js 에이전트가 공유하는 성능 최적화 원칙.
metadata:
  category: "💻 개발"
  type: shared
  version: "1.0.0"
  consumers:
    - fastapi-agent-skills/37-performance
    - flutter-agent-skills/18-performance
    - nextjs-agent-skills/24-performance
---
# Performance Skill (Shared)

프레임워크에 관계없이 적용되는 성능 최적화 공통 방법론입니다.

## Triggers

- "성능 최적화", "performance", "프로파일링", "속도 개선"

---

## Input (공통)

| 항목 | 필수 | 설명 |
|------|------|------|
| `target` | ✅ | 최적화 대상 |

---

## Impact Level System

코드 생성 및 리뷰 시 다음 우선순위를 적용합니다:

| Level | 의미 | 액션 |
|-------|------|------|
| **CRITICAL** | 2-10x 성능 영향 | 반드시 적용 |
| **HIGH** | 현저한 성능 개선 | 강력 권고 |
| **MEDIUM** | 점진적 개선 | 고려 |
| **LOW** | 마이크로 최적화 | 핫패스만 |

---

## 공통 최적화 원칙

### 1. [CRITICAL] Waterfall 제거 - 병렬 실행

독립적인 비동기 작업은 항상 병렬로 실행합니다:

```
Bad:  순차적 실행 (총 3초 = 1+1+1초)
   result1 = await task1()  # 1초
   result2 = await task2()  # 1초
   result3 = await task3()  # 1초

Good: 병렬 실행 (총 1초 = max(1,1,1)초)
   [result1, result2, result3] = await parallel(task1, task2, task3)
```

### 2. [CRITICAL] N+1 쿼리 방지

목록 조회 시 관련 데이터를 한번에 가져옵니다:

```
Bad:  N+1 쿼리 (1 + N번 DB 호출)
   items = query(items)
   for item in items:
       item.details = query(details, item.id)  # N번 호출

Good: Join 또는 Batch 로딩 (1-2번 DB 호출)
   items = query(items JOIN details)
```

### 3. [HIGH] 캐싱 전략

| 캐시 레이어 | 용도 | TTL 권장 |
|-------------|------|---------|
| 인메모리 | 자주 변경되지 않는 설정/메타 데이터 | 5-60분 |
| 분산 캐시 (Redis) | API 응답 캐시 | 1-60분 |
| 분산 캐시 (Redis) | 세션 저장 | 1-7일 (보안 정책에 따라) |
| CDN | 정적 자산, 이미지, 폰트 | 1일-1년 |
| 브라우저 | 정적 파일 | Cache-Control 헤더 |

### 4. [HIGH] 지연 로딩 (Lazy Loading)

화면에 보이지 않는 리소스는 필요할 때 로딩합니다:

- 이미지: 뷰포트 진입 시 로딩
- 코드: 라우트/기능 단위 분할
- 데이터: 무한 스크롤, 페이지네이션

### 5. [HIGH] 불필요한 리렌더링 방지

UI 업데이트가 필요하지 않은 상태 변경은 리렌더링을 트리거하지 않아야 합니다.

### 6. [MEDIUM] 번들/패키지 크기 최적화

- 사용하지 않는 의존성 제거
- Tree-shaking 활용
- 필요한 모듈만 import

### 7. [MEDIUM] 이미지 최적화

- 적절한 포맷 사용 (WebP, AVIF)
- 표시 크기에 맞는 해상도 제공
- 압축 적용

---

## 성능 측정

### 측정 없이 최적화하지 않는다

최적화 전후로 반드시 측정하여 개선 효과를 확인합니다.

### 공통 성능 지표

| 지표 | 설명 | 목표 |
|------|------|------|
| 응답 시간 (P50/P95/P99) | API 또는 페이지 응답 시간 | P95 < 500ms |
| 처리량 (RPS) | 초당 처리 가능한 요청 수 | 서비스 SLA 충족 |
| 메모리 사용량 | 프로세스 메모리 사용 | 메모리 누수 없음 |
| 에러율 | 전체 대비 에러 비율 | < 0.1% |

---

## 프레임워크별 오버라이드

각 에이전트별 스킬에서 다음 항목을 프레임워크에 맞게 구체화합니다:

| 항목 | FastAPI | Flutter | Next.js |
|------|---------|---------|---------|
| 병렬 실행 | asyncio.gather, Semaphore | Future.wait | Promise.all |
| 캐싱 | Redis, fastapi-cache2 | 인메모리, Drift | unstable_cache, ISR |
| 프로파일링 | cProfile, py-spy | DevTools, Timeline | Lighthouse, Next.js Analytics |
| 지연 로딩 | 비동기 엔드포인트 | ListView.builder | dynamic import, Suspense |
| 리렌더링 방지 | - | const, select, Consumer | React.memo, useMemo |
| 이미지 | python-magic, 리사이징 | cached_network_image | next/image |
| 번들 분석 | - | --analyze-size | @next/bundle-analyzer |
| 주요 지표 | TTFB, RPS | 프레임 레이트, 빌드 크기 | LCP, FID, CLS (Core Web Vitals) |

## References

- `_references/REACT-PERF-RULES.md` (Next.js)
- `_references/UI-GUIDELINES.md` (Next.js)
