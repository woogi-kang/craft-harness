# Clean Architecture Pattern Reference

Flutter Clean Architecture 구현을 위한 패턴 및 샘플 코드 레퍼런스입니다.

## 공식 Flutter MVVM 매핑

Flutter 공식 아키텍처 가이드는 MVVM을 기준으로 UI layer와 Data layer를 나눈다. 이 하니스에서는 Clean Architecture를 유지하되 다음 이름으로 매핑한다.

| 공식 Flutter 용어 | 하니스 구조 | 책임 |
|------------------|-------------|------|
| View | `presentation/pages`, `presentation/widgets` | UI 렌더링, 사용자 입력 수신, ViewModel 명령 호출 |
| ViewModel | `presentation/notifiers` | UI 상태 생성, 사용자 액션 처리, Repository/UseCase 호출 |
| Repository | `domain/repositories` + `data/repositories` | 앱 데이터의 단일 진실 공급원, 캐싱/에러/동기화 정책 |
| Service | `data/datasources`, `core/network`, `core/database`, `core/platform` | 외부 API, DB, platform plugin/channel 접근 |
| Domain layer | `domain/usecases` | 복잡하거나 재사용되는 비즈니스 로직 |

UseCase는 선택적이다. 여러 Repository 조합, 복잡한 비즈니스 규칙, 여러 ViewModel에서 재사용되는 로직이 있을 때 추가한다.

## 레이어 구조

```
┌─────────────────────────────────────┐
│         Presentation Layer          │  ← UI, State Management
├─────────────────────────────────────┤
│           Domain Layer              │  ← Business Logic (순수 Dart)
├─────────────────────────────────────┤
│            Data Layer               │  ← External Data Sources
└─────────────────────────────────────┘
```

---

## 디렉토리 구조

```
lib/
├── core/                           # 공통 모듈
│   ├── error/
│   │   ├── exceptions.dart         # 예외 정의
│   │   └── failures.dart           # Failure 정의
│   ├── network/
│   │   ├── api_client.dart         # Retrofit API Client
│   │   ├── dio_client.dart         # Dio 설정
│   │   └── interceptors/           # Interceptors
│   ├── database/
│   │   └── app_database.dart       # Drift Database
│   ├── di/
│   │   └── injection.dart          # Injectable 설정
│   └── utils/
│       ├── extensions.dart
│       └── constants.dart
│
├── features/
│   └── {feature_name}/
│       ├── data/
│       │   ├── datasources/
│       │   │   ├── {feature}_remote_datasource.dart
│       │   │   └── {feature}_local_datasource.dart
│       │   ├── models/
│       │   │   └── {feature}_model.dart    # DTO (Freezed)
│       │   └── repositories/
│       │       └── {feature}_repository_impl.dart
│       │
│       ├── domain/
│       │   ├── entities/
│       │   │   └── {feature}_entity.dart   # Entity (Freezed)
│       │   ├── repositories/
│       │   │   └── {feature}_repository.dart   # Interface
│       │   └── usecases/
│       │       └── get_{feature}_usecase.dart
│       │
│       └── presentation/
│           ├── notifiers/
│           │   └── {feature}_notifier.dart
│           └── pages/
│               └── {feature}_page.dart
│
└── main.dart
```

---

## Layer 별 패턴

### 1. Domain Layer (핵심 비즈니스 로직)

#### Entity (Freezed)

```dart
// domain/entities/user_entity.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'user_entity.freezed.dart';
part 'user_entity.g.dart';

@freezed
class UserEntity with _$UserEntity {
  const factory UserEntity({
    required String id,
    required String email,
    required String name,
    String? avatarUrl,
    @Default(false) bool isVerified,
  }) = _UserEntity;

  factory UserEntity.fromJson(Map<String, dynamic> json) =>
      _$UserEntityFromJson(json);
}
```

#### Repository Interface

```dart
// domain/repositories/user_repository.dart
import 'package:fpdart/fpdart.dart';

abstract class UserRepository {
  /// 사용자 정보 조회
  Future<Either<Failure, UserEntity>> getUser(String id);

  /// 사용자 목록 조회
  Future<Either<Failure, List<UserEntity>>> getUsers();

  /// 사용자 정보 업데이트
  Future<Either<Failure, UserEntity>> updateUser(UserEntity user);

  /// 사용자 삭제
  Future<Either<Failure, Unit>> deleteUser(String id);
}
```

#### UseCase

```dart
// domain/usecases/get_user_usecase.dart
import 'package:fpdart/fpdart.dart';
import 'package:injectable/injectable.dart';

@injectable
class GetUserUseCase {
  final UserRepository _repository;

  GetUserUseCase(this._repository);

  Future<Either<Failure, UserEntity>> call(String userId) {
    return _repository.getUser(userId);
  }
}

// 파라미터가 여러 개인 경우
@injectable
class UpdateUserUseCase {
  final UserRepository _repository;

  UpdateUserUseCase(this._repository);

  Future<Either<Failure, UserEntity>> call(UpdateUserParams params) {
    return _repository.updateUser(params.toEntity());
  }
}

@freezed
class UpdateUserParams with _$UpdateUserParams {
  const factory UpdateUserParams({
    required String id,
    required String name,
    String? avatarUrl,
  }) = _UpdateUserParams;

  const UpdateUserParams._();

  UserEntity toEntity() => UserEntity(
        id: id,
        email: '', // 기존 값 유지
        name: name,
        avatarUrl: avatarUrl,
      );
}
```

---

### 2. Data Layer (외부 데이터 소스)

#### Model (DTO)

```dart
// data/models/user_model.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'user_model.freezed.dart';
part 'user_model.g.dart';

@freezed
class UserModel with _$UserModel {
  const factory UserModel({
    required String id,
    required String email,
    required String name,
    @JsonKey(name: 'avatar_url') String? avatarUrl,
    @JsonKey(name: 'is_verified') @Default(false) bool isVerified,
  }) = _UserModel;

  factory UserModel.fromJson(Map<String, dynamic> json) =>
      _$UserModelFromJson(json);

  const UserModel._();

  /// Model → Entity 변환
  UserEntity toEntity() => UserEntity(
        id: id,
        email: email,
        name: name,
        avatarUrl: avatarUrl,
        isVerified: isVerified,
      );

  /// Entity → Model 변환
  factory UserModel.fromEntity(UserEntity entity) => UserModel(
        id: entity.id,
        email: entity.email,
        name: entity.name,
        avatarUrl: entity.avatarUrl,
        isVerified: entity.isVerified,
      );
}
```

#### Remote DataSource

```dart
// data/datasources/user_remote_datasource.dart
import 'package:injectable/injectable.dart';

abstract class UserRemoteDataSource {
  Future<UserModel> getUser(String id);
  Future<List<UserModel>> getUsers();
  Future<UserModel> updateUser(UserModel user);
  Future<void> deleteUser(String id);
}

@Injectable(as: UserRemoteDataSource)
class UserRemoteDataSourceImpl implements UserRemoteDataSource {
  final ApiClient _apiClient;

  UserRemoteDataSourceImpl(this._apiClient);

  @override
  Future<UserModel> getUser(String id) async {
    return _apiClient.getUser(id);
  }

  @override
  Future<List<UserModel>> getUsers() async {
    return _apiClient.getUsers();
  }

  @override
  Future<UserModel> updateUser(UserModel user) async {
    return _apiClient.updateUser(user.id, user);
  }

  @override
  Future<void> deleteUser(String id) async {
    return _apiClient.deleteUser(id);
  }
}
```

#### Local DataSource (Drift)

```dart
// data/datasources/user_local_datasource.dart
import 'package:injectable/injectable.dart';

abstract class UserLocalDataSource {
  Future<UserModel?> getCachedUser(String id);
  Future<void> cacheUser(UserModel user);
  Future<void> clearCache();
}

@Injectable(as: UserLocalDataSource)
class UserLocalDataSourceImpl implements UserLocalDataSource {
  final AppDatabase _database;

  UserLocalDataSourceImpl(this._database);

  @override
  Future<UserModel?> getCachedUser(String id) async {
    final user = await _database.getUserById(id);
    return user?.toModel();
  }

  @override
  Future<void> cacheUser(UserModel user) async {
    await _database.insertOrUpdateUser(user.toCompanion());
  }

  @override
  Future<void> clearCache() async {
    await _database.clearUsers();
  }
}
```

#### Repository Implementation

```dart
// data/repositories/user_repository_impl.dart
import 'package:fpdart/fpdart.dart';
import 'package:injectable/injectable.dart';

@Injectable(as: UserRepository)
class UserRepositoryImpl implements UserRepository {
  final UserRemoteDataSource _remoteDataSource;
  final UserLocalDataSource _localDataSource;
  final NetworkInfo _networkInfo;

  UserRepositoryImpl(
    this._remoteDataSource,
    this._localDataSource,
    this._networkInfo,
  );

  @override
  Future<Either<Failure, UserEntity>> getUser(String id) async {
    if (await _networkInfo.isConnected) {
      try {
        final model = await _remoteDataSource.getUser(id);
        await _localDataSource.cacheUser(model);
        return Right(model.toEntity());
      } on ServerException catch (e) {
        return Left(ServerFailure(e.message));
      }
    } else {
      try {
        final cachedModel = await _localDataSource.getCachedUser(id);
        if (cachedModel != null) {
          return Right(cachedModel.toEntity());
        }
        return const Left(CacheFailure('No cached data'));
      } on CacheException catch (e) {
        return Left(CacheFailure(e.message));
      }
    }
  }

  @override
  Future<Either<Failure, List<UserEntity>>> getUsers() async {
    try {
      final models = await _remoteDataSource.getUsers();
      return Right(models.map((m) => m.toEntity()).toList());
    } on ServerException catch (e) {
      return Left(ServerFailure(e.message));
    }
  }

  @override
  Future<Either<Failure, UserEntity>> updateUser(UserEntity user) async {
    try {
      final model = UserModel.fromEntity(user);
      final updatedModel = await _remoteDataSource.updateUser(model);
      await _localDataSource.cacheUser(updatedModel);
      return Right(updatedModel.toEntity());
    } on ServerException catch (e) {
      return Left(ServerFailure(e.message));
    }
  }

  @override
  Future<Either<Failure, Unit>> deleteUser(String id) async {
    try {
      await _remoteDataSource.deleteUser(id);
      return const Right(unit);
    } on ServerException catch (e) {
      return Left(ServerFailure(e.message));
    }
  }
}
```

---

### 3. Presentation Layer (UI & State)

#### Notifier (Riverpod 3)

```dart
// presentation/notifiers/user_notifier.dart
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'user_notifier.g.dart';

@riverpod
class UserNotifier extends _$UserNotifier {
  @override
  FutureOr<UserEntity?> build() {
    return null;
  }

  Future<void> loadUser(String userId) async {
    state = const AsyncLoading();

    final useCase = ref.read(getUserUseCaseProvider);
    final result = await useCase(userId);

    state = result.fold(
      (failure) => AsyncError(failure, StackTrace.current),
      (user) => AsyncData(user),
    );
  }

  Future<void> updateUser(UpdateUserParams params) async {
    state = const AsyncLoading();

    final useCase = ref.read(updateUserUseCaseProvider);
    final result = await useCase(params);

    state = result.fold(
      (failure) => AsyncError(failure, StackTrace.current),
      (user) => AsyncData(user),
    );
  }
}

// 사용자 목록
@riverpod
class UsersNotifier extends _$UsersNotifier {
  @override
  FutureOr<List<UserEntity>> build() async {
    final useCase = ref.read(getUsersUseCaseProvider);
    final result = await useCase();

    return result.fold(
      (failure) => throw failure,
      (users) => users,
    );
  }

  Future<void> refresh() async {
    ref.invalidateSelf();
  }
}
```

#### Page (ConsumerWidget)

```dart
// presentation/pages/user_page.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class UserPage extends ConsumerWidget {
  final String userId;

  const UserPage({super.key, required this.userId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final userState = ref.watch(userNotifierProvider);

    // 초기 로드
    ref.listen(userNotifierProvider, (_, __) {});

    useEffect(() {
      ref.read(userNotifierProvider.notifier).loadUser(userId);
      return null;
    }, [userId]);

    return Scaffold(
      appBar: AppBar(title: const Text('사용자 정보')),
      body: userState.when(
        data: (user) => user != null
            ? UserContent(user: user)
            : const Center(child: Text('사용자를 찾을 수 없습니다')),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(child: Text('에러: $error')),
      ),
    );
  }
}

class UserContent extends StatelessWidget {
  final UserEntity user;

  const UserContent({super.key, required this.user});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(user.name, style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 8),
          Text(user.email),
          if (user.isVerified)
            const Chip(label: Text('인증됨')),
        ],
      ),
    );
  }
}
```

---

## Error Handling

### Exceptions

```dart
// core/error/exceptions.dart

/// 서버 통신 예외
class ServerException implements Exception {
  final String message;
  final int? statusCode;

  const ServerException(this.message, {this.statusCode});

  @override
  String toString() => 'ServerException: $message (code: $statusCode)';
}

/// 캐시 예외
class CacheException implements Exception {
  final String message;

  const CacheException(this.message);

  @override
  String toString() => 'CacheException: $message';
}

/// 네트워크 예외
class NetworkException implements Exception {
  final String message;

  const NetworkException(this.message);

  @override
  String toString() => 'NetworkException: $message';
}
```

### Failures

```dart
// core/error/failures.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'failures.freezed.dart';

@freezed
sealed class Failure with _$Failure {
  const factory Failure.server(String message, {int? statusCode}) = ServerFailure;
  const factory Failure.cache(String message) = CacheFailure;
  const factory Failure.network(String message) = NetworkFailure;
  const factory Failure.validation(String message) = ValidationFailure;
  const factory Failure.unknown(String message) = UnknownFailure;
}

extension FailureX on Failure {
  String get displayMessage => when(
        server: (msg, _) => msg,
        cache: (msg) => msg,
        network: (msg) => '네트워크 연결을 확인해주세요',
        validation: (msg) => msg,
        unknown: (msg) => '알 수 없는 오류가 발생했습니다',
      );
}
```

---

## DI (Injectable)

```dart
// core/di/injection.dart
import 'package:get_it/get_it.dart';
import 'package:injectable/injectable.dart';

final getIt = GetIt.instance;

@InjectableInit()
Future<void> configureDependencies() async => getIt.init();

// main.dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await configureDependencies();
  runApp(const MyApp());
}
```

---

## 의존성 방향

```
Presentation → Domain ← Data
     │           │         │
     │           │         │
     ▼           ▼         ▼
  Notifier    UseCase   Repository
     │           │      (Interface)
     │           │         │
     │           │         │
   Widget     Entity    Repository
                │        (Impl)
                │         │
                │         │
              Model  ←  DataSource
```

**핵심 원칙:**
- Domain Layer는 외부 의존성 없음 (순수 Dart)
- Data Layer는 Domain Layer에 의존
- Presentation Layer는 Domain Layer에 의존
- Entity ↔ Model 변환은 Data Layer에서 수행
- View는 데이터 표시와 이벤트 전달만 담당하고, 데이터 접근 로직은 ViewModel/UseCase/Repository로 이동
- Repository는 DataSource/API/DB/Platform Service를 감추는 단일 진실 공급원
