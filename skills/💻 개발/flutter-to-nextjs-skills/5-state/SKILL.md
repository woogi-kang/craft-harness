---
name: state
description: |
  Flutter 상태관리(BLoC/Riverpod/Provider/GetX)를 Zustand로 변환합니다.
  비동기 데이터는 React Query와 조합합니다.
triggers:
  - "상태 변환"
  - "state 변환"
  - "zustand"
---

# State Management Conversion Skill

Flutter 상태관리를 Zustand + React Query로 변환합니다.

## 입력

- Flutter 상태관리 코드 (BLoC/Riverpod/Provider/GetX)
- 매핑 전략 (mapping-strategy.md)

## 출력

- Zustand 스토어 (.ts)
- React Query 훅 (필요시)

---

## 변환 원칙

### 상태 분류

| 상태 유형 | Flutter | Next.js |
|----------|---------|---------|
| **클라이언트 상태** | BLoC/Provider | Zustand |
| **서버 상태** | Repository + BLoC | React Query |
| **UI 상태** | StatefulWidget | useState |
| **폼 상태** | TextEditingController | react-hook-form |
| **전역 상태** | Provider/GetX | Zustand (persist) |

### Zustand 사용 시점

- 인증 상태 (user, token)
- UI 설정 (theme, language)
- 장바구니/위시리스트
- 필터/정렬 상태
- 모달/사이드바 상태

### React Query 사용 시점

- API에서 가져오는 데이터
- 캐싱이 필요한 데이터
- 실시간 업데이트 데이터
- 페이지네이션/무한스크롤

---

## BLoC → Zustand 변환

### 기본 구조

```dart
// Flutter BLoC
// events
abstract class AuthEvent {}
class LoginRequested extends AuthEvent {
  final String email;
  final String password;
  LoginRequested(this.email, this.password);
}
class LogoutRequested extends AuthEvent {}

// states
abstract class AuthState {}
class AuthInitial extends AuthState {}
class AuthLoading extends AuthState {}
class AuthAuthenticated extends AuthState {
  final User user;
  AuthAuthenticated(this.user);
}
class AuthError extends AuthState {
  final String message;
  AuthError(this.message);
}

// bloc
class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final AuthRepository _authRepository;

  AuthBloc(this._authRepository) : super(AuthInitial()) {
    on<LoginRequested>(_onLoginRequested);
    on<LogoutRequested>(_onLogoutRequested);
  }

  Future<void> _onLoginRequested(
    LoginRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());
    try {
      final user = await _authRepository.login(event.email, event.password);
      emit(AuthAuthenticated(user));
    } catch (e) {
      emit(AuthError(e.toString()));
    }
  }

  Future<void> _onLogoutRequested(
    LogoutRequested event,
    Emitter<AuthState> emit,
  ) async {
    await _authRepository.logout();
    emit(AuthInitial());
  }
}
```

```typescript
// Zustand Store
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authApi } from '@/lib/api/auth'
import type { User } from '@/types'

// State 타입 정의
interface AuthState {
  user: User | null
  isLoading: boolean
  error: string | null
  isAuthenticated: boolean
}

// Actions 타입 정의
interface AuthActions {
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  clearError: () => void
  reset: () => void
}

// 초기 상태
const initialState: AuthState = {
  user: null,
  isLoading: false,
  error: null,
  isAuthenticated: false,
}

// Store 생성
export const useAuthStore = create<AuthState & AuthActions>()(
  persist(
    (set, get) => ({
      ...initialState,

      // LoginRequested 이벤트 → login 액션
      login: async (email, password) => {
        set({ isLoading: true, error: null })
        try {
          const user = await authApi.login(email, password)
          set({
            user,
            isLoading: false,
            isAuthenticated: true,
          })
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Login failed',
            isLoading: false,
            isAuthenticated: false,
          })
        }
      },

      // LogoutRequested 이벤트 → logout 액션
      logout: async () => {
        await authApi.logout()
        set(initialState)
      },

      clearError: () => set({ error: null }),
      reset: () => set(initialState),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)

// Selector hooks (성능 최적화)
export const useUser = () => useAuthStore((state) => state.user)
export const useIsAuthenticated = () => useAuthStore((state) => state.isAuthenticated)
export const useAuthLoading = () => useAuthStore((state) => state.isLoading)
export const useAuthError = () => useAuthStore((state) => state.error)
```

### BlocBuilder → useStore

```dart
// Flutter
BlocBuilder<AuthBloc, AuthState>(
  builder: (context, state) {
    if (state is AuthLoading) {
      return CircularProgressIndicator();
    }
    if (state is AuthAuthenticated) {
      return Text('Hello, ${state.user.name}');
    }
    return LoginForm();
  },
)
```

```tsx
// React
function AuthStatus() {
  const { user, isLoading, isAuthenticated } = useAuthStore()

  if (isLoading) {
    return <Loader2 className="animate-spin" />
  }

  if (isAuthenticated && user) {
    return <span>Hello, {user.name}</span>
  }

  return <LoginForm />
}
```

### BlocListener → useEffect

```dart
// Flutter
BlocListener<AuthBloc, AuthState>(
  listener: (context, state) {
    if (state is AuthError) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(state.message)),
      );
    }
    if (state is AuthAuthenticated) {
      Navigator.pushReplacementNamed(context, '/home');
    }
  },
  child: ...
)
```

```tsx
// React
'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { useAuthStore } from '@/stores'

function AuthListener({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const { error, isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (error) {
      toast.error(error)
    }
  }, [error])

  useEffect(() => {
    if (isAuthenticated) {
      router.replace('/home')
    }
  }, [isAuthenticated, router])

  return <>{children}</>
}
```

---

## Riverpod → Zustand + React Query

### StateNotifierProvider → Zustand

```dart
// Flutter Riverpod
class CartNotifier extends StateNotifier<CartState> {
  CartNotifier() : super(CartState.initial());

  void addItem(Product product) {
    state = state.copyWith(
      items: [...state.items, CartItem(product: product, quantity: 1)],
    );
  }

  void removeItem(String productId) {
    state = state.copyWith(
      items: state.items.where((item) => item.product.id != productId).toList(),
    );
  }
}

final cartProvider = StateNotifierProvider<CartNotifier, CartState>((ref) {
  return CartNotifier();
});
```

```typescript
// Zustand
interface CartItem {
  product: Product
  quantity: number
}

interface CartState {
  items: CartItem[]
  total: number
}

interface CartActions {
  addItem: (product: Product) => void
  removeItem: (productId: string) => void
  updateQuantity: (productId: string, quantity: number) => void
  clear: () => void
}

export const useCartStore = create<CartState & CartActions>()(
  persist(
    (set, get) => ({
      items: [],
      total: 0,

      addItem: (product) => {
        const items = get().items
        const existingIndex = items.findIndex(
          (item) => item.product.id === product.id
        )

        if (existingIndex >= 0) {
          const newItems = [...items]
          newItems[existingIndex].quantity += 1
          set({ items: newItems })
        } else {
          set({ items: [...items, { product, quantity: 1 }] })
        }

        // total 재계산
        set((state) => ({
          total: state.items.reduce(
            (sum, item) => sum + item.product.price * item.quantity,
            0
          ),
        }))
      },

      removeItem: (productId) => {
        set((state) => ({
          items: state.items.filter((item) => item.product.id !== productId),
        }))
        // total 재계산
        set((state) => ({
          total: state.items.reduce(
            (sum, item) => sum + item.product.price * item.quantity,
            0
          ),
        }))
      },

      updateQuantity: (productId, quantity) => {
        set((state) => ({
          items: state.items.map((item) =>
            item.product.id === productId ? { ...item, quantity } : item
          ),
        }))
        set((state) => ({
          total: state.items.reduce(
            (sum, item) => sum + item.product.price * item.quantity,
            0
          ),
        }))
      },

      clear: () => set({ items: [], total: 0 }),
    }),
    {
      name: 'cart-storage',
    }
  )
)
```

### FutureProvider → React Query

```dart
// Flutter Riverpod
final productsProvider = FutureProvider<List<Product>>((ref) async {
  final repository = ref.read(productRepositoryProvider);
  return repository.getProducts();
});

// 사용
Consumer(
  builder: (context, ref, child) {
    final productsAsync = ref.watch(productsProvider);
    return productsAsync.when(
      data: (products) => ProductList(products: products),
      loading: () => CircularProgressIndicator(),
      error: (error, stack) => Text('Error: $error'),
    );
  },
)
```

```typescript
// React Query
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { productApi } from '@/lib/api/product'

// 조회
export function useProducts() {
  return useQuery({
    queryKey: ['products'],
    queryFn: () => productApi.getProducts(),
  })
}

// 단일 조회
export function useProduct(id: string) {
  return useQuery({
    queryKey: ['product', id],
    queryFn: () => productApi.getProduct(id),
    enabled: !!id,
  })
}

// 생성/수정
export function useCreateProduct() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateProductInput) => productApi.createProduct(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
    },
  })
}

// 사용
function ProductList() {
  const { data: products, isLoading, error } = useProducts()

  if (isLoading) return <Loader2 className="animate-spin" />
  if (error) return <div>Error: {error.message}</div>

  return (
    <div className="grid grid-cols-3 gap-4">
      {products?.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  )
}
```

---

## Provider (ChangeNotifier) → Zustand

```dart
// Flutter Provider
class ThemeProvider extends ChangeNotifier {
  ThemeMode _themeMode = ThemeMode.system;

  ThemeMode get themeMode => _themeMode;

  void setThemeMode(ThemeMode mode) {
    _themeMode = mode;
    notifyListeners();
  }

  void toggleTheme() {
    _themeMode = _themeMode == ThemeMode.light
        ? ThemeMode.dark
        : ThemeMode.light;
    notifyListeners();
  }
}
```

```typescript
// Zustand
type ThemeMode = 'light' | 'dark' | 'system'

interface ThemeState {
  mode: ThemeMode
}

interface ThemeActions {
  setMode: (mode: ThemeMode) => void
  toggle: () => void
}

export const useThemeStore = create<ThemeState & ThemeActions>()(
  persist(
    (set) => ({
      mode: 'system',

      setMode: (mode) => set({ mode }),

      toggle: () =>
        set((state) => ({
          mode: state.mode === 'light' ? 'dark' : 'light',
        })),
    }),
    {
      name: 'theme-storage',
    }
  )
)
```

---

## GetX → Zustand

```dart
// Flutter GetX
class CounterController extends GetxController {
  var count = 0.obs;

  void increment() => count++;
  void decrement() => count--;
  void reset() => count.value = 0;
}

// 사용
Get.put(CounterController());
Obx(() => Text('${controller.count}'))
```

```typescript
// Zustand
interface CounterState {
  count: number
}

interface CounterActions {
  increment: () => void
  decrement: () => void
  reset: () => void
}

export const useCounterStore = create<CounterState & CounterActions>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
  reset: () => set({ count: 0 }),
}))

// 사용
function Counter() {
  const { count, increment, decrement, reset } = useCounterStore()

  return (
    <div>
      <span>{count}</span>
      <button onClick={increment}>+</button>
      <button onClick={decrement}>-</button>
      <button onClick={reset}>Reset</button>
    </div>
  )
}
```

---

## 출력 파일 구조

```
src/stores/
├── index.ts              # 모든 스토어 re-export
├── auth.store.ts         # 인증 상태
├── cart.store.ts         # 장바구니 상태
├── theme.store.ts        # 테마 상태
└── ui.store.ts           # UI 상태 (모달, 사이드바 등)

src/hooks/queries/
├── index.ts              # 모든 쿼리 훅 re-export
├── useProducts.ts        # 상품 관련 쿼리
├── useUsers.ts           # 사용자 관련 쿼리
└── useOrders.ts          # 주문 관련 쿼리
```

### 스토어 파일 템플릿

```typescript
// src/stores/{name}.store.ts

import { create } from 'zustand'
import { persist, devtools } from 'zustand/middleware'

/**
 * {Name} Store
 *
 * @flutter {OriginalBlocName} (lib/blocs/{name}/{name}_bloc.dart)
 */

// Types
interface {Name}State {
  // 상태 정의
}

interface {Name}Actions {
  // 액션 정의
}

// Initial State
const initialState: {Name}State = {
  // 초기값
}

// Store
export const use{Name}Store = create<{Name}State & {Name}Actions>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        // Actions
      }),
      {
        name: '{name}-storage',
        partialize: (state) => ({
          // 영속화할 상태만 선택
        }),
      }
    ),
    { name: '{Name}Store' }
  )
)

// Selectors (성능 최적화용)
export const use{Name}Selector = () => use{Name}Store((state) => state.someValue)
```
