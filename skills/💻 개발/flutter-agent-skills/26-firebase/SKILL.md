---
name: firebase
description: |
  Flutter 프로젝트에 Firebase 서비스를 설정하고 통합합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Firebase Skill

Flutter 프로젝트에 Firebase 서비스를 설정하고 통합합니다.

## Triggers

- "firebase", "파이어베이스", "FCM", "푸시 알림", "crashlytics", "analytics"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectName` | ✅ | 프로젝트 이름 |
| `services` | ❌ | 사용할 Firebase 서비스 (기본: core, auth, firestore) |
| `useFlavors` | ❌ | Flavor별 Firebase 설정 여부 (기본: true) |

---

## Firebase 서비스 목록

| 서비스 | 패키지 | 버전 | 설명 |
|--------|--------|------|------|
| **Core** | firebase_core | ^4.9.0 | Firebase 초기화 (필수) |
| **Auth** | firebase_auth | ^6.5.1 | 인증 (이메일, 소셜 로그인) |
| **Firestore** | cloud_firestore | ^6.4.1 | NoSQL 데이터베이스 |
| **Messaging** | firebase_messaging | ^16.2.2 | 푸시 알림 (FCM) |
| **Crashlytics** | firebase_crashlytics | ^5.2.2 | 크래시 리포팅 |
| **Analytics** | firebase_analytics | ^12.4.1 | 사용자 분석 |
| **Storage** | firebase_storage | ^13.4.1 | 파일 저장소 |
| **Remote Config** | firebase_remote_config | ^6.5.1 | 원격 설정 |

---

## 설정

### pubspec.yaml

```yaml
dependencies:
  # Firebase Core (필수)
  firebase_core: ^4.9.0

  # Authentication
  firebase_auth: ^6.5.1

  # Database
  cloud_firestore: ^6.4.1

  # Push Notifications
  firebase_messaging: ^16.2.2

  # Crash Reporting
  firebase_crashlytics: ^5.2.2

  # Analytics
  firebase_analytics: ^12.4.1

  # File Storage
  firebase_storage: ^13.4.1

  # Remote Config
  firebase_remote_config: ^6.5.1
```

---

## Output Templates

### 1. FlutterFire CLI 설정

```bash
# FlutterFire CLI 설치
dart pub global activate flutterfire_cli

# Firebase 프로젝트 설정 (Flavor 없이)
flutterfire configure

# Flavor별 Firebase 설정
flutterfire configure \
  --project=my-app-dev \
  --out=lib/firebase_options_dev.dart \
  --ios-bundle-id=com.example.app.dev \
  --android-app-id=com.example.app.dev

flutterfire configure \
  --project=my-app-staging \
  --out=lib/firebase_options_staging.dart \
  --ios-bundle-id=com.example.app.staging \
  --android-app-id=com.example.app.staging

flutterfire configure \
  --project=my-app-prod \
  --out=lib/firebase_options_prod.dart \
  --ios-bundle-id=com.example.app \
  --android-app-id=com.example.app
```

### 2. Firebase 초기화 (Flavor 통합)

```dart
// lib/core/firebase/firebase_initializer.dart
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_crashlytics/firebase_crashlytics.dart';
import 'package:firebase_analytics/firebase_analytics.dart';
import 'package:flutter/foundation.dart';
import '../config/flavor_config.dart';
import '../../firebase_options_dev.dart' as dev;
import '../../firebase_options_staging.dart' as staging;
import '../../firebase_options_prod.dart' as prod;

class FirebaseInitializer {
  static Future<void> initialize() async {
    // Flavor별 Firebase Options 선택
    final options = _getFirebaseOptions();

    await Firebase.initializeApp(options: options);

    // Crashlytics 설정
    await _initCrashlytics();

    // Analytics 설정
    await _initAnalytics();
  }

  static FirebaseOptions _getFirebaseOptions() {
    switch (FlavorConfig.instance.flavor) {
      case Flavor.dev:
        return dev.DefaultFirebaseOptions.currentPlatform;
      case Flavor.staging:
        return staging.DefaultFirebaseOptions.currentPlatform;
      case Flavor.prod:
        return prod.DefaultFirebaseOptions.currentPlatform;
    }
  }

  static Future<void> _initCrashlytics() async {
    // Debug 모드에서는 Crashlytics 비활성화
    if (kDebugMode) {
      await FirebaseCrashlytics.instance.setCrashlyticsCollectionEnabled(false);
      return;
    }

    // Release 모드에서 활성화
    await FirebaseCrashlytics.instance.setCrashlyticsCollectionEnabled(true);

    // Flutter 에러 캐치
    FlutterError.onError = FirebaseCrashlytics.instance.recordFlutterFatalError;

    // Async 에러 캐치
    PlatformDispatcher.instance.onError = (error, stack) {
      FirebaseCrashlytics.instance.recordError(error, stack, fatal: true);
      return true;
    };
  }

  static Future<void> _initAnalytics() async {
    final analytics = FirebaseAnalytics.instance;

    // Dev 환경에서는 Analytics 비활성화
    if (FlavorConfig.isDev) {
      await analytics.setAnalyticsCollectionEnabled(false);
    } else {
      await analytics.setAnalyticsCollectionEnabled(true);
    }
  }
}
```

### 3. Entry Point with Firebase

```dart
// lib/main_dev.dart
import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'core/config/flavor_config.dart';
import 'core/firebase/firebase_initializer.dart';
import 'app.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Flavor 설정
  FlavorConfig.dev();

  // Firebase 초기화
  await FirebaseInitializer.initialize();

  runApp(const App());
}
```

### 4. Firebase Auth Service

```dart
// lib/core/firebase/services/firebase_auth_service.dart
import 'package:firebase_auth/firebase_auth.dart';
import 'package:fpdart/fpdart.dart';
import '../../error/failures.dart';

abstract class FirebaseAuthService {
  Stream<User?> get authStateChanges;
  User? get currentUser;

  Future<Either<Failure, UserCredential>> signInWithEmail({
    required String email,
    required String password,
  });

  Future<Either<Failure, UserCredential>> signUpWithEmail({
    required String email,
    required String password,
  });

  Future<Either<Failure, void>> signOut();

  Future<Either<Failure, void>> sendPasswordResetEmail(String email);
}

class FirebaseAuthServiceImpl implements FirebaseAuthService {
  final FirebaseAuth _auth;

  FirebaseAuthServiceImpl({FirebaseAuth? auth})
      : _auth = auth ?? FirebaseAuth.instance;

  @override
  Stream<User?> get authStateChanges => _auth.authStateChanges();

  @override
  User? get currentUser => _auth.currentUser;

  @override
  Future<Either<Failure, UserCredential>> signInWithEmail({
    required String email,
    required String password,
  }) async {
    try {
      final credential = await _auth.signInWithEmailAndPassword(
        email: email,
        password: password,
      );
      return right(credential);
    } on FirebaseAuthException catch (e) {
      return left(_mapAuthException(e));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, UserCredential>> signUpWithEmail({
    required String email,
    required String password,
  }) async {
    try {
      final credential = await _auth.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );
      return right(credential);
    } on FirebaseAuthException catch (e) {
      return left(_mapAuthException(e));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, void>> signOut() async {
    try {
      await _auth.signOut();
      return right(null);
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, void>> sendPasswordResetEmail(String email) async {
    try {
      await _auth.sendPasswordResetEmail(email: email);
      return right(null);
    } on FirebaseAuthException catch (e) {
      return left(_mapAuthException(e));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  Failure _mapAuthException(FirebaseAuthException e) {
    switch (e.code) {
      case 'user-not-found':
        return const AuthFailure(message: '사용자를 찾을 수 없습니다.');
      case 'wrong-password':
        return const AuthFailure(message: '비밀번호가 올바르지 않습니다.');
      case 'email-already-in-use':
        return const AuthFailure(message: '이미 사용 중인 이메일입니다.');
      case 'weak-password':
        return const AuthFailure(message: '비밀번호가 너무 약합니다.');
      case 'invalid-email':
        return const AuthFailure(message: '이메일 형식이 올바르지 않습니다.');
      case 'too-many-requests':
        return const AuthFailure(message: '너무 많은 요청입니다. 잠시 후 다시 시도해주세요.');
      default:
        return AuthFailure(message: e.message ?? '인증 오류가 발생했습니다.');
    }
  }
}
```

### 5. Firestore Service

```dart
// lib/core/firebase/services/firestore_service.dart
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:fpdart/fpdart.dart';
import '../../error/failures.dart';

abstract class FirestoreService {
  Future<Either<Failure, T>> getDocument<T>({
    required String collection,
    required String id,
    required T Function(Map<String, dynamic>) fromJson,
  });

  Future<Either<Failure, List<T>>> getCollection<T>({
    required String collection,
    required T Function(Map<String, dynamic>) fromJson,
    Query<Map<String, dynamic>> Function(CollectionReference<Map<String, dynamic>>)? query,
  });

  Future<Either<Failure, String>> addDocument({
    required String collection,
    required Map<String, dynamic> data,
  });

  Future<Either<Failure, void>> updateDocument({
    required String collection,
    required String id,
    required Map<String, dynamic> data,
  });

  Future<Either<Failure, void>> deleteDocument({
    required String collection,
    required String id,
  });

  Stream<List<T>> streamCollection<T>({
    required String collection,
    required T Function(Map<String, dynamic>) fromJson,
    Query<Map<String, dynamic>> Function(CollectionReference<Map<String, dynamic>>)? query,
  });
}

class FirestoreServiceImpl implements FirestoreService {
  final FirebaseFirestore _firestore;

  FirestoreServiceImpl({FirebaseFirestore? firestore})
      : _firestore = firestore ?? FirebaseFirestore.instance;

  @override
  Future<Either<Failure, T>> getDocument<T>({
    required String collection,
    required String id,
    required T Function(Map<String, dynamic>) fromJson,
  }) async {
    try {
      final doc = await _firestore.collection(collection).doc(id).get();
      if (!doc.exists) {
        return left(const NotFoundFailure(message: '문서를 찾을 수 없습니다.'));
      }
      return right(fromJson({...doc.data()!, 'id': doc.id}));
    } on FirebaseException catch (e) {
      return left(ServerFailure(message: e.message ?? '서버 오류'));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, List<T>>> getCollection<T>({
    required String collection,
    required T Function(Map<String, dynamic>) fromJson,
    Query<Map<String, dynamic>> Function(CollectionReference<Map<String, dynamic>>)? query,
  }) async {
    try {
      Query<Map<String, dynamic>> ref = _firestore.collection(collection);
      if (query != null) {
        ref = query(_firestore.collection(collection));
      }
      final snapshot = await ref.get();
      final items = snapshot.docs
          .map((doc) => fromJson({...doc.data(), 'id': doc.id}))
          .toList();
      return right(items);
    } on FirebaseException catch (e) {
      return left(ServerFailure(message: e.message ?? '서버 오류'));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, String>> addDocument({
    required String collection,
    required Map<String, dynamic> data,
  }) async {
    try {
      final doc = await _firestore.collection(collection).add({
        ...data,
        'createdAt': FieldValue.serverTimestamp(),
        'updatedAt': FieldValue.serverTimestamp(),
      });
      return right(doc.id);
    } on FirebaseException catch (e) {
      return left(ServerFailure(message: e.message ?? '서버 오류'));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, void>> updateDocument({
    required String collection,
    required String id,
    required Map<String, dynamic> data,
  }) async {
    try {
      await _firestore.collection(collection).doc(id).update({
        ...data,
        'updatedAt': FieldValue.serverTimestamp(),
      });
      return right(null);
    } on FirebaseException catch (e) {
      return left(ServerFailure(message: e.message ?? '서버 오류'));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, void>> deleteDocument({
    required String collection,
    required String id,
  }) async {
    try {
      await _firestore.collection(collection).doc(id).delete();
      return right(null);
    } on FirebaseException catch (e) {
      return left(ServerFailure(message: e.message ?? '서버 오류'));
    } catch (e) {
      return left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Stream<List<T>> streamCollection<T>({
    required String collection,
    required T Function(Map<String, dynamic>) fromJson,
    Query<Map<String, dynamic>> Function(CollectionReference<Map<String, dynamic>>)? query,
  }) {
    Query<Map<String, dynamic>> ref = _firestore.collection(collection);
    if (query != null) {
      ref = query(_firestore.collection(collection));
    }
    return ref.snapshots().map(
      (snapshot) => snapshot.docs
          .map((doc) => fromJson({...doc.data(), 'id': doc.id}))
          .toList(),
    );
  }
}
```

### 6. FCM (Push Notifications) Service

```dart
// lib/core/firebase/services/fcm_service.dart
import 'dart:convert';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:talker/talker.dart';

// Background message handler (최상위 함수)
@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  // Background에서 메시지 처리
  print('Background message: ${message.messageId}');
}

class FCMService {
  final FirebaseMessaging _messaging;
  final FlutterLocalNotificationsPlugin _localNotifications;
  final Talker _talker;

  FCMService({
    FirebaseMessaging? messaging,
    FlutterLocalNotificationsPlugin? localNotifications,
    Talker? talker,
  })  : _messaging = messaging ?? FirebaseMessaging.instance,
        _localNotifications = localNotifications ?? FlutterLocalNotificationsPlugin(),
        _talker = talker ?? Talker();

  Future<void> initialize() async {
    // Background handler 등록
    FirebaseMessaging.onBackgroundMessage(firebaseMessagingBackgroundHandler);

    // 권한 요청
    await _requestPermission();

    // Local notifications 초기화
    await _initLocalNotifications();

    // FCM 토큰 획득
    final token = await getToken();
    _talker.info('FCM Token: $token');

    // Foreground 메시지 리스너
    FirebaseMessaging.onMessage.listen(_handleForegroundMessage);

    // 앱이 열린 상태에서 알림 탭 처리
    FirebaseMessaging.onMessageOpenedApp.listen(_handleMessageOpenedApp);

    // 앱이 종료된 상태에서 알림으로 열린 경우
    final initialMessage = await _messaging.getInitialMessage();
    if (initialMessage != null) {
      _handleMessageOpenedApp(initialMessage);
    }
  }

  Future<void> _requestPermission() async {
    final settings = await _messaging.requestPermission(
      alert: true,
      announcement: false,
      badge: true,
      carPlay: false,
      criticalAlert: false,
      provisional: false,
      sound: true,
    );

    _talker.info('FCM Permission: ${settings.authorizationStatus}');
  }

  Future<void> _initLocalNotifications() async {
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );

    const settings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );

    await _localNotifications.initialize(
      settings,
      onDidReceiveNotificationResponse: (response) {
        // 알림 탭 처리
        final payload = response.payload;
        if (payload != null) {
          final data = jsonDecode(payload) as Map<String, dynamic>;
          _handleNotificationTap(data);
        }
      },
    );

    // Android 알림 채널 생성
    const channel = AndroidNotificationChannel(
      'high_importance_channel',
      'High Importance Notifications',
      description: 'Important notifications',
      importance: Importance.high,
    );

    await _localNotifications
        .resolvePlatformSpecificImplementation<
            AndroidFlutterLocalNotificationsPlugin>()
        ?.createNotificationChannel(channel);
  }

  Future<String?> getToken() async {
    return _messaging.getToken();
  }

  Stream<String> get onTokenRefresh => _messaging.onTokenRefresh;

  Future<void> subscribeToTopic(String topic) async {
    await _messaging.subscribeToTopic(topic);
    _talker.info('Subscribed to topic: $topic');
  }

  Future<void> unsubscribeFromTopic(String topic) async {
    await _messaging.unsubscribeFromTopic(topic);
    _talker.info('Unsubscribed from topic: $topic');
  }

  void _handleForegroundMessage(RemoteMessage message) {
    _talker.info('Foreground message: ${message.messageId}');

    final notification = message.notification;
    if (notification != null) {
      _localNotifications.show(
        notification.hashCode,
        notification.title,
        notification.body,
        const NotificationDetails(
          android: AndroidNotificationDetails(
            'high_importance_channel',
            'High Importance Notifications',
            icon: '@mipmap/ic_launcher',
            importance: Importance.high,
            priority: Priority.high,
          ),
          iOS: DarwinNotificationDetails(
            presentAlert: true,
            presentBadge: true,
            presentSound: true,
          ),
        ),
        payload: jsonEncode(message.data),
      );
    }
  }

  void _handleMessageOpenedApp(RemoteMessage message) {
    _talker.info('Message opened app: ${message.messageId}');
    _handleNotificationTap(message.data);
  }

  void _handleNotificationTap(Map<String, dynamic> data) {
    // 알림 데이터에 따른 네비게이션 처리
    // 예: GoRouter를 사용한 딥링크 처리
    final route = data['route'] as String?;
    if (route != null) {
      // router.push(route);
    }
  }
}
```

### 7. Analytics Service

```dart
// lib/core/firebase/services/analytics_service.dart
import 'package:firebase_analytics/firebase_analytics.dart';

class AnalyticsService {
  final FirebaseAnalytics _analytics;

  AnalyticsService({FirebaseAnalytics? analytics})
      : _analytics = analytics ?? FirebaseAnalytics.instance;

  FirebaseAnalyticsObserver get observer =>
      FirebaseAnalyticsObserver(analytics: _analytics);

  // 사용자 속성 설정
  Future<void> setUserId(String? userId) async {
    await _analytics.setUserId(id: userId);
  }

  Future<void> setUserProperty({
    required String name,
    required String? value,
  }) async {
    await _analytics.setUserProperty(name: name, value: value);
  }

  // 화면 추적
  Future<void> logScreenView({
    required String screenName,
    String? screenClass,
  }) async {
    await _analytics.logScreenView(
      screenName: screenName,
      screenClass: screenClass,
    );
  }

  // 이벤트 로깅
  Future<void> logEvent({
    required String name,
    Map<String, Object?>? parameters,
  }) async {
    await _analytics.logEvent(
      name: name,
      parameters: parameters,
    );
  }

  // 미리 정의된 이벤트
  Future<void> logLogin({String? loginMethod}) async {
    await _analytics.logLogin(loginMethod: loginMethod);
  }

  Future<void> logSignUp({required String signUpMethod}) async {
    await _analytics.logSignUp(signUpMethod: signUpMethod);
  }

  Future<void> logPurchase({
    required double value,
    required String currency,
    String? transactionId,
    List<AnalyticsEventItem>? items,
  }) async {
    await _analytics.logPurchase(
      value: value,
      currency: currency,
      transactionId: transactionId,
      items: items,
    );
  }

  Future<void> logAddToCart({
    required String itemId,
    required String itemName,
    required double value,
    String? currency,
  }) async {
    await _analytics.logAddToCart(
      items: [
        AnalyticsEventItem(
          itemId: itemId,
          itemName: itemName,
          price: value,
        ),
      ],
      value: value,
      currency: currency ?? 'KRW',
    );
  }

  Future<void> logSearch({required String searchTerm}) async {
    await _analytics.logSearch(searchTerm: searchTerm);
  }

  Future<void> logShare({
    required String contentType,
    required String itemId,
    required String method,
  }) async {
    await _analytics.logShare(
      contentType: contentType,
      itemId: itemId,
      method: method,
    );
  }
}
```

### 8. Crashlytics Service

```dart
// lib/core/firebase/services/crashlytics_service.dart
import 'package:firebase_crashlytics/firebase_crashlytics.dart';

class CrashlyticsService {
  final FirebaseCrashlytics _crashlytics;

  CrashlyticsService({FirebaseCrashlytics? crashlytics})
      : _crashlytics = crashlytics ?? FirebaseCrashlytics.instance;

  // 사용자 식별
  Future<void> setUserId(String userId) async {
    await _crashlytics.setUserIdentifier(userId);
  }

  // 커스텀 키-값 추가
  Future<void> setCustomKey(String key, dynamic value) async {
    await _crashlytics.setCustomKey(key, value);
  }

  // 로그 추가 (크래시 시 표시됨)
  Future<void> log(String message) async {
    await _crashlytics.log(message);
  }

  // Non-fatal 에러 기록
  Future<void> recordError(
    dynamic exception,
    StackTrace? stack, {
    String? reason,
    bool fatal = false,
  }) async {
    await _crashlytics.recordError(
      exception,
      stack,
      reason: reason,
      fatal: fatal,
    );
  }

  // 테스트용 크래시
  void crash() {
    _crashlytics.crash();
  }
}
```

### 9. Remote Config Service

```dart
// lib/core/firebase/services/remote_config_service.dart
import 'package:firebase_remote_config/firebase_remote_config.dart';

class RemoteConfigService {
  final FirebaseRemoteConfig _remoteConfig;

  RemoteConfigService({FirebaseRemoteConfig? remoteConfig})
      : _remoteConfig = remoteConfig ?? FirebaseRemoteConfig.instance;

  Future<void> initialize({
    Map<String, dynamic>? defaults,
    Duration fetchTimeout = const Duration(minutes: 1),
    Duration minimumFetchInterval = const Duration(hours: 1),
  }) async {
    await _remoteConfig.setConfigSettings(
      RemoteConfigSettings(
        fetchTimeout: fetchTimeout,
        minimumFetchInterval: minimumFetchInterval,
      ),
    );

    if (defaults != null) {
      await _remoteConfig.setDefaults(defaults);
    }

    await fetchAndActivate();
  }

  Future<bool> fetchAndActivate() async {
    try {
      return await _remoteConfig.fetchAndActivate();
    } catch (e) {
      return false;
    }
  }

  // 값 가져오기
  String getString(String key) => _remoteConfig.getString(key);
  int getInt(String key) => _remoteConfig.getInt(key);
  double getDouble(String key) => _remoteConfig.getDouble(key);
  bool getBool(String key) => _remoteConfig.getBool(key);

  // 실시간 업데이트 리스너
  Stream<RemoteConfigUpdate> get onConfigUpdated =>
      _remoteConfig.onConfigUpdated;
}
```

### 10. Firebase Providers (Riverpod)

```dart
// lib/core/firebase/providers/firebase_providers.dart
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_analytics/firebase_analytics.dart';
import 'package:firebase_crashlytics/firebase_crashlytics.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:firebase_remote_config/firebase_remote_config.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../services/firebase_auth_service.dart';
import '../services/firestore_service.dart';
import '../services/fcm_service.dart';
import '../services/analytics_service.dart';
import '../services/crashlytics_service.dart';
import '../services/remote_config_service.dart';

part 'firebase_providers.g.dart';

// Firebase 인스턴스 Provider
@riverpod
FirebaseAuth firebaseAuth(FirebaseAuthRef ref) => FirebaseAuth.instance;

@riverpod
FirebaseFirestore firestore(FirestoreRef ref) => FirebaseFirestore.instance;

@riverpod
FirebaseMessaging firebaseMessaging(FirebaseMessagingRef ref) =>
    FirebaseMessaging.instance;

@riverpod
FirebaseAnalytics firebaseAnalytics(FirebaseAnalyticsRef ref) =>
    FirebaseAnalytics.instance;

@riverpod
FirebaseCrashlytics firebaseCrashlytics(FirebaseCrashlyticsRef ref) =>
    FirebaseCrashlytics.instance;

@riverpod
FirebaseRemoteConfig firebaseRemoteConfig(FirebaseRemoteConfigRef ref) =>
    FirebaseRemoteConfig.instance;

@riverpod
FirebaseStorage firebaseStorage(FirebaseStorageRef ref) =>
    FirebaseStorage.instance;

// 서비스 Provider
@riverpod
FirebaseAuthService firebaseAuthService(FirebaseAuthServiceRef ref) {
  return FirebaseAuthServiceImpl(auth: ref.watch(firebaseAuthProvider));
}

@riverpod
FirestoreService firestoreService(FirestoreServiceRef ref) {
  return FirestoreServiceImpl(firestore: ref.watch(firestoreProvider));
}

@riverpod
FCMService fcmService(FCMServiceRef ref) {
  return FCMService(messaging: ref.watch(firebaseMessagingProvider));
}

@riverpod
AnalyticsService analyticsService(AnalyticsServiceRef ref) {
  return AnalyticsService(analytics: ref.watch(firebaseAnalyticsProvider));
}

@riverpod
CrashlyticsService crashlyticsService(CrashlyticsServiceRef ref) {
  return CrashlyticsService(crashlytics: ref.watch(firebaseCrashlyticsProvider));
}

@riverpod
RemoteConfigService remoteConfigService(RemoteConfigServiceRef ref) {
  return RemoteConfigService(remoteConfig: ref.watch(firebaseRemoteConfigProvider));
}

// Auth State Stream
@riverpod
Stream<User?> authState(AuthStateRef ref) {
  return ref.watch(firebaseAuthServiceProvider).authStateChanges;
}
```

### 11. 디렉토리 구조

```
lib/
├── core/
│   ├── firebase/
│   │   ├── firebase_initializer.dart      # Firebase 초기화
│   │   ├── providers/
│   │   │   └── firebase_providers.dart    # Riverpod Providers
│   │   └── services/
│   │       ├── firebase_auth_service.dart
│   │       ├── firestore_service.dart
│   │       ├── fcm_service.dart
│   │       ├── analytics_service.dart
│   │       ├── crashlytics_service.dart
│   │       └── remote_config_service.dart
│   └── ...
├── firebase_options_dev.dart              # FlutterFire CLI 생성
├── firebase_options_staging.dart
├── firebase_options_prod.dart
├── main_dev.dart
├── main_staging.dart
└── main_prod.dart
```

---

## 실행 명령어

```bash
# FlutterFire CLI 설치
dart pub global activate flutterfire_cli

# Firebase 설정 (각 Flavor별)
flutterfire configure --project=my-app-dev \
  --out=lib/firebase_options_dev.dart \
  --android-app-id=com.example.app.dev \
  --ios-bundle-id=com.example.app.dev

# 코드 생성
dart run build_runner build --delete-conflicting-outputs

# Flavor별 실행
flutter run --flavor dev -t lib/main_dev.dart
```

---

## iOS 추가 설정

### Info.plist (푸시 알림)

```xml
<!-- ios/Runner/Info.plist -->
<key>UIBackgroundModes</key>
<array>
  <string>fetch</string>
  <string>remote-notification</string>
</array>
```

### AppDelegate.swift

```swift
import UIKit
import Flutter
import FirebaseCore
import FirebaseMessaging

@main
@objc class AppDelegate: FlutterAppDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    // Firebase는 Dart에서 초기화하므로 여기서는 제거
    GeneratedPluginRegistrant.register(with: self)

    // 푸시 알림 델리게이트 설정
    UNUserNotificationCenter.current().delegate = self

    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }
}
```

---

## Android 추가 설정

### build.gradle (app)

```groovy
// android/app/build.gradle
android {
    // ...
}

dependencies {
    // Crashlytics NDK 지원 (선택)
    implementation 'com.google.firebase:firebase-crashlytics-ndk'
}

// Crashlytics 플러그인
apply plugin: 'com.google.firebase.crashlytics'
```

### build.gradle (project)

```groovy
// android/build.gradle
buildscript {
    dependencies {
        classpath 'com.google.gms:google-services:4.4.2'
        classpath 'com.google.firebase:firebase-crashlytics-gradle:3.0.3'
    }
}
```

---

## Failure 타입

```dart
// lib/core/error/failures.dart
sealed class Failure {
  final String message;
  const Failure({required this.message});
}

class ServerFailure extends Failure {
  const ServerFailure({required super.message});
}

class AuthFailure extends Failure {
  const AuthFailure({required super.message});
}

class NotFoundFailure extends Failure {
  const NotFoundFailure({required super.message});
}

class CacheFailure extends Failure {
  const CacheFailure({required super.message});
}
```

---

## References

- `_references/RECENT-FLUTTER-CHANGES.md`
- `_references/ARCHITECTURE-PATTERN.md`
- `25-flavor/SKILL.md` (Flavor 통합)
