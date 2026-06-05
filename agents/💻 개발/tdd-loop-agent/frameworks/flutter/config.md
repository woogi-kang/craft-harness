# Flutter Framework Configuration

> **Version**: 2.0.0 | Flutter 3.24+ / Dart 3.5+ | Full Test Support

---

## Framework Detection

**Fingerprint files:**
- `pubspec.yaml` (required, contains `flutter:`)
- `lib/main.dart` (common)
- `.metadata` (Flutter-specific)

---

## Testing Pyramid Strategy

```
                    /\
                   /  \      E2E (Patrol)
                  /----\     5-10%
                 /      \
                /--------\   Golden Tests (Alchemist)
               /          \  10-15%
              /------------\
             /   Widget    \ 15-20%
            /----------------\
           /      Unit       \ 60-70%
          /--------------------\
```

| Test Type | Target % | Coverage Goal | Priority |
|-----------|----------|---------------|----------|
| **Unit** | 60-70% | 80%+ | High |
| **Widget** | 15-20% | 60%+ | Medium |
| **Golden** | 10-15% | Visual coverage | Medium |
| **E2E** | 5-10% | Critical flows | Low |

---

## Test Commands by Type

| Test Type | Command | Coverage |
|-----------|---------|----------|
| **All Tests** | `flutter test` | `flutter test --coverage` |
| **Unit Only** | `flutter test test/unit/` | `flutter test test/unit/ --coverage` |
| **Widget Only** | `flutter test test/widget/` | - |
| **Golden Only** | `flutter test test/golden/` | - |
| **Golden Update** | `flutter test --update-goldens` | - |
| **E2E (Patrol)** | `patrol test` | - |
| **E2E Specific** | `patrol test integration_test/{file}.dart` | - |
| **E2E Develop** | `patrol develop` | - |
| **Single File** | `flutter test {filePath}` | - |
| **By Name** | `flutter test --name "{testName}"` | - |
| **Verbose** | `flutter test --reporter expanded` | - |

---

## Dependencies

### Required (pubspec.yaml)

```yaml
dev_dependencies:
  flutter_test:
    sdk: flutter
  mocktail: ^1.0.4
```

### Full Testing Stack

```yaml
dev_dependencies:
  # Core
  flutter_test:
    sdk: flutter

  # Mocking
  mocktail: ^1.0.4

  # Golden Tests
  alchemist: ^0.13.0

  # E2E Tests
  patrol: ^4.1.0
  integration_test:
    sdk: flutter

  # Utilities
  fake_async: ^1.3.1
  clock: ^1.1.1
```

---

## 1. Unit Test Support

### Test Structure (AAA Pattern)

```dart
void main() {
  late SUT sut; // System Under Test
  late MockDependency mockDep;

  setUp(() {
    mockDep = MockDependency();
    sut = SUT(mockDep);
  });

  group('MethodName', () {
    test('should return X when Y', () async {
      // Arrange
      when(() => mockDep.method()).thenReturn(value);

      // Act
      final result = await sut.method();

      // Assert
      expect(result, expected);
      verify(() => mockDep.method()).called(1);
    });
  });
}
```

### Common Unit Test Errors

#### Error: MissingStubError

```
MissingStubError: 'login'
No stub was found for this method call: login(any, any)
```

**Fix (L1 - Auto-apply):**
```dart
when(() => mockRepo.login(any, any)).thenAnswer((_) async => result);
```

#### Error: Type Mismatch in Mock

```
type 'Null' is not a subtype of type 'Future<User>'
```

**Fix (L1 - Auto-apply):**
```dart
when(() => mock.method(any)).thenAnswer((_) async => User(...));
```

---

## 2. Widget Test Support

### Common Widget Test Errors

#### Error: Timer Pending

```
The following assertion was thrown during a test:
A Timer is still pending even after the widget tree was disposed.
```

**Fix (L1 - Auto-apply):**
```dart
await tester.pumpAndSettle();
```

#### Error: Async Test Completion

```
This test failed after it had already completed.
Make sure to use [expectAsync] or [completes] to prevent this.
```

**Fix (L2 - Apply with caution):**
```dart
// Change from:
test('async test', () {
  expect(future, completion(...));
});

// To:
test('async test', () async {
  expect(await future, equals(...));
});
```

#### Error: Provider Not Found

```
ProviderNotFoundException: Could not find the correct Provider<AuthNotifier>
```

**Fix (L2 - Apply with caution):**
```dart
await tester.pumpWidget(
  ProviderScope(
    overrides: [
      authProvider.overrideWith(() => MockAuthNotifier()),
    ],
    child: MaterialApp(home: TargetWidget()),
  ),
);
```

---

## 3. Golden Test Support (Alchemist)

### Setup Required

```dart
// test/flutter_test_config.dart
import 'dart:async';
import 'package:alchemist/alchemist.dart';

Future<void> testExecutable(FutureOr<void> Function() testMain) async {
  return AlchemistConfig.runWithConfig(
    config: AlchemistConfig(
      theme: ThemeData.light(),
      platformGoldensConfig: const PlatformGoldensConfig(enabled: true),
    ),
    run: testMain,
  );
}
```

### Golden Test Pattern

```dart
goldenTest(
  'renders correctly in all variants',
  fileName: 'widget_variants',
  builder: () => GoldenTestGroup(
    scenarioConstraints: const BoxConstraints(maxWidth: 200),
    children: [
      GoldenTestScenario(
        name: 'Variant A',
        child: Widget(variant: A),
      ),
      GoldenTestScenario(
        name: 'Variant B',
        child: Widget(variant: B),
      ),
    ],
  ),
);
```

### Theme/Device Matrix

```dart
goldenTest(
  'renders on different devices',
  fileName: 'widget_devices',
  builder: () => GoldenTestGroup(
    children: [
      GoldenTestScenario(
        name: 'iPhone SE',
        constraints: BoxConstraints(maxWidth: 375, maxHeight: 667),
        child: Widget(),
      ),
      GoldenTestScenario(
        name: 'iPhone 14 Pro',
        constraints: BoxConstraints(maxWidth: 393, maxHeight: 852),
        child: Widget(),
      ),
      GoldenTestScenario(
        name: 'iPad',
        constraints: BoxConstraints(maxWidth: 768, maxHeight: 1024),
        child: Widget(),
      ),
    ],
  ),
);
```

### Golden Test Errors

#### Error: Golden Mismatch

```
Golden file did not match.
Expected: goldens/widget.png
Actual: differs by 5.2%
```

**Decision Logic (L3 - Human decision required):**

```
IF error_percentage < 1%:
  → Likely font rendering difference, consider updating golden
IF error_percentage > 5%:
  → Significant visual regression, investigate code changes
IF new_widget:
  → Run: flutter test --update-goldens test/golden/{file}_test.dart
```

**Agent Action:**
1. Check git diff for recent visual changes
2. If intentional change → Suggest `--update-goldens`
3. If unintentional → Fix the regression
4. Document decision in work-log.md

---

## 4. E2E Test Support (Patrol)

### Setup Required

```yaml
# patrol.yaml
app_name: My App
android:
  package_name: com.example.app
ios:
  bundle_id: com.example.app
```

### Patrol Test Pattern

```dart
patrolTest(
  'User can login successfully',
  ($) async {
    await $.pumpWidgetAndSettle(const MyApp());

    // Find and interact
    await $(#emailInput).enterText('test@example.com');
    await $(#passwordInput).enterText('password');
    await $(#loginButton).tap();

    // Assert
    await $(#homePage).waitUntilVisible();
  },
);
```

### Patrol Selectors

```dart
// By text
await $('Login').tap();

// By Key
await $(#loginButton).tap();

// By Type
await $(ElevatedButton).tap();

// By Icon
await $(Icons.add).tap();

// Chaining
await $(Scaffold).$(AppBar).$('Title').tap();

// Index
await $('Item').at(0).tap();
```

### Native Interactions

```dart
// Permission dialogs
await $.native.grantPermissionWhenInUse();
await $.native.grantPermissionOnlyThisTime();
await $.native.denyPermission();

// Notifications
await $.native.waitForNotification(title: 'New Message');
await $.native.tapOnNotification(title: 'New Message');

// System dialogs
await $.native.tap(Selector(text: 'Allow'));
```

### E2E Test Errors

#### Error: Element Not Found

```
Finder found zero widgets with text "Login"
```

**Fix (L2):**
```dart
// Add wait before interaction
await $('Login').waitUntilVisible(timeout: Duration(seconds: 10));
await $('Login').tap();
```

#### Error: Test Timeout

```
TimeoutException after 0:00:30.000000: Test timed out
```

**Fix (L2):**
```dart
patrolTest(
  'Long running test',
  timeout: Timeout(Duration(minutes: 2)),
  ($) async {
    // ...
  },
);
```

#### Error: Native Interaction Failed

```
NativeAutomatorException: Could not find element
```

**Fix (L3 - May need manual check):**
- Check if app is in foreground
- Verify selector matches actual UI
- Consider platform-specific behavior

---

## Test Output Parsing

### Success Pattern

```
00:05 +10: All tests passed!
```
**Regex:** `(\d+):(\d+) \+(\d+): All tests passed!`

### Failure Pattern

```
00:03 +5 -2: Some tests failed.
```
**Regex:** `(\d+):(\d+) \+(\d+) -(\d+):`

### Skip Pattern

```
00:02 +3 ~1 -1: Some tests failed.
```
**Regex:** `\+(\d+) ~(\d+) -(\d+)`

### Patrol Output Pattern

```
patrol test
✓ User can login successfully (15.2s)
✗ User can checkout (timeout)
```

---

## Coverage Analysis

```bash
# Generate coverage
flutter test --coverage

# Parse percentage
lcov --summary coverage/lcov.info 2>&1 | grep "lines" | awk '{print $2}'

# Generate HTML report
genhtml coverage/lcov.info -o coverage/html
```

### Coverage Exclusions

```yaml
# Exclude generated files from coverage
coverage:
  exclude:
    - "**/*.g.dart"
    - "**/*.freezed.dart"
    - "**/generated/**"
    - "lib/main.dart"
```

---

## Directory Structure

```
project/
├── lib/
│   └── features/{feature}/
│       ├── data/
│       ├── domain/
│       └── presentation/
├── test/
│   ├── unit/
│   │   └── features/{feature}/
│   │       ├── data/
│   │       │   └── {name}_repository_test.dart
│   │       └── domain/
│   │           └── {name}_usecase_test.dart
│   ├── widget/
│   │   └── features/{feature}/
│   │       └── {name}_widget_test.dart
│   ├── golden/
│   │   └── features/{feature}/
│   │       └── {name}_golden_test.dart
│   ├── mocks/
│   │   └── mocks.dart
│   ├── fixtures/
│   │   └── fixtures.dart
│   └── flutter_test_config.dart
└── integration_test/
    ├── {feature}_flow_test.dart
    └── patrol_config.dart
```

---

## Auto-Fix Level Summary

| Error Type | Level | Action |
|------------|-------|--------|
| MissingStubError | L1 | Auto-apply mock |
| Timer pending | L1 | Add pumpAndSettle |
| Type mismatch | L1 | Fix return type |
| Async completion | L2 | Convert to async/await |
| Provider not found | L2 | Add ProviderScope |
| Element not found | L2 | Add waitUntilVisible |
| Test timeout | L2 | Increase timeout |
| Golden mismatch | L3 | Human decision |
| Native interaction | L3 | Manual verification |

---

## Build Verification

```bash
# Quick (analyze only)
flutter analyze

# Medium (compile check)
dart analyze lib/

# Full (build APK)
flutter build apk --debug
```

---

## Diagnostic Commands

```bash
# Environment
flutter doctor -v

# Clean rebuild
flutter clean && flutter pub get

# Regenerate code
dart run build_runner build --delete-conflicting-outputs

# Check dependencies
flutter pub outdated
```

---

Version: 2.0.0
Last Updated: 2025-01-28
Test Types: Unit, Widget, Golden (Alchemist), E2E (Patrol)
