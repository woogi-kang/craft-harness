---
name: supabase
description: |
  Flutter 프로젝트에 Supabase 백엔드 서비스를 설정하고 통합합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Supabase Skill

Flutter 프로젝트에 Supabase 백엔드 서비스를 설정하고 통합합니다.

## Triggers

- "supabase", "수파베이스", "postgresql", "realtime db", "rls"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectName` | ✅ | 프로젝트 이름 |
| `supabaseUrl` | ✅ | Supabase 프로젝트 URL |
| `supabaseAnonKey` | ✅ | Supabase Anonymous Key |
| `useFlavors` | ❌ | Flavor별 Supabase 설정 여부 (기본: true) |

---

## Supabase vs Firebase

| 항목 | Supabase | Firebase |
|------|----------|----------|
| **DB 타입** | PostgreSQL (관계형) | Firestore (NoSQL) |
| **쿼리** | SQL 전체 지원 (JOIN, 서브쿼리) | 제한적 복합 쿼리 |
| **보안** | Row Level Security (RLS) | Security Rules |
| **오프라인** | 별도 구현 필요 | Built-in |
| **오픈소스** | ✅ (셀프호스팅 가능) | ❌ |
| **무료 티어** | 50K MAU, 500MB DB | 제한적 |

---

## 설정

### pubspec.yaml

```yaml
dependencies:
  # Supabase
  supabase_flutter: ^2.12.4
```

---

## Output Templates

### 1. Supabase 초기화 (Flavor 통합)

```dart
// lib/core/supabase/supabase_initializer.dart
import 'package:supabase_flutter/supabase_flutter.dart';
import '../config/flavor_config.dart';
import '../config/env/env_dev.dart' as dev;
import '../config/env/env_staging.dart' as staging;
import '../config/env/env_prod.dart' as prod;

class SupabaseInitializer {
  static Future<void> initialize() async {
    final config = _getSupabaseConfig();

    await Supabase.initialize(
      url: config.url,
      anonKey: config.anonKey,
      debug: FlavorConfig.isDev,
      authOptions: const FlutterAuthClientOptions(
        authFlowType: AuthFlowType.pkce,
      ),
      realtimeClientOptions: const RealtimeClientOptions(
        logLevel: RealtimeLogLevel.info,
      ),
    );
  }

  static ({String url, String anonKey}) _getSupabaseConfig() {
    switch (FlavorConfig.instance.flavor) {
      case Flavor.dev:
        return (url: dev.EnvDev.supabaseUrl, anonKey: dev.EnvDev.supabaseAnonKey);
      case Flavor.staging:
        return (url: staging.EnvStaging.supabaseUrl, anonKey: staging.EnvStaging.supabaseAnonKey);
      case Flavor.prod:
        return (url: prod.EnvProd.supabaseUrl, anonKey: prod.EnvProd.supabaseAnonKey);
    }
  }

  static SupabaseClient get client => Supabase.instance.client;
}
```

### 2. 환경 변수 (envied)

```dart
// lib/core/config/env/env_dev.dart
import 'package:envied/envied.dart';

part 'env_dev.g.dart';

@Envied(path: '.env.dev', obfuscate: true)
abstract class EnvDev {
  @EnviedField(varName: 'SUPABASE_URL')
  static const String supabaseUrl = _EnvDev.supabaseUrl;

  @EnviedField(varName: 'SUPABASE_ANON_KEY')
  static const String supabaseAnonKey = _EnvDev.supabaseAnonKey;
}
```

```
# .env.dev
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3. Entry Point with Supabase

```dart
// lib/main_dev.dart
import 'package:flutter/material.dart';
import 'core/config/flavor_config.dart';
import 'core/supabase/supabase_initializer.dart';
import 'app.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Flavor 설정
  FlavorConfig.dev();

  // Supabase 초기화
  await SupabaseInitializer.initialize();

  runApp(const App());
}
```

### 4. Supabase Auth Service

```dart
// lib/core/supabase/services/supabase_auth_service.dart
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:fpdart/fpdart.dart';
import '../../error/failures.dart';

abstract class SupabaseAuthService {
  Stream<AuthState> get authStateChanges;
  User? get currentUser;
  Session? get currentSession;

  Future<Either<Failure, AuthResponse>> signInWithEmail({
    required String email,
    required String password,
  });

  Future<Either<Failure, AuthResponse>> signUpWithEmail({
    required String email,
    required String password,
    Map<String, dynamic>? data,
  });

  Future<Either<Failure, void>> signInWithOAuth(OAuthProvider provider);

  Future<Either<Failure, void>> signInWithMagicLink(String email);

  Future<Either<Failure, void>> signOut();

  Future<Either<Failure, void>> resetPassword(String email);

  Future<Either<Failure, UserResponse>> updateUser({
    String? email,
    String? password,
    Map<String, dynamic>? data,
  });
}

class SupabaseAuthServiceImpl implements SupabaseAuthService {
  final SupabaseClient _client;

  SupabaseAuthServiceImpl({SupabaseClient? client})
      : _client = client ?? Supabase.instance.client;

  @override
  Stream<AuthState> get authStateChanges =>
      _client.auth.onAuthStateChange;

  @override
  User? get currentUser => _client.auth.currentUser;

  @override
  Session? get currentSession => _client.auth.currentSession;

  @override
  Future<Either<Failure, AuthResponse>> signInWithEmail({
    required String email,
    required String password,
  }) async {
    try {
      final response = await _client.auth.signInWithPassword(
        email: email,
        password: password,
      );
      return right(response);
    } on AuthException catch (e) {
      return left(_mapAuthException(e));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, AuthResponse>> signUpWithEmail({
    required String email,
    required String password,
    Map<String, dynamic>? data,
  }) async {
    try {
      final response = await _client.auth.signUp(
        email: email,
        password: password,
        data: data,
      );
      return right(response);
    } on AuthException catch (e) {
      return left(_mapAuthException(e));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, void>> signInWithOAuth(OAuthProvider provider) async {
    try {
      await _client.auth.signInWithOAuth(
        provider,
        redirectTo: 'io.supabase.app://login-callback',
      );
      return right(null);
    } on AuthException catch (e) {
      return left(_mapAuthException(e));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, void>> signInWithMagicLink(String email) async {
    try {
      await _client.auth.signInWithOtp(
        email: email,
        emailRedirectTo: 'io.supabase.app://login-callback',
      );
      return right(null);
    } on AuthException catch (e) {
      return left(_mapAuthException(e));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, void>> signOut() async {
    try {
      await _client.auth.signOut();
      return right(null);
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, void>> resetPassword(String email) async {
    try {
      await _client.auth.resetPasswordForEmail(email);
      return right(null);
    } on AuthException catch (e) {
      return left(_mapAuthException(e));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, UserResponse>> updateUser({
    String? email,
    String? password,
    Map<String, dynamic>? data,
  }) async {
    try {
      final response = await _client.auth.updateUser(
        UserAttributes(
          email: email,
          password: password,
          data: data,
        ),
      );
      return right(response);
    } on AuthException catch (e) {
      return left(_mapAuthException(e));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  Failure _mapAuthException(AuthException e) {
    switch (e.statusCode) {
      case '400':
        return AuthFailure(message: e.message);
      case '401':
        return const AuthFailure(message: '인증이 필요합니다.');
      case '422':
        return const AuthFailure(message: '입력값을 확인해주세요.');
      case '429':
        return const AuthFailure(message: '너무 많은 요청입니다. 잠시 후 다시 시도해주세요.');
      default:
        return AuthFailure(message: e.message);
    }
  }
}
```

### 5. Supabase Database Service

```dart
// lib/core/supabase/services/supabase_database_service.dart
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:fpdart/fpdart.dart';
import '../../error/failures.dart';

abstract class SupabaseDatabaseService {
  // Single Record
  Future<Either<Failure, T>> getById<T>({
    required String table,
    required String id,
    required T Function(Map<String, dynamic>) fromJson,
    String? select,
  });

  // List Records
  Future<Either<Failure, List<T>>> getAll<T>({
    required String table,
    required T Function(Map<String, dynamic>) fromJson,
    String? select,
    Map<String, dynamic>? filters,
    String? orderBy,
    bool ascending = true,
    int? limit,
    int? offset,
  });

  // Insert
  Future<Either<Failure, T>> insert<T>({
    required String table,
    required Map<String, dynamic> data,
    required T Function(Map<String, dynamic>) fromJson,
  });

  // Update
  Future<Either<Failure, T>> update<T>({
    required String table,
    required String id,
    required Map<String, dynamic> data,
    required T Function(Map<String, dynamic>) fromJson,
  });

  // Upsert
  Future<Either<Failure, T>> upsert<T>({
    required String table,
    required Map<String, dynamic> data,
    required T Function(Map<String, dynamic>) fromJson,
  });

  // Delete
  Future<Either<Failure, void>> delete({
    required String table,
    required String id,
  });

  // Stream (Realtime)
  Stream<List<T>> stream<T>({
    required String table,
    required T Function(Map<String, dynamic>) fromJson,
    String? primaryKey,
  });

  // RPC (Stored Procedure)
  Future<Either<Failure, T>> rpc<T>({
    required String functionName,
    Map<String, dynamic>? params,
    required T Function(dynamic) fromJson,
  });
}

class SupabaseDatabaseServiceImpl implements SupabaseDatabaseService {
  final SupabaseClient _client;

  SupabaseDatabaseServiceImpl({SupabaseClient? client})
      : _client = client ?? Supabase.instance.client;

  @override
  Future<Either<Failure, T>> getById<T>({
    required String table,
    required String id,
    required T Function(Map<String, dynamic>) fromJson,
    String? select,
  }) async {
    try {
      final response = await _client
          .from(table)
          .select(select ?? '*')
          .eq('id', id)
          .single();
      return right(fromJson(response));
    } on PostgrestException catch (e) {
      return left(_mapPostgrestException(e));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, List<T>>> getAll<T>({
    required String table,
    required T Function(Map<String, dynamic>) fromJson,
    String? select,
    Map<String, dynamic>? filters,
    String? orderBy,
    bool ascending = true,
    int? limit,
    int? offset,
  }) async {
    try {
      var query = _client.from(table).select(select ?? '*');

      // Apply filters
      if (filters != null) {
        filters.forEach((key, value) {
          if (value is List) {
            query = query.inFilter(key, value);
          } else {
            query = query.eq(key, value);
          }
        });
      }

      // Apply ordering
      if (orderBy != null) {
        query = query.order(orderBy, ascending: ascending);
      }

      // Apply pagination
      if (limit != null) {
        query = query.limit(limit);
      }
      if (offset != null) {
        query = query.range(offset, offset + (limit ?? 10) - 1);
      }

      final response = await query;
      final items = (response as List)
          .map((item) => fromJson(item as Map<String, dynamic>))
          .toList();
      return right(items);
    } on PostgrestException catch (e) {
      return left(_mapPostgrestException(e));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, T>> insert<T>({
    required String table,
    required Map<String, dynamic> data,
    required T Function(Map<String, dynamic>) fromJson,
  }) async {
    try {
      final response = await _client
          .from(table)
          .insert(data)
          .select()
          .single();
      return right(fromJson(response));
    } on PostgrestException catch (e) {
      return left(_mapPostgrestException(e));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, T>> update<T>({
    required String table,
    required String id,
    required Map<String, dynamic> data,
    required T Function(Map<String, dynamic>) fromJson,
  }) async {
    try {
      final response = await _client
          .from(table)
          .update(data)
          .eq('id', id)
          .select()
          .single();
      return right(fromJson(response));
    } on PostgrestException catch (e) {
      return left(_mapPostgrestException(e));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, T>> upsert<T>({
    required String table,
    required Map<String, dynamic> data,
    required T Function(Map<String, dynamic>) fromJson,
  }) async {
    try {
      final response = await _client
          .from(table)
          .upsert(data)
          .select()
          .single();
      return right(fromJson(response));
    } on PostgrestException catch (e) {
      return left(_mapPostgrestException(e));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, void>> delete({
    required String table,
    required String id,
  }) async {
    try {
      await _client.from(table).delete().eq('id', id);
      return right(null);
    } on PostgrestException catch (e) {
      return left(_mapPostgrestException(e));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Stream<List<T>> stream<T>({
    required String table,
    required T Function(Map<String, dynamic>) fromJson,
    String? primaryKey,
  }) {
    return _client
        .from(table)
        .stream(primaryKey: [primaryKey ?? 'id'])
        .map((data) => data.map((item) => fromJson(item)).toList());
  }

  @override
  Future<Either<Failure, T>> rpc<T>({
    required String functionName,
    Map<String, dynamic>? params,
    required T Function(dynamic) fromJson,
  }) async {
    try {
      final response = await _client.rpc(functionName, params: params);
      return right(fromJson(response));
    } on PostgrestException catch (e) {
      return left(_mapPostgrestException(e));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  Failure _mapPostgrestException(PostgrestException e) {
    switch (e.code) {
      case '23505': // unique_violation
        return const ServerFailure(message: '이미 존재하는 데이터입니다.');
      case '23503': // foreign_key_violation
        return const ServerFailure(message: '참조 데이터가 존재하지 않습니다.');
      case '42501': // insufficient_privilege
        return const ServerFailure(message: '권한이 없습니다.');
      case 'PGRST116': // not found
        return const NotFoundFailure(message: '데이터를 찾을 수 없습니다.');
      default:
        return ServerFailure(message: e.message);
    }
  }
}
```

### 6. 복합 쿼리 예시 (JOIN, 필터링)

```dart
// lib/features/post/data/datasources/post_remote_datasource.dart
import 'package:supabase_flutter/supabase_flutter.dart';

class PostRemoteDataSource {
  final SupabaseClient _client;

  PostRemoteDataSource({SupabaseClient? client})
      : _client = client ?? Supabase.instance.client;

  // JOIN 쿼리 (author 정보 포함)
  Future<List<Map<String, dynamic>>> getPostsWithAuthor() async {
    final response = await _client
        .from('posts')
        .select('''
          id,
          title,
          content,
          created_at,
          author:profiles(id, username, avatar_url)
        ''')
        .order('created_at', ascending: false);
    return List<Map<String, dynamic>>.from(response);
  }

  // 복합 필터 쿼리
  Future<List<Map<String, dynamic>>> searchPosts({
    String? keyword,
    String? categoryId,
    DateTime? startDate,
    DateTime? endDate,
    int limit = 20,
    int offset = 0,
  }) async {
    var query = _client.from('posts').select('''
      *,
      author:profiles(username, avatar_url),
      category:categories(name)
    ''');

    // 키워드 검색 (제목 또는 내용)
    if (keyword != null && keyword.isNotEmpty) {
      query = query.or('title.ilike.%$keyword%,content.ilike.%$keyword%');
    }

    // 카테고리 필터
    if (categoryId != null) {
      query = query.eq('category_id', categoryId);
    }

    // 날짜 범위 필터
    if (startDate != null) {
      query = query.gte('created_at', startDate.toIso8601String());
    }
    if (endDate != null) {
      query = query.lte('created_at', endDate.toIso8601String());
    }

    // 정렬 및 페이지네이션
    final response = await query
        .order('created_at', ascending: false)
        .range(offset, offset + limit - 1);

    return List<Map<String, dynamic>>.from(response);
  }

  // Full Text Search (PostgreSQL)
  Future<List<Map<String, dynamic>>> fullTextSearch(String query) async {
    final response = await _client
        .from('posts')
        .select()
        .textSearch('fts', query, type: TextSearchType.websearch);
    return List<Map<String, dynamic>>.from(response);
  }

  // Count 쿼리
  Future<int> getPostCount({String? categoryId}) async {
    var query = _client.from('posts').select('id');
    if (categoryId != null) {
      query = query.eq('category_id', categoryId);
    }
    final response = await query.count(CountOption.exact);
    return response.count;
  }
}
```

### 7. Supabase Storage Service

```dart
// lib/core/supabase/services/supabase_storage_service.dart
import 'dart:io';
import 'dart:typed_data';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:fpdart/fpdart.dart';
import 'package:path/path.dart' as path;
import '../../error/failures.dart';

abstract class SupabaseStorageService {
  Future<Either<Failure, String>> uploadFile({
    required String bucket,
    required String filePath,
    required File file,
  });

  Future<Either<Failure, String>> uploadBytes({
    required String bucket,
    required String filePath,
    required Uint8List bytes,
    String? contentType,
  });

  Future<Either<Failure, Uint8List>> downloadFile({
    required String bucket,
    required String filePath,
  });

  Future<Either<Failure, void>> deleteFile({
    required String bucket,
    required String filePath,
  });

  Future<Either<Failure, List<FileObject>>> listFiles({
    required String bucket,
    String? folderPath,
  });

  String getPublicUrl({
    required String bucket,
    required String filePath,
  });

  Future<Either<Failure, String>> createSignedUrl({
    required String bucket,
    required String filePath,
    required Duration expiresIn,
  });
}

class SupabaseStorageServiceImpl implements SupabaseStorageService {
  final SupabaseClient _client;

  SupabaseStorageServiceImpl({SupabaseClient? client})
      : _client = client ?? Supabase.instance.client;

  @override
  Future<Either<Failure, String>> uploadFile({
    required String bucket,
    required String filePath,
    required File file,
  }) async {
    try {
      final bytes = await file.readAsBytes();
      final extension = path.extension(file.path);
      final contentType = _getContentType(extension);

      await _client.storage.from(bucket).uploadBinary(
        filePath,
        bytes,
        fileOptions: FileOptions(contentType: contentType),
      );

      return right(getPublicUrl(bucket: bucket, filePath: filePath));
    } on StorageException catch (e) {
      return left(ServerFailure(message: e.message));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, String>> uploadBytes({
    required String bucket,
    required String filePath,
    required Uint8List bytes,
    String? contentType,
  }) async {
    try {
      await _client.storage.from(bucket).uploadBinary(
        filePath,
        bytes,
        fileOptions: FileOptions(contentType: contentType),
      );

      return right(getPublicUrl(bucket: bucket, filePath: filePath));
    } on StorageException catch (e) {
      return left(ServerFailure(message: e.message));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, Uint8List>> downloadFile({
    required String bucket,
    required String filePath,
  }) async {
    try {
      final bytes = await _client.storage.from(bucket).download(filePath);
      return right(bytes);
    } on StorageException catch (e) {
      return left(ServerFailure(message: e.message));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, void>> deleteFile({
    required String bucket,
    required String filePath,
  }) async {
    try {
      await _client.storage.from(bucket).remove([filePath]);
      return right(null);
    } on StorageException catch (e) {
      return left(ServerFailure(message: e.message));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, List<FileObject>>> listFiles({
    required String bucket,
    String? folderPath,
  }) async {
    try {
      final files = await _client.storage.from(bucket).list(path: folderPath);
      return right(files);
    } on StorageException catch (e) {
      return left(ServerFailure(message: e.message));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  String getPublicUrl({
    required String bucket,
    required String filePath,
  }) {
    return _client.storage.from(bucket).getPublicUrl(filePath);
  }

  @override
  Future<Either<Failure, String>> createSignedUrl({
    required String bucket,
    required String filePath,
    required Duration expiresIn,
  }) async {
    try {
      final url = await _client.storage
          .from(bucket)
          .createSignedUrl(filePath, expiresIn.inSeconds);
      return right(url);
    } on StorageException catch (e) {
      return left(ServerFailure(message: e.message));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  String _getContentType(String extension) {
    switch (extension.toLowerCase()) {
      case '.jpg':
      case '.jpeg':
        return 'image/jpeg';
      case '.png':
        return 'image/png';
      case '.gif':
        return 'image/gif';
      case '.webp':
        return 'image/webp';
      case '.pdf':
        return 'application/pdf';
      case '.mp4':
        return 'video/mp4';
      default:
        return 'application/octet-stream';
    }
  }
}
```

### 8. Supabase Realtime Service

```dart
// lib/core/supabase/services/supabase_realtime_service.dart
import 'package:supabase_flutter/supabase_flutter.dart';

enum RealtimeEvent { insert, update, delete, all }

class SupabaseRealtimeService {
  final SupabaseClient _client;
  final Map<String, RealtimeChannel> _channels = {};

  SupabaseRealtimeService({SupabaseClient? client})
      : _client = client ?? Supabase.instance.client;

  /// PostgreSQL Changes 구독
  RealtimeChannel subscribeToTable<T>({
    required String table,
    required void Function(T payload) onInsert,
    void Function(T payload)? onUpdate,
    void Function(T payload)? onDelete,
    required T Function(Map<String, dynamic>) fromJson,
    String? schema,
    String? filter,
  }) {
    final channelName = 'public:$table';

    final channel = _client.channel(channelName);

    channel.onPostgresChanges(
      event: PostgresChangeEvent.insert,
      schema: schema ?? 'public',
      table: table,
      filter: filter,
      callback: (payload) {
        onInsert(fromJson(payload.newRecord));
      },
    );

    if (onUpdate != null) {
      channel.onPostgresChanges(
        event: PostgresChangeEvent.update,
        schema: schema ?? 'public',
        table: table,
        callback: (payload) {
          onUpdate(fromJson(payload.newRecord));
        },
      );
    }

    if (onDelete != null) {
      channel.onPostgresChanges(
        event: PostgresChangeEvent.delete,
        schema: schema ?? 'public',
        table: table,
        callback: (payload) {
          onDelete(fromJson(payload.oldRecord));
        },
      );
    }

    channel.subscribe();
    _channels[channelName] = channel;

    return channel;
  }

  /// Broadcast 채널 (커스텀 이벤트)
  RealtimeChannel subscribeToBroadcast({
    required String channelName,
    required String event,
    required void Function(Map<String, dynamic> payload) onMessage,
  }) {
    final channel = _client.channel(channelName);

    channel.onBroadcast(
      event: event,
      callback: (payload) => onMessage(payload),
    );

    channel.subscribe();
    _channels[channelName] = channel;

    return channel;
  }

  /// Broadcast 메시지 전송
  Future<void> broadcast({
    required String channelName,
    required String event,
    required Map<String, dynamic> payload,
  }) async {
    final channel = _channels[channelName];
    if (channel != null) {
      await channel.sendBroadcastMessage(
        event: event,
        payload: payload,
      );
    }
  }

  /// Presence (온라인 상태)
  RealtimeChannel subscribeToPresence({
    required String channelName,
    required void Function(List<Map<String, dynamic>> users) onSync,
    void Function(Map<String, dynamic> newUser)? onJoin,
    void Function(Map<String, dynamic> leftUser)? onLeave,
  }) {
    final channel = _client.channel(channelName);

    channel.onPresenceSync((payload) {
      final users = channel.presenceState().values.expand((e) => e).toList();
      onSync(users.map((u) => u.payload).toList());
    });

    if (onJoin != null) {
      channel.onPresenceJoin((payload) {
        onJoin(payload.newPresences.first.payload);
      });
    }

    if (onLeave != null) {
      channel.onPresenceLeave((payload) {
        onLeave(payload.leftPresences.first.payload);
      });
    }

    channel.subscribe((status, error) async {
      if (status == RealtimeSubscribeStatus.subscribed) {
        await channel.track({
          'user_id': _client.auth.currentUser?.id,
          'online_at': DateTime.now().toIso8601String(),
        });
      }
    });

    _channels[channelName] = channel;
    return channel;
  }

  /// 채널 해제
  Future<void> unsubscribe(String channelName) async {
    final channel = _channels[channelName];
    if (channel != null) {
      await _client.removeChannel(channel);
      _channels.remove(channelName);
    }
  }

  /// 모든 채널 해제
  Future<void> unsubscribeAll() async {
    for (final channel in _channels.values) {
      await _client.removeChannel(channel);
    }
    _channels.clear();
  }
}
```

### 9. Edge Functions 호출

```dart
// lib/core/supabase/services/supabase_functions_service.dart
import 'dart:convert';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:fpdart/fpdart.dart';
import '../../error/failures.dart';

class SupabaseFunctionsService {
  final SupabaseClient _client;

  SupabaseFunctionsService({SupabaseClient? client})
      : _client = client ?? Supabase.instance.client;

  Future<Either<Failure, T>> invoke<T>({
    required String functionName,
    Map<String, dynamic>? body,
    Map<String, String>? headers,
    required T Function(dynamic) fromJson,
  }) async {
    try {
      final response = await _client.functions.invoke(
        functionName,
        body: body,
        headers: headers,
      );

      if (response.status >= 400) {
        return left(ServerFailure(
          message: response.data?['error'] ?? 'Function error',
        ));
      }

      return right(fromJson(response.data));
    } on FunctionException catch (e) {
      return left(ServerFailure(message: e.details?.toString() ?? e.toString()));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }
}
```

### 10. Supabase Providers (Riverpod)

```dart
// lib/core/supabase/providers/supabase_providers.dart
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../services/supabase_auth_service.dart';
import '../services/supabase_database_service.dart';
import '../services/supabase_storage_service.dart';
import '../services/supabase_realtime_service.dart';
import '../services/supabase_functions_service.dart';

part 'supabase_providers.g.dart';

// Supabase Client
@riverpod
SupabaseClient supabaseClient(SupabaseClientRef ref) {
  return Supabase.instance.client;
}

// Services
@riverpod
SupabaseAuthService supabaseAuthService(SupabaseAuthServiceRef ref) {
  return SupabaseAuthServiceImpl(client: ref.watch(supabaseClientProvider));
}

@riverpod
SupabaseDatabaseService supabaseDatabaseService(SupabaseDatabaseServiceRef ref) {
  return SupabaseDatabaseServiceImpl(client: ref.watch(supabaseClientProvider));
}

@riverpod
SupabaseStorageService supabaseStorageService(SupabaseStorageServiceRef ref) {
  return SupabaseStorageServiceImpl(client: ref.watch(supabaseClientProvider));
}

@riverpod
SupabaseRealtimeService supabaseRealtimeService(SupabaseRealtimeServiceRef ref) {
  return SupabaseRealtimeService(client: ref.watch(supabaseClientProvider));
}

@riverpod
SupabaseFunctionsService supabaseFunctionsService(SupabaseFunctionsServiceRef ref) {
  return SupabaseFunctionsService(client: ref.watch(supabaseClientProvider));
}

// Auth State Stream
@riverpod
Stream<AuthState> supabaseAuthState(SupabaseAuthStateRef ref) {
  return ref.watch(supabaseAuthServiceProvider).authStateChanges;
}

// Current User
@riverpod
User? currentUser(CurrentUserRef ref) {
  ref.watch(supabaseAuthStateProvider);
  return ref.watch(supabaseAuthServiceProvider).currentUser;
}
```

### 11. Row Level Security (RLS) 정책 예시

```sql
-- Supabase SQL Editor에서 실행

-- 1. profiles 테이블 생성
CREATE TABLE profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  username TEXT UNIQUE,
  avatar_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. RLS 활성화
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- 3. 정책 생성

-- 누구나 프로필 조회 가능
CREATE POLICY "Public profiles are viewable by everyone"
  ON profiles FOR SELECT
  USING (true);

-- 본인만 프로필 수정 가능
CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- 본인만 프로필 생성 가능
CREATE POLICY "Users can insert own profile"
  ON profiles FOR INSERT
  WITH CHECK (auth.uid() = id);

-- 4. posts 테이블 예시
CREATE TABLE posts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  title TEXT NOT NULL,
  content TEXT,
  is_public BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- 공개 게시물은 누구나 조회 가능
CREATE POLICY "Public posts are viewable by everyone"
  ON posts FOR SELECT
  USING (is_public = true);

-- 본인 게시물은 비공개여도 조회 가능
CREATE POLICY "Users can view own posts"
  ON posts FOR SELECT
  USING (auth.uid() = user_id);

-- 본인만 게시물 작성 가능
CREATE POLICY "Users can create own posts"
  ON posts FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- 본인만 게시물 수정/삭제 가능
CREATE POLICY "Users can update own posts"
  ON posts FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own posts"
  ON posts FOR DELETE
  USING (auth.uid() = user_id);
```

### 12. 디렉토리 구조

```
lib/
├── core/
│   ├── config/
│   │   └── env/                  # Supabase URL, Key
│   ├── supabase/
│   │   ├── supabase_initializer.dart
│   │   ├── providers/
│   │   │   └── supabase_providers.dart
│   │   └── services/
│   │       ├── supabase_auth_service.dart
│   │       ├── supabase_database_service.dart
│   │       ├── supabase_storage_service.dart
│   │       ├── supabase_realtime_service.dart
│   │       └── supabase_functions_service.dart
│   └── ...
└── ...
```

---

## Deep Link 설정

### Android (AndroidManifest.xml)

```xml
<intent-filter>
  <action android:name="android.intent.action.VIEW" />
  <category android:name="android.intent.category.DEFAULT" />
  <category android:name="android.intent.category.BROWSABLE" />
  <data
    android:scheme="io.supabase.app"
    android:host="login-callback" />
</intent-filter>
```

### iOS (Info.plist)

```xml
<key>CFBundleURLTypes</key>
<array>
  <dict>
    <key>CFBundleURLSchemes</key>
    <array>
      <string>io.supabase.app</string>
    </array>
  </dict>
</array>
```

---

## 실행 명령어

```bash
# 의존성 설치
flutter pub get

# 코드 생성 (Riverpod, envied)
dart run build_runner build --delete-conflicting-outputs

# Flavor별 실행
flutter run --flavor dev -t lib/main_dev.dart
```

---

## Supabase CLI (선택)

```bash
# Supabase CLI 설치
npm install -g supabase

# 프로젝트 초기화
supabase init

# 로컬 개발 환경 시작
supabase start

# 마이그레이션 생성
supabase migration new create_users_table

# 마이그레이션 실행
supabase db push

# 타입 생성 (TypeScript - 참고용)
supabase gen types typescript --local > types/supabase.ts
```

---

## References

- `_references/ARCHITECTURE-PATTERN.md`
- `25-flavor/SKILL.md` (Flavor 통합)
