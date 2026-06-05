---
name: platform-channel
description: |
  pub.dev 패키지 검토 후 필요한 경우 Pigeon 기반 네이티브 플랫폼 통신을 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Platform Channel Skill

pub.dev 패키지 검토 후 필요한 경우 Pigeon 기반 네이티브 플랫폼 통신을 구현합니다.

## Triggers

- "platform channel", "pigeon", "네이티브 연동"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `apiName` | ✅ | API 이름 |
| `methods` | ✅ | 메서드 목록 |
| `platforms` | ❌ | 대상 플랫폼 (iOS, Android, Windows 등) |

---

## 의사결정 흐름

1. pub.dev에서 공식/활성 패키지와 플랫폼 지원 범위를 먼저 확인한다.
2. 패키지가 요구사항, 보안, 유지보수, 대상 플랫폼을 충족하면 Dart Service 인터페이스 뒤에 감싸 사용한다.
3. 패키지가 없거나 native API 직접 제어가 필요할 때 Pigeon 기반 Platform Channel을 구현한다.
4. Platform Channel 코드는 Service/DataSource 계층에 격리하고, UI/ViewModel에는 Repository/UseCase 인터페이스만 노출한다.
5. iOS/macOS 네이티브 의존성은 Flutter 3.44+ 기준 Swift Package Manager를 우선 검토하고, 호환성 문제가 있을 때 CocoaPods를 fallback으로 둔다.
6. AI/MCP를 사용할 수 있으면 현재 pub.dev 문서와 프로젝트 SDK 버전을 확인한 뒤 코드를 생성한다.

---

## Output Template

### Pigeon 인터페이스 정의

```dart
// pigeons/device_api.dart
import 'package:pigeon/pigeon.dart';

// 데이터 클래스
class DeviceInfo {
  String? model;
  String? osVersion;
  int? batteryLevel;
}

class AppSettings {
  bool? notificationsEnabled;
  String? theme;
}

// Flutter → Native (Host API)
@HostApi()
abstract class DeviceApi {
  DeviceInfo getDeviceInfo();
  void openSettings();
  bool checkPermission(String permission);
  void requestPermission(String permission);
}

// Native → Flutter (Flutter API)
@FlutterApi()
abstract class DeviceEventApi {
  void onBatteryLevelChanged(int level);
  void onPermissionResult(String permission, bool granted);
}
```

### 코드 생성 명령어

```bash
dart run pigeon \
  --input pigeons/device_api.dart \
  --dart_out lib/src/platform/device_api.g.dart \
  --kotlin_out android/app/src/main/kotlin/com/example/app/DeviceApi.g.kt \
  --kotlin_package "com.example.app" \
  --swift_out ios/Runner/DeviceApi.g.swift
```

### build.yaml 설정

```yaml
# build.yaml에 pigeon 스크립트 추가
targets:
  $default:
    sources:
      - pigeons/**
```

### Flutter에서 사용

```dart
// lib/src/platform/device_service.dart
import 'package:injectable/injectable.dart';

@injectable
class DeviceService {
  final DeviceApi _deviceApi = DeviceApi();

  Future<DeviceInfo> getDeviceInfo() async {
    return _deviceApi.getDeviceInfo();
  }

  Future<void> openSettings() async {
    return _deviceApi.openSettings();
  }

  Future<bool> checkPermission(String permission) async {
    return _deviceApi.checkPermission(permission);
  }
}

// Flutter API 구현 (Native에서 호출)
class DeviceEventApiImpl implements DeviceEventApi {
  final void Function(int) onBatteryChanged;
  final void Function(String, bool) onPermissionResultCallback;

  DeviceEventApiImpl({
    required this.onBatteryChanged,
    required this.onPermissionResultCallback,
  });

  @override
  void onBatteryLevelChanged(int level) {
    onBatteryChanged(level);
  }

  @override
  void onPermissionResult(String permission, bool granted) {
    onPermissionResultCallback(permission, granted);
  }
}
```

### Android (Kotlin) 구현

```kotlin
// android/app/src/main/kotlin/.../DeviceApiImpl.kt
class DeviceApiImpl(private val context: Context) : DeviceApi {
    override fun getDeviceInfo(): DeviceInfo {
        return DeviceInfo().apply {
            model = Build.MODEL
            osVersion = Build.VERSION.RELEASE
            batteryLevel = getBatteryLevel()
        }
    }

    override fun openSettings() {
        val intent = Intent(Settings.ACTION_SETTINGS)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
        context.startActivity(intent)
    }

    override fun checkPermission(permission: String): Boolean {
        return ContextCompat.checkSelfPermission(context, permission) ==
            PackageManager.PERMISSION_GRANTED
    }

    private fun getBatteryLevel(): Int {
        val batteryManager = context.getSystemService(Context.BATTERY_SERVICE) as BatteryManager
        return batteryManager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
    }
}

// MainActivity.kt에 등록
class MainActivity : FlutterActivity() {
    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        DeviceApi.setUp(flutterEngine.dartExecutor.binaryMessenger, DeviceApiImpl(this))
    }
}
```

### iOS (Swift) 구현

```swift
// ios/Runner/DeviceApiImpl.swift
class DeviceApiImpl: DeviceApi {
    func getDeviceInfo() throws -> DeviceInfo {
        let device = UIDevice.current
        let batteryLevel = Int64(device.batteryLevel * 100)

        return DeviceInfo(
            model: device.model,
            osVersion: device.systemVersion,
            batteryLevel: batteryLevel
        )
    }

    func openSettings() throws {
        if let url = URL(string: UIApplication.openSettingsURLString) {
            UIApplication.shared.open(url)
        }
    }

    func checkPermission(permission: String) throws -> Bool {
        // Permission 체크 로직
        return true
    }
}

// AppDelegate.swift에 등록
@UIApplicationMain
class AppDelegate: FlutterAppDelegate {
    override func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {
        let controller = window?.rootViewController as! FlutterViewController
        DeviceApiSetup.setUp(binaryMessenger: controller.binaryMessenger, api: DeviceApiImpl())
        return super.application(application, didFinishLaunchingWithOptions: launchOptions)
    }
}
```

---

## Pigeon 지원 타입

| Dart | Kotlin | Swift |
|------|--------|-------|
| bool | Boolean | Bool |
| int | Long | Int64 |
| double | Double | Double |
| String | String | String |
| Uint8List | ByteArray | FlutterStandardTypedData |
| List<T> | List<T> | [T] |
| Map<K, V> | Map<K, V> | [K: V] |
| 클래스 | 클래스 | 클래스 |
| enum | enum | enum |

## References

- `_references/RECENT-FLUTTER-CHANGES.md`
- `_references/QUALITY-CODE-PATTERN.md`
- `_references/ARCHITECTURE-PATTERN.md`
