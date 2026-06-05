# Riverpod 3 Pattern Reference

Riverpod 3.x 상태관리 패턴 및 샘플 코드 레퍼런스입니다.

## 버전 정보

```yaml
dependencies:
  flutter_riverpod: ^3.3.1
  riverpod_annotation: ^4.0.2

dev_dependencies:
  riverpod_generator: ^4.0.3
  build_runner: ^2.15.0
```

---

## Provider 유형

### 1. 기본 Provider (동기)

```dart
// 단순 값 제공
@riverpod
String appTitle(Ref ref) {
  return 'My App';
}

// 의존성 있는 Provider
@riverpod
String greeting(Ref ref) {
  final title = ref.watch(appTitleProvider);
  return 'Welcome to $title';
}
```

### 2. FutureProvider (비동기 단일 값)

```dart
@riverpod
Future<User> currentUser(Ref ref) async {
  final authService = ref.watch(authServiceProvider);
  return authService.getCurrentUser();
}

// 사용
class ProfilePage extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final userAsync = ref.watch(currentUserProvider);

    return userAsync.when(
      data: (user) => Text(user.name),
      loading: () => const CircularProgressIndicator(),
      error: (e, st) => Text('Error: $e'),
    );
  }
}
```

### 3. StreamProvider (실시간 스트림)

```dart
@riverpod
Stream<List<Message>> messages(Ref ref) {
  final chatService = ref.watch(chatServiceProvider);
  return chatService.messagesStream();
}

// 사용
class ChatPage extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final messagesAsync = ref.watch(messagesProvider);

    return messagesAsync.when(
      data: (messages) => ListView.builder(
        itemCount: messages.length,
        itemBuilder: (_, i) => MessageTile(messages[i]),
      ),
      loading: () => const CircularProgressIndicator(),
      error: (e, st) => Text('Error: $e'),
    );
  }
}
```

---

## Notifier 패턴

### 1. Notifier (동기 상태)

```dart
@riverpod
class Counter extends _$Counter {
  @override
  int build() {
    return 0;
  }

  void increment() {
    state++;
  }

  void decrement() {
    state--;
  }

  void reset() {
    state = 0;
  }
}

// 사용
class CounterPage extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final count = ref.watch(counterProvider);

    return Column(
      children: [
        Text('Count: $count'),
        ElevatedButton(
          onPressed: () => ref.read(counterProvider.notifier).increment(),
          child: const Text('+'),
        ),
      ],
    );
  }
}
```

### 2. AsyncNotifier (비동기 상태)

```dart
@riverpod
class UserNotifier extends _$UserNotifier {
  @override
  FutureOr<User?> build() async {
    // 초기 로드 (자동 실행)
    return null;
  }

  Future<void> loadUser(String userId) async {
    state = const AsyncLoading();

    try {
      final user = await ref.read(userRepositoryProvider).getUser(userId);
      state = AsyncData(user);
    } catch (e, st) {
      state = AsyncError(e, st);
    }
  }

  Future<void> updateName(String name) async {
    final currentUser = state.valueOrNull;
    if (currentUser == null) return;

    state = const AsyncLoading();

    try {
      final updated = await ref.read(userRepositoryProvider).updateUser(
        currentUser.copyWith(name: name),
      );
      state = AsyncData(updated);
    } catch (e, st) {
      state = AsyncError(e, st);
    }
  }
}
```

### 3. StreamNotifier (스트림 기반)

```dart
@riverpod
class LiveData extends _$LiveData {
  @override
  Stream<List<Item>> build() {
    return ref.watch(databaseProvider).watchAllItems();
  }

  Future<void> addItem(Item item) async {
    await ref.read(databaseProvider).insertItem(item);
    // 스트림이 자동으로 업데이트됨
  }
}
```

---

## Family Provider (파라미터)

### 기본 Family

```dart
@riverpod
Future<Product> product(Ref ref, String productId) async {
  final repository = ref.watch(productRepositoryProvider);
  return repository.getProduct(productId);
}

// 사용
class ProductPage extends ConsumerWidget {
  final String productId;

  const ProductPage({required this.productId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final productAsync = ref.watch(productProvider(productId));

    return productAsync.when(
      data: (product) => ProductDetail(product),
      loading: () => const CircularProgressIndicator(),
      error: (e, st) => Text('Error: $e'),
    );
  }
}
```

### Family Notifier

```dart
@riverpod
class ProductDetail extends _$ProductDetail {
  @override
  FutureOr<Product?> build(String productId) async {
    return ref.watch(productRepositoryProvider).getProduct(productId);
  }

  Future<void> refresh() async {
    ref.invalidateSelf();
  }

  Future<void> addToCart() async {
    final product = state.valueOrNull;
    if (product == null) return;

    await ref.read(cartNotifierProvider.notifier).addItem(product);
  }
}
```

### 복잡한 파라미터 (Freezed 권장)

```dart
@freezed
class ProductFilter with _$ProductFilter {
  const factory ProductFilter({
    String? category,
    @Default(0) double minPrice,
    @Default(double.infinity) double maxPrice,
    @Default(SortBy.newest) SortBy sortBy,
  }) = _ProductFilter;
}

@riverpod
Future<List<Product>> filteredProducts(
  Ref ref,
  ProductFilter filter,
) async {
  final repository = ref.watch(productRepositoryProvider);
  return repository.getProducts(filter);
}

// 사용
ref.watch(filteredProductsProvider(
  const ProductFilter(category: 'electronics', minPrice: 100),
));
```

---

## Riverpod 3 신규 기능

### 1. Mutations (실험적)

```dart
@riverpod
class LoginForm extends _$LoginForm {
  @override
  LoginState build() {
    return const LoginState.idle();
  }

  @mutation
  Future<void> submit(String email, String password) async {
    // mutation이 자동으로 상태 관리 (Idle → Pending → Success/Error)
    final authService = ref.read(authServiceProvider);
    await authService.login(email, password);
  }
}

@freezed
sealed class LoginState with _$LoginState {
  const factory LoginState.idle() = _Idle;
  const factory LoginState.pending() = _Pending;
  const factory LoginState.success() = _Success;
  const factory LoginState.error(String message) = _Error;
}

// 사용
class LoginPage extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final formState = ref.watch(loginFormProvider);
    final mutation = ref.watch(loginFormProvider.notifier).submit;

    return Column(
      children: [
        // ... form fields
        ElevatedButton(
          onPressed: mutation.isPending ? null : () => mutation(email, password),
          child: mutation.isPending
              ? const CircularProgressIndicator()
              : const Text('로그인'),
        ),
        if (mutation.hasError)
          Text('에러: ${mutation.error}', style: TextStyle(color: Colors.red)),
      ],
    );
  }
}
```

### 2. Offline Persistence

```dart
@Riverpod(
  persistence: RiverpodPersistence(
    storage: SharedPreferencesStorage(),
    key: 'user_settings',
  ),
)
class UserSettings extends _$UserSettings {
  @override
  Settings build() {
    // 앱 시작 시 자동으로 저장된 값 복원
    return const Settings();
  }

  void setTheme(ThemeMode mode) {
    state = state.copyWith(themeMode: mode);
    // 자동으로 저장됨
  }
}
```

### 3. Automatic Retry

```dart
@Riverpod(retry: RetryOptions(
  maxAttempts: 3,
  delay: Duration(milliseconds: 200),
  // 지수 백오프: 200ms → 400ms → 800ms
))
Future<Data> fetchData(Ref ref) async {
  // 실패 시 자동 재시도
  return ref.watch(apiClientProvider).fetchData();
}
```

### 4. Pause/Resume (자동)

```dart
@riverpod
Stream<int> timer(Ref ref) async* {
  var i = 0;
  while (true) {
    await Future.delayed(const Duration(seconds: 1));
    yield i++;
  }
}

// TickerMode가 false일 때 (화면 밖) 자동 일시정지
class TimerWidget extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final timerValue = ref.watch(timerProvider);
    return Text('Timer: ${timerValue.valueOrNull ?? 0}');
  }
}
```

### 5. ref.mounted

```dart
@riverpod
class DataLoader extends _$DataLoader {
  @override
  FutureOr<Data?> build() => null;

  Future<void> loadData() async {
    state = const AsyncLoading();

    final data = await ref.read(apiProvider).fetchData();

    // 비동기 작업 후 Provider가 여전히 활성 상태인지 확인
    if (ref.mounted) {
      state = AsyncData(data);
    }
  }
}
```

---

## 테스트 패턴

### ProviderContainer()

```dart
void main() {
  test('Counter increments', () async {
    // test()는 테스트 후 자동 dispose
    final container = ProviderContainer(
      overrides: [
        // 필요한 오버라이드
      ],
    );

    expect(container.read(counterProvider), 0);

    container.read(counterProvider.notifier).increment();

    expect(container.read(counterProvider), 1);
  });
}
```

### AsyncNotifier 테스트

```dart
void main() {
  test('UserNotifier loads user', () async {
    final mockRepository = MockUserRepository();
    when(() => mockRepository.getUser('123'))
        .thenAnswer((_) async => testUser);

    final container = ProviderContainer(
      overrides: [
        userRepositoryProvider.overrideWithValue(mockRepository),
      ],
    );

    // 초기 상태
    expect(container.read(userNotifierProvider).isLoading, false);

    // 로드 실행
    await container.read(userNotifierProvider.notifier).loadUser('123');

    // 결과 확인
    expect(container.read(userNotifierProvider).value, testUser);
  });
}
```

### Widget 테스트

```dart
void main() {
  testWidgets('CounterPage displays count', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          counterProvider.overrideWith(() => TestCounter()),
        ],
        child: const MaterialApp(home: CounterPage()),
      ),
    );

    expect(find.text('Count: 0'), findsOneWidget);

    await tester.tap(find.text('+'));
    await tester.pump();

    expect(find.text('Count: 1'), findsOneWidget);
  });
}

class TestCounter extends _$Counter {
  @override
  int build() => 0;
}
```

### NotifierProvider.overrideWithBuild()

```dart
test('Override only build logic', () {
  final container = ProviderContainer(
    overrides: [
      // build 로직만 오버라이드, 메서드는 원본 유지
      userNotifierProvider.overrideWithBuild(
        (ref) => AsyncData(testUser),
      ),
    ],
  );

  // 초기 값이 testUser
  expect(container.read(userNotifierProvider).value, testUser);

  // 메서드는 원본 동작
  container.read(userNotifierProvider.notifier).updateName('New Name');
});
```

---

## 베스트 프랙티스

### 1. Provider 분리

```dart
// ❌ Bad: 하나의 큰 Provider
@riverpod
class AppState extends _$AppState {
  @override
  AppData build() => AppData();

  void setUser(User user) { ... }
  void setTheme(ThemeMode mode) { ... }
  void setProducts(List<Product> products) { ... }
}

// ✅ Good: 관심사별 분리
@riverpod
class AuthNotifier extends _$AuthNotifier { ... }

@riverpod
class ThemeNotifier extends _$ThemeNotifier { ... }

@riverpod
class ProductsNotifier extends _$ProductsNotifier { ... }
```

### 2. select로 리빌드 최소화

```dart
// ❌ Bad: 전체 상태 watch
final user = ref.watch(userNotifierProvider);
Text(user.value?.name ?? '');

// ✅ Good: 필요한 값만 select
final userName = ref.watch(
  userNotifierProvider.select((state) => state.value?.name),
);
Text(userName ?? '');
```

### 3. 비동기 의존성

```dart
// ❌ Bad: 동기적 접근 시도
@riverpod
SomeService someService(Ref ref) {
  final user = ref.watch(currentUserProvider).value!; // 위험!
  return SomeService(user);
}

// ✅ Good: FutureProvider로 의존성 체인
@riverpod
Future<SomeService> someService(Ref ref) async {
  final user = await ref.watch(currentUserProvider.future);
  return SomeService(user);
}
```

### 4. 에러 처리

```dart
@riverpod
class DataNotifier extends _$DataNotifier {
  @override
  FutureOr<Data?> build() => null;

  Future<void> loadData() async {
    state = const AsyncLoading();

    try {
      final data = await ref.read(repositoryProvider).getData();
      state = AsyncData(data);
    } on NetworkException catch (e) {
      state = AsyncError(e, StackTrace.current);
      // 선택적: 에러 로깅
      ref.read(loggerProvider).error('Network error', e);
    } on ValidationException catch (e) {
      state = AsyncError(e, StackTrace.current);
    } catch (e, st) {
      state = AsyncError(e, st);
    }
  }
}
```

### 5. 캐싱 전략

```dart
// keepAlive: Provider 유지 (dispose 방지)
@Riverpod(keepAlive: true)
Future<Config> appConfig(Ref ref) async {
  return ref.watch(configServiceProvider).loadConfig();
}

// 수동 캐시 무효화
void refreshConfig(WidgetRef ref) {
  ref.invalidate(appConfigProvider);
}
```

---

## Provider 의존성 그래프

```
┌─────────────────┐
│  authProvider   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  userProvider   │────▶│ profileProvider │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐
│ settingsProvider│
└─────────────────┘
```

**주의:** 순환 의존성 피하기

```dart
// ❌ Bad: 순환 의존성
@riverpod
A providerA(Ref ref) {
  final b = ref.watch(providerBProvider); // A → B
  return A(b);
}

@riverpod
B providerB(Ref ref) {
  final a = ref.watch(providerAProvider); // B → A (순환!)
  return B(a);
}
```
