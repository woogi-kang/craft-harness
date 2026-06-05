---
name: project-setup
description: |
  Flutter 프로젝트 초기 설정 및 의존성 구성을 수행합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Project Setup Skill

Extends: `../../_shared/project-setup/SKILL.md` (공통 프로세스 참조)

Flutter 프로젝트 초기 설정 및 의존성 구성을 수행합니다.

## Triggers

- "프로젝트 생성", "프로젝트 설정", "flutter init", "flutter create"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectName` | ✅ | 프로젝트 이름 (snake_case) |
| `packageName` | ✅ | 패키지 이름 (com.example.app) |

---

## Output

### pubspec.yaml

```yaml
name: {project_name}
description: A Flutter application with Clean Architecture.
version: 1.0.0+1

environment:
  sdk: '>=3.12.0 <4.0.0'
  flutter: '>=3.44.0'

dependencies:
  flutter:
    sdk: flutter

  # 상태관리
  flutter_riverpod: ^3.3.1
  riverpod_annotation: ^4.0.2

  # 라우팅
  go_router: ^17.2.3

  # 네트워킹
  dio: ^5.9.2
  retrofit: ^4.9.2

  # 로컬 DB
  drift: ^2.33.0
  sqlite3: ^3.3.1
  path_provider: ^2.1.5
  path: ^1.9.1

  # 로깅
  talker: ^5.1.17
  talker_flutter: ^5.1.17
  talker_dio_logger: ^5.1.17
  talker_riverpod_logger: ^5.1.17

  # 코드 생성 (annotations)
  freezed_annotation: ^3.1.0
  json_annotation: ^4.12.0

  # DI
  injectable: ^3.0.0
  get_it: ^9.2.1

  # 유틸리티
  fpdart: ^1.2.0
  connectivity_plus: ^7.1.1

  # 환경 변수
  envied: ^1.3.5

  # 반응형 UI 보조 (선택: 레이아웃 분기는 MediaQuery/LayoutBuilder 우선)
  flutter_screenutil: ^5.9.3

  # 다국어
  easy_localization: ^3.0.8
  flutter_localizations:
    sdk: flutter

  # Firebase
  firebase_core: ^4.9.0
  firebase_auth: ^6.5.1
  cloud_firestore: ^6.4.1
  firebase_messaging: ^16.2.2
  firebase_crashlytics: ^5.2.2
  firebase_analytics: ^12.4.1
  firebase_storage: ^13.4.1
  firebase_remote_config: ^6.5.1

  # Local Notifications (FCM)
  flutter_local_notifications: ^21.0.0

  # Supabase (Firebase 대안)
  supabase_flutter: ^2.12.4

  # 보안
  flutter_secure_storage: ^10.3.0
  local_auth: ^3.0.1
  flutter_jailbreak_detection: ^1.10.0
  encrypt: ^5.0.3

  # 딥링크
  app_links: ^7.0.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^6.0.0
  build_runner: ^2.15.0
  freezed: ^3.2.5
  json_serializable: ^6.14.0
  riverpod_generator: ^4.0.3
  go_router_builder: ^4.3.0
  injectable_generator: ^3.0.2
  retrofit_generator: ^10.2.6
  drift_dev: ^2.33.0
  pigeon: ^26.3.4
  mocktail: ^1.0.5
  # 타입 지향 assertion (선택)
  checks: ^0.3.1
  patrol: ^4.6.0
  alchemist: ^0.14.0
  # Flavor & 환경 변수
  flutter_flavorizr: ^2.5.0
  envied_generator: ^1.3.5
```

최신 패키지 조합을 유지하되 레거시 프로젝트에 적용할 때는 `_references/RECENT-FLUTTER-CHANGES.md`의 호환 최소선을 먼저 확인한다.

### 디렉토리 구조

```
lib/
├── core/
│   ├── config/
│   │   ├── env/              # envied 환경 변수
│   │   └── flavor_config.dart
│   ├── firebase/
│   │   ├── firebase_initializer.dart
│   │   ├── providers/        # Riverpod providers
│   │   └── services/         # Auth, Firestore, FCM 등
│   ├── supabase/             # Firebase 대안
│   │   ├── supabase_initializer.dart
│   │   ├── providers/
│   │   └── services/         # Auth, Database, Storage, Realtime
│   ├── security/             # 보안 모듈
│   │   ├── secure_storage_service.dart
│   │   ├── biometric_service.dart
│   │   ├── device_security_service.dart
│   │   └── ssl_pinning_interceptor.dart
│   ├── deeplink/             # 딥링크 모듈
│   │   ├── deep_link_service.dart
│   │   └── deep_link_handler.dart
│   ├── design_system/
│   │   ├── tokens/
│   │   ├── atoms/
│   │   ├── molecules/
│   │   ├── organisms/
│   │   └── templates/
│   ├── error/
│   ├── network/
│   ├── database/
│   ├── di/
│   └── utils/
├── features/
├── routes/
├── firebase_options_dev.dart     # FlutterFire CLI 생성
├── firebase_options_staging.dart
├── firebase_options_prod.dart
├── main_dev.dart             # Dev entry point
├── main_staging.dart         # Staging entry point
├── main_prod.dart            # Prod entry point
└── app.dart

test/
├── unit/
├── widget/
├── golden/
└── helpers/

integration_test/
```

### 실행 명령어

```bash
flutter create --org {org} {project_name}
cd {project_name}
flutter pub get
dart run build_runner build --delete-conflicting-outputs
```

## References

- `_references/RECENT-FLUTTER-CHANGES.md`
- `_references/ARCHITECTURE-PATTERN.md`
