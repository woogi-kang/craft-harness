# UI Guidelines Reference

> Based on Vercel's web-interface-guidelines.
> 모든 UI 코드에 이 가이드라인을 자동 적용합니다.

---

## 1. Accessibility (접근성)

### 1.1 아이콘 버튼에 레이블 필수

```tsx
// ❌ Bad: 스크린 리더가 버튼 용도를 알 수 없음
<button onClick={handleClose}>
  <X className="h-4 w-4" />
</button>

// ✅ Good: aria-label로 버튼 설명
<button onClick={handleClose} aria-label="닫기">
  <X className="h-4 w-4" aria-hidden="true" />
</button>

// ✅ Alternative: sr-only 텍스트 사용
<button onClick={handleClose}>
  <X className="h-4 w-4" aria-hidden="true" />
  <span className="sr-only">닫기</span>
</button>

// ✅ shadcn/ui Button 사용
<Button variant="ghost" size="icon" aria-label="메뉴 열기">
  <Menu className="h-4 w-4" />
</Button>
```

---

### 1.2 Semantic HTML 사용

```tsx
// ❌ Bad: div with click handler - 접근성 문제
<div onClick={handleClick} className="cursor-pointer">
  Click me
</div>

// ✅ Good: Semantic button element
<button onClick={handleClick}>
  Click me
</button>

// ❌ Bad: div as link
<div onClick={() => router.push('/about')} className="text-blue-500">
  About us
</div>

// ✅ Good: Semantic anchor with Link
<Link href="/about" className="text-blue-500">
  About us
</Link>

// ❌ Bad: span with role
<span role="heading" aria-level={1}>Title</span>

// ✅ Good: Native heading
<h1>Title</h1>
```

**Semantic Element 선택 가이드:**

| 용도 | Element |
|-----|---------|
| 클릭 가능한 액션 | `<button>` |
| 페이지 이동 | `<a>` / `<Link>` |
| 제목 | `<h1>`-`<h6>` |
| 문단 | `<p>` |
| 목록 | `<ul>`, `<ol>`, `<li>` |
| 네비게이션 | `<nav>` |
| 주요 콘텐츠 | `<main>` |
| 섹션 | `<section>`, `<article>` |
| 사이드바 | `<aside>` |
| 푸터 | `<footer>` |

---

### 1.3 키보드 네비게이션 지원

```tsx
// ❌ Bad: 마우스만 지원
<div onClick={handleClick}>Interactive element</div>

// ✅ Good: 키보드도 지원
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      handleClick()
    }
  }}
>
  Interactive element
</div>

// ✅ Better: 그냥 button 사용
<button onClick={handleClick}>
  Interactive element
</button>
```

**키보드 지원 요구사항:**
- 모든 interactive element는 Tab으로 도달 가능
- Enter/Space로 활성화 가능
- Escape로 닫기/취소 가능
- 화살표 키로 목록/그리드 탐색

---

### 1.4 ARIA 속성 올바르게 사용

```tsx
// 확장/축소 콘텐츠
<button
  aria-expanded={isOpen}
  aria-controls="panel-content"
  onClick={togglePanel}
>
  {isOpen ? '접기' : '펼치기'}
</button>
<div id="panel-content" hidden={!isOpen}>
  Content here
</div>

// 로딩 상태
<button disabled={isLoading} aria-busy={isLoading}>
  {isLoading ? '로딩 중...' : '제출'}
</button>

// 에러 연결
<input
  id="email"
  aria-describedby="email-error"
  aria-invalid={!!error}
/>
{error && (
  <span id="email-error" role="alert">
    {error}
  </span>
)}

// 현재 페이지 표시
<nav aria-label="메인 네비게이션">
  <a href="/" aria-current={pathname === '/' ? 'page' : undefined}>홈</a>
  <a href="/about" aria-current={pathname === '/about' ? 'page' : undefined}>소개</a>
</nav>
```

---

### 1.5 색상 대비 준수

```tsx
// ❌ Bad: 낮은 대비
<p className="text-gray-400 bg-gray-100">
  읽기 어려운 텍스트
</p>

// ✅ Good: WCAG AA 기준 충족 (4.5:1 이상)
<p className="text-gray-700 bg-gray-100">
  읽기 쉬운 텍스트
</p>

// 대형 텍스트 (18pt+)는 3:1
<h1 className="text-gray-600 text-2xl">
  대형 제목은 대비 요구가 낮음
</h1>
```

**대비 기준:**
- 일반 텍스트: 4.5:1 이상
- 대형 텍스트 (24px+ 또는 19px+ bold): 3:1 이상
- UI 컴포넌트/그래픽: 3:1 이상

---

## 2. Focus States (포커스 상태)

### 2.1 focus-visible 링 필수

```tsx
// ❌ Bad: outline 제거만
<button className="outline-none">Click</button>

// ✅ Good: focus-visible 대체 스타일
<button className="outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
  Click
</button>

// ✅ Better: shadcn/ui 기본 스타일 활용
<Button>Click</Button>  // 자동으로 focus-visible 처리
```

---

### 2.2 focus vs focus-visible

```css
/* ❌ Bad: 모든 포커스에 스타일 (마우스 클릭에도 보임) */
button:focus {
  outline: 2px solid blue;
}

/* ✅ Good: 키보드 포커스만 */
button:focus-visible {
  outline: 2px solid blue;
}

/* Tailwind */
/* ❌ Bad */
className="focus:ring-2"

/* ✅ Good */
className="focus-visible:ring-2"
```

---

### 2.3 포커스 트랩 (모달)

```tsx
// ✅ Dialog에서 포커스 트랩 구현
import { Dialog, DialogContent, DialogTitle } from '@/components/ui/dialog'

function Modal({ isOpen, onClose, children }) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        {/* Radix UI가 자동으로 포커스 트랩 관리 */}
        <DialogTitle>제목</DialogTitle>
        {children}
      </DialogContent>
    </Dialog>
  )
}

// 커스텀 구현 시
import { FocusTrap } from 'focus-trap-react'

function CustomModal({ isOpen, children }) {
  return isOpen ? (
    <FocusTrap>
      <div role="dialog" aria-modal="true">
        {children}
      </div>
    </FocusTrap>
  ) : null
}
```

---

### 2.4 초기 포커스 설정

```tsx
// 모달 열릴 때 첫 번째 입력에 포커스
function LoginModal() {
  const emailRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    emailRef.current?.focus()
  }, [])

  return (
    <form>
      <input ref={emailRef} type="email" />
      <input type="password" />
      <button type="submit">로그인</button>
    </form>
  )
}

// shadcn/ui Dialog - autoFocus 사용
<DialogContent>
  <DialogTitle>로그인</DialogTitle>
  <Input autoFocus type="email" placeholder="이메일" />
</DialogContent>
```

---

## 3. Forms (폼)

### 3.1 input 필수 속성

```tsx
// ❌ Bad: 속성 누락
<input type="text" />

// ✅ Good: 필수 속성 포함
<div className="space-y-2">
  <Label htmlFor="email">이메일</Label>
  <Input
    id="email"
    type="email"
    autoComplete="email"
    placeholder="name@example.com"
    aria-describedby="email-description"
  />
  <p id="email-description" className="text-sm text-muted-foreground">
    로그인에 사용할 이메일 주소
  </p>
</div>
```

**input type별 권장 속성:**

| type | autocomplete | 추가 속성 |
|------|-------------|----------|
| email | `email` | - |
| password (현재) | `current-password` | - |
| password (새) | `new-password` | - |
| name (전체) | `name` | - |
| name (이름) | `given-name` | - |
| name (성) | `family-name` | - |
| tel | `tel` | - |
| address | `street-address` | - |
| cc-number | `cc-number` | `inputMode="numeric"` |
| otp | `one-time-code` | `inputMode="numeric"` |

---

### 3.2 paste 차단 금지

```tsx
// ❌ Bad: paste 차단 - 비밀번호 관리자 사용 방해
<input
  type="password"
  onPaste={(e) => e.preventDefault()}
/>

// ✅ Good: paste 허용
<input
  type="password"
  autoComplete="current-password"
/>

// ❌ Bad: 이메일 확인 필드에서 paste 차단
<input
  type="email"
  placeholder="이메일 다시 입력"
  onPaste={(e) => e.preventDefault()}
/>

// ✅ Good: paste 허용하고 다른 방법으로 검증
<input
  type="email"
  placeholder="이메일 다시 입력"
  // JS로 blur 시 일치 여부 검증
/>
```

---

### 3.3 제출 버튼 상태

```tsx
// ❌ Bad: 제출 중 버튼 비활성화 - 피드백 부족
<Button type="submit" disabled={isSubmitting}>
  {isSubmitting ? 'Loading...' : 'Submit'}
</Button>

// ✅ Good: 버튼 활성 상태 유지 + 로딩 인디케이터
<Button type="submit" disabled={isSubmitting}>
  {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
  제출
</Button>

// ✅ Alternative: 버튼 텍스트 변경
<Button type="submit" disabled={isSubmitting}>
  {isSubmitting ? (
    <>
      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
      처리 중...
    </>
  ) : (
    '제출'
  )}
</Button>
```

---

### 3.4 에러 처리

```tsx
// ✅ 인라인 에러 + 첫 에러 필드 포커스
function ContactForm() {
  const {
    register,
    handleSubmit,
    formState: { errors },
    setFocus
  } = useForm<FormData>()

  const onSubmit = handleSubmit((data) => {
    // 제출 로직
  }, (errors) => {
    // 첫 번째 에러 필드에 포커스
    const firstError = Object.keys(errors)[0]
    if (firstError) {
      setFocus(firstError as keyof FormData)
    }
  })

  return (
    <form onSubmit={onSubmit}>
      <div>
        <Label htmlFor="email">이메일</Label>
        <Input
          id="email"
          {...register('email', { required: '이메일을 입력하세요' })}
          aria-invalid={!!errors.email}
          aria-describedby={errors.email ? 'email-error' : undefined}
        />
        {errors.email && (
          <p id="email-error" role="alert" className="text-sm text-destructive mt-1">
            {errors.email.message}
          </p>
        )}
      </div>
    </form>
  )
}
```

---

### 3.5 실시간 검증

```tsx
// ✅ 타이핑 중이 아닌 blur 시 검증
<Input
  {...register('email', {
    validate: {
      format: (v) => isEmail(v) || '올바른 이메일 형식이 아닙니다'
    }
  })}
  onBlur={() => trigger('email')}  // blur 시 검증
/>

// ✅ 비밀번호 강도 표시 (실시간 피드백은 OK)
function PasswordInput() {
  const [password, setPassword] = useState('')
  const strength = calculateStrength(password)

  return (
    <div>
      <Input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <PasswordStrengthIndicator strength={strength} />
    </div>
  )
}
```

---

## 4. Animation (애니메이션)

### 4.1 prefers-reduced-motion 존중

```tsx
// ✅ Framer Motion에서 자동 감지
import { useReducedMotion } from 'framer-motion'

function AnimatedCard({ children }) {
  const shouldReduceMotion = useReducedMotion()

  return (
    <motion.div
      initial={{ opacity: 0, y: shouldReduceMotion ? 0 : 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: shouldReduceMotion ? 0 : 0.3,
        ease: 'easeOut'
      }}
    >
      {children}
    </motion.div>
  )
}

// CSS로 처리
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

// Tailwind 방식
<div className="motion-safe:animate-bounce motion-reduce:animate-none">
  Animated content
</div>
```

---

### 4.2 GPU 가속 속성만 애니메이션

```css
/* ❌ Bad: Layout 속성 애니메이션 - 성능 저하 */
.element {
  transition: all 0.3s;  /* width, height 등 포함 */
}

.element {
  transition: width 0.3s, height 0.3s;  /* Layout 트리거 */
}

/* ✅ Good: transform/opacity만 - GPU 가속 */
.element {
  transition: transform 0.3s, opacity 0.3s;
}

/* Tailwind */
/* ❌ Bad */
<div className="transition-all hover:w-full" />

/* ✅ Good */
<div className="transition-transform hover:scale-110" />
<div className="transition-opacity hover:opacity-50" />
```

**GPU 가속 속성:**
- `transform` (translate, scale, rotate)
- `opacity`

**피해야 할 속성:**
- `width`, `height`
- `top`, `left`, `right`, `bottom`
- `margin`, `padding`
- `border-width`
- `font-size`

---

### 4.3 중단 가능한 애니메이션

```tsx
// ✅ 새 상태로 즉시 전환 가능
<motion.div
  animate={{ x: isOpen ? 0 : -300 }}
  transition={{
    type: 'spring',
    damping: 20,
    stiffness: 300
  }}
/>

// ❌ Bad: 애니메이션 완료까지 차단
<motion.div
  animate={{ x: isOpen ? 0 : -300 }}
  transition={{ duration: 0.5 }}
  onAnimationComplete={() => {
    // 완료 전까지 다른 상태 변경 무시
  }}
/>

// ✅ Good: 언제든 중단 가능
function Sidebar({ isOpen }) {
  return (
    <motion.aside
      initial={false}
      animate={{ x: isOpen ? 0 : -300 }}
      transition={{ type: 'spring', bounce: 0.2 }}
    >
      {/* 콘텐츠 */}
    </motion.aside>
  )
}
```

---

### 4.4 애니메이션 지속 시간

```tsx
// ✅ 권장 지속 시간
const durations = {
  instant: 100,    // 즉각적인 피드백
  fast: 150,       // 호버, 버튼 클릭
  normal: 200,     // 드롭다운, 토글
  slow: 300,       // 모달, 사이드바
  slower: 400,     // 페이지 전환
}

// ❌ Bad: 너무 긴 애니메이션
<motion.div transition={{ duration: 1 }} />

// ✅ Good: 적절한 길이
<motion.div transition={{ duration: 0.2 }} />

// Tailwind duration 클래스
className="duration-150"  // 호버
className="duration-200"  // 일반
className="duration-300"  // 복잡한 전환
```

---

## 5. Typography (타이포그래피)

### 5.1 올바른 구두점

```tsx
// ❌ Bad: ASCII 구두점
<p>Loading...</p>              // 마침표 3개
<p>"Hello World"</p>           // 직선 따옴표
<p>It's nice - isn't it?</p>  // 하이픈

// ✅ Good: 타이포그래피 구두점
<p>Loading…</p>                // 말줄임표 (U+2026)
<p>"Hello World"</p>           // 둥근 따옴표 (U+201C, U+201D)
<p>It's nice – isn't it?</p>  // en dash (U+2013)

// 화살표
// ❌ Bad: ->
// ✅ Good: →

// 저작권
// ❌ Bad: (c)
// ✅ Good: ©
```

---

### 5.2 제목 텍스트 밸런싱

```css
/* ✅ 제목에 text-wrap: balance */
h1, h2, h3 {
  text-wrap: balance;
}

/* 본문에 text-wrap: pretty */
p {
  text-wrap: pretty;
}
```

```tsx
// Tailwind
<h1 className="text-wrap-balance">
  이 제목은 줄바꿈이 균형있게 됩니다
</h1>

// 또는 인라인
<h1 style={{ textWrap: 'balance' }}>
  제목
</h1>
```

---

### 5.3 Non-breaking Spaces

```tsx
// ❌ Bad: 단위가 줄바꿈될 수 있음
<span>100 MB</span>
<span>2:30 PM</span>

// ✅ Good: &nbsp; 사용
<span>100&nbsp;MB</span>
<span>2:30&nbsp;PM</span>

// 또는 유니코드
<span>100{'\u00A0'}MB</span>

// 컴포넌트로 처리
function FileSize({ bytes }: { bytes: number }) {
  const formatted = formatBytes(bytes)
  // "100 MB" → "100\u00A0MB"
  return <span>{formatted.replace(/ /g, '\u00A0')}</span>
}
```

---

### 5.4 텍스트 오버플로우

```tsx
// ✅ 긴 텍스트 처리
// 말줄임
<p className="truncate">
  아주 긴 텍스트가 있을 때 말줄임으로 표시됩니다...
</p>

// 여러 줄 말줄임
<p className="line-clamp-3">
  여러 줄에 걸친 텍스트를 3줄까지만 보여주고 말줄임 처리
</p>

// 줄바꿈 허용
<p className="break-words">
  verylongwordwithoutspaces를 적절히 줄바꿈
</p>
```

---

## 6. Performance (성능)

### 6.1 리스트 가상화 (50+ 아이템)

```tsx
// ❌ Bad: 50개 이상 직접 렌더링
{items.map(item => <Item key={item.id} {...item} />)}

// ✅ Good: 가상화 사용
import { useVirtualizer } from '@tanstack/react-virtual'

function VirtualList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
  })

  return (
    <div ref={parentRef} className="h-[400px] overflow-auto">
      <div style={{ height: virtualizer.getTotalSize(), position: 'relative' }}>
        {virtualizer.getVirtualItems().map(row => (
          <div
            key={items[row.index].id}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: row.size,
              transform: `translateY(${row.start}px)`,
            }}
          >
            <Item {...items[row.index]} />
          </div>
        ))}
      </div>
    </div>
  )
}
```

---

### 6.2 이미지 차원 명시

```tsx
// ❌ Bad: CLS(Cumulative Layout Shift) 유발
<img src={url} alt="Product" />

// ✅ Good: 차원 명시
<Image
  src={url}
  alt="Product image"
  width={400}
  height={300}
/>

// 반응형 이미지
<Image
  src={url}
  alt="Hero image"
  fill
  className="object-cover"
  sizes="(max-width: 768px) 100vw, 50vw"
  priority  // LCP 이미지
/>
```

---

### 6.3 CDN Preconnect

```tsx
// app/layout.tsx
export default function RootLayout({ children }) {
  return (
    <html>
      <head>
        {/* 폰트 CDN */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />

        {/* 이미지 CDN */}
        <link rel="preconnect" href="https://images.yourcdn.com" />

        {/* 분석 */}
        <link rel="preconnect" href="https://www.googletagmanager.com" />
      </head>
      <body>{children}</body>
    </html>
  )
}
```

---

### 6.4 content-visibility

```css
/* 긴 리스트/섹션에 적용 */
.list-item {
  content-visibility: auto;
  contain-intrinsic-size: 0 80px;
}

.page-section {
  content-visibility: auto;
  contain-intrinsic-size: 0 500px;
}
```

```tsx
// Tailwind 커스텀
// tailwind.config.ts
module.exports = {
  plugins: [
    function({ addUtilities }) {
      addUtilities({
        '.content-auto': { 'content-visibility': 'auto' },
        '.contain-80': { 'contain-intrinsic-size': '0 80px' },
        '.contain-200': { 'contain-intrinsic-size': '0 200px' },
        '.contain-500': { 'contain-intrinsic-size': '0 500px' },
      })
    }
  ]
}

// 사용
<div className="content-auto contain-80">
  <ListItem />
</div>
```

---

## 7. Navigation (네비게이션)

### 7.1 URL 상태 반영

```tsx
// ✅ 필터, 정렬, 페이지는 URL에 반영
import { useQueryState } from 'nuqs'

function ProductFilters() {
  const [category, setCategory] = useQueryState('category')
  const [sort, setSort] = useQueryState('sort', { defaultValue: 'newest' })
  const [page, setPage] = useQueryState('page', {
    parse: (v) => parseInt(v) || 1,
    serialize: String
  })

  // URL: /products?category=electronics&sort=price&page=2

  return (
    <div>
      <Select value={category} onValueChange={setCategory}>
        {/* options */}
      </Select>
      <Select value={sort} onValueChange={setSort}>
        {/* options */}
      </Select>
    </div>
  )
}

// 뒤로가기/앞으로가기에서 상태 복원됨
// 공유 가능한 URL
// 새로고침해도 상태 유지
```

**URL에 반영해야 할 상태:**
- 필터 (카테고리, 가격 범위 등)
- 정렬 순서
- 페이지네이션
- 검색어
- 탭 선택

---

### 7.2 파괴적 액션 확인

```tsx
// ✅ 삭제/취소 전 확인
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'

function DeleteButton({ onDelete }) {
  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button variant="destructive">삭제</Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>정말 삭제하시겠습니까?</AlertDialogTitle>
          <AlertDialogDescription>
            이 작업은 되돌릴 수 없습니다. 모든 데이터가 영구적으로 삭제됩니다.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>취소</AlertDialogCancel>
          <AlertDialogAction onClick={onDelete}>삭제</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
```

**확인이 필요한 액션:**
- 삭제 (데이터, 계정, 파일)
- 구독 취소
- 결제
- 내보내기 전 데이터 손실
- 페이지 이탈 시 저장되지 않은 변경

---

### 7.3 페이지 이탈 경고

```tsx
// ✅ 저장되지 않은 변경이 있을 때 경고
import { useBeforeUnload } from 'react-use'

function Editor() {
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)

  // 브라우저 이탈 경고
  useBeforeUnload(hasUnsavedChanges, '저장되지 않은 변경사항이 있습니다.')

  // Next.js 라우팅 이탈 경고
  useEffect(() => {
    const handleRouteChange = () => {
      if (hasUnsavedChanges) {
        if (!confirm('저장되지 않은 변경사항이 있습니다. 페이지를 나가시겠습니까?')) {
          throw 'Route change aborted'
        }
      }
    }

    router.events.on('routeChangeStart', handleRouteChange)
    return () => router.events.off('routeChangeStart', handleRouteChange)
  }, [hasUnsavedChanges])

  return <form>{/* ... */}</form>
}
```

---

## 8. Layout (레이아웃)

### 8.1 터치 타겟 크기

```tsx
// ❌ Bad: 너무 작은 터치 타겟
<button className="p-1">
  <Icon className="w-4 h-4" />
</button>

// ✅ Good: 최소 44x44px (모바일)
<button className="p-3 min-w-[44px] min-h-[44px]">
  <Icon className="w-4 h-4" />
</button>

// shadcn/ui Button size="icon"은 이미 적절한 크기
<Button variant="ghost" size="icon">
  <Menu className="h-4 w-4" />
</Button>
```

**권장 터치 타겟:**
- 모바일: 44x44px 이상
- 데스크톱: 24x24px 이상

---

### 8.2 입력 필드 크기 (iOS 줌 방지)

```tsx
// ❌ Bad: 16px 미만 - iOS에서 줌 트리거
<input className="text-sm" />  // 14px

// ✅ Good: 16px 이상
<input className="text-base" />  // 16px

// 모바일에서만 16px, 데스크톱에서 작게
<input className="text-base md:text-sm" />
```

---

### 8.3 스크롤 복원

```tsx
// ✅ Next.js App Router - 기본으로 스크롤 복원
// next.config.ts에서 커스터마이즈
const nextConfig = {
  experimental: {
    scrollRestoration: true
  }
}

// 특정 컨테이너 스크롤 복원
function VirtualList() {
  const scrollRef = useRef<HTMLDivElement>(null)
  const scrollKey = `scroll-${pathname}`

  useEffect(() => {
    // 저장된 스크롤 위치 복원
    const saved = sessionStorage.getItem(scrollKey)
    if (saved && scrollRef.current) {
      scrollRef.current.scrollTop = parseInt(saved)
    }

    return () => {
      // 스크롤 위치 저장
      if (scrollRef.current) {
        sessionStorage.setItem(scrollKey, String(scrollRef.current.scrollTop))
      }
    }
  }, [scrollKey])

  return <div ref={scrollRef} className="overflow-auto">{/* ... */}</div>
}
```

---

## Anti-Patterns Checklist

코드 생성/리뷰 시 다음을 검출하고 수정합니다:

### 🔴 Critical (반드시 수정)

- [ ] `user-scalable=no` in viewport meta tag
- [ ] `transition: all` without specific properties
- [ ] `outline-none` without `focus-visible` replacement
- [ ] `<div>` with `onClick` but no `role`/`tabIndex`
- [ ] `<img>` without `width`/`height` or `fill`
- [ ] paste blocked on inputs (`onPaste={e => e.preventDefault()}`)
- [ ] 50+ items without virtualization

### 🟠 High (권장 수정)

- [ ] hardcoded date/number formats (use `Intl.*`)
- [ ] Icon button without `aria-label`
- [ ] Form input without `label`
- [ ] Form input without `autocomplete`
- [ ] Error message without `role="alert"`
- [ ] Animation without `prefers-reduced-motion` check

### 🟡 Medium (권고)

- [ ] `:focus` instead of `:focus-visible`
- [ ] ASCII quotes/ellipsis instead of typography marks
- [ ] Missing `text-wrap: balance` on headings
- [ ] Non-semantic elements for interactive content

---

## Quick Reference

### 접근성

```tsx
// 아이콘 버튼
<Button aria-label="닫기"><X /></Button>

// 링크
<Link href="/about">소개</Link>

// 폼 입력
<Label htmlFor="email">이메일</Label>
<Input id="email" type="email" autoComplete="email" />
```

### 포커스

```tsx
// 포커스 스타일
className="focus-visible:ring-2 focus-visible:ring-ring"
```

### 애니메이션

```tsx
// 모션 감지
const shouldReduce = useReducedMotion()
transition={{ duration: shouldReduce ? 0 : 0.2 }}
```

### 성능

```tsx
// 가상화
import { useVirtualizer } from '@tanstack/react-virtual'

// 이미지
<Image src={url} alt="" width={400} height={300} />
```
