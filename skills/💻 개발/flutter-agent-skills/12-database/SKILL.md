---
name: database
description: |
  Drift 로컬 데이터베이스를 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Database Skill

Drift 로컬 데이터베이스를 구현합니다.

## Triggers

- "로컬 DB", "drift", "sqlite", "오프라인 저장"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `tables` | ✅ | 테이블 정의 |

---

## Output Template

### Table 정의

```dart
// core/database/tables/{entity}_table.dart
import 'package:drift/drift.dart';

class {Entity}Table extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get externalId => text().unique()();
  TextColumn get name => text().withLength(min: 1, max: 100)();
  TextColumn get description => text().nullable()();
  BoolColumn get isActive => boolean().withDefault(const Constant(true))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
  DateTimeColumn get updatedAt => dateTime().nullable()();

  @override
  String get tableName => '{entity}s';
}
```

### Database 클래스

```dart
// core/database/app_database.dart
import 'dart:io';
import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as p;
import 'package:injectable/injectable.dart';

part 'app_database.g.dart';

@DriftDatabase(tables: [{Entity}Table], daos: [{Entity}Dao])
@singleton
class AppDatabase extends _$AppDatabase {
  AppDatabase() : super(_openConnection());

  @override
  int get schemaVersion => 1;

  @override
  MigrationStrategy get migration => MigrationStrategy(
        onCreate: (m) async => await m.createAll(),
        onUpgrade: (m, from, to) async {
          // 마이그레이션 로직
        },
      );
}

LazyDatabase _openConnection() {
  return LazyDatabase(() async {
    final dbFolder = await getApplicationDocumentsDirectory();
    final file = File(p.join(dbFolder.path, 'app.sqlite'));
    return NativeDatabase.createInBackground(file);
  });
}
```

### DAO 클래스

```dart
// core/database/daos/{entity}_dao.dart
import 'package:drift/drift.dart';

part '{entity}_dao.g.dart';

@DriftAccessor(tables: [{Entity}Table])
class {Entity}Dao extends DatabaseAccessor<AppDatabase> with _${Entity}DaoMixin {
  {Entity}Dao(super.db);

  // Create
  Future<int> insert{Entity}({Entity}TableCompanion entity) {
    return into({entity}Table).insert(entity);
  }

  Future<void> insertOrUpdate{Entity}({Entity}TableCompanion entity) {
    return into({entity}Table).insertOnConflictUpdate(entity);
  }

  // Read
  Future<List<{Entity}TableData>> getAll{Entity}s() {
    return select({entity}Table).get();
  }

  Stream<List<{Entity}TableData>> watchAll{Entity}s() {
    return select({entity}Table).watch();
  }

  Future<{Entity}TableData?> get{Entity}ById(String externalId) {
    return (select({entity}Table)
          ..where((t) => t.externalId.equals(externalId)))
        .getSingleOrNull();
  }

  // Update
  Future<int> update{Entity}({Entity}TableCompanion entity) {
    return (update({entity}Table)
          ..where((t) => t.externalId.equals(entity.externalId.value)))
        .write(entity);
  }

  // Delete
  Future<int> delete{Entity}(String externalId) {
    return (delete({entity}Table)
          ..where((t) => t.externalId.equals(externalId)))
        .go();
  }

  Future<int> deleteAll() {
    return delete({entity}Table).go();
  }
}
```

### Model ↔ TableData 변환

```dart
// 확장 메서드로 변환
extension {Entity}ModelX on {Entity}Model {
  {Entity}TableCompanion toCompanion() => {Entity}TableCompanion(
        externalId: Value(id),
        name: Value(name),
        description: Value(description),
        updatedAt: Value(DateTime.now()),
      );
}

extension {Entity}TableDataX on {Entity}TableData {
  {Entity}Model toModel() => {Entity}Model(
        id: externalId,
        name: name,
        description: description,
      );
}
```

---

## 코드 생성

```bash
dart run build_runner build --delete-conflicting-outputs
```

## References

- `_references/DATABASE-PATTERN.md`
