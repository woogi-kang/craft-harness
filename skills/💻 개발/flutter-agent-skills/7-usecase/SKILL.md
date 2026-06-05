---
name: usecase
description: |
  UseCase/Interactor를 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# UseCase Skill

UseCase/Interactor를 구현합니다.

## Triggers

- "usecase 생성", "비즈니스 로직"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `useCaseName` | ✅ | UseCase 이름 (Get{Entity}, Create{Entity} 등) |
| `featurePath` | ✅ | Feature 경로 |
| `params` | ❌ | 파라미터 정의 |

---

## Output Template

### 단순 UseCase (파라미터 없음)

```dart
// features/{feature}/domain/usecases/get_{entity}_list_usecase.dart
import 'package:fpdart/fpdart.dart';
import 'package:injectable/injectable.dart';

@injectable
class Get{Entity}ListUseCase {
  final {Entity}Repository _repository;

  Get{Entity}ListUseCase(this._repository);

  Future<Either<Failure, List<{Entity}Entity>>> call() {
    return _repository.get{Entity}List();
  }
}
```

### 단일 파라미터 UseCase

```dart
// features/{feature}/domain/usecases/get_{entity}_usecase.dart
import 'package:fpdart/fpdart.dart';
import 'package:injectable/injectable.dart';

@injectable
class Get{Entity}UseCase {
  final {Entity}Repository _repository;

  Get{Entity}UseCase(this._repository);

  Future<Either<Failure, {Entity}Entity>> call(String id) {
    return _repository.get{Entity}(id);
  }
}
```

### 복합 파라미터 UseCase

```dart
// features/{feature}/domain/usecases/create_{entity}_usecase.dart
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:fpdart/fpdart.dart';
import 'package:injectable/injectable.dart';

part 'create_{entity}_usecase.freezed.dart';

@injectable
class Create{Entity}UseCase {
  final {Entity}Repository _repository;

  Create{Entity}UseCase(this._repository);

  Future<Either<Failure, {Entity}Entity>> call(Create{Entity}Params params) {
    return _repository.create{Entity}(params.toEntity());
  }
}

@freezed
class Create{Entity}Params with _$Create{Entity}Params {
  const factory Create{Entity}Params({
    required String name,
    String? description,
  }) = _Create{Entity}Params;

  const Create{Entity}Params._();

  {Entity}Entity toEntity() => {Entity}Entity(
        id: '', // 서버에서 생성
        name: name,
        description: description,
      );
}
```

### Stream UseCase

```dart
// features/{feature}/domain/usecases/watch_{entity}_usecase.dart
@injectable
class Watch{Entity}UseCase {
  final {Entity}Repository _repository;

  Watch{Entity}UseCase(this._repository);

  Stream<Either<Failure, {Entity}Entity>> call(String id) {
    return _repository.watch{Entity}(id);
  }
}
```

---

## UseCase 원칙

1. **단일 책임**: 하나의 비즈니스 액션만 수행
2. **Either 반환**: 성공/실패를 명시적으로 반환
3. **Repository 의존**: Domain Layer의 Repository Interface에만 의존
4. **순수 Dart**: 외부 프레임워크 의존성 없음

## References

- `_references/ARCHITECTURE-PATTERN.md`
