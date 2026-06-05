---
name: logging
description: |
  Talker 로깅 시스템을 설정합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Logging Skill

Talker 로깅 시스템을 설정합니다.

## Triggers

- "로깅 설정", "talker", "디버깅"

---

## 설정

### Talker 초기화

```dart
// core/di/injection.dart
@module
abstract class TalkerModule {
  @singleton
  Talker talker() {
    return TalkerFlutter.init(
      settings: TalkerSettings(
        maxHistoryItems: 1000,
        useConsoleLogs: true,
        useHistory: true,
      ),
    );
  }
}
```

### Dio 로깅

```dart
// core/network/dio_client.dart
dio.interceptors.add(
  TalkerDioLogger(
    talker: talker,
    settings: const TalkerDioLoggerSettings(
      printRequestHeaders: true,
      printResponseHeaders: true,
      printResponseMessage: true,
      printRequestData: true,
      printResponseData: true,
      requestPen: AnsiPen()..cyan(),
      responsePen: AnsiPen()..green(),
      errorPen: AnsiPen()..red(),
    ),
  ),
);
```

### Riverpod 로깅

```dart
// main.dart
runApp(
  ProviderScope(
    observers: [
      TalkerRiverpodObserver(talker: getIt<Talker>()),
    ],
    child: const MyApp(),
  ),
);
```

---

## 사용법

### 로그 레벨

```dart
final talker = getIt<Talker>();

// Debug (개발용)
talker.debug('Debug message');

// Info (일반 정보)
talker.info('User logged in: ${user.id}');

// Warning (경고)
talker.warning('API rate limit approaching');

// Error (에러)
talker.error('Failed to load data', error, stackTrace);

// Critical (심각한 에러)
talker.critical('Database connection lost');
```

### 커스텀 로그

```dart
// 커스텀 로그 타입
class AnalyticsLog extends TalkerLog {
  AnalyticsLog(String message) : super(message);

  @override
  String get title => 'ANALYTICS';

  @override
  AnsiPen get pen => AnsiPen()..magenta();
}

talker.logCustom(AnalyticsLog('Button clicked: login'));
```

---

## UI 로그 뷰어

### TalkerScreen

```dart
// 개발 메뉴에서 호출
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => TalkerScreen(talker: getIt<Talker>()),
  ),
);

// 또는 라우트 추가
GoRoute(
  path: '/dev/logs',
  builder: (context, state) => TalkerScreen(talker: getIt<Talker>()),
),
```

### TalkerWrapper (개발용 오버레이)

```dart
// 개발 빌드에서만 활성화
MaterialApp(
  builder: (context, child) {
    if (kDebugMode) {
      return TalkerWrapper(
        talker: getIt<Talker>(),
        child: child!,
      );
    }
    return child!;
  },
);
```

---

## 로그 공유

```dart
// 로그 텍스트 추출
final logText = talker.history
    .map((log) => '[${log.title}] ${log.message}')
    .join('\n');

// share_plus로 공유
Share.share(logText);
```

---

## 프로덕션 설정

```dart
// 프로덕션에서는 콘솔 로그 비활성화
Talker talker() {
  return TalkerFlutter.init(
    settings: TalkerSettings(
      useConsoleLogs: kDebugMode, // 개발 모드에서만
      maxHistoryItems: kDebugMode ? 1000 : 100,
    ),
  );
}

// 프로덕션에서 에러만 Crashlytics로 전송
if (!kDebugMode) {
  talker.stream
      .where((log) => log is TalkerError)
      .listen((log) {
        FirebaseCrashlytics.instance.recordError(
          (log as TalkerError).error,
          log.stackTrace,
        );
      });
}
```
