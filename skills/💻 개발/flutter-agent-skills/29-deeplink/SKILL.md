---
name: deeplink
description: |
  딥링크 및 유니버셜 링크 설정을 구성합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Deep Link Skill

딥링크 및 유니버셜 링크 설정을 구성합니다.

## Triggers

- "딥링크", "deeplink", "universal link", "app link", "dynamic link"

---

## 딥링크 유형

```
┌─────────────────────────────────────────────────────────────┐
│                      Deep Link Types                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐  │
│  │ URI Scheme     │  │ Universal Link │  │ App Link      │  │
│  │ (Custom)       │  │ (iOS)          │  │ (Android)     │  │
│  ├────────────────┤  ├────────────────┤  ├───────────────┤  │
│  │ myapp://       │  │ https://       │  │ https://      │  │
│  │ product/123    │  │ example.com/   │  │ example.com/  │  │
│  │                │  │ product/123    │  │ product/123   │  │
│  └────────────────┘  └────────────────┘  └───────────────┘  │
│                                                              │
│  ✗ 앱 미설치시     │  ✓ 앱 미설치시     │  ✓ 앱 미설치시   │
│    동작 안함        │    웹으로 이동     │    웹으로 이동   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Dependencies

```yaml
dependencies:
  # Deep Link handling
  app_links: ^7.0.0

  # GoRouter (already included)
  go_router: ^17.2.3
```

---

## 1. Android Configuration

### AndroidManifest.xml

```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<manifest>
    <application>
        <activity
            android:name=".MainActivity"
            android:launchMode="singleTask">

            <!-- URI Scheme (Custom) -->
            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="myapp" />
            </intent-filter>

            <!-- App Links (Verified) -->
            <intent-filter android:autoVerify="true">
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data
                    android:scheme="https"
                    android:host="example.com"
                    android:pathPrefix="/app" />
            </intent-filter>

        </activity>
    </application>
</manifest>
```

### Digital Asset Links

```json
// https://example.com/.well-known/assetlinks.json
[{
  "relation": ["delegate_permission/common.handle_all_urls"],
  "target": {
    "namespace": "android_app",
    "package_name": "com.example.myapp",
    "sha256_cert_fingerprints": [
      "AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99"
    ]
  }
}]
```

---

## 2. iOS Configuration

### Info.plist

```xml
<!-- ios/Runner/Info.plist -->
<dict>
    <!-- URI Scheme -->
    <key>CFBundleURLTypes</key>
    <array>
        <dict>
            <key>CFBundleURLSchemes</key>
            <array>
                <string>myapp</string>
            </array>
            <key>CFBundleURLName</key>
            <string>com.example.myapp</string>
        </dict>
    </array>

    <!-- Universal Links -->
    <key>FlutterDeepLinkingEnabled</key>
    <true/>
</dict>
```

### Associated Domains

```xml
<!-- ios/Runner/Runner.entitlements -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.developer.associated-domains</key>
    <array>
        <string>applinks:example.com</string>
        <string>applinks:www.example.com</string>
    </array>
</dict>
</plist>
```

### Apple App Site Association

```json
// https://example.com/.well-known/apple-app-site-association
{
  "applinks": {
    "apps": [],
    "details": [
      {
        "appIDs": ["TEAMID.com.example.myapp"],
        "paths": ["/app/*", "/product/*", "/user/*"],
        "components": [
          {
            "/": "/product/*",
            "comment": "Product deep links"
          }
        ]
      }
    ]
  }
}
```

---

## 3. Deep Link Service

```dart
// lib/core/deeplink/deep_link_service.dart
import 'package:app_links/app_links.dart';
import 'package:fpdart/fpdart.dart';

abstract class DeepLinkService {
  Future<Uri?> getInitialLink();
  Stream<Uri> get linkStream;
  Future<Either<Failure, void>> handleLink(Uri uri);
}

class DeepLinkServiceImpl implements DeepLinkService {
  final AppLinks _appLinks;
  final GoRouter _router;

  DeepLinkServiceImpl(this._router) : _appLinks = AppLinks();

  @override
  Future<Uri?> getInitialLink() async {
    try {
      return await _appLinks.getInitialLink();
    } catch (e) {
      return null;
    }
  }

  @override
  Stream<Uri> get linkStream => _appLinks.uriLinkStream;

  @override
  Future<Either<Failure, void>> handleLink(Uri uri) async {
    try {
      final path = _convertToAppPath(uri);
      _router.go(path);
      return const Right(null);
    } catch (e) {
      return Left(DeepLinkFailure('Failed to handle link: $e'));
    }
  }

  String _convertToAppPath(Uri uri) {
    // Handle different schemes
    if (uri.scheme == 'myapp') {
      // myapp://product/123 -> /product/123
      return uri.path.isEmpty ? '/${uri.host}' : uri.path;
    }

    // Universal/App Links: https://example.com/app/product/123
    final path = uri.path;
    if (path.startsWith('/app')) {
      return path.substring(4); // Remove /app prefix
    }
    return path;
  }
}
```

---

## 4. Deep Link Handler

```dart
// lib/core/deeplink/deep_link_handler.dart
import 'dart:async';

class DeepLinkHandler {
  final DeepLinkService _deepLinkService;
  final Talker _talker;
  StreamSubscription<Uri>? _subscription;

  DeepLinkHandler(this._deepLinkService, this._talker);

  Future<void> initialize() async {
    // Handle initial link (cold start)
    final initialLink = await _deepLinkService.getInitialLink();
    if (initialLink != null) {
      _talker.info('Initial deep link: $initialLink');
      await _deepLinkService.handleLink(initialLink);
    }

    // Listen for incoming links (warm start)
    _subscription = _deepLinkService.linkStream.listen(
      (uri) {
        _talker.info('Incoming deep link: $uri');
        _deepLinkService.handleLink(uri);
      },
      onError: (error) {
        _talker.error('Deep link error: $error');
      },
    );
  }

  void dispose() {
    _subscription?.cancel();
  }
}
```

---

## 5. GoRouter Integration

```dart
// lib/routes/app_router.dart
import 'package:go_router/go_router.dart';

@riverpod
GoRouter appRouter(Ref ref) {
  final authState = ref.watch(authNotifierProvider);

  return GoRouter(
    initialLocation: '/',
    debugLogDiagnostics: true,

    // Deep link configuration
    redirect: (context, state) {
      final isLoggedIn = authState.isAuthenticated;
      final isAuthRoute = state.matchedLocation.startsWith('/auth');

      // Redirect logic for protected routes
      if (!isLoggedIn && !isAuthRoute) {
        // Save intended destination for after login
        return '/auth/login?redirect=${state.matchedLocation}';
      }

      return null;
    },

    routes: [
      GoRoute(
        path: '/',
        builder: (context, state) => const HomePage(),
      ),

      // Product deep link: myapp://product/123 or https://example.com/app/product/123
      GoRoute(
        path: '/product/:id',
        builder: (context, state) {
          final productId = state.pathParameters['id']!;
          return ProductDetailPage(productId: productId);
        },
      ),

      // User profile: /user/abc
      GoRoute(
        path: '/user/:userId',
        builder: (context, state) {
          final userId = state.pathParameters['userId']!;
          return UserProfilePage(userId: userId);
        },
      ),

      // Category with query params: /category/electronics?sort=price
      GoRoute(
        path: '/category/:name',
        builder: (context, state) {
          final name = state.pathParameters['name']!;
          final sort = state.uri.queryParameters['sort'];
          return CategoryPage(name: name, sortBy: sort);
        },
      ),

      // Auth routes
      GoRoute(
        path: '/auth/login',
        builder: (context, state) {
          final redirect = state.uri.queryParameters['redirect'];
          return LoginPage(redirectTo: redirect);
        },
      ),
    ],
  );
}
```

---

## 6. App Initialization

```dart
// lib/main.dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await configureDependencies();

  // Initialize deep link handler
  final deepLinkHandler = getIt<DeepLinkHandler>();
  await deepLinkHandler.initialize();

  runApp(const MyApp());
}

// lib/app.dart
class MyApp extends ConsumerStatefulWidget {
  const MyApp({super.key});

  @override
  ConsumerState<MyApp> createState() => _MyAppState();
}

class _MyAppState extends ConsumerState<MyApp> {
  @override
  void dispose() {
    getIt<DeepLinkHandler>().dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final router = ref.watch(appRouterProvider);

    return MaterialApp.router(
      routerConfig: router,
      // ...
    );
  }
}
```

---

## 7. Deep Link Testing

```dart
// test/unit/core/deeplink/deep_link_service_test.dart
void main() {
  late DeepLinkServiceImpl sut;
  late MockGoRouter mockRouter;

  setUp(() {
    mockRouter = MockGoRouter();
    sut = DeepLinkServiceImpl(mockRouter);
  });

  group('handleLink', () {
    test('should navigate to product page for custom scheme', () async {
      // Arrange
      final uri = Uri.parse('myapp://product/123');

      // Act
      await sut.handleLink(uri);

      // Assert
      verify(() => mockRouter.go('/product/123')).called(1);
    });

    test('should strip /app prefix from universal links', () async {
      // Arrange
      final uri = Uri.parse('https://example.com/app/product/456');

      // Act
      await sut.handleLink(uri);

      // Assert
      verify(() => mockRouter.go('/product/456')).called(1);
    });
  });
}
```

### Manual Testing

```bash
# Android - Custom scheme
adb shell am start -a android.intent.action.VIEW \
  -d "myapp://product/123" \
  com.example.myapp

# Android - App Link
adb shell am start -a android.intent.action.VIEW \
  -d "https://example.com/app/product/123" \
  com.example.myapp

# iOS - Custom scheme (Simulator)
xcrun simctl openurl booted "myapp://product/123"

# iOS - Universal Link (Simulator)
xcrun simctl openurl booted "https://example.com/app/product/123"
```

---

## 8. Firebase Dynamic Links (Alternative)

```yaml
# Firebase Dynamic Links 사용시
dependencies:
  firebase_dynamic_links: ^6.0.8
```

```dart
// Firebase Dynamic Links 핸들러
class FirebaseDynamicLinkHandler {
  final FirebaseDynamicLinks _dynamicLinks = FirebaseDynamicLinks.instance;

  Future<void> initialize() async {
    // Cold start
    final initialLink = await _dynamicLinks.getInitialLink();
    if (initialLink != null) {
      _handleDynamicLink(initialLink);
    }

    // Warm start
    _dynamicLinks.onLink.listen(_handleDynamicLink);
  }

  void _handleDynamicLink(PendingDynamicLinkData data) {
    final deepLink = data.link;
    // Navigate based on deep link
  }

  // Create dynamic link
  Future<Uri> createProductLink(String productId) async {
    final parameters = DynamicLinkParameters(
      uriPrefix: 'https://myapp.page.link',
      link: Uri.parse('https://example.com/product/$productId'),
      androidParameters: const AndroidParameters(
        packageName: 'com.example.myapp',
        minimumVersion: 1,
      ),
      iosParameters: const IOSParameters(
        bundleId: 'com.example.myapp',
        minimumVersion: '1.0.0',
        appStoreId: '123456789',
      ),
    );

    final shortLink = await _dynamicLinks.buildShortLink(parameters);
    return shortLink.shortUrl;
  }
}
```

---

## Checklist

- [ ] Android URI Scheme 설정
- [ ] Android App Links (assetlinks.json)
- [ ] iOS URI Scheme 설정
- [ ] iOS Universal Links (apple-app-site-association)
- [ ] DeepLinkService 구현
- [ ] GoRouter 통합
- [ ] 인증 리다이렉트 처리
- [ ] 딥링크 테스트
- [ ] Dynamic Links (선택)

---

## References

- `_references/RECENT-FLUTTER-CHANGES.md`
- `10-routing/SKILL.md`
