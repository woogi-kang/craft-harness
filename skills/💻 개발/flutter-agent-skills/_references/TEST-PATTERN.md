# Test Pattern Reference

Flutter 테스트 패턴 및 샘플 코드 레퍼런스입니다.

## Testing Pyramid

```
                    ╱╲
                   ╱  ╲      E2E (Patrol)
                  ╱────╲     5-10%
                 ╱      ╲
                ╱────────╲   Golden Tests (Alchemist)
               ╱          ╲  10-15%
              ╱────────────╲
             ╱   Widget    ╲ 15-20%
            ╱────────────────╲
           ╱      Unit       ╲ 60-70%
          ╱────────────────────╲
```

## 버전 정보

```yaml
dev_dependencies:
  flutter_test:
    sdk: flutter
  mocktail: ^1.0.5
  checks: ^0.3.1
  patrol: ^4.6.0
  alchemist: ^0.14.0
```

`checks`는 값과 도메인 객체를 타입 지향으로 검증할 때 선택적으로 사용한다. Flutter finder/matcher와 기존 테스트 헬퍼는 `expect`를 유지해도 된다.

---

## 1. Unit Test

### 테스트 구조 (AAA 패턴)

```dart
// test/features/auth/domain/usecases/login_usecase_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:checks/checks.dart';
import 'package:fpdart/fpdart.dart';

// Mock 클래스
class MockAuthRepository extends Mock implements AuthRepository {}

void main() {
  late LoginUseCase sut; // System Under Test
  late MockAuthRepository mockRepository;

  setUp(() {
    mockRepository = MockAuthRepository();
    sut = LoginUseCase(mockRepository);
  });

  group('LoginUseCase', () {
    const testEmail = 'test@example.com';
    const testPassword = 'password123';
    final testUser = UserEntity(
      id: '1',
      email: testEmail,
      name: 'Test User',
    );

    test('should return UserEntity when login is successful', () async {
      // Arrange
      when(() => mockRepository.login(testEmail, testPassword))
          .thenAnswer((_) async => Right(testUser));

      // Act
      final result = await sut(LoginParams(
        email: testEmail,
        password: testPassword,
      ));

      // Assert
      check(result).equals(Right(testUser));
      verify(() => mockRepository.login(testEmail, testPassword)).called(1);
    });

    test('should return ServerFailure when login fails', () async {
      // Arrange
      const failure = ServerFailure('Invalid credentials');
      when(() => mockRepository.login(testEmail, testPassword))
          .thenAnswer((_) async => const Left(failure));

      // Act
      final result = await sut(LoginParams(
        email: testEmail,
        password: testPassword,
      ));

      // Assert
      check(result).equals(const Left(failure));
    });
  });
}
```

### Repository 테스트

```dart
// test/features/auth/data/repositories/auth_repository_impl_test.dart
class MockAuthRemoteDataSource extends Mock implements AuthRemoteDataSource {}
class MockAuthLocalDataSource extends Mock implements AuthLocalDataSource {}
class MockNetworkInfo extends Mock implements NetworkInfo {}

void main() {
  late AuthRepositoryImpl sut;
  late MockAuthRemoteDataSource mockRemoteDataSource;
  late MockAuthLocalDataSource mockLocalDataSource;
  late MockNetworkInfo mockNetworkInfo;

  setUp(() {
    mockRemoteDataSource = MockAuthRemoteDataSource();
    mockLocalDataSource = MockAuthLocalDataSource();
    mockNetworkInfo = MockNetworkInfo();
    sut = AuthRepositoryImpl(
      mockRemoteDataSource,
      mockLocalDataSource,
      mockNetworkInfo,
    );
  });

  group('login', () {
    const testEmail = 'test@example.com';
    const testPassword = 'password123';
    final testUserModel = UserModel(
      id: '1',
      email: testEmail,
      name: 'Test User',
    );

    test('should return user when online and login succeeds', () async {
      // Arrange
      when(() => mockNetworkInfo.isConnected).thenAnswer((_) async => true);
      when(() => mockRemoteDataSource.login(testEmail, testPassword))
          .thenAnswer((_) async => testUserModel);
      when(() => mockLocalDataSource.cacheUser(testUserModel))
          .thenAnswer((_) async {});

      // Act
      final result = await sut.login(testEmail, testPassword);

      // Assert
      expect(result.isRight(), true);
      result.fold(
        (failure) => fail('Should not return failure'),
        (user) => expect(user.email, testEmail),
      );
    });

    test('should return cached user when offline', () async {
      // Arrange
      when(() => mockNetworkInfo.isConnected).thenAnswer((_) async => false);
      when(() => mockLocalDataSource.getCachedUser())
          .thenAnswer((_) async => testUserModel);

      // Act
      final result = await sut.getCurrentUser();

      // Assert
      expect(result.isRight(), true);
      verifyNever(() => mockRemoteDataSource.login(any(), any()));
    });
  });
}
```

### Riverpod Notifier 테스트

```dart
// test/features/auth/presentation/notifiers/auth_notifier_test.dart
void main() {
  late ProviderContainer container;
  late MockLoginUseCase mockLoginUseCase;
  late MockLogoutUseCase mockLogoutUseCase;

  setUp(() {
    mockLoginUseCase = MockLoginUseCase();
    mockLogoutUseCase = MockLogoutUseCase();

    container = ProviderContainer(
      overrides: [
        loginUseCaseProvider.overrideWithValue(mockLoginUseCase),
        logoutUseCaseProvider.overrideWithValue(mockLogoutUseCase),
      ],
    );
  });

  tearDown(() {
    container.dispose();
  });

  group('AuthNotifier', () {
    test('initial state should be AsyncData(null)', () {
      // Assert
      expect(
        container.read(authNotifierProvider),
        const AsyncData<UserEntity?>(null),
      );
    });

    test('login should update state to AsyncData with user', () async {
      // Arrange
      final testUser = UserEntity(id: '1', email: 'test@test.com', name: 'Test');
      when(() => mockLoginUseCase(any()))
          .thenAnswer((_) async => Right(testUser));

      // Act
      await container.read(authNotifierProvider.notifier).login(
            'test@test.com',
            'password',
          );

      // Assert
      expect(
        container.read(authNotifierProvider),
        AsyncData<UserEntity?>(testUser),
      );
    });

    test('login should update state to AsyncError on failure', () async {
      // Arrange
      const failure = ServerFailure('Invalid credentials');
      when(() => mockLoginUseCase(any()))
          .thenAnswer((_) async => const Left(failure));

      // Act
      await container.read(authNotifierProvider.notifier).login(
            'test@test.com',
            'wrong_password',
          );

      // Assert
      final state = container.read(authNotifierProvider);
      expect(state.hasError, true);
    });
  });
}
```

---

## 2. Widget Test

### 기본 Widget Test

```dart
// test/core/design_system/atoms/app_button_test.dart
void main() {
  group('AppButton', () {
    testWidgets('renders label correctly', (tester) async {
      // Arrange & Act
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppButton(
              label: 'Test Button',
              onPressed: () {},
            ),
          ),
        ),
      );

      // Assert
      expect(find.text('Test Button'), findsOneWidget);
    });

    testWidgets('calls onPressed when tapped', (tester) async {
      // Arrange
      var pressed = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppButton(
              label: 'Test Button',
              onPressed: () => pressed = true,
            ),
          ),
        ),
      );

      // Act
      await tester.tap(find.byType(AppButton));
      await tester.pump();

      // Assert
      expect(pressed, true);
    });

    testWidgets('shows loading indicator when isLoading is true', (tester) async {
      // Arrange & Act
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppButton(
              label: 'Test Button',
              onPressed: () {},
              isLoading: true,
            ),
          ),
        ),
      );

      // Assert
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      expect(find.text('Test Button'), findsNothing);
    });

    testWidgets('is disabled when isDisabled is true', (tester) async {
      // Arrange
      var pressed = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppButton(
              label: 'Test Button',
              onPressed: () => pressed = true,
              isDisabled: true,
            ),
          ),
        ),
      );

      // Act
      await tester.tap(find.byType(AppButton));
      await tester.pump();

      // Assert
      expect(pressed, false);
    });
  });
}
```

### Riverpod Widget Test

```dart
// test/features/auth/presentation/pages/login_page_test.dart
void main() {
  late MockAuthNotifier mockAuthNotifier;

  setUp(() {
    mockAuthNotifier = MockAuthNotifier();
  });

  Widget createWidgetUnderTest() {
    return ProviderScope(
      overrides: [
        authNotifierProvider.overrideWith(() => mockAuthNotifier),
      ],
      child: const MaterialApp(home: LoginPage()),
    );
  }

  group('LoginPage', () {
    testWidgets('renders login form', (tester) async {
      // Arrange
      when(() => mockAuthNotifier.build()).thenReturn(const AsyncData(null));

      // Act
      await tester.pumpWidget(createWidgetUnderTest());

      // Assert
      expect(find.text('이메일'), findsOneWidget);
      expect(find.text('비밀번호'), findsOneWidget);
      expect(find.text('로그인'), findsOneWidget);
    });

    testWidgets('shows loading state', (tester) async {
      // Arrange
      when(() => mockAuthNotifier.build()).thenReturn(const AsyncLoading());

      // Act
      await tester.pumpWidget(createWidgetUnderTest());

      // Assert
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('calls login on form submit', (tester) async {
      // Arrange
      when(() => mockAuthNotifier.build()).thenReturn(const AsyncData(null));
      when(() => mockAuthNotifier.login(any(), any()))
          .thenAnswer((_) async {});

      await tester.pumpWidget(createWidgetUnderTest());

      // Act
      await tester.enterText(
        find.byType(TextFormField).first,
        'test@example.com',
      );
      await tester.enterText(
        find.byType(TextFormField).last,
        'password123',
      );
      await tester.tap(find.text('로그인'));
      await tester.pump();

      // Assert
      verify(() => mockAuthNotifier.login('test@example.com', 'password123'))
          .called(1);
    });

    testWidgets('shows error snackbar on login failure', (tester) async {
      // Arrange
      when(() => mockAuthNotifier.build()).thenReturn(
        AsyncError('Invalid credentials', StackTrace.current),
      );

      // Act
      await tester.pumpWidget(createWidgetUnderTest());
      await tester.pump();

      // Assert
      expect(find.text('로그인 실패'), findsOneWidget);
    });
  });
}
```

### 네비게이션 테스트

```dart
// test/features/home/presentation/pages/home_page_test.dart
void main() {
  testWidgets('navigates to profile page on avatar tap', (tester) async {
    // Arrange
    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp.router(
          routerConfig: goRouter,
        ),
      ),
    );

    // Act
    await tester.tap(find.byType(AvatarWithName));
    await tester.pumpAndSettle();

    // Assert
    expect(find.byType(ProfilePage), findsOneWidget);
  });
}
```

---

## 3. Golden Test (Alchemist)

### 설정

```dart
// test/flutter_test_config.dart
import 'dart:async';
import 'package:alchemist/alchemist.dart';

Future<void> testExecutable(FutureOr<void> Function() testMain) async {
  return AlchemistConfig.runWithConfig(
    config: const AlchemistConfig(
      theme: ThemeData.light(),
      platformGoldensConfig: PlatformGoldensConfig(
        enabled: true,
      ),
    ),
    run: testMain,
  );
}
```

### 기본 Golden Test

```dart
// test/core/design_system/atoms/app_button_golden_test.dart
import 'package:alchemist/alchemist.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('AppButton Golden Tests', () {
    goldenTest(
      'renders correctly in all variants',
      fileName: 'app_button_variants',
      builder: () => GoldenTestGroup(
        scenarioConstraints: const BoxConstraints(maxWidth: 200),
        children: [
          GoldenTestScenario(
            name: 'Primary',
            child: AppButton(
              label: 'Primary Button',
              onPressed: () {},
              variant: AppButtonVariant.primary,
            ),
          ),
          GoldenTestScenario(
            name: 'Secondary',
            child: AppButton(
              label: 'Secondary Button',
              onPressed: () {},
              variant: AppButtonVariant.secondary,
            ),
          ),
          GoldenTestScenario(
            name: 'Outline',
            child: AppButton(
              label: 'Outline Button',
              onPressed: () {},
              variant: AppButtonVariant.outline,
            ),
          ),
          GoldenTestScenario(
            name: 'Ghost',
            child: AppButton(
              label: 'Ghost Button',
              onPressed: () {},
              variant: AppButtonVariant.ghost,
            ),
          ),
          GoldenTestScenario(
            name: 'Destructive',
            child: AppButton(
              label: 'Destructive Button',
              onPressed: () {},
              variant: AppButtonVariant.destructive,
            ),
          ),
        ],
      ),
    );

    goldenTest(
      'renders correctly in all sizes',
      fileName: 'app_button_sizes',
      builder: () => GoldenTestGroup(
        scenarioConstraints: const BoxConstraints(maxWidth: 200),
        children: [
          GoldenTestScenario(
            name: 'Small',
            child: AppButton(
              label: 'Small Button',
              onPressed: () {},
              size: AppButtonSize.sm,
            ),
          ),
          GoldenTestScenario(
            name: 'Medium',
            child: AppButton(
              label: 'Medium Button',
              onPressed: () {},
              size: AppButtonSize.md,
            ),
          ),
          GoldenTestScenario(
            name: 'Large',
            child: AppButton(
              label: 'Large Button',
              onPressed: () {},
              size: AppButtonSize.lg,
            ),
          ),
        ],
      ),
    );

    goldenTest(
      'renders correctly in different states',
      fileName: 'app_button_states',
      builder: () => GoldenTestGroup(
        scenarioConstraints: const BoxConstraints(maxWidth: 200),
        children: [
          GoldenTestScenario(
            name: 'Normal',
            child: AppButton(
              label: 'Normal',
              onPressed: () {},
            ),
          ),
          GoldenTestScenario(
            name: 'Loading',
            child: AppButton(
              label: 'Loading',
              onPressed: () {},
              isLoading: true,
            ),
          ),
          GoldenTestScenario(
            name: 'Disabled',
            child: AppButton(
              label: 'Disabled',
              onPressed: () {},
              isDisabled: true,
            ),
          ),
          GoldenTestScenario(
            name: 'With Icon',
            child: AppButton(
              label: 'With Icon',
              onPressed: () {},
              icon: Icons.add,
            ),
          ),
        ],
      ),
    );
  });
}
```

### 다중 테마 Golden Test

```dart
// test/features/auth/presentation/pages/login_page_golden_test.dart
void main() {
  group('LoginPage Golden Tests', () {
    goldenTest(
      'renders correctly in light and dark themes',
      fileName: 'login_page_themes',
      builder: () => GoldenTestGroup(
        children: [
          GoldenTestScenario(
            name: 'Light Theme',
            child: Theme(
              data: lightTheme,
              child: const LoginPage(),
            ),
          ),
          GoldenTestScenario(
            name: 'Dark Theme',
            child: Theme(
              data: darkTheme,
              child: const LoginPage(),
            ),
          ),
        ],
      ),
    );

    goldenTest(
      'renders correctly on different devices',
      fileName: 'login_page_devices',
      builder: () => GoldenTestGroup(
        children: [
          GoldenTestScenario(
            name: 'iPhone SE',
            constraints: const BoxConstraints(
              maxWidth: 375,
              maxHeight: 667,
            ),
            child: const LoginPage(),
          ),
          GoldenTestScenario(
            name: 'iPhone 14 Pro',
            constraints: const BoxConstraints(
              maxWidth: 393,
              maxHeight: 852,
            ),
            child: const LoginPage(),
          ),
          GoldenTestScenario(
            name: 'iPad',
            constraints: const BoxConstraints(
              maxWidth: 768,
              maxHeight: 1024,
            ),
            child: const LoginPage(),
          ),
        ],
      ),
    );
  });
}
```

### Golden Test 실행

```bash
# 골든 파일 업데이트
flutter test --update-goldens

# 골든 테스트 실행
flutter test test/golden
```

---

## 4. E2E Test (Patrol)

### 설정

```yaml
# pubspec.yaml
dev_dependencies:
  patrol: ^4.6.0
```

```dart
// integration_test/patrol_config.dart
import 'package:patrol/patrol.dart';

void main() {
  patrolSetUp(() async {
    // 앱 시작 전 설정
  });

  patrolTearDown(() async {
    // 테스트 후 정리
  });
}
```

### 기본 E2E Test

```dart
// integration_test/auth_flow_test.dart
import 'package:patrol/patrol.dart';

void main() {
  patrolTest(
    'User can login successfully',
    ($) async {
      // 앱 시작
      await $.pumpWidgetAndSettle(const MyApp());

      // 로그인 페이지 확인
      await $(#emailInput).waitUntilVisible();

      // 이메일 입력
      await $(#emailInput).enterText('test@example.com');

      // 비밀번호 입력
      await $(#passwordInput).enterText('password123');

      // 로그인 버튼 탭
      await $(#loginButton).tap();

      // 홈 페이지로 이동 확인
      await $(#homePage).waitUntilVisible();

      // 사용자 이름 확인
      expect($(#userName).text, 'Test User');
    },
  );
}
```

### 네이티브 상호작용 테스트

```dart
// integration_test/permissions_test.dart
import 'package:patrol/patrol.dart';

void main() {
  patrolTest(
    'Handles camera permission correctly',
    ($) async {
      await $.pumpWidgetAndSettle(const MyApp());

      // 카메라 버튼 탭
      await $(#cameraButton).tap();

      // 네이티브 권한 다이얼로그 처리
      await $.native.grantPermissionWhenInUse();

      // 카메라 화면 확인
      await $(#cameraPreview).waitUntilVisible();
    },
  );

  patrolTest(
    'Handles push notification',
    ($) async {
      await $.pumpWidgetAndSettle(const MyApp());

      // 알림 권한 허용
      await $.native.grantPermissionWhenInUse();

      // 푸시 알림 대기
      await $.native.waitForNotification(
        title: 'New Message',
        timeout: const Duration(seconds: 30),
      );

      // 알림 탭
      await $.native.tapOnNotification(title: 'New Message');

      // 메시지 화면 확인
      await $(#messagePage).waitUntilVisible();
    },
  );
}
```

### WebView OAuth 테스트

```dart
// integration_test/oauth_test.dart
import 'package:patrol/patrol.dart';

void main() {
  patrolTest(
    'Google OAuth login flow',
    ($) async {
      await $.pumpWidgetAndSettle(const MyApp());

      // Google 로그인 버튼 탭
      await $(#googleLoginButton).tap();

      // WebView에서 Google 로그인 처리
      await $.native.enterText(
        Selector(text: 'Email'),
        'test@gmail.com',
      );
      await $.native.tap(Selector(text: 'Next'));

      await $.native.enterText(
        Selector(text: 'Password'),
        'password123',
      );
      await $.native.tap(Selector(text: 'Next'));

      // 로그인 완료 후 홈 화면 확인
      await $(#homePage).waitUntilVisible();
    },
  );
}
```

### E2E Test 실행

```bash
# 연결된 디바이스에서 실행
patrol test

# 특정 테스트 실행
patrol test integration_test/auth_flow_test.dart

# Hot Restart 모드로 개발
patrol develop

# CI에서 실행
patrol test --ci
```

---

## 테스트 유틸리티

### Test Helper

```dart
// test/helpers/test_helper.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// 테스트용 위젯 래퍼
Widget createTestWidget({
  required Widget child,
  List<Override> overrides = const [],
  ThemeData? theme,
}) {
  return ProviderScope(
    overrides: overrides,
    child: MaterialApp(
      theme: theme ?? ThemeData.light(),
      home: child,
    ),
  );
}

/// 테스트용 ProviderContainer
ProviderContainer createTestContainer({
  List<Override> overrides = const [],
}) {
  return ProviderContainer(overrides: overrides);
}

/// 비동기 상태 대기
Future<void> waitForAsyncValue<T>(
  ProviderContainer container,
  ProviderListenable<AsyncValue<T>> provider,
) async {
  while (container.read(provider).isLoading) {
    await Future.delayed(const Duration(milliseconds: 10));
  }
}
```

### Mock 클래스 정의

```dart
// test/mocks/mocks.dart
import 'package:mocktail/mocktail.dart';

// Repository Mocks
class MockAuthRepository extends Mock implements AuthRepository {}
class MockUserRepository extends Mock implements UserRepository {}
class MockProductRepository extends Mock implements ProductRepository {}

// UseCase Mocks
class MockLoginUseCase extends Mock implements LoginUseCase {}
class MockGetUserUseCase extends Mock implements GetUserUseCase {}

// DataSource Mocks
class MockAuthRemoteDataSource extends Mock implements AuthRemoteDataSource {}
class MockAuthLocalDataSource extends Mock implements AuthLocalDataSource {}

// Service Mocks
class MockNetworkInfo extends Mock implements NetworkInfo {}
class MockApiClient extends Mock implements ApiClient {}

// Notifier Mocks
class MockAuthNotifier extends _$AuthNotifier with Mock {}
class MockUserNotifier extends _$UserNotifier with Mock {}

// Fake 클래스 (registerFallbackValue용)
class FakeLoginParams extends Fake implements LoginParams {}
class FakeUserEntity extends Fake implements UserEntity {}

// 전역 setUp
void setUpMocks() {
  registerFallbackValue(FakeLoginParams());
  registerFallbackValue(FakeUserEntity());
}
```

### Fixture 데이터

```dart
// test/fixtures/fixtures.dart

// User Fixtures
final testUser = UserEntity(
  id: '1',
  email: 'test@example.com',
  name: 'Test User',
  avatarUrl: 'https://example.com/avatar.png',
  isVerified: true,
);

final testUserModel = UserModel(
  id: '1',
  email: 'test@example.com',
  name: 'Test User',
  avatarUrl: 'https://example.com/avatar.png',
  isVerified: true,
);

// Product Fixtures
final testProduct = ProductEntity(
  id: '1',
  name: 'Test Product',
  price: 10000,
  description: 'Test Description',
);

final testProducts = List.generate(
  10,
  (index) => ProductEntity(
    id: '${index + 1}',
    name: 'Product ${index + 1}',
    price: (index + 1) * 1000,
  ),
);
```

---

## 테스트 커버리지

### 커버리지 측정

```bash
# 커버리지 측정
flutter test --coverage

# 커버리지 리포트 생성 (lcov 필요)
genhtml coverage/lcov.info -o coverage/html

# 커버리지 리포트 열기
open coverage/html/index.html
```

### CI 설정 (GitHub Actions)

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.44.0'

      - name: Install dependencies
        run: flutter pub get

      - name: Run tests
        run: flutter test --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: coverage/lcov.info
```

---

## 테스트 체크리스트

### Unit Test
- [ ] UseCase 테스트 (성공/실패 케이스)
- [ ] Repository 테스트 (온라인/오프라인)
- [ ] Notifier 테스트 (상태 변화)
- [ ] Entity/Model 변환 테스트
- [ ] Validation 테스트

### Widget Test
- [ ] 렌더링 테스트
- [ ] 상호작용 테스트 (tap, scroll, input)
- [ ] 상태별 UI 테스트 (loading, error, data)
- [ ] 네비게이션 테스트

### Golden Test
- [ ] Atoms 컴포넌트
- [ ] Molecules 컴포넌트
- [ ] Organisms 컴포넌트
- [ ] Light/Dark 테마
- [ ] 다양한 화면 크기

### E2E Test
- [ ] 핵심 사용자 흐름
- [ ] 네이티브 권한 처리
- [ ] 오프라인 동작
- [ ] 에러 복구
