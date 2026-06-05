---
name: network
description: |
  Dio + Retrofit 기반 네트워크 레이어를 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Network Skill

Dio + Retrofit 기반 네트워크 레이어를 구현합니다.

## Triggers

- "API 클라이언트", "네트워크 설정", "retrofit", "dio"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `baseUrl` | ✅ | API Base URL |
| `endpoints` | ✅ | API 엔드포인트 목록 |

---

## Output Template

### API Client

```dart
// core/network/api_client.dart
import 'package:dio/dio.dart';
import 'package:retrofit/retrofit.dart';

part 'api_client.g.dart';

@RestApi()
abstract class ApiClient {
  factory ApiClient(Dio dio, {String baseUrl}) = _ApiClient;

  // Auth
  @POST('/auth/login')
  Future<LoginResponse> login(@Body() LoginRequest request);

  @POST('/auth/logout')
  Future<void> logout();

  // {Entity}
  @GET('/{entity}')
  Future<List<{Entity}Model>> get{Entity}List({
    @Query('page') int? page,
    @Query('limit') int? limit,
  });

  @GET('/{entity}/{id}')
  Future<{Entity}Model> get{Entity}(@Path('id') String id);

  @POST('/{entity}')
  Future<{Entity}Model> create{Entity}(@Body() {Entity}Model entity);

  @PUT('/{entity}/{id}')
  Future<{Entity}Model> update{Entity}(
    @Path('id') String id,
    @Body() {Entity}Model entity,
  );

  @DELETE('/{entity}/{id}')
  Future<void> delete{Entity}(@Path('id') String id);
}
```

### Dio Module

```dart
// core/network/dio_client.dart
import 'package:dio/dio.dart';
import 'package:injectable/injectable.dart';
import 'package:talker_dio_logger/talker_dio_logger.dart';

@module
abstract class DioModule {
  @singleton
  Dio dio(
    AuthInterceptor authInterceptor,
    ErrorInterceptor errorInterceptor,
    Talker talker,
  ) {
    final dio = Dio(
      BaseOptions(
        baseUrl: ApiEndpoints.baseUrl,
        connectTimeout: const Duration(seconds: 30),
        receiveTimeout: const Duration(seconds: 30),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    dio.interceptors.addAll([
      authInterceptor,
      errorInterceptor,
      TalkerDioLogger(
        talker: talker,
        settings: const TalkerDioLoggerSettings(
          printRequestHeaders: true,
          printResponseHeaders: true,
        ),
      ),
    ]);

    return dio;
  }
}
```

### Auth Interceptor

```dart
// core/network/interceptors/auth_interceptor.dart
@injectable
class AuthInterceptor extends Interceptor {
  final TokenStorage _tokenStorage;

  AuthInterceptor(this._tokenStorage);

  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final token = await _tokenStorage.getAccessToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      // Token refresh 시도
      final refreshed = await _refreshToken();
      if (refreshed) {
        // 새 토큰으로 재요청
        final opts = err.requestOptions;
        final token = await _tokenStorage.getAccessToken();
        opts.headers['Authorization'] = 'Bearer $token';

        try {
          final response = await Dio().fetch(opts);
          return handler.resolve(response);
        } catch (e) {
          return handler.next(err);
        }
      }
    }
    handler.next(err);
  }

  Future<bool> _refreshToken() async {
    try {
      final refreshToken = await _tokenStorage.getRefreshToken();
      if (refreshToken == null) return false;

      final dio = Dio();
      final response = await dio.post(
        '${ApiEndpoints.baseUrl}/auth/refresh',
        data: {'refresh_token': refreshToken},
      );

      final newAccessToken = response.data['access_token'] as String;
      final newRefreshToken = response.data['refresh_token'] as String;

      await _tokenStorage.saveTokens(
        accessToken: newAccessToken,
        refreshToken: newRefreshToken,
      );

      return true;
    } catch (e) {
      await _tokenStorage.clearTokens();
      return false;
    }
  }
}
```

### Error Interceptor

```dart
// core/network/interceptors/error_interceptor.dart
@injectable
class ErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    final exception = switch (err.type) {
      DioExceptionType.connectionTimeout ||
      DioExceptionType.sendTimeout ||
      DioExceptionType.receiveTimeout =>
        const ServerException('서버 응답 시간 초과'),
      DioExceptionType.connectionError =>
        const ServerException('네트워크 연결 오류'),
      DioExceptionType.badResponse => _handleBadResponse(err.response),
      _ => ServerException(err.message ?? '알 수 없는 오류'),
    };

    handler.next(DioException(
      requestOptions: err.requestOptions,
      error: exception,
    ));
  }

  ServerException _handleBadResponse(Response? response) {
    final statusCode = response?.statusCode ?? 500;
    final message = switch (statusCode) {
      400 => '잘못된 요청',
      401 => '인증 필요',
      403 => '접근 권한 없음',
      404 => '리소스를 찾을 수 없음',
      500 => '서버 오류',
      _ => '오류 발생 ($statusCode)',
    };
    return ServerException(message, statusCode: statusCode);
  }
}
```

---

## 코드 생성

```bash
dart run build_runner build --delete-conflicting-outputs
```

## References

- `_references/NETWORK-PATTERN.md`
