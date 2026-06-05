---
name: entity
description: |
  Freezed 기반 Domain Entity를 생성합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Entity Skill

Freezed 기반 Domain Entity를 생성합니다.

## Triggers

- "entity 생성", "모델 생성", "데이터 클래스"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `entityName` | ✅ | Entity 이름 (PascalCase) |
| `fields` | ✅ | 필드 목록 |
| `featurePath` | ✅ | Feature 경로 |

---

## Output Template

### Entity (Domain Layer)

```dart
// features/{feature}/domain/entities/{entity}_entity.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part '{entity}_entity.freezed.dart';
part '{entity}_entity.g.dart';

@freezed
class {Entity}Entity with _${Entity}Entity {
  const factory {Entity}Entity({
    required String id,
    required String name,
    // ... 필드들
    String? optionalField,
    @Default(false) bool isActive,
  }) = _{Entity}Entity;

  factory {Entity}Entity.fromJson(Map<String, dynamic> json) =>
      _${Entity}EntityFromJson(json);
}
```

### Model (Data Layer)

```dart
// features/{feature}/data/models/{entity}_model.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part '{entity}_model.freezed.dart';
part '{entity}_model.g.dart';

@freezed
class {Entity}Model with _${Entity}Model {
  const factory {Entity}Model({
    required String id,
    required String name,
    @JsonKey(name: 'optional_field') String? optionalField,
    @JsonKey(name: 'is_active') @Default(false) bool isActive,
  }) = _{Entity}Model;

  factory {Entity}Model.fromJson(Map<String, dynamic> json) =>
      _${Entity}ModelFromJson(json);

  const {Entity}Model._();

  /// Model → Entity 변환
  {Entity}Entity toEntity() => {Entity}Entity(
        id: id,
        name: name,
        optionalField: optionalField,
        isActive: isActive,
      );

  /// Entity → Model 변환
  factory {Entity}Model.fromEntity({Entity}Entity entity) => {Entity}Model(
        id: entity.id,
        name: entity.name,
        optionalField: entity.optionalField,
        isActive: entity.isActive,
      );
}
```

---

## Freezed 기능

### Union Types (Sealed Class)

```dart
@freezed
sealed class Result<T> with _$Result<T> {
  const factory Result.success(T data) = Success<T>;
  const factory Result.failure(String message) = Failure<T>;
}

// 사용
final result = Result.success(data);
result.when(
  success: (data) => print(data),
  failure: (message) => print(message),
);
```

### copyWith

```dart
final user = UserEntity(id: '1', name: 'John');
final updated = user.copyWith(name: 'Jane');
```

### JSON Serialization

```dart
// JsonKey로 필드명 매핑
@JsonKey(name: 'created_at') DateTime createdAt,

// 기본값
@Default([]) List<String> tags,

// nullable
String? description,
```

## 코드 생성

```bash
dart run build_runner build --delete-conflicting-outputs
```

## References

- `_references/ARCHITECTURE-PATTERN.md`
