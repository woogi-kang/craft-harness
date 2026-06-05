# Network Pattern Reference

Dio + Retrofit 네트워크 레이어 패턴 및 샘플 코드 레퍼런스입니다.

## 버전 정보

```yaml
dependencies:
  dio: ^5.9.2
  retrofit: ^4.9.2

dev_dependencies:
  retrofit_generator: ^10.2.6
  build_runner: ^2.15.0
```

---

## 디렉토리 구조

```
lib/
├── core/
│   └── network/
│       ├── api_client.dart           # Retrofit API Client
│       ├── api_client.g.dart         # Generated
│       ├── dio_client.dart           # Dio 설정
│       ├── interceptors/
│       │   ├── auth_interceptor.dart
│       │   ├── error_interceptor.dart
│       │   └── logging_interceptor.dart
│       ├── network_info.dart         # 네트워크 상태 체크
│       └── api_endpoints.dart        # 엔드포인트 상수
│
└── features/
    └── {feature}/
        └── data/
            └── datasources/
                └── {feature}_remote_datasource.dart
```

---

## Dio 설정

### DioClient

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
        sendTimeout: const Duration(seconds: 30),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    // Interceptors 추가 순서 중요
    dio.interceptors.addAll([
      authInterceptor,
      errorInterceptor,
      TalkerDioLogger(
        talker: talker,
        settings: const TalkerDioLoggerSettings(
          printRequestHeaders: true,
          printResponseHeaders: true,
          printResponseMessage: true,
        ),
      ),
    ]);

    return dio;
  }
}
```

### API Endpoints

```dart
// core/network/api_endpoints.dart
abstract class ApiEndpoints {
  // Base URL
  static const String baseUrl = 'https://api.example.com/v1';

  // Auth
  static const String login = '/auth/login';
  static const String logout = '/auth/logout';
  static const String refresh = '/auth/refresh';
  static const String register = '/auth/register';

  // User
  static const String users = '/users';
  static const String userById = '/users/{id}';
  static const String me = '/users/me';

  // Product
  static const String products = '/products';
  static const String productById = '/products/{id}';
  static const String productSearch = '/products/search';

  // Order
  static const String orders = '/orders';
  static const String orderById = '/orders/{id}';
}
```

---

## Interceptors

### AuthInterceptor

```dart
// core/network/interceptors/auth_interceptor.dart
import 'package:dio/dio.dart';
import 'package:injectable/injectable.dart';

@injectable
class AuthInterceptor extends Interceptor {
  final TokenStorage _tokenStorage;
  final Dio _dio;

  AuthInterceptor(this._tokenStorage, @Named('plain') this._dio);

  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    // 토큰이 필요 없는 엔드포인트
    final noAuthPaths = [
      ApiEndpoints.login,
      ApiEndpoints.register,
      ApiEndpoints.refresh,
    ];

    if (noAuthPaths.contains(options.path)) {
      return handler.next(options);
    }

    final accessToken = await _tokenStorage.getAccessToken();
    if (accessToken != null) {
      options.headers['Authorization'] = 'Bearer $accessToken';
    }

    handler.next(options);
  }

  @override
  void onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    if (err.response?.statusCode == 401) {
      // 토큰 갱신 시도
      final refreshed = await _refreshToken();
      if (refreshed) {
        // 원래 요청 재시도
        final response = await _retryRequest(err.requestOptions);
        return handler.resolve(response);
      }
    }

    handler.next(err);
  }

  Future<bool> _refreshToken() async {
    try {
      final refreshToken = await _tokenStorage.getRefreshToken();
      if (refreshToken == null) return false;

      final response = await _dio.post(
        ApiEndpoints.refresh,
        data: {'refresh_token': refreshToken},
      );

      final newAccessToken = response.data['access_token'];
      final newRefreshToken = response.data['refresh_token'];

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

  Future<Response> _retryRequest(RequestOptions options) async {
    final accessToken = await _tokenStorage.getAccessToken();
    options.headers['Authorization'] = 'Bearer $accessToken';
    return _dio.fetch(options);
  }
}
```

### ErrorInterceptor

```dart
// core/network/interceptors/error_interceptor.dart
import 'package:dio/dio.dart';
import 'package:injectable/injectable.dart';

@injectable
class ErrorInterceptor extends Interceptor {
  final Talker _talker;

  ErrorInterceptor(this._talker);

  @override
  void onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) {
    final exception = _mapDioException(err);
    _talker.error('API Error: ${exception.message}', err);

    handler.next(
      DioException(
        requestOptions: err.requestOptions,
        error: exception,
        type: err.type,
        response: err.response,
      ),
    );
  }

  ServerException _mapDioException(DioException err) {
    switch (err.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return const ServerException(
          '서버 응답 시간이 초과되었습니다',
          statusCode: 408,
        );

      case DioExceptionType.connectionError:
        return const ServerException(
          '네트워크 연결을 확인해주세요',
          statusCode: 0,
        );

      case DioExceptionType.badResponse:
        return _handleBadResponse(err.response);

      case DioExceptionType.cancel:
        return const ServerException(
          '요청이 취소되었습니다',
          statusCode: 499,
        );

      default:
        return ServerException(
          err.message ?? '알 수 없는 오류가 발생했습니다',
        );
    }
  }

  ServerException _handleBadResponse(Response? response) {
    final statusCode = response?.statusCode ?? 500;
    final data = response?.data;

    String message;
    if (data is Map<String, dynamic> && data.containsKey('message')) {
      message = data['message'];
    } else {
      message = switch (statusCode) {
        400 => '잘못된 요청입니다',
        401 => '인증이 필요합니다',
        403 => '접근 권한이 없습니다',
        404 => '요청한 리소스를 찾을 수 없습니다',
        409 => '중복된 데이터입니다',
        422 => '처리할 수 없는 요청입니다',
        429 => '너무 많은 요청입니다. 잠시 후 다시 시도해주세요',
        500 => '서버 오류가 발생했습니다',
        502 => '서버가 응답하지 않습니다',
        503 => '서비스를 일시적으로 사용할 수 없습니다',
        _ => '오류가 발생했습니다 ($statusCode)',
      };
    }

    return ServerException(message, statusCode: statusCode);
  }
}
```

---

## Retrofit API Client

### 기본 API Client

```dart
// core/network/api_client.dart
import 'package:dio/dio.dart';
import 'package:retrofit/retrofit.dart';

part 'api_client.g.dart';

@RestApi()
abstract class ApiClient {
  factory ApiClient(Dio dio, {String baseUrl}) = _ApiClient;

  // ============ Auth ============

  @POST(ApiEndpoints.login)
  Future<LoginResponse> login(@Body() LoginRequest request);

  @POST(ApiEndpoints.logout)
  Future<void> logout();

  @POST(ApiEndpoints.register)
  Future<UserModel> register(@Body() RegisterRequest request);

  @POST(ApiEndpoints.refresh)
  Future<TokenResponse> refreshToken(@Body() RefreshRequest request);

  // ============ User ============

  @GET(ApiEndpoints.me)
  Future<UserModel> getCurrentUser();

  @GET(ApiEndpoints.userById)
  Future<UserModel> getUser(@Path('id') String id);

  @GET(ApiEndpoints.users)
  Future<List<UserModel>> getUsers({
    @Query('page') int? page,
    @Query('limit') int? limit,
  });

  @PUT(ApiEndpoints.userById)
  Future<UserModel> updateUser(
    @Path('id') String id,
    @Body() UpdateUserRequest request,
  );

  @DELETE(ApiEndpoints.userById)
  Future<void> deleteUser(@Path('id') String id);

  // ============ Product ============

  @GET(ApiEndpoints.products)
  Future<PaginatedResponse<ProductModel>> getProducts({
    @Query('page') int? page,
    @Query('limit') int? limit,
    @Query('category') String? category,
    @Query('sort') String? sort,
  });

  @GET(ApiEndpoints.productById)
  Future<ProductModel> getProduct(@Path('id') String id);

  @GET(ApiEndpoints.productSearch)
  Future<List<ProductModel>> searchProducts(@Query('q') String query);

  @POST(ApiEndpoints.products)
  Future<ProductModel> createProduct(@Body() CreateProductRequest request);

  @PUT(ApiEndpoints.productById)
  Future<ProductModel> updateProduct(
    @Path('id') String id,
    @Body() UpdateProductRequest request,
  );

  @DELETE(ApiEndpoints.productById)
  Future<void> deleteProduct(@Path('id') String id);

  // ============ Order ============

  @GET(ApiEndpoints.orders)
  Future<List<OrderModel>> getOrders();

  @GET(ApiEndpoints.orderById)
  Future<OrderModel> getOrder(@Path('id') String id);

  @POST(ApiEndpoints.orders)
  Future<OrderModel> createOrder(@Body() CreateOrderRequest request);

  // ============ File Upload ============

  @POST('/upload')
  @MultiPart()
  Future<UploadResponse> uploadFile(@Part(name: 'file') File file);

  @POST('/upload/multiple')
  @MultiPart()
  Future<List<UploadResponse>> uploadFiles(
    @Part(name: 'files') List<File> files,
  );
}
```

### Request/Response Models

```dart
// core/network/models/login_request.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'login_request.freezed.dart';
part 'login_request.g.dart';

@freezed
class LoginRequest with _$LoginRequest {
  const factory LoginRequest({
    required String email,
    required String password,
    @JsonKey(name: 'device_id') String? deviceId,
  }) = _LoginRequest;

  factory LoginRequest.fromJson(Map<String, dynamic> json) =>
      _$LoginRequestFromJson(json);
}

// core/network/models/login_response.dart
@freezed
class LoginResponse with _$LoginResponse {
  const factory LoginResponse({
    @JsonKey(name: 'access_token') required String accessToken,
    @JsonKey(name: 'refresh_token') required String refreshToken,
    @JsonKey(name: 'expires_in') required int expiresIn,
    required UserModel user,
  }) = _LoginResponse;

  factory LoginResponse.fromJson(Map<String, dynamic> json) =>
      _$LoginResponseFromJson(json);
}

// core/network/models/paginated_response.dart
@freezed
class PaginatedResponse<T> with _$PaginatedResponse<T> {
  const factory PaginatedResponse({
    required List<T> data,
    required int page,
    required int limit,
    required int total,
    @JsonKey(name: 'total_pages') required int totalPages,
    @JsonKey(name: 'has_next') required bool hasNext,
    @JsonKey(name: 'has_prev') required bool hasPrev,
  }) = _PaginatedResponse<T>;

  factory PaginatedResponse.fromJson(
    Map<String, dynamic> json,
    T Function(Object?) fromJsonT,
  ) =>
      _$PaginatedResponseFromJson(json, fromJsonT);
}
```

---

## DataSource 구현

### Remote DataSource

```dart
// features/product/data/datasources/product_remote_datasource.dart
import 'package:injectable/injectable.dart';

abstract class ProductRemoteDataSource {
  Future<List<ProductModel>> getProducts({
    int? page,
    int? limit,
    String? category,
  });
  Future<ProductModel> getProduct(String id);
  Future<List<ProductModel>> searchProducts(String query);
  Future<ProductModel> createProduct(CreateProductRequest request);
  Future<ProductModel> updateProduct(String id, UpdateProductRequest request);
  Future<void> deleteProduct(String id);
}

@Injectable(as: ProductRemoteDataSource)
class ProductRemoteDataSourceImpl implements ProductRemoteDataSource {
  final ApiClient _apiClient;

  ProductRemoteDataSourceImpl(this._apiClient);

  @override
  Future<List<ProductModel>> getProducts({
    int? page,
    int? limit,
    String? category,
  }) async {
    final response = await _apiClient.getProducts(
      page: page,
      limit: limit,
      category: category,
    );
    return response.data;
  }

  @override
  Future<ProductModel> getProduct(String id) async {
    return _apiClient.getProduct(id);
  }

  @override
  Future<List<ProductModel>> searchProducts(String query) async {
    return _apiClient.searchProducts(query);
  }

  @override
  Future<ProductModel> createProduct(CreateProductRequest request) async {
    return _apiClient.createProduct(request);
  }

  @override
  Future<ProductModel> updateProduct(
    String id,
    UpdateProductRequest request,
  ) async {
    return _apiClient.updateProduct(id, request);
  }

  @override
  Future<void> deleteProduct(String id) async {
    return _apiClient.deleteProduct(id);
  }
}
```

---

## Network Info

```dart
// core/network/network_info.dart
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:injectable/injectable.dart';

abstract class NetworkInfo {
  Future<bool> get isConnected;
  Stream<bool> get onConnectivityChanged;
}

@Injectable(as: NetworkInfo)
class NetworkInfoImpl implements NetworkInfo {
  final Connectivity _connectivity;

  NetworkInfoImpl(this._connectivity);

  @override
  Future<bool> get isConnected async {
    final result = await _connectivity.checkConnectivity();
    return result != ConnectivityResult.none;
  }

  @override
  Stream<bool> get onConnectivityChanged {
    return _connectivity.onConnectivityChanged.map(
      (result) => result != ConnectivityResult.none,
    );
  }
}
```

---

## Token Storage

```dart
// core/network/token_storage.dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:injectable/injectable.dart';

abstract class TokenStorage {
  Future<String?> getAccessToken();
  Future<String?> getRefreshToken();
  Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
  });
  Future<void> clearTokens();
}

@Injectable(as: TokenStorage)
class TokenStorageImpl implements TokenStorage {
  final FlutterSecureStorage _storage;

  static const _accessTokenKey = 'access_token';
  static const _refreshTokenKey = 'refresh_token';

  TokenStorageImpl(this._storage);

  @override
  Future<String?> getAccessToken() async {
    return _storage.read(key: _accessTokenKey);
  }

  @override
  Future<String?> getRefreshToken() async {
    return _storage.read(key: _refreshTokenKey);
  }

  @override
  Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    await Future.wait([
      _storage.write(key: _accessTokenKey, value: accessToken),
      _storage.write(key: _refreshTokenKey, value: refreshToken),
    ]);
  }

  @override
  Future<void> clearTokens() async {
    await Future.wait([
      _storage.delete(key: _accessTokenKey),
      _storage.delete(key: _refreshTokenKey),
    ]);
  }
}
```

---

## 에러 처리 통합

### Repository에서 사용

```dart
// features/product/data/repositories/product_repository_impl.dart
@Injectable(as: ProductRepository)
class ProductRepositoryImpl implements ProductRepository {
  final ProductRemoteDataSource _remoteDataSource;
  final ProductLocalDataSource _localDataSource;
  final NetworkInfo _networkInfo;

  ProductRepositoryImpl(
    this._remoteDataSource,
    this._localDataSource,
    this._networkInfo,
  );

  @override
  Future<Either<Failure, List<ProductEntity>>> getProducts({
    int? page,
    int? limit,
    String? category,
  }) async {
    if (await _networkInfo.isConnected) {
      try {
        final models = await _remoteDataSource.getProducts(
          page: page,
          limit: limit,
          category: category,
        );
        // 캐시 저장
        await _localDataSource.cacheProducts(models);
        return Right(models.map((m) => m.toEntity()).toList());
      } on ServerException catch (e) {
        return Left(ServerFailure(e.message, statusCode: e.statusCode));
      } on DioException catch (e) {
        final serverException = e.error as ServerException?;
        return Left(ServerFailure(
          serverException?.message ?? '네트워크 오류',
          statusCode: serverException?.statusCode,
        ));
      }
    } else {
      // 오프라인: 캐시에서 로드
      try {
        final cachedModels = await _localDataSource.getCachedProducts();
        if (cachedModels.isNotEmpty) {
          return Right(cachedModels.map((m) => m.toEntity()).toList());
        }
        return const Left(CacheFailure('캐시된 데이터가 없습니다'));
      } on CacheException catch (e) {
        return Left(CacheFailure(e.message));
      }
    }
  }
}
```

---

## 코드 생성

```bash
# Retrofit 코드 생성
dart run build_runner build --delete-conflicting-outputs

# Watch 모드
dart run build_runner watch --delete-conflicting-outputs
```

---

## 테스트

### API Client Mock

```dart
// test/mocks/mock_api_client.dart
import 'package:mocktail/mocktail.dart';

class MockApiClient extends Mock implements ApiClient {}

// 테스트 예시
void main() {
  late MockApiClient mockApiClient;
  late ProductRemoteDataSource sut;

  setUp(() {
    mockApiClient = MockApiClient();
    sut = ProductRemoteDataSourceImpl(mockApiClient);
  });

  test('getProducts returns list of products', () async {
    // Arrange
    final products = [testProductModel];
    when(() => mockApiClient.getProducts(
          page: any(named: 'page'),
          limit: any(named: 'limit'),
        )).thenAnswer((_) async => PaginatedResponse(
          data: products,
          page: 1,
          limit: 10,
          total: 1,
          totalPages: 1,
          hasNext: false,
          hasPrev: false,
        ));

    // Act
    final result = await sut.getProducts();

    // Assert
    expect(result, products);
  });
}
```

---

## 베스트 프랙티스

1. **Base URL 환경별 분리**
```dart
// 환경별 Base URL
abstract class ApiEndpoints {
  static String get baseUrl => switch (Environment.current) {
    Environment.dev => 'https://dev-api.example.com/v1',
    Environment.staging => 'https://staging-api.example.com/v1',
    Environment.prod => 'https://api.example.com/v1',
  };
}
```

2. **요청 취소 지원**
```dart
final cancelToken = CancelToken();

// 요청
dio.get('/products', cancelToken: cancelToken);

// 취소
cancelToken.cancel('User cancelled');
```

3. **재시도 로직**
```dart
// dio_retry 패키지 사용
dio.interceptors.add(
  RetryInterceptor(
    dio: dio,
    retries: 3,
    retryDelays: const [
      Duration(seconds: 1),
      Duration(seconds: 2),
      Duration(seconds: 3),
    ],
  ),
);
```

4. **캐시 전략**
```dart
// dio_cache_interceptor 패키지 사용
dio.interceptors.add(
  DioCacheInterceptor(
    options: CacheOptions(
      store: HiveCacheStore(path),
      maxStale: const Duration(days: 7),
    ),
  ),
);
```
