---
name: security
description: |
  앱 보안 설정 및 보안 베스트 프랙티스를 적용합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Security Skill

앱 보안 설정 및 보안 베스트 프랙티스를 적용합니다.

## Triggers

- "보안", "security", "SSL pinning", "난독화", "obfuscation"

---

## 보안 레이어

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Security                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Secure      │  │ SSL         │  │ Code                │  │
│  │ Storage     │  │ Pinning     │  │ Obfuscation         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Root/       │  │ Biometric   │  │ App                 │  │
│  │ Jailbreak   │  │ Auth        │  │ Integrity           │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Dependencies

```yaml
dependencies:
  # Secure Storage
  flutter_secure_storage: ^10.3.0

  # Biometric Authentication
  local_auth: ^3.0.1

  # Root/Jailbreak Detection
  flutter_jailbreak_detection: ^1.10.0

  # SSL Pinning (Dio interceptor)
  dio: ^5.9.2

  # Encryption
  encrypt: ^5.0.3
  pointycastle: ^4.0.0
```

---

## 1. Secure Storage

```dart
// lib/core/security/secure_storage_service.dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:fpdart/fpdart.dart';

abstract class SecureStorageService {
  Future<Either<Failure, void>> write(String key, String value);
  Future<Either<Failure, String?>> read(String key);
  Future<Either<Failure, void>> delete(String key);
  Future<Either<Failure, void>> deleteAll();
}

class SecureStorageServiceImpl implements SecureStorageService {
  final FlutterSecureStorage _storage;

  SecureStorageServiceImpl()
      : _storage = const FlutterSecureStorage(
          aOptions: AndroidOptions(
            encryptedSharedPreferences: true,
            keyCipherAlgorithm: KeyCipherAlgorithm.RSA_ECB_OAEPwithSHA_256andMGF1Padding,
            storageCipherAlgorithm: StorageCipherAlgorithm.AES_GCM_NoPadding,
          ),
          iOptions: IOSOptions(
            accessibility: KeychainAccessibility.first_unlock_this_device,
          ),
        );

  @override
  Future<Either<Failure, void>> write(String key, String value) async {
    try {
      await _storage.write(key: key, value: value);
      return const Right(null);
    } catch (e) {
      return Left(SecurityFailure('Failed to write: $e'));
    }
  }

  @override
  Future<Either<Failure, String?>> read(String key) async {
    try {
      final value = await _storage.read(key: key);
      return Right(value);
    } catch (e) {
      return Left(SecurityFailure('Failed to read: $e'));
    }
  }

  @override
  Future<Either<Failure, void>> delete(String key) async {
    try {
      await _storage.delete(key: key);
      return const Right(null);
    } catch (e) {
      return Left(SecurityFailure('Failed to delete: $e'));
    }
  }

  @override
  Future<Either<Failure, void>> deleteAll() async {
    try {
      await _storage.deleteAll();
      return const Right(null);
    } catch (e) {
      return Left(SecurityFailure('Failed to delete all: $e'));
    }
  }
}
```

### Token Storage

```dart
// lib/core/security/token_storage.dart
class TokenStorage {
  final SecureStorageService _storage;

  static const _accessTokenKey = 'access_token';
  static const _refreshTokenKey = 'refresh_token';

  TokenStorage(this._storage);

  Future<Either<Failure, void>> saveTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    final accessResult = await _storage.write(_accessTokenKey, accessToken);
    if (accessResult.isLeft()) return accessResult;

    return _storage.write(_refreshTokenKey, refreshToken);
  }

  Future<Either<Failure, ({String? access, String? refresh})>> getTokens() async {
    final accessResult = await _storage.read(_accessTokenKey);
    final refreshResult = await _storage.read(_refreshTokenKey);

    return accessResult.flatMap((access) =>
      refreshResult.map((refresh) => (access: access, refresh: refresh))
    );
  }

  Future<Either<Failure, void>> clearTokens() async {
    await _storage.delete(_accessTokenKey);
    return _storage.delete(_refreshTokenKey);
  }
}
```

---

## 2. SSL Pinning

```dart
// lib/core/network/ssl_pinning_interceptor.dart
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:dio/io.dart';

class SslPinningInterceptor {
  // SHA256 fingerprints of your server certificates
  static const List<String> _trustedFingerprints = [
    'SHA256:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    // Add backup certificate fingerprint
    'SHA256:YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY',
  ];

  static void configure(Dio dio) {
    (dio.httpClientAdapter as IOHttpClientAdapter).createHttpClient = () {
      final client = HttpClient();
      client.badCertificateCallback = (cert, host, port) {
        // In debug mode, allow self-signed certificates
        if (kDebugMode) return true;

        final fingerprint = _getCertificateFingerprint(cert);
        return _trustedFingerprints.contains(fingerprint);
      };
      return client;
    };
  }

  static String _getCertificateFingerprint(X509Certificate cert) {
    // Implementation using pointycastle
    final bytes = cert.der;
    final digest = sha256.convert(bytes);
    return 'SHA256:${digest.toString().toUpperCase()}';
  }
}

// Usage in DI
@module
abstract class NetworkModule {
  @singleton
  Dio provideDio(AuthInterceptor authInterceptor) {
    final dio = Dio(BaseOptions(
      baseUrl: Env.apiBaseUrl,
      connectTimeout: const Duration(seconds: 30),
    ));

    // Apply SSL Pinning
    SslPinningInterceptor.configure(dio);

    dio.interceptors.addAll([
      authInterceptor,
      LogInterceptor(),
    ]);

    return dio;
  }
}
```

---

## 3. Biometric Authentication

```dart
// lib/core/security/biometric_service.dart
import 'package:local_auth/local_auth.dart';
import 'package:fpdart/fpdart.dart';

enum BiometricType { fingerprint, face, iris, none }

abstract class BiometricService {
  Future<Either<Failure, bool>> isAvailable();
  Future<Either<Failure, List<BiometricType>>> getAvailableTypes();
  Future<Either<Failure, bool>> authenticate({required String reason});
}

class BiometricServiceImpl implements BiometricService {
  final LocalAuthentication _auth;

  BiometricServiceImpl() : _auth = LocalAuthentication();

  @override
  Future<Either<Failure, bool>> isAvailable() async {
    try {
      final canCheck = await _auth.canCheckBiometrics;
      final isDeviceSupported = await _auth.isDeviceSupported();
      return Right(canCheck && isDeviceSupported);
    } catch (e) {
      return Left(SecurityFailure('Biometric check failed: $e'));
    }
  }

  @override
  Future<Either<Failure, List<BiometricType>>> getAvailableTypes() async {
    try {
      final types = await _auth.getAvailableBiometrics();
      return Right(types.map(_mapBiometricType).toList());
    } catch (e) {
      return Left(SecurityFailure('Failed to get biometric types: $e'));
    }
  }

  @override
  Future<Either<Failure, bool>> authenticate({required String reason}) async {
    try {
      final result = await _auth.authenticate(
        localizedReason: reason,
        options: const AuthenticationOptions(
          stickyAuth: true,
          biometricOnly: false, // Allow PIN/password fallback
        ),
      );
      return Right(result);
    } catch (e) {
      return Left(SecurityFailure('Authentication failed: $e'));
    }
  }

  BiometricType _mapBiometricType(BiometricType type) {
    return switch (type) {
      BiometricType.fingerprint => BiometricType.fingerprint,
      BiometricType.face => BiometricType.face,
      BiometricType.iris => BiometricType.iris,
      _ => BiometricType.none,
    };
  }
}
```

---

## 4. Root/Jailbreak Detection

```dart
// lib/core/security/device_security_service.dart
import 'package:flutter_jailbreak_detection/flutter_jailbreak_detection.dart';
import 'package:fpdart/fpdart.dart';

abstract class DeviceSecurityService {
  Future<Either<Failure, bool>> isDeviceSecure();
  Future<Either<Failure, bool>> isRunningOnEmulator();
}

class DeviceSecurityServiceImpl implements DeviceSecurityService {
  @override
  Future<Either<Failure, bool>> isDeviceSecure() async {
    try {
      final isJailbroken = await FlutterJailbreakDetection.jailbroken;
      final isDeveloperMode = await FlutterJailbreakDetection.developerMode;

      // Device is secure if not jailbroken and not in developer mode
      return Right(!isJailbroken && !isDeveloperMode);
    } catch (e) {
      return Left(SecurityFailure('Security check failed: $e'));
    }
  }

  @override
  Future<Either<Failure, bool>> isRunningOnEmulator() async {
    try {
      // Additional check for emulator detection
      final isEmulator = await FlutterJailbreakDetection.developerMode;
      return Right(isEmulator);
    } catch (e) {
      return Left(SecurityFailure('Emulator check failed: $e'));
    }
  }
}

// Security gate at app startup
class SecurityGate extends StatefulWidget {
  final Widget child;
  const SecurityGate({required this.child, super.key});

  @override
  State<SecurityGate> createState() => _SecurityGateState();
}

class _SecurityGateState extends State<SecurityGate> {
  @override
  void initState() {
    super.initState();
    _checkSecurity();
  }

  Future<void> _checkSecurity() async {
    final service = getIt<DeviceSecurityService>();
    final result = await service.isDeviceSecure();

    result.fold(
      (failure) => _showSecurityWarning(),
      (isSecure) {
        if (!isSecure && !kDebugMode) {
          _showSecurityWarning();
        }
      },
    );
  }

  void _showSecurityWarning() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => AlertDialog(
        title: const Text('Security Warning'),
        content: const Text(
          'This device appears to be compromised. '
          'For your security, some features may be restricted.',
        ),
        actions: [
          TextButton(
            onPressed: () => exit(0),
            child: const Text('Exit App'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) => widget.child;
}
```

---

## 5. Code Obfuscation

### Android (build.gradle)

```groovy
// android/app/build.gradle
android {
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

### ProGuard Rules

```proguard
# android/app/proguard-rules.pro

# Flutter
-keep class io.flutter.** { *; }
-keep class io.flutter.plugins.** { *; }

# Keep your data models
-keep class com.yourapp.models.** { *; }

# Retrofit
-keepattributes Signature
-keepattributes Exceptions

# OkHttp
-dontwarn okhttp3.**
-dontwarn okio.**

# Gson
-keepattributes *Annotation*
-keep class sun.misc.Unsafe { *; }
```

### Flutter Build Command

```bash
# Release build with obfuscation
flutter build apk \
  --release \
  --obfuscate \
  --split-debug-info=build/debug-info

flutter build appbundle \
  --release \
  --obfuscate \
  --split-debug-info=build/debug-info

# iOS
flutter build ipa \
  --release \
  --obfuscate \
  --split-debug-info=build/debug-info
```

---

## 6. Data Encryption

```dart
// lib/core/security/encryption_service.dart
import 'package:encrypt/encrypt.dart';

class EncryptionService {
  late final Key _key;
  late final IV _iv;
  late final Encrypter _encrypter;

  EncryptionService() {
    // In production, get key from secure source
    _key = Key.fromSecureRandom(32); // AES-256
    _iv = IV.fromSecureRandom(16);
    _encrypter = Encrypter(AES(_key, mode: AESMode.cbc));
  }

  String encrypt(String plainText) {
    final encrypted = _encrypter.encrypt(plainText, iv: _iv);
    return encrypted.base64;
  }

  String decrypt(String encryptedText) {
    final encrypted = Encrypted.fromBase64(encryptedText);
    return _encrypter.decrypt(encrypted, iv: _iv);
  }

  // For sensitive data at rest
  Future<String> encryptForStorage(String data) async {
    // Add timestamp and nonce for additional security
    final payload = {
      'data': data,
      'timestamp': DateTime.now().millisecondsSinceEpoch,
      'nonce': IV.fromSecureRandom(8).base64,
    };
    return encrypt(jsonEncode(payload));
  }
}
```

---

## 7. Secure Network Requests

```dart
// lib/core/network/secure_dio_client.dart
class SecureDioClient {
  final Dio _dio;

  SecureDioClient(this._dio) {
    _configureSecureDefaults();
  }

  void _configureSecureDefaults() {
    _dio.options
      ..headers['X-Content-Type-Options'] = 'nosniff'
      ..headers['X-Frame-Options'] = 'DENY'
      ..headers['X-XSS-Protection'] = '1; mode=block';

    // Prevent caching of sensitive data
    _dio.options.headers['Cache-Control'] = 'no-store';
    _dio.options.headers['Pragma'] = 'no-cache';
  }
}
```

---

## Security Checklist

- [ ] flutter_secure_storage로 민감 데이터 저장
- [ ] SSL Pinning 적용
- [ ] 생체 인증 옵션 제공
- [ ] Root/Jailbreak 탐지
- [ ] 코드 난독화 (--obfuscate)
- [ ] ProGuard 규칙 설정
- [ ] 민감 데이터 암호화
- [ ] 보안 헤더 설정
- [ ] Debug 모드 체크
- [ ] 에뮬레이터 탐지 (선택)

---

## References

- `_references/RECENT-FLUTTER-CHANGES.md`
- `_references/NETWORK-PATTERN.md`
