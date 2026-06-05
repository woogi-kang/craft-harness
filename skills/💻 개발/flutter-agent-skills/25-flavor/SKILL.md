---
name: flavor
description: |
  Flutter 프로젝트의 환경별 빌드 구성 (dev, staging, prod)을 설정합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Flavor Skill

Flutter 프로젝트의 환경별 빌드 구성 (dev, staging, prod)을 설정합니다.

## Triggers

- "flavor", "환경 설정", "빌드 구성", "dev/staging/prod", "환경 변수"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectName` | ✅ | 프로젝트 이름 |
| `packageName` | ✅ | 기본 패키지명 (com.example.app) |
| `flavors` | ❌ | 환경 목록 (기본: dev, staging, prod) |

---

## 설정

### pubspec.yaml 추가

```yaml
dependencies:
  # 환경 변수
  envied: ^1.3.5

dev_dependencies:
  # Flavor 설정
  flutter_flavorizr: ^2.5.0
  envied_generator: ^1.3.5
```

---

## Output Templates

### 1. flavorizr.yaml

```yaml
# flavorizr.yaml
flavors:
  dev:
    app:
      name: "{AppName} Dev"
    android:
      applicationId: "{package_name}.dev"
      firebase:
        config: ".firebase/dev/google-services.json"
      resValues:
        env:
          type: "string"
          value: "dev"
    ios:
      bundleId: "{package_name}.dev"
      firebase:
        config: ".firebase/dev/GoogleService-Info.plist"
      buildSettings:
        PRODUCT_BUNDLE_IDENTIFIER: "{package_name}.dev"
    macos:
      bundleId: "{package_name}.dev"

  staging:
    app:
      name: "{AppName} Staging"
    android:
      applicationId: "{package_name}.staging"
      firebase:
        config: ".firebase/staging/google-services.json"
      resValues:
        env:
          type: "string"
          value: "staging"
    ios:
      bundleId: "{package_name}.staging"
      firebase:
        config: ".firebase/staging/GoogleService-Info.plist"
      buildSettings:
        PRODUCT_BUNDLE_IDENTIFIER: "{package_name}.staging"
    macos:
      bundleId: "{package_name}.staging"

  prod:
    app:
      name: "{AppName}"
    android:
      applicationId: "{package_name}"
      firebase:
        config: ".firebase/prod/google-services.json"
      resValues:
        env:
          type: "string"
          value: "prod"
    ios:
      bundleId: "{package_name}"
      firebase:
        config: ".firebase/prod/GoogleService-Info.plist"
      buildSettings:
        PRODUCT_BUNDLE_IDENTIFIER: "{package_name}"
    macos:
      bundleId: "{package_name}"

ide: idea

instructions:
  - assets:download
  - assets:extract
  - android:androidManifest
  - android:buildGradle
  - android:icons
  - ios:xcconfig
  - ios:buildTargets
  - ios:schema
  - ios:icons
  - macos:xcconfig
  - macos:configs
  - macos:buildTargets
  - macos:schema
  - macos:icons
  - assets:clean
  - ide:config
```

### 2. 환경 변수 파일

```
# .env.dev
API_BASE_URL=https://dev-api.example.com
API_KEY=dev_api_key_here
ENABLE_LOGGING=true
ANALYTICS_ENABLED=false

# .env.staging
API_BASE_URL=https://staging-api.example.com
API_KEY=staging_api_key_here
ENABLE_LOGGING=true
ANALYTICS_ENABLED=true

# .env.prod
API_BASE_URL=https://api.example.com
API_KEY=prod_api_key_here
ENABLE_LOGGING=false
ANALYTICS_ENABLED=true
```

### 3. Environment Config (envied)

```dart
// lib/core/config/env/env.dart
import 'package:envied/envied.dart';

part 'env.g.dart';

abstract class Env {
  static late final String apiBaseUrl;
  static late final String apiKey;
  static late final bool enableLogging;
  static late final bool analyticsEnabled;
}
```

```dart
// lib/core/config/env/env_dev.dart
import 'package:envied/envied.dart';

part 'env_dev.g.dart';

@Envied(path: '.env.dev', obfuscate: true)
abstract class EnvDev {
  @EnviedField(varName: 'API_BASE_URL')
  static const String apiBaseUrl = _EnvDev.apiBaseUrl;

  @EnviedField(varName: 'API_KEY')
  static const String apiKey = _EnvDev.apiKey;

  @EnviedField(varName: 'ENABLE_LOGGING', defaultValue: 'true')
  static const bool enableLogging = _EnvDev.enableLogging;

  @EnviedField(varName: 'ANALYTICS_ENABLED', defaultValue: 'false')
  static const bool analyticsEnabled = _EnvDev.analyticsEnabled;
}
```

```dart
// lib/core/config/env/env_staging.dart
import 'package:envied/envied.dart';

part 'env_staging.g.dart';

@Envied(path: '.env.staging', obfuscate: true)
abstract class EnvStaging {
  @EnviedField(varName: 'API_BASE_URL')
  static const String apiBaseUrl = _EnvStaging.apiBaseUrl;

  @EnviedField(varName: 'API_KEY')
  static const String apiKey = _EnvStaging.apiKey;

  @EnviedField(varName: 'ENABLE_LOGGING', defaultValue: 'true')
  static const bool enableLogging = _EnvStaging.enableLogging;

  @EnviedField(varName: 'ANALYTICS_ENABLED', defaultValue: 'true')
  static const bool analyticsEnabled = _EnvStaging.analyticsEnabled;
}
```

```dart
// lib/core/config/env/env_prod.dart
import 'package:envied/envied.dart';

part 'env_prod.g.dart';

@Envied(path: '.env.prod', obfuscate: true)
abstract class EnvProd {
  @EnviedField(varName: 'API_BASE_URL')
  static const String apiBaseUrl = _EnvProd.apiBaseUrl;

  @EnviedField(varName: 'API_KEY')
  static const String apiKey = _EnvProd.apiKey;

  @EnviedField(varName: 'ENABLE_LOGGING', defaultValue: 'false')
  static const bool enableLogging = _EnvProd.enableLogging;

  @EnviedField(varName: 'ANALYTICS_ENABLED', defaultValue: 'true')
  static const bool analyticsEnabled = _EnvProd.analyticsEnabled;
}
```

### 4. Flavor Config

```dart
// lib/core/config/flavor_config.dart
enum Flavor {
  dev,
  staging,
  prod,
}

class FlavorConfig {
  final Flavor flavor;
  final String name;
  final String apiBaseUrl;
  final String apiKey;
  final bool enableLogging;
  final bool analyticsEnabled;

  static late FlavorConfig _instance;

  FlavorConfig._({
    required this.flavor,
    required this.name,
    required this.apiBaseUrl,
    required this.apiKey,
    required this.enableLogging,
    required this.analyticsEnabled,
  });

  static FlavorConfig get instance => _instance;

  static bool get isDev => _instance.flavor == Flavor.dev;
  static bool get isStaging => _instance.flavor == Flavor.staging;
  static bool get isProd => _instance.flavor == Flavor.prod;

  factory FlavorConfig.dev() {
    _instance = FlavorConfig._(
      flavor: Flavor.dev,
      name: 'DEV',
      apiBaseUrl: EnvDev.apiBaseUrl,
      apiKey: EnvDev.apiKey,
      enableLogging: EnvDev.enableLogging,
      analyticsEnabled: EnvDev.analyticsEnabled,
    );
    return _instance;
  }

  factory FlavorConfig.staging() {
    _instance = FlavorConfig._(
      flavor: Flavor.staging,
      name: 'STAGING',
      apiBaseUrl: EnvStaging.apiBaseUrl,
      apiKey: EnvStaging.apiKey,
      enableLogging: EnvStaging.enableLogging,
      analyticsEnabled: EnvStaging.analyticsEnabled,
    );
    return _instance;
  }

  factory FlavorConfig.prod() {
    _instance = FlavorConfig._(
      flavor: Flavor.prod,
      name: 'PROD',
      apiBaseUrl: EnvProd.apiBaseUrl,
      apiKey: EnvProd.apiKey,
      enableLogging: EnvProd.enableLogging,
      analyticsEnabled: EnvProd.analyticsEnabled,
    );
    return _instance;
  }
}
```

### 5. Entry Points

```dart
// lib/main_dev.dart
import 'package:flutter/material.dart';
import 'core/config/flavor_config.dart';
import 'core/config/env/env_dev.dart';
import 'app.dart';

void main() {
  FlavorConfig.dev();
  runApp(const App());
}
```

```dart
// lib/main_staging.dart
import 'package:flutter/material.dart';
import 'core/config/flavor_config.dart';
import 'core/config/env/env_staging.dart';
import 'app.dart';

void main() {
  FlavorConfig.staging();
  runApp(const App());
}
```

```dart
// lib/main_prod.dart
import 'package:flutter/material.dart';
import 'core/config/flavor_config.dart';
import 'core/config/env/env_prod.dart';
import 'app.dart';

void main() {
  FlavorConfig.prod();
  runApp(const App());
}
```

### 6. App with Flavor Banner

```dart
// lib/app.dart
import 'package:flutter/material.dart';
import 'core/config/flavor_config.dart';

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MyApp',
      builder: (context, child) {
        // Dev/Staging 환경에서 배너 표시
        if (!FlavorConfig.isProd) {
          return Banner(
            message: FlavorConfig.instance.name,
            location: BannerLocation.topStart,
            color: FlavorConfig.isDev ? Colors.green : Colors.orange,
            child: child ?? const SizedBox.shrink(),
          );
        }
        return child ?? const SizedBox.shrink();
      },
      home: const HomePage(),
    );
  }
}
```

### 7. Flavor-aware Dio Setup

```dart
// lib/core/network/dio_client.dart
import 'package:dio/dio.dart';
import '../config/flavor_config.dart';

Dio createDio() {
  final dio = Dio(
    BaseOptions(
      baseUrl: FlavorConfig.instance.apiBaseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'X-API-Key': FlavorConfig.instance.apiKey,
      },
    ),
  );

  // Dev/Staging 환경에서만 로깅
  if (FlavorConfig.instance.enableLogging) {
    dio.interceptors.add(
      LogInterceptor(
        requestBody: true,
        responseBody: true,
      ),
    );
  }

  return dio;
}
```

### 8. .gitignore 추가

```gitignore
# Environment files
.env
.env.*
!.env.example

# Generated env files
lib/core/config/env/*.g.dart

# Firebase config
.firebase/
```

### 9. VS Code Launch Config

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Dev",
      "request": "launch",
      "type": "dart",
      "program": "lib/main_dev.dart",
      "args": ["--flavor", "dev"]
    },
    {
      "name": "Staging",
      "request": "launch",
      "type": "dart",
      "program": "lib/main_staging.dart",
      "args": ["--flavor", "staging"]
    },
    {
      "name": "Prod",
      "request": "launch",
      "type": "dart",
      "program": "lib/main_prod.dart",
      "args": ["--flavor", "prod"]
    },
    {
      "name": "Dev (Profile)",
      "request": "launch",
      "type": "dart",
      "program": "lib/main_dev.dart",
      "args": ["--flavor", "dev"],
      "flutterMode": "profile"
    },
    {
      "name": "Prod (Release)",
      "request": "launch",
      "type": "dart",
      "program": "lib/main_prod.dart",
      "args": ["--flavor", "prod"],
      "flutterMode": "release"
    }
  ]
}
```

### 10. 디렉토리 구조

```
lib/
├── core/
│   └── config/
│       ├── env/
│       │   ├── env.dart
│       │   ├── env_dev.dart
│       │   ├── env_dev.g.dart      # generated
│       │   ├── env_staging.dart
│       │   ├── env_staging.g.dart  # generated
│       │   ├── env_prod.dart
│       │   └── env_prod.g.dart     # generated
│       └── flavor_config.dart
├── main_dev.dart
├── main_staging.dart
├── main_prod.dart
└── app.dart

.firebase/
├── dev/
│   ├── google-services.json
│   └── GoogleService-Info.plist
├── staging/
│   ├── google-services.json
│   └── GoogleService-Info.plist
└── prod/
    ├── google-services.json
    └── GoogleService-Info.plist
```

---

## 실행 명령어

```bash
# Flavorizr 실행 (최초 1회)
flutter pub run flutter_flavorizr

# 환경 변수 코드 생성
dart run build_runner build --delete-conflicting-outputs

# Dev 환경 실행
flutter run --flavor dev -t lib/main_dev.dart

# Staging 환경 실행
flutter run --flavor staging -t lib/main_staging.dart

# Prod 환경 실행
flutter run --flavor prod -t lib/main_prod.dart

# Release 빌드 (APK)
flutter build apk --flavor prod -t lib/main_prod.dart --release

# Release 빌드 (App Bundle)
flutter build appbundle --flavor prod -t lib/main_prod.dart --release

# iOS Release 빌드
flutter build ios --flavor prod -t lib/main_prod.dart --release
```

---

## CI/CD 연동

```yaml
# .github/workflows/build.yml
jobs:
  build-android:
    strategy:
      matrix:
        flavor: [dev, staging, prod]
    steps:
      - name: Build APK
        run: |
          flutter build apk \
            --flavor ${{ matrix.flavor }} \
            -t lib/main_${{ matrix.flavor }}.dart \
            --release

  build-ios:
    strategy:
      matrix:
        flavor: [dev, staging, prod]
    steps:
      - name: Build iOS
        run: |
          flutter build ios \
            --flavor ${{ matrix.flavor }} \
            -t lib/main_${{ matrix.flavor }}.dart \
            --release --no-codesign
```

---

## Flavor별 앱 아이콘

```yaml
# flavorizr.yaml에 아이콘 경로 추가
flavors:
  dev:
    app:
      name: "{AppName} Dev"
    android:
      applicationId: "{package_name}.dev"
      icon: "assets/icons/ic_launcher_dev.png"
    ios:
      bundleId: "{package_name}.dev"
      icon: "assets/icons/ic_launcher_dev.png"

  staging:
    android:
      icon: "assets/icons/ic_launcher_staging.png"
    ios:
      icon: "assets/icons/ic_launcher_staging.png"

  prod:
    android:
      icon: "assets/icons/ic_launcher.png"
    ios:
      icon: "assets/icons/ic_launcher.png"
```

---

## References

- `_references/ARCHITECTURE-PATTERN.md`
