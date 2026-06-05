---
name: components
description: |
  Flutter 위젯을 React 컴포넌트로 변환합니다.
  WIDGET-MAP.md를 참조하여 일관된 변환을 수행합니다.
triggers:
  - "위젯 변환"
  - "컴포넌트 변환"
  - "components"
---

# Widget to Component Conversion Skill

Flutter 위젯을 React 컴포넌트로 변환합니다.

## 입력

- Flutter 위젯 코드 (.dart)
- 매핑 전략 (mapping-strategy.md)

## 출력

- React 컴포넌트 (.tsx)
- 필요시 스타일 파일

---

## 변환 프로세스

### Step 1: 위젯 분석

```dart
// 입력 예시
class ProductCard extends StatelessWidget {
  final Product product;
  final VoidCallback? onTap;

  const ProductCard({
    Key? key,
    required this.product,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 8,
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Image.network(product.imageUrl),
            SizedBox(height: 8),
            Text(product.name, style: TextStyle(fontWeight: FontWeight.bold)),
            Text('\$${product.price}'),
          ],
        ),
      ),
    );
  }
}
```

### Step 2: Props 인터페이스 생성

```typescript
interface ProductCardProps {
  product: Product
  onTap?: () => void
}
```

### Step 3: 컴포넌트 변환

```tsx
import Image from 'next/image'
import { cn } from '@/lib/utils'

interface ProductCardProps {
  product: Product
  onClick?: () => void
  className?: string
}

export function ProductCard({ product, onClick, className }: ProductCardProps) {
  return (
    <div
      onClick={onClick}
      className={cn(
        'p-4 bg-white rounded-xl shadow-md cursor-pointer',
        'hover:shadow-lg transition-shadow',
        className
      )}
    >
      <div className="relative aspect-square w-full overflow-hidden rounded-lg">
        <Image
          src={product.imageUrl}
          alt={product.name}
          fill
          className="object-cover"
        />
      </div>
      <div className="mt-2 space-y-1">
        <h3 className="font-bold text-foreground">{product.name}</h3>
        <p className="text-muted-foreground">${product.price}</p>
      </div>
    </div>
  )
}
```

---

## Best Practices 자동 적용

변환 시 다음 규칙을 자동으로 적용합니다.

### 접근성 변환

| Flutter | Next.js | 규칙 |
|---------|---------|------|
| `GestureDetector(onTap:)` | `<button onClick={} aria-label="">` | Semantic HTML + 접근성 |
| `IconButton(icon:)` | `<Button aria-label=""><Icon /></Button>` | aria-label 필수 |
| `Image.network()` | `<Image alt="설명" />` | alt 속성 필수 |
| `Semantics(label:)` | `aria-label=""` | ARIA 속성 매핑 |
| `Container(onTap:)` | `<button>` (div 금지) | Semantic HTML |

```tsx
// ❌ Bad: div with onClick
<div onClick={handleClick}>Click me</div>

// ✅ Good: button with aria-label (GestureDetector 변환 시)
<button onClick={handleClick} aria-label="상품 상세 보기">
  Click me
</button>
```

### 성능 변환

| Flutter | Next.js | 규칙 |
|---------|---------|------|
| `FutureBuilder` | `<Suspense>` + async component | Waterfall 제거 |
| 대형 위젯 | `dynamic(() => import())` | Bundle 최적화 |
| 병렬 API 호출 | `Promise.all()` | Waterfall 제거 |
| `ListView.builder` (50+ items) | 가상화 또는 `content-visibility` | 렌더링 성능 |

```tsx
// FutureBuilder → Suspense
// Flutter
FutureBuilder<User>(
  future: fetchUser(),
  builder: (context, snapshot) => UserCard(user: snapshot.data),
)

// Next.js
<Suspense fallback={<UserCardSkeleton />}>
  <UserCard />  {/* async Server Component */}
</Suspense>

async function UserCard() {
  const user = await fetchUser()
  return <Card>{user.name}</Card>
}
```

### 애니메이션 변환

| Flutter | Next.js | 규칙 |
|---------|---------|------|
| `AnimatedContainer` | `motion.div` + transform only | GPU 가속 속성만 |
| 모든 애니메이션 | `prefers-reduced-motion` 체크 | 모션 감도 존중 |

```tsx
// ✅ Good: 모션 감도 존중
import { useReducedMotion, motion } from 'framer-motion'

function AnimatedCard() {
  const shouldReduce = useReducedMotion()

  return (
    <motion.div
      animate={{ scale: shouldReduce ? 1 : 1.1 }}
      transition={{ duration: shouldReduce ? 0 : 0.3 }}
    />
  )
}
```

---

## 변환 규칙

### 1. 위젯 타입별 변환

#### StatelessWidget

```dart
// Flutter
class MyWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) => Container();
}
```

```tsx
// React (기본 함수형)
export function MyWidget() {
  return <div />
}
```

#### StatefulWidget

```dart
// Flutter
class MyWidget extends StatefulWidget {
  @override
  _MyWidgetState createState() => _MyWidgetState();
}

class _MyWidgetState extends State<MyWidget> {
  int _count = 0;

  @override
  Widget build(BuildContext context) {
    return Text('$_count');
  }
}
```

```tsx
// React (useState 사용)
'use client'

import { useState } from 'react'

export function MyWidget() {
  const [count, setCount] = useState(0)

  return <span>{count}</span>
}
```

### 2. 레이아웃 변환

#### Container → div + Tailwind

```dart
Container(
  width: 100,
  height: 50,
  padding: EdgeInsets.all(16),
  margin: EdgeInsets.symmetric(horizontal: 8),
  decoration: BoxDecoration(
    color: Colors.blue,
    borderRadius: BorderRadius.circular(8),
  ),
  child: Text('Hello'),
)
```

```tsx
<div className="w-[100px] h-[50px] p-4 mx-2 bg-blue-500 rounded-lg">
  Hello
</div>
```

#### Column/Row → flex

```dart
Column(
  mainAxisAlignment: MainAxisAlignment.center,
  crossAxisAlignment: CrossAxisAlignment.start,
  children: [Widget1(), Widget2()],
)
```

```tsx
<div className="flex flex-col justify-center items-start">
  <Widget1 />
  <Widget2 />
</div>
```

#### Stack → relative/absolute

```dart
Stack(
  children: [
    Positioned(
      top: 10,
      right: 10,
      child: Icon(Icons.close),
    ),
  ],
)
```

```tsx
<div className="relative">
  <div className="absolute top-2.5 right-2.5">
    <X className="h-4 w-4" />
  </div>
</div>
```

### 3. 스타일 변환

#### EdgeInsets → Tailwind spacing

| Flutter | Tailwind |
|---------|----------|
| `EdgeInsets.all(4)` | `p-1` |
| `EdgeInsets.all(8)` | `p-2` |
| `EdgeInsets.all(16)` | `p-4` |
| `EdgeInsets.symmetric(horizontal: 16)` | `px-4` |
| `EdgeInsets.symmetric(vertical: 8)` | `py-2` |
| `EdgeInsets.only(top: 16, bottom: 8)` | `pt-4 pb-2` |

#### Colors → Tailwind colors

| Flutter | Tailwind |
|---------|----------|
| `Colors.white` | `bg-white` |
| `Colors.black` | `bg-black` |
| `Colors.blue` | `bg-blue-500` |
| `Colors.grey[100]` | `bg-gray-100` |
| `Theme.of(context).primaryColor` | `bg-primary` |

#### TextStyle → Tailwind typography

| Flutter | Tailwind |
|---------|----------|
| `fontSize: 12` | `text-xs` |
| `fontSize: 14` | `text-sm` |
| `fontSize: 16` | `text-base` |
| `fontSize: 18` | `text-lg` |
| `fontWeight: FontWeight.bold` | `font-bold` |
| `fontWeight: FontWeight.w500` | `font-medium` |

### 4. 이벤트 핸들러 변환

```dart
// Flutter
GestureDetector(
  onTap: () => print('tapped'),
  onLongPress: () => print('long pressed'),
  child: Container(),
)
```

```tsx
// React
<div
  onClick={() => console.log('tapped')}
  onContextMenu={(e) => {
    e.preventDefault()
    console.log('long pressed')
  }}
/>
```

### 5. 조건부 렌더링

```dart
// Flutter
if (isLoading)
  CircularProgressIndicator()
else
  Content()

// 또는
isLoading ? CircularProgressIndicator() : Content()
```

```tsx
// React
{isLoading ? <Loader2 className="animate-spin" /> : <Content />}

// 또는
{isLoading && <Loader2 className="animate-spin" />}
{!isLoading && <Content />}
```

### 6. 리스트 렌더링

```dart
// Flutter
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) => ItemWidget(item: items[index]),
)
```

```tsx
// React
<div className="space-y-2">
  {items.map((item) => (
    <ItemWidget key={item.id} item={item} />
  ))}
</div>
```

### 7. 이미지 변환

```dart
// Flutter
Image.network(
  url,
  width: 100,
  height: 100,
  fit: BoxFit.cover,
)

Image.asset('assets/images/logo.png')
```

```tsx
// Next.js
import Image from 'next/image'

<Image
  src={url}
  alt="description"
  width={100}
  height={100}
  className="object-cover"
/>

// 또는 fill 모드
<div className="relative w-[100px] h-[100px]">
  <Image src={url} alt="description" fill className="object-cover" />
</div>

// Asset 이미지
<Image src="/images/logo.png" alt="Logo" width={100} height={100} />
```

---

## 복잡한 위젯 변환 예시

### CustomScrollView + SliverAppBar

```dart
// Flutter
CustomScrollView(
  slivers: [
    SliverAppBar(
      expandedHeight: 200,
      pinned: true,
      flexibleSpace: FlexibleSpaceBar(
        title: Text('Title'),
        background: Image.network(url, fit: BoxFit.cover),
      ),
    ),
    SliverList(
      delegate: SliverChildBuilderDelegate(
        (context, index) => ListTile(title: Text('Item $index')),
        childCount: 20,
      ),
    ),
  ],
)
```

```tsx
// React
'use client'

import { useRef } from 'react'
import Image from 'next/image'
import { useScroll, useTransform, motion } from 'framer-motion'

export function SliverPage() {
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollY } = useScroll({ container: containerRef })

  const headerHeight = useTransform(scrollY, [0, 200], [200, 60])
  const headerOpacity = useTransform(scrollY, [0, 150], [1, 0])

  return (
    <div ref={containerRef} className="h-screen overflow-auto">
      {/* SliverAppBar 대체 */}
      <motion.header
        style={{ height: headerHeight }}
        className="sticky top-0 z-10 overflow-hidden"
      >
        <motion.div style={{ opacity: headerOpacity }} className="absolute inset-0">
          <Image src={url} alt="" fill className="object-cover" />
        </motion.div>
        <div className="absolute bottom-4 left-4">
          <h1 className="text-2xl font-bold text-white">Title</h1>
        </div>
      </motion.header>

      {/* SliverList 대체 */}
      <div className="divide-y">
        {Array.from({ length: 20 }).map((_, index) => (
          <div key={index} className="p-4">
            Item {index}
          </div>
        ))}
      </div>
    </div>
  )
}
```

### 애니메이션 위젯

```dart
// Flutter
AnimatedContainer(
  duration: Duration(milliseconds: 300),
  width: isExpanded ? 200 : 100,
  height: isExpanded ? 200 : 100,
  color: isExpanded ? Colors.blue : Colors.red,
)
```

```tsx
// React + Framer Motion
import { motion } from 'framer-motion'

<motion.div
  animate={{
    width: isExpanded ? 200 : 100,
    height: isExpanded ? 200 : 100,
    backgroundColor: isExpanded ? '#3b82f6' : '#ef4444',
  }}
  transition={{ duration: 0.3 }}
/>
```

---

## 출력 파일 구조

```
src/components/
├── features/
│   └── product/
│       ├── ProductCard.tsx       # 변환된 컴포넌트
│       ├── ProductList.tsx
│       └── index.ts              # 배럴 export
└── common/
    ├── Button.tsx
    └── ...
```

### 컴포넌트 파일 템플릿

```tsx
// src/components/features/product/ProductCard.tsx

import Image from 'next/image'
import { cn } from '@/lib/utils'
import type { Product } from '@/types'

interface ProductCardProps {
  product: Product
  onClick?: () => void
  className?: string
}

/**
 * 상품 카드 컴포넌트
 *
 * @flutter ProductCard (lib/features/product/widgets/product_card.dart)
 */
export function ProductCard({ product, onClick, className }: ProductCardProps) {
  return (
    <div
      onClick={onClick}
      className={cn(
        // 기본 스타일
        'rounded-xl bg-card p-4 shadow-md',
        // 인터랙션
        'cursor-pointer transition-shadow hover:shadow-lg',
        // 커스텀 클래스
        className
      )}
    >
      {/* 이미지 */}
      <div className="relative aspect-square overflow-hidden rounded-lg">
        <Image
          src={product.imageUrl}
          alt={product.name}
          fill
          className="object-cover"
        />
      </div>

      {/* 정보 */}
      <div className="mt-3 space-y-1">
        <h3 className="font-semibold text-card-foreground">{product.name}</h3>
        <p className="text-sm text-muted-foreground">
          ${product.price.toLocaleString()}
        </p>
      </div>
    </div>
  )
}
```
