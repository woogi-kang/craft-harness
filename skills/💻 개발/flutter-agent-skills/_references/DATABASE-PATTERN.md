# Database Pattern Reference

Drift 로컬 데이터베이스 패턴 및 샘플 코드 레퍼런스입니다.

## 버전 정보

```yaml
dependencies:
  drift: ^2.33.0
  sqlite3: ^3.3.1
  path_provider: ^2.1.5
  path: ^1.9.1

dev_dependencies:
  drift_dev: ^2.33.0
  build_runner: ^2.15.0
```

`sqlite3_flutter_libs`는 `sqlite3 3.x` 이후 obsolete 상태다. 새 프로젝트는 `sqlite3`를 우선 사용하고, 기존 프로젝트에서만 마이그레이션 범위를 확인한다.

---

## 디렉토리 구조

```
lib/
├── core/
│   └── database/
│       ├── app_database.dart         # Main Database
│       ├── app_database.g.dart       # Generated
│       ├── tables/
│       │   ├── users_table.dart
│       │   ├── products_table.dart
│       │   └── orders_table.dart
│       ├── daos/
│       │   ├── user_dao.dart
│       │   ├── product_dao.dart
│       │   └── order_dao.dart
│       └── converters/
│           ├── datetime_converter.dart
│           └── json_converter.dart
│
└── features/
    └── {feature}/
        └── data/
            └── datasources/
                └── {feature}_local_datasource.dart
```

---

## Table 정의

### 기본 Table

```dart
// core/database/tables/users_table.dart
import 'package:drift/drift.dart';

class UsersTable extends Table {
  // 기본 키 (자동 증가)
  IntColumn get id => integer().autoIncrement()();

  // 외부 ID (API에서 받은 ID)
  TextColumn get externalId => text().unique()();

  // 필수 필드
  TextColumn get email => text().withLength(min: 1, max: 255)();
  TextColumn get name => text().withLength(min: 1, max: 100)();

  // 선택적 필드
  TextColumn get avatarUrl => text().nullable()();
  TextColumn get phone => text().nullable()();

  // Boolean
  BoolColumn get isVerified => boolean().withDefault(const Constant(false))();
  BoolColumn get isActive => boolean().withDefault(const Constant(true))();

  // DateTime
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
  DateTimeColumn get updatedAt => dateTime().nullable()();

  // Table 이름 커스터마이즈
  @override
  String get tableName => 'users';

  // 인덱스
  @override
  List<Set<Column>>? get uniqueKeys => [
        {email},
      ];
}
```

### 관계 Table

```dart
// core/database/tables/orders_table.dart
import 'package:drift/drift.dart';

class OrdersTable extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get externalId => text().unique()();

  // Foreign Key
  IntColumn get userId => integer().references(UsersTable, #id)();

  // Enum (숫자로 저장)
  IntColumn get status => intEnum<OrderStatus>()();

  // JSON 데이터 (문자열로 저장)
  TextColumn get itemsJson => text()();

  // 금액
  RealColumn get totalAmount => real()();
  TextColumn get currency => text().withDefault(const Constant('KRW'))();

  DateTimeColumn get orderedAt => dateTime()();
  DateTimeColumn get completedAt => dateTime().nullable()();

  @override
  String get tableName => 'orders';
}

enum OrderStatus {
  pending,
  confirmed,
  shipped,
  delivered,
  cancelled,
}
```

### 다대다 관계 Table

```dart
// core/database/tables/product_categories_table.dart
class ProductCategoriesTable extends Table {
  IntColumn get productId => integer().references(ProductsTable, #id)();
  IntColumn get categoryId => integer().references(CategoriesTable, #id)();

  @override
  Set<Column> get primaryKey => {productId, categoryId};

  @override
  String get tableName => 'product_categories';
}
```

---

## Database 클래스

### Main Database

```dart
// core/database/app_database.dart
import 'dart:io';
import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as p;
import 'package:injectable/injectable.dart';

part 'app_database.g.dart';

@DriftDatabase(
  tables: [
    UsersTable,
    ProductsTable,
    CategoriesTable,
    OrdersTable,
    ProductCategoriesTable,
  ],
  daos: [
    UserDao,
    ProductDao,
    OrderDao,
  ],
)
@singleton
class AppDatabase extends _$AppDatabase {
  AppDatabase() : super(_openConnection());

  // 스키마 버전 (마이그레이션 시 증가)
  @override
  int get schemaVersion => 1;

  // 마이그레이션 설정
  @override
  MigrationStrategy get migration => MigrationStrategy(
        onCreate: (Migrator m) async {
          await m.createAll();
        },
        onUpgrade: (Migrator m, int from, int to) async {
          // 버전별 마이그레이션
          if (from < 2) {
            // v1 → v2 마이그레이션
            // await m.addColumn(users, users.phone);
          }
          if (from < 3) {
            // v2 → v3 마이그레이션
          }
        },
        beforeOpen: (details) async {
          // Foreign Key 활성화
          await customStatement('PRAGMA foreign_keys = ON');
        },
      );
}

LazyDatabase _openConnection() {
  return LazyDatabase(() async {
    final dbFolder = await getApplicationDocumentsDirectory();
    final file = File(p.join(dbFolder.path, 'app_database.sqlite'));
    return NativeDatabase.createInBackground(file);
  });
}
```

---

## DAO (Data Access Object)

### User DAO

```dart
// core/database/daos/user_dao.dart
import 'package:drift/drift.dart';

part 'user_dao.g.dart';

@DriftAccessor(tables: [UsersTable])
class UserDao extends DatabaseAccessor<AppDatabase> with _$UserDaoMixin {
  UserDao(super.db);

  // ============ Create ============

  Future<int> insertUser(UsersTableCompanion user) {
    return into(usersTable).insert(user);
  }

  Future<void> insertOrUpdateUser(UsersTableCompanion user) {
    return into(usersTable).insertOnConflictUpdate(user);
  }

  Future<void> insertUsers(List<UsersTableCompanion> users) {
    return batch((batch) {
      batch.insertAllOnConflictUpdate(usersTable, users);
    });
  }

  // ============ Read ============

  Future<List<UsersTableData>> getAllUsers() {
    return select(usersTable).get();
  }

  Stream<List<UsersTableData>> watchAllUsers() {
    return select(usersTable).watch();
  }

  Future<UsersTableData?> getUserById(int id) {
    return (select(usersTable)..where((t) => t.id.equals(id))).getSingleOrNull();
  }

  Future<UsersTableData?> getUserByExternalId(String externalId) {
    return (select(usersTable)..where((t) => t.externalId.equals(externalId)))
        .getSingleOrNull();
  }

  Stream<UsersTableData?> watchUserById(int id) {
    return (select(usersTable)..where((t) => t.id.equals(id)))
        .watchSingleOrNull();
  }

  Future<List<UsersTableData>> searchUsers(String query) {
    return (select(usersTable)
          ..where((t) => t.name.like('%$query%') | t.email.like('%$query%')))
        .get();
  }

  Future<List<UsersTableData>> getActiveUsers() {
    return (select(usersTable)..where((t) => t.isActive.equals(true))).get();
  }

  Future<List<UsersTableData>> getUsersPaginated(int page, int limit) {
    return (select(usersTable)
          ..orderBy([(t) => OrderingTerm.desc(t.createdAt)])
          ..limit(limit, offset: page * limit))
        .get();
  }

  // ============ Update ============

  Future<int> updateUser(UsersTableCompanion user) {
    return (update(usersTable)..where((t) => t.id.equals(user.id.value)))
        .write(user);
  }

  Future<int> updateUserByExternalId(
    String externalId,
    UsersTableCompanion user,
  ) {
    return (update(usersTable)..where((t) => t.externalId.equals(externalId)))
        .write(user);
  }

  // ============ Delete ============

  Future<int> deleteUser(int id) {
    return (delete(usersTable)..where((t) => t.id.equals(id))).go();
  }

  Future<int> deleteUserByExternalId(String externalId) {
    return (delete(usersTable)..where((t) => t.externalId.equals(externalId)))
        .go();
  }

  Future<int> deleteAllUsers() {
    return delete(usersTable).go();
  }

  // ============ Count ============

  Future<int> getUserCount() async {
    final count = countAll();
    final query = selectOnly(usersTable)..addColumns([count]);
    final result = await query.getSingle();
    return result.read(count)!;
  }
}
```

### Order DAO (JOIN 예시)

```dart
// core/database/daos/order_dao.dart
part 'order_dao.g.dart';

@DriftAccessor(tables: [OrdersTable, UsersTable])
class OrderDao extends DatabaseAccessor<AppDatabase> with _$OrderDaoMixin {
  OrderDao(super.db);

  // JOIN 쿼리
  Future<List<OrderWithUser>> getOrdersWithUser() {
    final query = select(ordersTable).join([
      leftOuterJoin(usersTable, usersTable.id.equalsExp(ordersTable.userId)),
    ]);

    return query.map((row) {
      return OrderWithUser(
        order: row.readTable(ordersTable),
        user: row.readTableOrNull(usersTable),
      );
    }).get();
  }

  Stream<List<OrderWithUser>> watchOrdersWithUser() {
    final query = select(ordersTable).join([
      leftOuterJoin(usersTable, usersTable.id.equalsExp(ordersTable.userId)),
    ]);

    return query.map((row) {
      return OrderWithUser(
        order: row.readTable(ordersTable),
        user: row.readTableOrNull(usersTable),
      );
    }).watch();
  }

  // 필터링
  Future<List<OrdersTableData>> getOrdersByStatus(OrderStatus status) {
    return (select(ordersTable)..where((t) => t.status.equals(status.index)))
        .get();
  }

  Future<List<OrdersTableData>> getOrdersByUser(int userId) {
    return (select(ordersTable)..where((t) => t.userId.equals(userId))).get();
  }

  // 집계 쿼리
  Future<double> getTotalSales() async {
    final sum = ordersTable.totalAmount.sum();
    final query = selectOnly(ordersTable)
      ..addColumns([sum])
      ..where(ordersTable.status.equals(OrderStatus.delivered.index));

    final result = await query.getSingle();
    return result.read(sum) ?? 0.0;
  }

  Future<Map<OrderStatus, int>> getOrderCountByStatus() async {
    final count = countAll();
    final query = selectOnly(ordersTable)
      ..addColumns([ordersTable.status, count])
      ..groupBy([ordersTable.status]);

    final results = await query.get();
    return {
      for (final row in results)
        OrderStatus.values[row.read(ordersTable.status)!]: row.read(count)!
    };
  }
}

class OrderWithUser {
  final OrdersTableData order;
  final UsersTableData? user;

  OrderWithUser({required this.order, this.user});
}
```

---

## Type Converter

### DateTime Converter

```dart
// core/database/converters/datetime_converter.dart
import 'package:drift/drift.dart';

class DateTimeConverter extends TypeConverter<DateTime, int> {
  const DateTimeConverter();

  @override
  DateTime fromSql(int fromDb) {
    return DateTime.fromMillisecondsSinceEpoch(fromDb);
  }

  @override
  int toSql(DateTime value) {
    return value.millisecondsSinceEpoch;
  }
}
```

### JSON Converter

```dart
// core/database/converters/json_converter.dart
import 'dart:convert';
import 'package:drift/drift.dart';

class JsonListConverter<T> extends TypeConverter<List<T>, String> {
  final T Function(Map<String, dynamic>) fromJson;
  final Map<String, dynamic> Function(T) toJson;

  const JsonListConverter({
    required this.fromJson,
    required this.toJson,
  });

  @override
  List<T> fromSql(String fromDb) {
    final list = json.decode(fromDb) as List;
    return list.map((e) => fromJson(e as Map<String, dynamic>)).toList();
  }

  @override
  String toSql(List<T> value) {
    return json.encode(value.map((e) => toJson(e)).toList());
  }
}

// 사용 예시 (Order Items)
class OrderItemConverter extends TypeConverter<List<OrderItem>, String> {
  const OrderItemConverter();

  @override
  List<OrderItem> fromSql(String fromDb) {
    final list = json.decode(fromDb) as List;
    return list.map((e) => OrderItem.fromJson(e)).toList();
  }

  @override
  String toSql(List<OrderItem> value) {
    return json.encode(value.map((e) => e.toJson()).toList());
  }
}
```

---

## Local DataSource 구현

```dart
// features/user/data/datasources/user_local_datasource.dart
import 'package:injectable/injectable.dart';

abstract class UserLocalDataSource {
  Future<UserModel?> getCachedUser(String externalId);
  Future<List<UserModel>> getCachedUsers();
  Stream<List<UserModel>> watchCachedUsers();
  Future<void> cacheUser(UserModel user);
  Future<void> cacheUsers(List<UserModel> users);
  Future<void> clearUserCache();
}

@Injectable(as: UserLocalDataSource)
class UserLocalDataSourceImpl implements UserLocalDataSource {
  final UserDao _userDao;

  UserLocalDataSourceImpl(this._userDao);

  @override
  Future<UserModel?> getCachedUser(String externalId) async {
    final data = await _userDao.getUserByExternalId(externalId);
    return data?.toModel();
  }

  @override
  Future<List<UserModel>> getCachedUsers() async {
    final dataList = await _userDao.getAllUsers();
    return dataList.map((d) => d.toModel()).toList();
  }

  @override
  Stream<List<UserModel>> watchCachedUsers() {
    return _userDao.watchAllUsers().map(
          (dataList) => dataList.map((d) => d.toModel()).toList(),
        );
  }

  @override
  Future<void> cacheUser(UserModel user) async {
    await _userDao.insertOrUpdateUser(user.toCompanion());
  }

  @override
  Future<void> cacheUsers(List<UserModel> users) async {
    await _userDao.insertUsers(users.map((u) => u.toCompanion()).toList());
  }

  @override
  Future<void> clearUserCache() async {
    await _userDao.deleteAllUsers();
  }
}
```

---

## Model ↔ TableData 변환

```dart
// features/user/data/models/user_model.dart
extension UserModelX on UserModel {
  /// Model → TableCompanion
  UsersTableCompanion toCompanion() {
    return UsersTableCompanion(
      externalId: Value(id),
      email: Value(email),
      name: Value(name),
      avatarUrl: Value(avatarUrl),
      isVerified: Value(isVerified),
      updatedAt: Value(DateTime.now()),
    );
  }
}

extension UsersTableDataX on UsersTableData {
  /// TableData → Model
  UserModel toModel() {
    return UserModel(
      id: externalId,
      email: email,
      name: name,
      avatarUrl: avatarUrl,
      isVerified: isVerified,
    );
  }
}
```

---

## Transaction

```dart
// 여러 테이블에 걸친 작업
Future<void> createOrderWithItems(
  OrderModel order,
  List<OrderItemModel> items,
) async {
  await db.transaction(() async {
    // 주문 생성
    final orderId = await db.into(db.ordersTable).insert(
          order.toCompanion(),
        );

    // 주문 아이템 생성
    for (final item in items) {
      await db.into(db.orderItemsTable).insert(
            item.toCompanion(orderId),
          );
    }

    // 재고 감소
    for (final item in items) {
      await (db.update(db.productsTable)
            ..where((t) => t.id.equals(item.productId)))
          .write(
        ProductsTableCompanion(
          stock: db.productsTable.stock - item.quantity,
        ),
      );
    }
  });
}
```

---

## 마이그레이션

### 스키마 버전 업그레이드

```dart
@override
int get schemaVersion => 3;

@override
MigrationStrategy get migration => MigrationStrategy(
      onCreate: (Migrator m) async {
        await m.createAll();
      },
      onUpgrade: (Migrator m, int from, int to) async {
        // v1 → v2: users 테이블에 phone 컬럼 추가
        if (from < 2) {
          await m.addColumn(usersTable, usersTable.phone);
        }

        // v2 → v3: products 테이블에 인덱스 추가
        if (from < 3) {
          await m.createIndex(Index(
            'idx_products_category',
            'CREATE INDEX idx_products_category ON products (category_id)',
          ));
        }
      },
    );
```

### 복잡한 마이그레이션

```dart
onUpgrade: (Migrator m, int from, int to) async {
  // 테이블 이름 변경
  if (from < 2) {
    await m.renameTable(oldOrders, 'legacy_orders');
    await m.createTable(ordersTable);

    // 데이터 이전
    await customStatement('''
      INSERT INTO orders (id, user_id, total_amount, status)
      SELECT id, customer_id, amount, order_status
      FROM legacy_orders
    ''');

    await m.deleteTable('legacy_orders');
  }
},
```

---

## 테스트

### In-Memory Database

```dart
// test/core/database/user_dao_test.dart
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  late AppDatabase db;
  late UserDao sut;

  setUp(() {
    // 인메모리 데이터베이스
    db = AppDatabase.forTesting(NativeDatabase.memory());
    sut = db.userDao;
  });

  tearDown(() async {
    await db.close();
  });

  group('UserDao', () {
    test('insertUser should insert user', () async {
      // Arrange
      final user = UsersTableCompanion.insert(
        externalId: '123',
        email: 'test@example.com',
        name: 'Test User',
      );

      // Act
      final id = await sut.insertUser(user);

      // Assert
      expect(id, isPositive);

      final savedUser = await sut.getUserById(id);
      expect(savedUser?.email, 'test@example.com');
    });

    test('watchAllUsers should emit updates', () async {
      // Arrange
      final user1 = UsersTableCompanion.insert(
        externalId: '1',
        email: 'user1@example.com',
        name: 'User 1',
      );

      // Act & Assert
      expectLater(
        sut.watchAllUsers(),
        emitsInOrder([
          [], // 초기 빈 리스트
          hasLength(1), // 삽입 후
        ]),
      );

      await Future.delayed(const Duration(milliseconds: 100));
      await sut.insertUser(user1);
    });
  });
}

// Database에 테스트용 생성자 추가
class AppDatabase extends _$AppDatabase {
  AppDatabase() : super(_openConnection());

  // 테스트용 생성자
  AppDatabase.forTesting(super.e);

  // ...
}
```

---

## 베스트 프랙티스

1. **반응형 쿼리 활용**
```dart
// UI에서 직접 Stream 구독
class UserListPage extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final usersAsync = ref.watch(usersStreamProvider);

    return usersAsync.when(
      data: (users) => ListView.builder(...),
      loading: () => CircularProgressIndicator(),
      error: (e, st) => Text('Error: $e'),
    );
  }
}

@riverpod
Stream<List<UserEntity>> usersStream(Ref ref) {
  return ref.watch(userLocalDataSourceProvider).watchCachedUsers().map(
        (models) => models.map((m) => m.toEntity()).toList(),
      );
}
```

2. **배치 작업**
```dart
// 대량 데이터 삽입
Future<void> bulkInsert(List<UserModel> users) async {
  await db.batch((batch) {
    for (final user in users) {
      batch.insert(
        db.usersTable,
        user.toCompanion(),
        mode: InsertMode.insertOrReplace,
      );
    }
  });
}
```

3. **캐시 만료 전략**
```dart
// 캐시 만료 시간 컬럼 추가
DateTimeColumn get cacheExpiresAt => dateTime().nullable()();

// 만료된 캐시 삭제
Future<int> deleteExpiredCache() {
  return (delete(usersTable)
        ..where((t) => t.cacheExpiresAt.isSmallerThanValue(DateTime.now())))
      .go();
}
```

4. **Full-Text Search**
```dart
// FTS5 테이블 생성 (raw SQL)
await customStatement('''
  CREATE VIRTUAL TABLE products_fts USING fts5(
    name,
    description,
    content='products',
    content_rowid='id'
  )
''');

// 검색
Future<List<ProductsTableData>> fullTextSearch(String query) async {
  return customSelect(
    'SELECT * FROM products WHERE id IN (SELECT rowid FROM products_fts WHERE products_fts MATCH ?)',
    variables: [Variable.withString(query)],
  ).map((row) => ProductsTableData.fromData(row.data)).get();
}
```
