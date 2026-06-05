---
name: review
description: |
  변환된 프로젝트의 최종 품질을 검토합니다.
  기능 동일성, 코드 품질, 성능을 평가하고 최종 리포트를 생성합니다.
triggers:
  - "리뷰"
  - "review"
  - "최종 검토"
---

# Final Review Skill

변환 프로젝트의 최종 품질을 검토하고 리포트를 생성합니다.

## 입력

- 변환된 Next.js 프로젝트
- Flutter 원본 프로젝트 (비교용)
- validation-report.md

## 출력

- `workspace/flutter-migration/{project-name}/analysis/final-review.md`

---

## 검토 영역

### 1. 기능 동일성 검토

#### 화면별 체크리스트

| 화면 | Flutter | Next.js | 동일성 |
|------|---------|---------|--------|
| 홈 | ✓ | ✓ | ✅ |
| 로그인 | ✓ | ✓ | ✅ |
| 상품 목록 | ✓ | ✓ | ⚠️ (페이지네이션 다름) |
| 상품 상세 | ✓ | ✓ | ✅ |
| 장바구니 | ✓ | ✓ | ✅ |

#### 기능별 체크리스트

- [ ] 사용자 인증 (로그인/로그아웃/회원가입)
- [ ] 데이터 조회 (리스트/상세)
- [ ] 데이터 생성/수정/삭제
- [ ] 검색/필터링
- [ ] 페이지네이션/무한스크롤
- [ ] 폼 제출 및 유효성 검사
- [ ] 에러 처리
- [ ] 로딩 상태

### 2. 코드 품질 검토

#### TypeScript 품질

| 항목 | 기준 | 결과 |
|------|------|------|
| any 사용 | 0개 | ✅ / ⚠️ {count}개 |
| 타입 정의 | 모든 Props | ✅ / ⚠️ |
| Strict mode | true | ✅ / ❌ |

#### 컴포넌트 품질

| 항목 | 기준 | 결과 |
|------|------|------|
| 단일 책임 | 컴포넌트당 하나의 역할 | ✅ / ⚠️ |
| Props 개수 | < 7개 권장 | ✅ / ⚠️ |
| 중복 코드 | 없음 | ✅ / ⚠️ |
| 네이밍 | PascalCase | ✅ |

#### 상태관리 품질

| 항목 | 기준 | 결과 |
|------|------|------|
| 스토어 분리 | 도메인별 분리 | ✅ / ⚠️ |
| 불필요한 리렌더 | 없음 | ✅ / ⚠️ |
| 비동기 처리 | React Query 사용 | ✅ / ⚠️ |

### 3. 성능 검토

#### 번들 크기

| 페이지 | 크기 | 기준 | 결과 |
|--------|------|------|------|
| / | 5.2KB | < 50KB | ✅ |
| /login | 3.1KB | < 50KB | ✅ |
| First Load | 89.5KB | < 100KB | ✅ |

#### Core Web Vitals (예상)

| 메트릭 | 기준 | 예상 |
|--------|------|------|
| LCP | < 2.5s | ✅ Good |
| FID | < 100ms | ✅ Good |
| CLS | < 0.1 | ✅ Good |

### 4. 반응형 검토

| 뷰포트 | 레이아웃 | 네비게이션 | 결과 |
|--------|----------|-----------|------|
| Mobile (< 768px) | 단일 컬럼 | 하단 네비게이션 | ✅ |
| Tablet (768px+) | 2컬럼 | 사이드바 | ✅ |
| Desktop (1024px+) | 3컬럼 | 헤더 네비게이션 | ✅ |

### 5. 접근성 검토

| 항목 | 기준 | 결과 |
|------|------|------|
| 이미지 alt | 모든 이미지 | ✅ / ⚠️ |
| 버튼 레이블 | aria-label | ✅ / ⚠️ |
| 키보드 네비게이션 | Tab 순서 | ✅ / ⚠️ |
| 색상 대비 | WCAG AA | ✅ / ⚠️ |

---

## 최종 리포트

### final-review.md

```markdown
# Final Review Report: {project-name}

## 프로젝트 요약

| 항목 | 값 |
|------|-----|
| Flutter 버전 | {version} |
| Next.js 버전 | 15.x |
| 변환된 화면 | {count}개 |
| 변환된 컴포넌트 | {count}개 |
| Zustand 스토어 | {count}개 |

## 변환 결과

### 화면 변환 ({count}/{total})

| # | 화면 | Flutter | Next.js | 상태 |
|---|------|---------|---------|------|
| 1 | 홈 | HomeScreen | app/page.tsx | ✅ 완료 |
| 2 | 로그인 | LoginScreen | app/(auth)/login/page.tsx | ✅ 완료 |
| ... |

### 컴포넌트 변환 ({count}/{total})

| # | 컴포넌트 | Flutter | Next.js | 상태 |
|---|----------|---------|---------|------|
| 1 | Button | CustomButton | components/ui/button | ✅ shadcn |
| 2 | ProductCard | ProductCard | components/features/product/ProductCard | ✅ 커스텀 |
| ... |

### 상태관리 변환 ({count}/{total})

| # | 원본 | 타입 | Zustand Store | 상태 |
|---|------|------|---------------|------|
| 1 | AuthBloc | BLoC | useAuthStore | ✅ 완료 |
| 2 | CartProvider | Provider | useCartStore | ✅ 완료 |
| ... |

## 품질 점수

| 영역 | 점수 | 상세 |
|------|------|------|
| 기능 동일성 | 95% | 페이지네이션 방식 변경 |
| 코드 품질 | 90% | any 타입 2개 존재 |
| 성능 | 95% | 번들 크기 최적화 완료 |
| 반응형 | 100% | 모든 뷰포트 대응 |
| 접근성 | 85% | 일부 aria-label 누락 |

**종합 점수: 93%**

## 개선 필요 항목

### 높은 우선순위

1. **any 타입 제거**
   - `src/components/ProductList.tsx:15`
   - `src/stores/cart.store.ts:32`

2. **aria-label 추가**
   - IconButton 컴포넌트들

### 낮은 우선순위

1. **페이지네이션 개선**
   - Flutter: 버튼 방식
   - Next.js: 무한스크롤로 변경됨
   - 필요시 버튼 방식으로 수정 가능

## 테스트 권장사항

### 수동 테스트

- [ ] 전체 사용자 플로우 테스트
- [ ] 에지 케이스 테스트
- [ ] 오프라인 동작 확인

### 자동화 테스트 추가 권장

```typescript
// 권장 테스트 케이스
describe('Auth Flow', () => {
  it('should login successfully')
  it('should handle login error')
  it('should logout')
})

describe('Cart', () => {
  it('should add item to cart')
  it('should remove item from cart')
  it('should calculate total correctly')
})
```

## 배포 체크리스트

### 환경 변수

```env
# 필수
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_APP_URL=

# 인증 (선택)
AUTH_SECRET=
```

### 배포 전 확인

- [ ] 환경 변수 설정
- [ ] 프로덕션 빌드 성공
- [ ] API 엔드포인트 확인
- [ ] 에러 모니터링 설정 (Sentry 등)

## 결론

{project-name} Flutter → Next.js 마이그레이션이 **성공적으로 완료**되었습니다.

### 주요 성과

- ✅ {count}개 화면 변환 완료
- ✅ Zustand 기반 상태관리 통일
- ✅ 반응형 웹 대응
- ✅ TypeScript strict mode

### 후속 작업 권장

1. E2E 테스트 추가
2. 성능 모니터링 설정
3. SEO 최적화 (메타태그, sitemap)
```

---

## 변환 품질 기준

### 점수 산정 기준

| 등급 | 점수 | 기준 |
|------|------|------|
| A+ | 95-100% | 모든 기능 완벽 동작, 코드 품질 최상 |
| A | 90-94% | 대부분 기능 동작, 사소한 이슈 존재 |
| B | 80-89% | 핵심 기능 동작, 일부 개선 필요 |
| C | 70-79% | 기본 기능 동작, 상당한 개선 필요 |
| D | < 70% | 추가 작업 필요 |

### 통과 기준

- 기능 동일성: ≥ 90%
- 코드 품질: ≥ 80%
- 빌드 성공: 필수
- 런타임 에러: 0개
