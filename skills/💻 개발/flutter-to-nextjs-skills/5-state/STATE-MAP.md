# Flutter State → Zustand/React Query 매핑 레퍼런스

빠른 참조를 위한 상태관리 매핑 가이드입니다.

---

## BLoC 패턴 매핑

### 구조 매핑

| BLoC | Zustand |
|------|---------|
| `Event` | Action 함수 파라미터 |
| `State` | State interface |
| `Bloc<Event, State>` | `create<State & Actions>()` |
| `emit(state)` | `set(state)` |
| `state` | `get()` |

### 메서드 매핑

| BLoC | Zustand |
|------|---------|
| `on<Event>(handler)` | Action 함수 |
| `add(event)` | Action 함수 호출 |
| `stream` | `subscribe()` |
| `close()` | 불필요 (자동 GC) |

### 위젯 매핑

| Flutter | React |
|---------|-------|
| `BlocProvider` | 불필요 (전역 스토어) |
| `BlocBuilder` | Hook 사용 |
| `BlocListener` | `useEffect` |
| `BlocConsumer` | Hook + `useEffect` |
| `context.read<Bloc>()` | `useStore.getState()` |
| `context.watch<Bloc>()` | `useStore()` |
| `BlocSelector` | Selector 함수 |

---

## Riverpod 패턴 매핑

### Provider 타입 매핑

| Riverpod | Next.js |
|----------|---------|
| `Provider` | Zustand (읽기 전용) |
| `StateProvider` | Zustand |
| `StateNotifierProvider` | Zustand |
| `FutureProvider` | React Query `useQuery` |
| `StreamProvider` | React Query + WebSocket |
| `ChangeNotifierProvider` | Zustand |

### 메서드 매핑

| Riverpod | Zustand/React Query |
|----------|-------------------|
| `ref.watch(provider)` | `useStore()` / `useQuery()` |
| `ref.read(provider)` | `useStore.getState()` |
| `ref.listen(provider)` | `useEffect` + subscribe |
| `ref.invalidate(provider)` | `queryClient.invalidateQueries()` |
| `ref.refresh(provider)` | `queryClient.refetchQueries()` |

### AsyncValue 매핑

| Riverpod | React Query |
|----------|-------------|
| `AsyncLoading` | `isLoading: true` |
| `AsyncData(data)` | `data` |
| `AsyncError(error)` | `error` |
| `when(data:, loading:, error:)` | 조건부 렌더링 |

---

## Provider 패턴 매핑

| Provider | Zustand |
|----------|---------|
| `ChangeNotifier` | Store state + actions |
| `notifyListeners()` | `set()` (자동 리렌더) |
| `Provider.of<T>(context)` | `useStore()` |
| `Consumer<T>` | 컴포넌트에서 Hook 사용 |
| `Selector<T, S>` | Selector 함수 |
| `MultiProvider` | 여러 Store 사용 |

---

## GetX 패턴 매핑

| GetX | Zustand |
|------|---------|
| `GetxController` | Store |
| `.obs` | State property |
| `Obx(() => ...)` | Hook + 컴포넌트 |
| `Get.put<T>()` | 불필요 (전역 스토어) |
| `Get.find<T>()` | `useStore()` |
| `Get.delete<T>()` | `reset()` 액션 |
| `ever(rx, callback)` | `useEffect` + subscribe |
| `once(rx, callback)` | `useEffect` + flag |

---

## 비동기 상태 패턴

### 로딩 상태

```typescript
// Zustand 패턴
interface AsyncState<T> {
  data: T | null
  isLoading: boolean
  error: string | null
}

// React Query 패턴 (권장)
const { data, isLoading, error } = useQuery(...)
```

### 낙관적 업데이트

```typescript
// React Query
const mutation = useMutation({
  mutationFn: updateTodo,
  onMutate: async (newTodo) => {
    await queryClient.cancelQueries({ queryKey: ['todos'] })
    const previous = queryClient.getQueryData(['todos'])
    queryClient.setQueryData(['todos'], (old) => [...old, newTodo])
    return { previous }
  },
  onError: (err, newTodo, context) => {
    queryClient.setQueryData(['todos'], context.previous)
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ['todos'] })
  },
})
```

---

## 영속화 (Persistence)

### Flutter

```dart
// SharedPreferences
final prefs = await SharedPreferences.getInstance();
await prefs.setString('key', value);

// Hive
final box = await Hive.openBox('settings');
box.put('key', value);
```

### Zustand

```typescript
// persist 미들웨어
create(
  persist(
    (set) => ({ ... }),
    {
      name: 'storage-key',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ user: state.user }), // 선택적 저장
    }
  )
)
```

---

## 상태 구독

### Flutter

```dart
// BLoC
bloc.stream.listen((state) {
  // 상태 변경 처리
});
```

### Zustand

```typescript
// subscribe
const unsubscribe = useStore.subscribe(
  (state) => state.count,
  (count, prevCount) => {
    console.log('count changed:', prevCount, '->', count)
  }
)

// useEffect에서
useEffect(() => {
  const unsubscribe = useStore.subscribe(...)
  return unsubscribe
}, [])
```

---

## 파생 상태 (Computed/Derived)

### Flutter

```dart
// BLoC
int get totalPrice => state.items.fold(0, (sum, item) => sum + item.price);

// Riverpod
final totalPriceProvider = Provider<int>((ref) {
  final items = ref.watch(cartProvider).items;
  return items.fold(0, (sum, item) => sum + item.price);
});
```

### Zustand

```typescript
// Store 내부 getter (권장하지 않음)
// 대신 Selector 사용

// Selector 패턴
const useCartTotal = () =>
  useCartStore((state) =>
    state.items.reduce((sum, item) => sum + item.price, 0)
  )

// 또는 useMemo 사용
function CartSummary() {
  const items = useCartStore((state) => state.items)
  const total = useMemo(
    () => items.reduce((sum, item) => sum + item.price, 0),
    [items]
  )
  return <span>Total: {total}</span>
}
```

---

## 액션 조합

### Flutter

```dart
// BLoC
on<CheckoutRequested>((event, emit) async {
  emit(CheckoutLoading());
  try {
    await _cartRepository.checkout(state.items);
    add(ClearCart()); // 다른 이벤트 트리거
    emit(CheckoutSuccess());
  } catch (e) {
    emit(CheckoutError(e.toString()));
  }
});
```

### Zustand

```typescript
// 액션 내에서 다른 액션 호출
const useCheckoutStore = create((set, get) => ({
  checkout: async () => {
    set({ isLoading: true })
    try {
      await cartApi.checkout(get().items)
      useCartStore.getState().clear() // 다른 스토어 액션 호출
      set({ isLoading: false, success: true })
    } catch (error) {
      set({ isLoading: false, error: error.message })
    }
  },
}))
```

---

## 테스트

### Flutter BLoC

```dart
blocTest<AuthBloc, AuthState>(
  'emits [AuthLoading, AuthAuthenticated] when login succeeds',
  build: () => AuthBloc(mockRepository),
  act: (bloc) => bloc.add(LoginRequested('email', 'password')),
  expect: () => [AuthLoading(), AuthAuthenticated(mockUser)],
);
```

### Zustand

```typescript
import { act, renderHook } from '@testing-library/react'

test('login updates user state', async () => {
  const { result } = renderHook(() => useAuthStore())

  await act(async () => {
    await result.current.login('email', 'password')
  })

  expect(result.current.user).toEqual(mockUser)
  expect(result.current.isAuthenticated).toBe(true)
})
```
