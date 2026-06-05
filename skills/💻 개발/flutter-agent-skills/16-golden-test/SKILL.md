---
name: golden-test
description: |
  Golden Test (시각적 회귀 테스트)를 작성합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Golden Test Skill

Golden Test (시각적 회귀 테스트)를 작성합니다.

## Triggers

- "golden test", "스냅샷 테스트", "visual regression"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `widgetName` | ✅ | 테스트 대상 위젯 |
| `scenarios` | ✅ | 테스트 시나리오 (variants, sizes, themes) |

---

## 설정

### flutter_test_config.dart

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

---

## Test Templates

### Component Golden Test

```dart
// test/golden/core/design_system/atoms/app_button_golden_test.dart
import 'package:alchemist/alchemist.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('AppButton Golden Tests', () {
    goldenTest(
      'renders correctly in all variants',
      fileName: 'app_button_variants',
      builder: () => GoldenTestGroup(
        scenarioConstraints: const BoxConstraints(maxWidth: 200),
        children: [
          GoldenTestScenario(
            name: 'Primary',
            child: AppButton(label: 'Primary', onPressed: () {}),
          ),
          GoldenTestScenario(
            name: 'Secondary',
            child: AppButton(
              label: 'Secondary',
              onPressed: () {},
              variant: AppButtonVariant.secondary,
            ),
          ),
          GoldenTestScenario(
            name: 'Outline',
            child: AppButton(
              label: 'Outline',
              onPressed: () {},
              variant: AppButtonVariant.outline,
            ),
          ),
          GoldenTestScenario(
            name: 'Ghost',
            child: AppButton(
              label: 'Ghost',
              onPressed: () {},
              variant: AppButtonVariant.ghost,
            ),
          ),
        ],
      ),
    );

    goldenTest(
      'renders correctly in all sizes',
      fileName: 'app_button_sizes',
      builder: () => GoldenTestGroup(
        children: [
          GoldenTestScenario(
            name: 'Small',
            child: AppButton(label: 'Small', onPressed: () {}, size: AppButtonSize.sm),
          ),
          GoldenTestScenario(
            name: 'Medium',
            child: AppButton(label: 'Medium', onPressed: () {}, size: AppButtonSize.md),
          ),
          GoldenTestScenario(
            name: 'Large',
            child: AppButton(label: 'Large', onPressed: () {}, size: AppButtonSize.lg),
          ),
        ],
      ),
    );

    goldenTest(
      'renders correctly in different states',
      fileName: 'app_button_states',
      builder: () => GoldenTestGroup(
        children: [
          GoldenTestScenario(
            name: 'Normal',
            child: AppButton(label: 'Normal', onPressed: () {}),
          ),
          GoldenTestScenario(
            name: 'Loading',
            child: AppButton(label: 'Loading', onPressed: () {}, isLoading: true),
          ),
          GoldenTestScenario(
            name: 'Disabled',
            child: AppButton(label: 'Disabled', onPressed: () {}, isDisabled: true),
          ),
          GoldenTestScenario(
            name: 'With Icon',
            child: AppButton(label: 'With Icon', onPressed: () {}, icon: Icons.add),
          ),
        ],
      ),
    );
  });
}
```

### Page Golden Test

```dart
// test/golden/features/{feature}/presentation/pages/{feature}_page_golden_test.dart
void main() {
  group('{Feature}Page Golden Tests', () {
    goldenTest(
      'renders correctly in light and dark themes',
      fileName: '{feature}_page_themes',
      builder: () => GoldenTestGroup(
        children: [
          GoldenTestScenario(
            name: 'Light Theme',
            child: Theme(
              data: ThemeData.light(),
              child: const {Feature}Page(),
            ),
          ),
          GoldenTestScenario(
            name: 'Dark Theme',
            child: Theme(
              data: ThemeData.dark(),
              child: const {Feature}Page(),
            ),
          ),
        ],
      ),
    );

    goldenTest(
      'renders correctly on different devices',
      fileName: '{feature}_page_devices',
      builder: () => GoldenTestGroup(
        children: [
          GoldenTestScenario(
            name: 'iPhone SE',
            constraints: const BoxConstraints(maxWidth: 375, maxHeight: 667),
            child: const {Feature}Page(),
          ),
          GoldenTestScenario(
            name: 'iPhone 14 Pro',
            constraints: const BoxConstraints(maxWidth: 393, maxHeight: 852),
            child: const {Feature}Page(),
          ),
          GoldenTestScenario(
            name: 'iPad',
            constraints: const BoxConstraints(maxWidth: 768, maxHeight: 1024),
            child: const {Feature}Page(),
          ),
        ],
      ),
    );
  });
}
```

---

## 테스트 실행

```bash
# Golden 파일 업데이트 (새로운 기준 이미지 생성)
flutter test --update-goldens

# Golden 테스트 실행 (비교)
flutter test test/golden/

# 특정 파일 업데이트
flutter test --update-goldens test/golden/app_button_golden_test.dart
```

---

## CI 설정

```yaml
# .github/workflows/golden.yml
- name: Run golden tests
  run: flutter test test/golden/

- name: Upload golden failures
  if: failure()
  uses: actions/upload-artifact@v4
  with:
    name: golden-failures
    path: test/golden/failures/
```

## References

- `_references/RECENT-FLUTTER-CHANGES.md`
- `_references/TEST-PATTERN.md`
