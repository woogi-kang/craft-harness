---
name: unit-test
description: |
  Unit Test를 작성합니다 (Repository, UseCase, Notifier).
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Unit Test Skill

Extends: `../../_shared/unit-test/SKILL.md` (공통 테스트 원칙 참조)

Unit Test를 작성합니다 (Repository, UseCase, Notifier).

## Triggers

- "unit test", "단위 테스트"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `targetClass` | ✅ | 테스트 대상 클래스 |
| `targetPath` | ✅ | 대상 파일 경로 |

---

## 테스트 구조

```
test/
├── unit/
│   ├── features/
│   │   └── {feature}/
│   │       ├── data/
│   │       │   └── repositories/
│   │       │       └── {feature}_repository_impl_test.dart
│   │       ├── domain/
│   │       │   └── usecases/
│   │       │       └── {action}_{feature}_usecase_test.dart
│   │       └── presentation/
│   │           └── notifiers/
│   │               └── {feature}_notifier_test.dart
│   └── core/
└── helpers/
    ├── test_helper.dart
    └── mocks.dart
```

---

## Assertion 스타일

- 값/도메인 객체 검증은 `checks`를 선택적으로 사용해 타입 지향 assertion을 작성한다.
- Flutter finder, widget matcher, 기존 테스트 유틸리티와의 호환성이 더 중요한 곳은 `expect`를 유지한다.
- 한 파일 안에서 `checks`와 `expect`를 혼합할 수 있지만, 같은 assertion을 중복 작성하지 않는다.

```dart
import 'package:checks/checks.dart';

check(result.isRight()).isTrue();

result.match(
  (failure) => fail('Should not return failure'),
  (entity) {
    check(entity.id).equals('1');
    check(entity.name).isNotEmpty();
  },
);
```

---

## Test Templates

### UseCase Test

```dart
// test/unit/features/{feature}/domain/usecases/{action}_{feature}_usecase_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:checks/checks.dart';
import 'package:fpdart/fpdart.dart';

class Mock{Feature}Repository extends Mock implements {Feature}Repository {}

void main() {
  late {Action}{Feature}UseCase sut;
  late Mock{Feature}Repository mockRepository;

  setUp(() {
    mockRepository = Mock{Feature}Repository();
    sut = {Action}{Feature}UseCase(mockRepository);
  });

  group('{Action}{Feature}UseCase', () {
    final testEntity = {Feature}Entity(id: '1', name: 'Test');

    test('should return entity when repository succeeds', () async {
      // Arrange
      when(() => mockRepository.get{Feature}(any()))
          .thenAnswer((_) async => Right(testEntity));

      // Act
      final result = await sut('1');

      // Assert
      check(result).equals(Right(testEntity));
      verify(() => mockRepository.get{Feature}('1')).called(1);
    });

    test('should return failure when repository fails', () async {
      // Arrange
      const failure = ServerFailure('Server error');
      when(() => mockRepository.get{Feature}(any()))
          .thenAnswer((_) async => const Left(failure));

      // Act
      final result = await sut('1');

      // Assert
      check(result).equals(const Left(failure));
    });
  });
}
```

### Repository Test

```dart
// test/unit/features/{feature}/data/repositories/{feature}_repository_impl_test.dart
class Mock{Feature}RemoteDataSource extends Mock implements {Feature}RemoteDataSource {}
class Mock{Feature}LocalDataSource extends Mock implements {Feature}LocalDataSource {}
class MockNetworkInfo extends Mock implements NetworkInfo {}

void main() {
  late {Feature}RepositoryImpl sut;
  late Mock{Feature}RemoteDataSource mockRemoteDataSource;
  late Mock{Feature}LocalDataSource mockLocalDataSource;
  late MockNetworkInfo mockNetworkInfo;

  setUp(() {
    mockRemoteDataSource = Mock{Feature}RemoteDataSource();
    mockLocalDataSource = Mock{Feature}LocalDataSource();
    mockNetworkInfo = MockNetworkInfo();
    sut = {Feature}RepositoryImpl(
      mockRemoteDataSource,
      mockLocalDataSource,
      mockNetworkInfo,
    );
  });

  group('get{Feature}', () {
    final testModel = {Feature}Model(id: '1', name: 'Test');

    group('when online', () {
      setUp(() {
        when(() => mockNetworkInfo.isConnected).thenAnswer((_) async => true);
      });

      test('should return entity from remote', () async {
        // Arrange
        when(() => mockRemoteDataSource.get{Feature}(any()))
            .thenAnswer((_) async => testModel);
        when(() => mockLocalDataSource.cache{Feature}(any()))
            .thenAnswer((_) async {});

        // Act
        final result = await sut.get{Feature}('1');

        // Assert
        expect(result.isRight(), true);
        verify(() => mockLocalDataSource.cache{Feature}(testModel)).called(1);
      });
    });

    group('when offline', () {
      setUp(() {
        when(() => mockNetworkInfo.isConnected).thenAnswer((_) async => false);
      });

      test('should return cached entity', () async {
        // Arrange
        when(() => mockLocalDataSource.getCached{Feature}(any()))
            .thenAnswer((_) async => testModel);

        // Act
        final result = await sut.get{Feature}('1');

        // Assert
        expect(result.isRight(), true);
        verifyNever(() => mockRemoteDataSource.get{Feature}(any()));
      });
    });
  });
}
```

### Notifier Test

```dart
// test/unit/features/{feature}/presentation/notifiers/{feature}_notifier_test.dart
void main() {
  late ProviderContainer container;
  late MockGet{Feature}UseCase mockGetUseCase;

  setUp(() {
    mockGetUseCase = MockGet{Feature}UseCase();
    container = ProviderContainer(
      overrides: [
        get{Feature}UseCaseProvider.overrideWithValue(mockGetUseCase),
      ],
    );
  });

  tearDown(() => container.dispose());

  group('{Feature}Notifier', () {
    test('initial state should be AsyncData(null)', () {
      expect(
        container.read({feature}NotifierProvider),
        const AsyncData<{Feature}Entity?>(null),
      );
    });

    test('load{Feature} should update state to AsyncData', () async {
      // Arrange
      final testEntity = {Feature}Entity(id: '1', name: 'Test');
      when(() => mockGetUseCase(any()))
          .thenAnswer((_) async => Right(testEntity));

      // Act
      await container.read({feature}NotifierProvider.notifier).load{Feature}('1');

      // Assert
      expect(
        container.read({feature}NotifierProvider),
        AsyncData<{Feature}Entity?>(testEntity),
      );
    });

    test('load{Feature} should update state to AsyncError on failure', () async {
      // Arrange
      const failure = ServerFailure('Error');
      when(() => mockGetUseCase(any()))
          .thenAnswer((_) async => const Left(failure));

      // Act
      await container.read({feature}NotifierProvider.notifier).load{Feature}('1');

      // Assert
      expect(container.read({feature}NotifierProvider).hasError, true);
    });
  });
}
```

---

## 테스트 실행

```bash
# 전체 테스트
flutter test

# 특정 파일
flutter test test/unit/features/{feature}/domain/usecases/{action}_{feature}_usecase_test.dart

# 커버리지
flutter test --coverage
```

## References

- `_references/RECENT-FLUTTER-CHANGES.md`
- `_references/QUALITY-CODE-PATTERN.md`
- `_references/TEST-PATTERN.md`
