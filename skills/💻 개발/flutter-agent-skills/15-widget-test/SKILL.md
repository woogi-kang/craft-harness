---
name: widget-test
description: |
  Widget Test를 작성합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Widget Test Skill

Widget Test를 작성합니다.

## Triggers

- "widget test", "위젯 테스트"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `widgetName` | ✅ | 테스트 대상 위젯 |
| `widgetPath` | ✅ | 대상 파일 경로 |

---

## Test Templates

Widget test는 위젯을 앱 전체 실행 없이 메모리에서 렌더링해 검증합니다. 독립 위젯은 상태별 렌더링, 사용자 이벤트, 작은/큰 제약 조건 분기를 함께 테스트합니다.

- Finder 검증은 `expect(find..., finds...)`를 유지한다.
- 콜백 호출 여부, ViewModel 입력값, 계산 결과처럼 일반 Dart 값은 `checks`를 선택적으로 사용한다.
- 반응형 위젯은 `SizedBox` 또는 `MediaQuery`로 작은/큰 제약 조건을 만들어 각각 검증한다.

### Atom Widget Test

```dart
// test/widget/core/design_system/atoms/app_button_test.dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:checks/checks.dart';

void main() {
  group('AppButton', () {
    testWidgets('renders label correctly', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppButton(
              label: 'Test Button',
              onPressed: () {},
            ),
          ),
        ),
      );

      expect(find.text('Test Button'), findsOneWidget);
    });

    testWidgets('calls onPressed when tapped', (tester) async {
      var pressed = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppButton(
              label: 'Test Button',
              onPressed: () => pressed = true,
            ),
          ),
        ),
      );

      await tester.tap(find.byType(AppButton));
      await tester.pump();

      check(pressed).isTrue();
    });

    testWidgets('shows loading indicator when isLoading', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppButton(
              label: 'Test Button',
              onPressed: () {},
              isLoading: true,
            ),
          ),
        ),
      );

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('is disabled when isDisabled', (tester) async {
      var pressed = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppButton(
              label: 'Test Button',
              onPressed: () => pressed = true,
              isDisabled: true,
            ),
          ),
        ),
      );

      await tester.tap(find.byType(AppButton));
      await tester.pump();

      check(pressed).isFalse();
    });
  });
}
```

### Constraints 분기 Widget Test

```dart
testWidgets('uses compact layout under 720px', (tester) async {
  await tester.pumpWidget(
    MaterialApp(
      home: SizedBox(
        width: 360,
        child: ProductPane(
          products: const [],
          onProductTap: (_) {},
        ),
      ),
    ),
  );

  expect(find.byType(ProductList), findsOneWidget);
  expect(find.byType(ProductGrid), findsNothing);
});

testWidgets('uses grid layout at 720px and wider', (tester) async {
  await tester.pumpWidget(
    MaterialApp(
      home: SizedBox(
        width: 840,
        child: ProductPane(
          products: const [],
          onProductTap: (_) {},
        ),
      ),
    ),
  );

  expect(find.byType(ProductGrid), findsOneWidget);
  expect(find.byType(ProductList), findsNothing);
});
```

### Page Widget Test

```dart
// test/widget/features/{feature}/presentation/pages/{feature}_list_page_test.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class Mock{Feature}ListNotifier extends _${Feature}ListNotifier with Mock {}

void main() {
  late Mock{Feature}ListNotifier mockNotifier;

  setUp(() {
    mockNotifier = Mock{Feature}ListNotifier();
  });

  Widget createWidget() {
    return ProviderScope(
      overrides: [
        {feature}ListNotifierProvider.overrideWith(() => mockNotifier),
      ],
      child: const MaterialApp(home: {Feature}ListPage()),
    );
  }

  group('{Feature}ListPage', () {
    testWidgets('shows loading indicator when loading', (tester) async {
      when(() => mockNotifier.build()).thenReturn(const AsyncLoading());

      await tester.pumpWidget(createWidget());

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('shows list when data loaded', (tester) async {
      final entities = [
        {Feature}Entity(id: '1', name: 'Item 1'),
        {Feature}Entity(id: '2', name: 'Item 2'),
      ];
      when(() => mockNotifier.build()).thenReturn(AsyncData(entities));

      await tester.pumpWidget(createWidget());

      expect(find.text('Item 1'), findsOneWidget);
      expect(find.text('Item 2'), findsOneWidget);
    });

    testWidgets('shows empty view when no data', (tester) async {
      when(() => mockNotifier.build()).thenReturn(const AsyncData([]));

      await tester.pumpWidget(createWidget());

      expect(find.text('데이터가 없습니다'), findsOneWidget);
    });

    testWidgets('shows error view on error', (tester) async {
      when(() => mockNotifier.build())
          .thenReturn(AsyncError('Error', StackTrace.current));

      await tester.pumpWidget(createWidget());

      expect(find.text('Error'), findsOneWidget);
      expect(find.text('다시 시도'), findsOneWidget);
    });
  });
}
```

### Form Widget Test

```dart
// test/widget/features/{feature}/presentation/pages/{feature}_form_page_test.dart
void main() {
  group('{Feature}FormPage', () {
    testWidgets('validates empty fields', (tester) async {
      await tester.pumpWidget(createWidget());

      await tester.tap(find.text('저장'));
      await tester.pump();

      expect(find.text('이름을 입력해주세요'), findsOneWidget);
    });

    testWidgets('submits form with valid data', (tester) async {
      when(() => mockNotifier.submit()).thenAnswer((_) async {});

      await tester.pumpWidget(createWidget());

      await tester.enterText(find.byType(TextFormField).first, 'Test Name');
      await tester.tap(find.text('저장'));
      await tester.pump();

      verify(() => mockNotifier.submit()).called(1);
    });
  });
}
```

---

## Test Utilities

### Test Helper

```dart
// test/helpers/test_helper.dart
Widget createTestWidget({
  required Widget child,
  List<Override> overrides = const [],
}) {
  return ProviderScope(
    overrides: overrides,
    child: MaterialApp(home: child),
  );
}
```

### Finder Utilities

```dart
// 텍스트로 찾기
find.text('Hello');

// 타입으로 찾기
find.byType(AppButton);

// 키로 찾기
find.byKey(const Key('submit_button'));

// 위젯 인스턴스로 찾기
find.byWidget(myWidget);

// 조건으로 찾기
find.byWidgetPredicate((widget) => widget is Text && widget.data == 'Hello');
```

---

## 테스트 실행

```bash
flutter test test/widget/
```

## References

- `_references/RECENT-FLUTTER-CHANGES.md`
- `_references/QUALITY-CODE-PATTERN.md`
- `_references/TEST-PATTERN.md`
