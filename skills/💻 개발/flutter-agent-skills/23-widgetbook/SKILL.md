---
name: widgetbook
description: |
  Widget Previewer와 Widgetbook을 사용한 컴포넌트 프리뷰 및 디자인 시스템 문서화를 구성합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Widgetbook Skill

Widget Previewer와 Widgetbook을 사용한 컴포넌트 프리뷰 및 디자인 시스템 문서화를 구성합니다.

## Triggers

- "widget preview", "widget previewer", "widgetbook", "컴포넌트 카탈로그", "storybook", "디자인 문서화"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectName` | ✅ | 프로젝트 이름 |
| `components` | ✅ | 문서화할 컴포넌트 목록 |

---

## 설정

### 도구 선택

| 도구 | 사용 시점 |
|------|-----------|
| Widget Previewer | Flutter 3.35+에서 개별 위젯 상태를 빠르게 실험할 때 |
| Widgetbook | Flutter 3.38+에서 디자인 시스템 카탈로그, 팀 공유, 다중 테마/디바이스/접근성 문서화가 필요할 때 |

Widget Previewer와 Widgetbook 모두 위젯이 순수해야 효과가 큽니다. 위젯은 생성자로 데이터를 받고 콜백으로 이벤트를 올려야 하며, 내부에서 Repository/API/DB를 직접 호출하지 않습니다.

### Widget Previewer 예시

```dart
import 'package:flutter/material.dart';
import 'package:flutter/widget_previews.dart';

@Preview(name: 'Primary')
Widget primaryButtonPreview() {
  return MaterialApp(
    home: Scaffold(
      body: Center(
        child: AppButton(
          label: '확인',
          onPressed: () {},
        ),
      ),
    ),
  );
}

@Preview(name: 'Loading')
Widget loadingButtonPreview() {
  return MaterialApp(
    home: Scaffold(
      body: Center(
        child: AppButton(
          label: '저장 중',
          isLoading: true,
          onPressed: () {},
        ),
      ),
    ),
  );
}
```

### pubspec.yaml

```yaml
dev_dependencies:
  widgetbook: ^3.23.0
  widgetbook_annotation: ^3.11.0
  widgetbook_generator: ^3.23.0
```

### 디렉토리 구조

```
widgetbook/
├── lib/
│   └── main.dart              # Widgetbook 앱 진입점
├── pubspec.yaml               # Widgetbook 전용 pubspec
└── test/
    └── widgetbook_test.dart   # 선택적 테스트
```

---

## Output Templates

### 1. Widgetbook 프로젝트 설정

```yaml
# widgetbook/pubspec.yaml
name: widgetbook_app
description: Component catalog for {project_name}

environment:
  sdk: '>=3.12.0 <4.0.0'
  flutter: '>=3.44.0'

dependencies:
  flutter:
    sdk: flutter
  {project_name}:
    path: ../

dev_dependencies:
  widgetbook: ^3.23.0
  widgetbook_annotation: ^3.11.0
  widgetbook_generator: ^3.23.0
```

### 2. Widgetbook Main

```dart
// widgetbook/lib/main.dart
import 'package:flutter/material.dart';
import 'package:widgetbook/widgetbook.dart';
import 'package:{project_name}/core/design_system/tokens/app_colors.dart';
import 'package:{project_name}/core/design_system/tokens/app_typography.dart';

// Use Cases
import 'use_cases/atoms/app_button_use_case.dart';
import 'use_cases/atoms/app_text_use_case.dart';
import 'use_cases/atoms/app_input_use_case.dart';
import 'use_cases/molecules/search_bar_use_case.dart';
import 'use_cases/organisms/login_form_use_case.dart';

void main() {
  runApp(const WidgetbookApp());
}

class WidgetbookApp extends StatelessWidget {
  const WidgetbookApp({super.key});

  @override
  Widget build(BuildContext context) {
    return Widgetbook.material(
      directories: [
        // Design Tokens
        WidgetbookFolder(
          name: 'Tokens',
          children: [
            WidgetbookLeafComponent(
              name: 'Colors',
              useCase: colorTokensUseCase(),
            ),
            WidgetbookLeafComponent(
              name: 'Typography',
              useCase: typographyTokensUseCase(),
            ),
            WidgetbookLeafComponent(
              name: 'Spacing',
              useCase: spacingTokensUseCase(),
            ),
          ],
        ),

        // Atoms
        WidgetbookFolder(
          name: 'Atoms',
          children: [
            appButtonComponent(),
            appTextComponent(),
            appInputComponent(),
            appIconComponent(),
          ],
        ),

        // Molecules
        WidgetbookFolder(
          name: 'Molecules',
          children: [
            searchBarComponent(),
            labeledInputComponent(),
            avatarWithNameComponent(),
          ],
        ),

        // Organisms
        WidgetbookFolder(
          name: 'Organisms',
          children: [
            loginFormComponent(),
            appHeaderComponent(),
            productCardComponent(),
          ],
        ),

        // Feature-specific Widgets
        WidgetbookFolder(
          name: 'Features',
          children: [
            WidgetbookFolder(
              name: 'Auth',
              children: [
                // auth feature specific widgets
              ],
            ),
            WidgetbookFolder(
              name: 'Product',
              children: [
                // product feature specific widgets
              ],
            ),
          ],
        ),
      ],
      addons: [
        // 테마 전환
        MaterialThemeAddon(
          themes: [
            WidgetbookTheme(
              name: 'Light',
              data: ThemeData.light().copyWith(
                colorScheme: ColorScheme.fromSeed(
                  seedColor: AppColors.primary,
                ),
              ),
            ),
            WidgetbookTheme(
              name: 'Dark',
              data: ThemeData.dark().copyWith(
                colorScheme: ColorScheme.fromSeed(
                  seedColor: AppColors.primary,
                  brightness: Brightness.dark,
                ),
              ),
            ),
          ],
        ),

        // 디바이스 프리뷰
        DeviceFrameAddon(
          devices: [
            Devices.ios.iPhone13,
            Devices.ios.iPhone13ProMax,
            Devices.android.samsungGalaxyS20,
            Devices.android.smallPhone,
          ],
        ),

        // 텍스트 스케일
        TextScaleAddon(
          scales: [0.85, 1.0, 1.15, 1.3, 2.0],
        ),

        // 언어 (l10n 연동)
        LocalizationAddon(
          locales: [
            const Locale('ko', 'KR'),
            const Locale('en', 'US'),
            const Locale('ja', 'JP'),
          ],
        ),

        // 접근성
        AccessibilityAddon(),

        // 그리드 오버레이
        GridAddon(100),
      ],
    );
  }
}
```

### 3. Atom Use Case 예시

```dart
// widgetbook/lib/use_cases/atoms/app_button_use_case.dart
import 'package:flutter/material.dart';
import 'package:widgetbook/widgetbook.dart';
import 'package:{project_name}/core/design_system/atoms/app_button.dart';

WidgetbookComponent appButtonComponent() {
  return WidgetbookComponent(
    name: 'AppButton',
    useCases: [
      // Primary Button
      WidgetbookUseCase(
        name: 'Primary',
        builder: (context) => AppButton(
          label: context.knobs.string(
            label: 'Label',
            initialValue: '확인',
          ),
          onPressed: context.knobs.boolean(
            label: 'Enabled',
            initialValue: true,
          )
              ? () {}
              : null,
          variant: ButtonVariant.primary,
          size: context.knobs.list(
            label: 'Size',
            options: ButtonSize.values,
            initialOption: ButtonSize.medium,
          ),
          isLoading: context.knobs.boolean(
            label: 'Loading',
            initialValue: false,
          ),
        ),
      ),

      // Secondary Button
      WidgetbookUseCase(
        name: 'Secondary',
        builder: (context) => AppButton(
          label: context.knobs.string(
            label: 'Label',
            initialValue: '취소',
          ),
          onPressed: () {},
          variant: ButtonVariant.secondary,
        ),
      ),

      // Outline Button
      WidgetbookUseCase(
        name: 'Outline',
        builder: (context) => AppButton(
          label: context.knobs.string(
            label: 'Label',
            initialValue: '더보기',
          ),
          onPressed: () {},
          variant: ButtonVariant.outline,
        ),
      ),

      // Text Button
      WidgetbookUseCase(
        name: 'Text',
        builder: (context) => AppButton(
          label: '건너뛰기',
          onPressed: () {},
          variant: ButtonVariant.text,
        ),
      ),

      // With Icon
      WidgetbookUseCase(
        name: 'With Icon',
        builder: (context) => AppButton(
          label: '다음',
          onPressed: () {},
          icon: Icons.arrow_forward,
          iconPosition: context.knobs.list(
            label: 'Icon Position',
            options: [IconPosition.left, IconPosition.right],
          ),
        ),
      ),
    ],
  );
}
```

### 4. Molecule Use Case 예시

```dart
// widgetbook/lib/use_cases/molecules/search_bar_use_case.dart
import 'package:flutter/material.dart';
import 'package:widgetbook/widgetbook.dart';
import 'package:{project_name}/core/design_system/molecules/search_bar.dart';

WidgetbookComponent searchBarComponent() {
  return WidgetbookComponent(
    name: 'SearchBar',
    useCases: [
      WidgetbookUseCase(
        name: 'Default',
        builder: (context) => SearchBar(
          hint: context.knobs.string(
            label: 'Hint',
            initialValue: '검색어를 입력하세요',
          ),
          onChanged: (value) {},
          onSubmitted: (value) {},
        ),
      ),
      WidgetbookUseCase(
        name: 'With Filter',
        builder: (context) => SearchBar(
          hint: '검색',
          onChanged: (value) {},
          showFilter: true,
          onFilterTap: () {},
        ),
      ),
      WidgetbookUseCase(
        name: 'Loading State',
        builder: (context) => SearchBar(
          hint: '검색',
          onChanged: (value) {},
          isLoading: true,
        ),
      ),
    ],
  );
}
```

### 5. Organism Use Case 예시

```dart
// widgetbook/lib/use_cases/organisms/login_form_use_case.dart
import 'package:flutter/material.dart';
import 'package:widgetbook/widgetbook.dart';
import 'package:{project_name}/core/design_system/organisms/login_form.dart';

WidgetbookComponent loginFormComponent() {
  return WidgetbookComponent(
    name: 'LoginForm',
    useCases: [
      WidgetbookUseCase(
        name: 'Default',
        builder: (context) => LoginForm(
          onSubmit: (email, password) {},
        ),
      ),
      WidgetbookUseCase(
        name: 'With Error',
        builder: (context) => LoginForm(
          onSubmit: (email, password) {},
          errorMessage: context.knobs.string(
            label: 'Error Message',
            initialValue: '이메일 또는 비밀번호가 올바르지 않습니다.',
          ),
        ),
      ),
      WidgetbookUseCase(
        name: 'Loading',
        builder: (context) => LoginForm(
          onSubmit: (email, password) {},
          isLoading: true,
        ),
      ),
    ],
  );
}
```

### 6. Token 시각화

```dart
// widgetbook/lib/use_cases/tokens/color_tokens_use_case.dart
import 'package:flutter/material.dart';
import 'package:widgetbook/widgetbook.dart';
import 'package:{project_name}/core/design_system/tokens/app_colors.dart';

WidgetbookUseCase colorTokensUseCase() {
  return WidgetbookUseCase(
    name: 'All Colors',
    builder: (context) => SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Wrap(
        spacing: 16,
        runSpacing: 16,
        children: [
          _ColorTile('Primary', AppColors.primary),
          _ColorTile('Secondary', AppColors.secondary),
          _ColorTile('Background', AppColors.background),
          _ColorTile('Surface', AppColors.surface),
          _ColorTile('Error', AppColors.error),
          _ColorTile('Success', AppColors.success),
          _ColorTile('Warning', AppColors.warning),
          _ColorTile('Info', AppColors.info),
          _ColorTile('Text Primary', AppColors.textPrimary),
          _ColorTile('Text Secondary', AppColors.textSecondary),
          _ColorTile('Disabled', AppColors.disabled),
          _ColorTile('Border', AppColors.border),
        ],
      ),
    ),
  );
}

class _ColorTile extends StatelessWidget {
  final String name;
  final Color color;

  const _ColorTile(this.name, this.color);

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.grey.shade300),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          name,
          style: const TextStyle(fontSize: 12),
        ),
        Text(
          '#${color.value.toRadixString(16).substring(2).toUpperCase()}',
          style: TextStyle(
            fontSize: 10,
            color: Colors.grey.shade600,
          ),
        ),
      ],
    );
  }
}
```

---

## 실행 명령어

```bash
# Widgetbook 로컬 실행
cd widgetbook
flutter run -d chrome

# macOS 실행 (더 나은 성능)
flutter run -d macos

# Hot Reload 지원
flutter run -d chrome --web-port=8080
```

---

## Cloud Hosting (Widgetbook Cloud)

```yaml
# .github/workflows/widgetbook.yml
name: Widgetbook

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.44.0'

      - name: Build Widgetbook
        run: |
          cd widgetbook
          flutter pub get
          flutter build web --release

      - name: Upload to Widgetbook Cloud
        uses: widgetbook/widgetbook-hosting@v1
        with:
          api-key: ${{ secrets.WIDGETBOOK_API_KEY }}
          path: widgetbook/build/web
```

---

## Knobs 타입

| Knob | 사용 |
|------|------|
| `context.knobs.string()` | 텍스트 입력 |
| `context.knobs.boolean()` | true/false 토글 |
| `context.knobs.list()` | enum/리스트 선택 |
| `context.knobs.double.slider()` | 숫자 슬라이더 |
| `context.knobs.color()` | 색상 선택 |

## References

- `_references/RECENT-FLUTTER-CHANGES.md`
- `_references/QUALITY-CODE-PATTERN.md`
- `_references/ATOMIC-DESIGN-PATTERN.md`
