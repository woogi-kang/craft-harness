---
name: mapping
description: |
  Flutter 분석 결과를 바탕으로 Next.js 변환 전략을 수립합니다.
  위젯-컴포넌트 매핑, 상태-스토어 매핑, 변환 우선순위를 결정합니다.
triggers:
  - "매핑 전략"
  - "변환 전략"
  - "mapping"
---

# Conversion Mapping Strategy Skill

Flutter 분석 결과를 기반으로 Next.js 변환 전략을 수립합니다.

## 입력

- `flutter-analysis.md` (1-analyze 출력)

## 출력

- `workspace/flutter-migration/{project-name}/analysis/mapping-strategy.md`

---

## 매핑 전략 수립

### 1. 위젯 → 컴포넌트 매핑

#### 기본 위젯 매핑

| Flutter | Next.js | 비고 |
|---------|---------|------|
| `Container` | `<div>` + Tailwind | className으로 스타일 |
| `Padding` | `p-*` class | Tailwind padding |
| `Margin` | `m-*` class | Tailwind margin |
| `SizedBox` | `w-*`, `h-*` | Tailwind width/height |
| `Column` | `flex flex-col` | Flexbox |
| `Row` | `flex flex-row` | Flexbox |
| `Stack` | `relative` + `absolute` | Position |
| `Expanded` | `flex-1` | Flex grow |
| `Spacer` | `flex-1` 또는 `gap-*` | Flexbox |

#### Material 위젯 → shadcn/ui

| Flutter | shadcn/ui | Import |
|---------|-----------|--------|
| `ElevatedButton` | `Button` | `@/components/ui/button` |
| `TextButton` | `Button variant="ghost"` | |
| `OutlinedButton` | `Button variant="outline"` | |
| `IconButton` | `Button size="icon"` | |
| `TextField` | `Input` | `@/components/ui/input` |
| `TextFormField` | `Input` + react-hook-form | |
| `Checkbox` | `Checkbox` | `@/components/ui/checkbox` |
| `Switch` | `Switch` | `@/components/ui/switch` |
| `Radio` | `RadioGroup` | `@/components/ui/radio-group` |
| `Slider` | `Slider` | `@/components/ui/slider` |
| `DropdownButton` | `Select` | `@/components/ui/select` |
| `AlertDialog` | `AlertDialog` | `@/components/ui/alert-dialog` |
| `BottomSheet` | `Sheet` | `@/components/ui/sheet` |
| `Snackbar` | `Toast` (sonner) | `sonner` |
| `CircularProgressIndicator` | `Loader2` (spinning) | `lucide-react` |
| `LinearProgressIndicator` | `Progress` | `@/components/ui/progress` |
| `Card` | `Card` | `@/components/ui/card` |
| `ListTile` | 커스텀 컴포넌트 | Flex 기반 |
| `AppBar` | 커스텀 Header | |
| `Drawer` | `Sheet side="left"` | |
| `BottomNavigationBar` | 커스텀 BottomNav | |
| `TabBar` | `Tabs` | `@/components/ui/tabs` |
| `Chip` | `Badge` | `@/components/ui/badge` |
| `Tooltip` | `Tooltip` | `@/components/ui/tooltip` |
| `PopupMenuButton` | `DropdownMenu` | `@/components/ui/dropdown-menu` |

#### 레이아웃 위젯

| Flutter | Next.js | 구현 |
|---------|---------|------|
| `Scaffold` | Layout + `<main>` | App Router layout.tsx |
| `SafeArea` | 불필요 | 웹은 safe area 없음 |
| `SingleChildScrollView` | `overflow-auto` | Tailwind |
| `ListView` | `map()` | 가상화 필요시 react-virtual |
| `ListView.builder` | `map()` + virtualization | @tanstack/react-virtual |
| `GridView` | `grid` | Tailwind grid |
| `CustomScrollView` | 커스텀 구현 | |
| `SliverAppBar` | 커스텀 Header | Intersection Observer |
| `RefreshIndicator` | pull-to-refresh 라이브러리 | |

#### 이미지/미디어

| Flutter | Next.js | 구현 |
|---------|---------|------|
| `Image.network` | `next/image` | 최적화 자동 |
| `Image.asset` | `next/image` | public/ 폴더 |
| `Icon` | Lucide React | `lucide-react` |
| `SvgPicture` | React SVG | 또는 next/image |

#### 네비게이션

| Flutter | Next.js | 구현 |
|---------|---------|------|
| `Navigator.push` | `router.push()` | `useRouter` |
| `Navigator.pop` | `router.back()` | |
| `Navigator.pushReplacement` | `router.replace()` | |
| `Navigator.pushNamed` | `router.push('/path')` | |
| `GoRouter.go` | `router.push()` | |
| `GoRouter.push` | `router.push()` | |
| `Link` (go_router) | `Link` (next/link) | |

#### 폼/입력

| Flutter | Next.js | 구현 |
|---------|---------|------|
| `Form` | `<form>` + react-hook-form | |
| `FormField` | Controller (RHF) | |
| `TextEditingController` | `register()` 또는 `ref` | |
| `FocusNode` | `ref.focus()` | |
| `GlobalKey<FormState>` | `useForm()` | |

### 2. 상태관리 → Zustand 매핑

#### BLoC → Zustand

```dart
// Flutter BLoC
class AuthBloc extends Bloc<AuthEvent, AuthState> {
  AuthBloc() : super(AuthInitial()) {
    on<LoginRequested>(_onLoginRequested);
    on<LogoutRequested>(_onLogoutRequested);
  }
}
```

```typescript
// Zustand Store
interface AuthState {
  user: User | null
  isLoading: boolean
  error: string | null
}

interface AuthActions {
  login: (credentials: Credentials) => Promise<void>
  logout: () => void
}

export const useAuthStore = create<AuthState & AuthActions>((set) => ({
  user: null,
  isLoading: false,
  error: null,

  login: async (credentials) => {
    set({ isLoading: true, error: null })
    try {
      const user = await authApi.login(credentials)
      set({ user, isLoading: false })
    } catch (error) {
      set({ error: error.message, isLoading: false })
    }
  },

  logout: () => {
    set({ user: null })
  },
}))
```

#### Riverpod → Zustand + React Query

```dart
// Flutter Riverpod
final userProvider = FutureProvider<User>((ref) async {
  return await userRepository.getUser();
});
```

```typescript
// React Query (비동기 데이터)
export function useUser() {
  return useQuery({
    queryKey: ['user'],
    queryFn: () => userApi.getUser(),
  })
}

// Zustand (클라이언트 상태)
export const useUserStore = create<UserState>((set) => ({
  preferences: {},
  setPreferences: (prefs) => set({ preferences: prefs }),
}))
```

#### Provider → Zustand

```dart
// Flutter Provider
class CounterProvider extends ChangeNotifier {
  int _count = 0;
  int get count => _count;

  void increment() {
    _count++;
    notifyListeners();
  }
}
```

```typescript
// Zustand
export const useCounterStore = create<CounterState>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
}))
```

### 3. 라우팅 → App Router 매핑

#### 경로 구조 변환

```dart
// GoRouter
GoRoute(
  path: '/',
  builder: (context, state) => HomeScreen(),
  routes: [
    GoRoute(
      path: 'user/:id',
      builder: (context, state) => UserScreen(id: state.params['id']!),
    ),
  ],
)
```

```
// App Router 디렉토리 구조
src/app/
├── page.tsx              # /
├── layout.tsx
└── user/
    └── [id]/
        └── page.tsx      # /user/:id
```

#### 파라미터 접근

```dart
// Flutter
final id = GoRouterState.of(context).params['id'];
```

```typescript
// Next.js
export default function UserPage({ params }: { params: { id: string } }) {
  const { id } = params
}
```

#### 쿼리 파라미터

```dart
// Flutter
final query = GoRouterState.of(context).queryParams['search'];
```

```typescript
// Next.js
'use client'
import { useSearchParams } from 'next/navigation'

function SearchPage() {
  const searchParams = useSearchParams()
  const search = searchParams.get('search')
}
```

### 4. API 호출 매핑

#### Repository 패턴 유지

```dart
// Flutter Repository
abstract class UserRepository {
  Future<User> getUser(String id);
  Future<void> updateUser(User user);
}
```

```typescript
// Next.js Repository (서버 사이드)
// lib/repositories/user.repository.ts
export const userRepository = {
  getUser: async (id: string): Promise<User> => {
    const res = await fetch(`${API_URL}/users/${id}`)
    return res.json()
  },

  updateUser: async (user: User): Promise<void> => {
    await fetch(`${API_URL}/users/${user.id}`, {
      method: 'PUT',
      body: JSON.stringify(user),
    })
  },
}
```

#### Server Component에서 직접 호출

```typescript
// app/user/[id]/page.tsx
import { userRepository } from '@/lib/repositories/user.repository'

export default async function UserPage({ params }: { params: { id: string } }) {
  const user = await userRepository.getUser(params.id)
  return <UserProfile user={user} />
}
```

#### Server Action으로 Mutation

```typescript
// app/user/[id]/actions.ts
'use server'

import { userRepository } from '@/lib/repositories/user.repository'
import { revalidatePath } from 'next/cache'

export async function updateUser(formData: FormData) {
  const user = {
    id: formData.get('id') as string,
    name: formData.get('name') as string,
  }
  await userRepository.updateUser(user)
  revalidatePath(`/user/${user.id}`)
}
```

---

## 변환 우선순위 결정

### 우선순위 기준

1. **의존성 낮음**: 다른 컴포넌트에 의존하지 않는 것 먼저
2. **재사용성 높음**: 여러 곳에서 사용되는 공통 컴포넌트
3. **핵심 기능**: 앱의 핵심 플로우
4. **복잡도 낮음**: 간단한 것부터 시작

### 권장 변환 순서

```
Phase 1: 기반 구축
├── 프로젝트 스캐폴딩
├── 공통 유틸리티 (cn, formatDate 등)
├── 타입 정의 (models → types)
└── API 클라이언트 설정

Phase 2: 공통 컴포넌트
├── Button, Input, Card 등 기본 UI
├── Layout 컴포넌트 (Header, Footer)
└── 공유 위젯 → 공유 컴포넌트

Phase 3: 상태 설정
├── 전역 상태 스토어 (Auth, Theme)
├── React Query 설정
└── Provider 설정

Phase 4: 화면 변환 (우선순위 순)
├── 인증 화면 (로그인, 회원가입)
├── 메인 화면 (홈)
├── 핵심 기능 화면
└── 부가 기능 화면

Phase 5: 통합 및 검증
├── 라우팅 통합
├── 전체 플로우 테스트
└── 반응형 검증
```

---

## 출력 형식

### mapping-strategy.md

```markdown
# Conversion Mapping Strategy: {project-name}

## 매핑 요약

| 영역 | Flutter | Next.js | 변환 수 |
|------|---------|---------|--------|
| 위젯 | {count} | React Components | {count} |
| 상태 | BLoC ({count}) | Zustand Stores | {count} |
| 라우트 | GoRouter ({count}) | App Router | {count} |
| API | Dio ({count}) | fetch/Server Actions | {count} |

## 위젯 매핑 상세

### 화면 (Screens)

| Flutter | Next.js | 경로 | 복잡도 |
|---------|---------|------|--------|
| HomeScreen | app/page.tsx | / | 중 |
| LoginScreen | app/(auth)/login/page.tsx | /login | 저 |
| ... |

### 공통 컴포넌트

| Flutter | Next.js | shadcn | 커스텀 |
|---------|---------|--------|--------|
| CustomButton | Button | ✓ | |
| UserAvatar | Avatar | ✓ | |
| ProductCard | ProductCard | | ✓ |
| ... |

## 상태 매핑 상세

### Zustand Stores

| BLoC/Provider | Store | 파일 | 주요 상태 |
|---------------|-------|------|----------|
| AuthBloc | useAuthStore | stores/auth.ts | user, isLoading |
| CartBloc | useCartStore | stores/cart.ts | items, total |
| ... |

### React Query

| 데이터 | Query Key | 엔드포인트 |
|--------|-----------|-----------|
| 사용자 목록 | ['users'] | GET /api/users |
| 상품 상세 | ['product', id] | GET /api/products/:id |
| ... |

## 라우트 매핑 상세

| Flutter Path | Next.js Path | 파라미터 |
|--------------|--------------|---------|
| / | / | - |
| /user/:id | /user/[id] | id |
| /product/:id/review | /product/[id]/review | id |
| ... |

## 변환 우선순위

### Phase 1: 기반 ({예상 시간})
- [ ] 프로젝트 스캐폴딩
- [ ] 타입 정의
- [ ] API 설정

### Phase 2: 공통 컴포넌트 ({예상 시간})
- [ ] Button, Input, Card
- [ ] Header, Footer
- [ ] ...

### Phase 3: 상태 ({예상 시간})
- [ ] useAuthStore
- [ ] useCartStore
- [ ] React Query 설정

### Phase 4: 화면 ({예상 시간})
- [ ] 로그인 (우선순위: 1)
- [ ] 홈 (우선순위: 2)
- [ ] ...

## 특이사항

### 커스텀 구현 필요
- {위젯명}: {사유}
- ...

### 웹 대안 필요
- {Flutter 기능}: {웹 대안}
- ...

### 주의 필요
- {항목}: {주의사항}
- ...
```
