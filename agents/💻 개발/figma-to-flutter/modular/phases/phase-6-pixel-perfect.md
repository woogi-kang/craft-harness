---
name: "Phase 6: Pixel-Perfect Validation"
description: "Pixel-perfect verification with Flutter golden tests"
---

# Phase 6: Pixel-Perfect Validation

> Figma 디자인과 1:1 검증

---

## 실행 조건

- Phase 5 완료
- 모든 에셋 처리됨

---

## Step 6-1: 스크린샷 비교 준비

### Figma 스크린샷 생성

```typescript
// MCP 호출
get_screenshot({
  fileKey: "ABC123",
  nodeId: "123-456",
  format: "png",
  scale: 2
})
```

### Flutter 스크린샷 생성

```dart
// Integration test에서 스크린샷
import 'package:integration_test/integration_test.dart';

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('Screenshot test', (tester) async {
    await tester.pumpWidget(MyApp());
    await tester.pumpAndSettle();

    await binding.takeScreenshot('home_screen');
  });
}
```

---

## Step 6-2: 치수 검증

### 크기 매핑 테이블

| 요소 | Figma | Flutter | 일치 |
|------|-------|---------|------|
| Screen Width | 390px | 390.0 | O |
| Screen Height | 844px | 844.0 | O |
| AppBar Height | 56px | 56.0 | O |
| Card Width | 358px | 358.0 | O |
| Card Height | 120px | 120.0 | O |
| Button Height | 48px | 48.0 | O |
| Icon Size | 24px | 24.0 | O |

### 검증 코드

```dart
// 위젯 크기 검증 테스트
testWidgets('Button size matches Figma', (tester) async {
  await tester.pumpWidget(
    MaterialApp(
      home: Scaffold(
        body: AppButton(label: 'Test', onPressed: () {}),
      ),
    ),
  );

  final button = tester.widget<ElevatedButton>(find.byType(ElevatedButton));
  final size = tester.getSize(find.byType(ElevatedButton));

  expect(size.height, equals(48.0));
});
```

---

## Step 6-3: 색상 검증

### 색상 비교 테이블

| 요소 | Figma | Flutter | 일치 |
|------|-------|---------|------|
| Primary | #3B82F6 | 0xFF3B82F6 | O |
| Background | #FFFFFF | 0xFFFFFFFF | O |
| Text | #1F2937 | 0xFF1F2937 | O |
| Border | #E5E7EB | 0xFFE5E7EB | O |

### 색상 검증 테스트

```dart
testWidgets('Primary button uses correct color', (tester) async {
  await tester.pumpWidget(
    MaterialApp(
      theme: AppTheme.light,
      home: Scaffold(
        body: ElevatedButton(
          onPressed: () {},
          child: Text('Test'),
        ),
      ),
    ),
  );

  final button = tester.widget<ElevatedButton>(find.byType(ElevatedButton));
  final style = button.style;

  // 배경색 검증
  expect(
    style?.backgroundColor?.resolve({}),
    equals(AppColors.primary),
  );
});
```

---

## Step 6-4: 타이포그래피 검증

### 폰트 스타일 비교

| 스타일 | Figma | Flutter | 일치 |
|--------|-------|---------|------|
| H1 Size | 32px | 32.0 | O |
| H1 Weight | 700 | FontWeight.w700 | O |
| H1 Line Height | 1.25 | 1.25 | O |
| Body Size | 16px | 16.0 | O |
| Body Weight | 400 | FontWeight.w400 | O |

### 타이포그래피 검증 테스트

```dart
testWidgets('Heading style matches Figma', (tester) async {
  await tester.pumpWidget(
    MaterialApp(
      theme: AppTheme.light,
      home: Scaffold(
        body: Text(
          'Heading',
          style: AppTypography.headlineLarge,
        ),
      ),
    ),
  );

  final text = tester.widget<Text>(find.text('Heading'));
  final style = text.style!;

  expect(style.fontSize, equals(32.0));
  expect(style.fontWeight, equals(FontWeight.w700));
  expect(style.height, equals(1.25));
});
```

---

## Step 6-5: 간격 검증

### Padding/Margin 비교

| 요소 | Figma | Flutter | 일치 |
|------|-------|---------|------|
| Screen Padding | 16px | 16.0 | O |
| Section Gap | 24px | 24.0 | O |
| Card Padding | 16px | 16.0 | O |
| Item Gap | 12px | 12.0 | O |

### 간격 검증 테스트

```dart
testWidgets('Card has correct padding', (tester) async {
  await tester.pumpWidget(
    MaterialApp(
      home: Scaffold(
        body: FeatureCard(
          icon: Icons.star,
          title: 'Test',
          description: 'Description',
        ),
      ),
    ),
  );

  final container = tester.widget<Container>(
    find.ancestor(
      of: find.text('Test'),
      matching: find.byType(Container),
    ).first,
  );

  final padding = container.padding as EdgeInsets;
  expect(padding.left, equals(16.0));
  expect(padding.top, equals(16.0));
});
```

---

## Step 6-6: 시각적 회귀 테스트

### Golden Test 설정

```dart
// test/golden/home_screen_test.dart

import 'package:flutter_test/flutter_test.dart';
import 'package:golden_toolkit/golden_toolkit.dart';

void main() {
  testGoldens('HomePage golden test', (tester) async {
    final builder = DeviceBuilder()
      ..addScenario(
        widget: HomePage(),
        name: 'default',
      );

    await tester.pumpDeviceBuilder(builder);
    await screenMatchesGolden(tester, 'home_page');
  });
}
```

### Golden 파일 생성/비교

```bash
# Golden 파일 생성
flutter test --update-goldens

# Golden 테스트 실행
flutter test test/golden/
```

---

## Step 6-7: 플랫폼별 검증

### iOS 검증

```dart
testWidgets('iOS rendering', (tester) async {
  debugDefaultTargetPlatformOverride = TargetPlatform.iOS;

  await tester.pumpWidget(MyApp());
  await screenMatchesGolden(tester, 'home_ios');

  debugDefaultTargetPlatformOverride = null;
});
```

### Android 검증

```dart
testWidgets('Android rendering', (tester) async {
  debugDefaultTargetPlatformOverride = TargetPlatform.android;

  await tester.pumpWidget(MyApp());
  await screenMatchesGolden(tester, 'home_android');

  debugDefaultTargetPlatformOverride = null;
});
```

---

## Step 6-8: 정확도 계산

### 픽셀 차이 분석

```dart
import 'dart:ui' as ui;
import 'package:image/image.dart' as img;

Future<double> calculatePixelAccuracy(
  ui.Image figmaImage,
  ui.Image flutterImage,
) async {
  final figmaBytes = await figmaImage.toByteData();
  final flutterBytes = await flutterImage.toByteData();

  int matchingPixels = 0;
  int totalPixels = figmaImage.width * figmaImage.height;

  for (int i = 0; i < totalPixels * 4; i += 4) {
    final tolerance = 5; // RGB tolerance

    bool matches =
      (figmaBytes!.getUint8(i) - flutterBytes!.getUint8(i)).abs() <= tolerance &&
      (figmaBytes.getUint8(i + 1) - flutterBytes.getUint8(i + 1)).abs() <= tolerance &&
      (figmaBytes.getUint8(i + 2) - flutterBytes.getUint8(i + 2)).abs() <= tolerance;

    if (matches) matchingPixels++;
  }

  return (matchingPixels / totalPixels) * 100;
}
```

---

## 산출물

```markdown
# Pixel-Perfect Validation Report

## Overall Score: 97.5%

## Dimension Accuracy
| Element | Status | Accuracy |
|---------|--------|----------|
| Screen Size | Pass | 100% |
| AppBar | Pass | 100% |
| Cards | Pass | 100% |
| Buttons | Pass | 100% |
| Icons | Pass | 100% |

## Color Accuracy
| Element | Status | Delta E |
|---------|--------|---------|
| Primary | Pass | 0.0 |
| Background | Pass | 0.0 |
| Text | Pass | 0.0 |
| Border | Pass | 0.0 |

## Typography Accuracy
| Style | Status | Issues |
|-------|--------|--------|
| Heading | Pass | None |
| Body | Pass | None |
| Label | Pass | None |

## Spacing Accuracy
| Element | Status | Diff |
|---------|--------|------|
| Screen Padding | Pass | 0px |
| Section Gap | Pass | 0px |
| Card Padding | Pass | 0px |

## Issues Found
1. Minor: Icon alignment 1px off in NavBar
   - **Fix**: Adjusted container alignment

## Golden Tests
- home_page.png: Pass
- feature_card.png: Pass
- button_variants.png: Pass

## Final Status: APPROVED

## Next Phase
Phase 7: Responsive 진행 가능
```
