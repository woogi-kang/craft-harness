# Recent Flutter Changes Reference

최신 Flutter/Dart 릴리스와 pub.dev 패키지 기준을 반영하기 위한 운영 레퍼런스입니다. 기준일은 2026-05-25입니다.

## SDK 기준선

| 목적 | 권장 기준 |
|------|-----------|
| 최신 우선 신규 프로젝트 | Flutter `>=3.44.0`, Dart `>=3.12.0` |
| 최신 패키지 호환 최소선 | Flutter `>=3.38.1`, Dart `>=3.10.0` |
| 레거시 유지보수 | 프로젝트 `flutter --version`, `pubspec.yaml`, CI SDK를 먼저 확인 |

- Flutter stable 최신판은 `3.44.0`, 번들 Dart SDK는 `3.12.0`이다.
- Widgetbook `3.23.x`는 Flutter `>=3.38.0`, `app_links 7.x`와 `flutter_local_notifications 21.x`는 Flutter `>=3.38.1`을 요구한다.
- `go_router 17.x`, `local_auth 3.x`는 Flutter `>=3.35.0`을 요구한다.
- 최신 Drift/SQLite 조합은 `sqlite3_flutter_libs` 대신 `sqlite3 3.x`를 우선 검토한다. `sqlite3_flutter_libs 0.6.0+eol`은 더 이상 실제 번들링 역할을 하지 않는다.

## Flutter 3.44 주요 반영점

- Swift Package Manager가 iOS/macOS 기본 의존성 관리자다. 새 프로젝트와 플러그인 검토 시 SwiftPM 우선, 호환성 문제가 있으면 CocoaPods fallback을 사용한다.
- `flutter build swift-package`로 Flutter module을 Swift Package로 빌드할 수 있다.
- Android 빌드 체인은 최신 AGP/Kotlin Gradle Plugin 변화와 Java 17 이상을 전제로 검토한다.
- Web은 `prefers-reduced-motion`, `aria-description`, `flutter run --base-href` 개선을 반영한다.
- UI/플랫폼 적응 로직에서 `MediaQueryData.displayCornerRadii`를 사용할 수 있다.
- iOS inline predictive text, HCPP 등은 요구사항과 플랫폼 안정성을 확인한 뒤 opt-in한다.

## Flutter 3.41/3.38/3.35 주요 반영점

- Flutter 3.41: 플랫폼별 asset bundling, Widget Previewer 개선, accessibility matcher, content-sized Add-to-App, DevTools wasm 빌드가 추가/개선되었다.
- Flutter 3.38: Java 17 기준, Widget Previewer IDE 지원, DevTools Inspector/Network 개선, `AssetManifest.json` 기본 생성 중단에 유의한다.
- Flutter 3.35: Web hot reload 기본화, Widget Previewer stable channel 실험 기능, Dart/Flutter MCP server stable channel 지원, Android min SDK API 24 하한을 반영한다.

## Dart 3.12/3.11/3.10 주요 반영점

- Dart 3.12: private named initializing formal을 사용할 수 있다. Primary constructor는 실험 기능이므로 기본 템플릿에는 사용하지 않는다.
- Dart 3.12: Agentic Hot Reload, Genkit Dart preview, `dart pub` Git LFS 지원을 DX 후보로 검토한다.
- Dart 3.11: 언어 변경은 없고, MCP `read_package_uris`, analysis server 성능, pub workspace glob, `dart pub cache gc` 개선이 중심이다.
- Dart 3.10: dot shorthands를 사용할 수 있다. 문맥 타입이 명확하고 가독성이 좋아질 때만 적용한다.
- Dart 3.10: analyzer plugins, build hooks stable, `@Deprecated.*` 세분화 어노테이션을 도구/패키지 작성 시 고려한다.

## DX 도구 정책

- Flutter DevTools는 레이아웃, 성능, 네트워크, 메모리 문제의 1차 진단 도구다.
- Widget Previewer는 순수 위젯의 빠른 상태 실험에 사용한다. 팀 공유/디자인 시스템 카탈로그가 필요하면 Widgetbook을 사용한다.
- Dart and Flutter MCP server가 사용 가능하면 analyzer, runtime errors, running app introspection, pub.dev 문서 확인, 테스트 실행을 AI 어시스턴트에 연결한다.
- Widget Previewer, MCP, Agentic Hot Reload 등 실험/프리뷰 성격의 기능은 프로젝트 Flutter 버전과 팀 안정성 기준을 먼저 확인한다.

## 최신 패키지 기준

| 영역 | 패키지 | 기준 버전 |
|------|--------|-----------|
| State | `flutter_riverpod` / `riverpod_annotation` / `riverpod_generator` | `3.3.1` / `4.0.2` / `4.0.3` |
| Routing | `go_router` / `go_router_builder` | `17.2.3` / `4.3.0` |
| Network | `dio` / `retrofit` / `retrofit_generator` | `5.9.2` / `4.9.2` / `10.2.6` |
| Database | `drift` / `drift_dev` / `sqlite3` | `2.33.0` / `2.33.0` / `3.3.1` |
| Codegen | `freezed` / `json_serializable` / `injectable` | `3.2.5` / `6.14.0` / `3.0.0` |
| Platform | `pigeon` | `26.3.4` |
| UI/DX | `widgetbook` / `flutter_screenutil` / `easy_localization` | `3.23.0` / `5.9.3` / `3.0.8` |
| Test | `mocktail` / `checks` / `patrol` / `alchemist` | `1.0.5` / `0.3.1` / `4.6.0` / `0.14.0` |
| Firebase | `firebase_core` / `firebase_auth` / `cloud_firestore` / `firebase_messaging` | `4.9.0` / `6.5.1` / `6.4.1` / `16.2.2` |
| Security | `flutter_secure_storage` / `local_auth` | `10.3.0` / `3.0.1` |
| Deep link | `app_links` | `7.0.0` |

## 업데이트 체크리스트

- [ ] `pubspec.yaml` SDK constraint와 CI Flutter 버전이 같은 기준선을 바라본다.
- [ ] 최신 패키지가 요구하는 Flutter/Dart 하한을 확인한다.
- [ ] Android는 Java 17 이상, min SDK API 24 이상을 기본값으로 검토한다.
- [ ] iOS/macOS 네이티브 의존성은 SwiftPM 우선으로 검토한다.
- [ ] 실험 기능은 기본 템플릿이 아니라 선택 지침으로만 둔다.

## References

- Flutter release notes: https://docs.flutter.dev/release/release-notes
- Flutter SDK archive: https://docs.flutter.dev/install/archive
- Flutter 3.44: https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527
- Flutter 3.41: https://blog.flutter.dev/whats-new-in-flutter-3-41-302ec140e632
- Flutter 3.38: https://blog.flutter.dev/whats-new-in-flutter-3-38-3f7b258f7228
- Flutter 3.35: https://blog.flutter.dev/whats-new-in-flutter-3-35-c58ef72e3766
- Dart 3.12: https://dart.dev/blog/announcing-dart-3-12
- Dart 3.11: https://dart.dev/blog/announcing-dart-3-11
- Dart 3.10: https://dart.dev/blog/announcing-dart-3-10
- Widget Previewer: https://docs.flutter.dev/tools/widget-previewer
- Dart and Flutter MCP server: https://docs.flutter.dev/ai/mcp-server
- Swift Package Manager: https://docs.flutter.dev/packages-and-plugins/swift-package-manager/for-app-developers
- `sqlite3_flutter_libs`: https://pub.dev/packages/sqlite3_flutter_libs
