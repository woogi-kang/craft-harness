---
name: "Phase 4: Code Generate"
description: "Flutter widget code generation from Figma design"
---

# Phase 4: Code Generate

> Flutter 위젯 코드 생성

---

## 실행 조건

- Phase 3 완료
- 위젯 매핑 완료

---

## Step 4-1: 코드 생성 원칙

### 네이밍 컨벤션

| Figma | Dart |
|-------|------|
| hero-section | HeroSection (class) |
| primary-button | PrimaryButton (class) |
| feature_card | FeatureCard (class) |
| Home Screen | home_screen.dart (file) |

### 파일 구조

```
lib/
├── features/
│   └── home/
│       └── presentation/
│           ├── pages/
│           │   └── home_page.dart
│           └── widgets/
│               ├── hero_section.dart
│               ├── feature_grid.dart
│               └── cta_section.dart
│
└── shared/
    └── widgets/
        ├── buttons/
        │   ├── primary_button.dart
        │   └── outline_button.dart
        ├── cards/
        │   └── feature_card.dart
        └── index.dart
```

---

## Step 4-1.5: 위젯 타입 선택 가이드

### State Management Decision Matrix

| Figma 컴포넌트 특성 | Flutter 위젯 타입 | 이유 |
|---------------------|-------------------|------|
| 정적 UI (텍스트, 이미지 표시) | StatelessWidget | 상태 없음 |
| 인터랙션 variants (hover, pressed, focused) | StatefulWidget | 로컬 UI 상태 |
| 애니메이션/전환 효과 | StatefulWidget + AnimationController | 애니메이션 상태 |
| 폼 입력 (TextField, Checkbox) | StatefulWidget 또는 FormField | 입력 상태 |
| 토글/스위치 | StatefulWidget | 로컬 on/off 상태 |
| 데이터 표시 (목록, 상세) | ConsumerWidget (Riverpod) | 공유 상태/비동기 |
| 선택 가능 목록 | StatefulWidget 또는 Riverpod | 선택 상태 |

### 선택 플로우차트

```
Figma 컴포넌트 분석
    │
    ├── 인터랙션 없음? ──────────────────────> StatelessWidget
    │
    ├── 로컬 상태만 필요? (hover, toggle)
    │       └── Yes ─────────────────────────> StatefulWidget
    │
    ├── 애니메이션 있음?
    │       └── Yes ─────────────────────────> StatefulWidget + Controller
    │
    ├── 공유 상태 필요? (다른 위젯과 데이터 공유)
    │       └── Yes ─────────────────────────> ConsumerWidget (Riverpod)
    │
    └── 비동기 데이터? (API 호출)
            └── Yes ─────────────────────────> ConsumerWidget + AsyncValue
```

### Riverpod 사용 시 (Optional)

```dart
// Riverpod가 설치된 경우
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ProductList extends ConsumerWidget {
  const ProductList({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final products = ref.watch(productsProvider);

    return products.when(
      data: (items) => ListView.builder(...),
      loading: () => const CircularProgressIndicator(),
      error: (e, st) => Text('Error: $e'),
    );
  }
}
```

---

## Step 4-2: 위젯 코드 템플릿

### StatelessWidget 템플릿

```dart
import 'package:flutter/material.dart';
import 'package:my_app/core/theme/theme.dart';

/// {{description}}
class {{WidgetName}} extends StatelessWidget {
  {{#props}}
  final {{type}} {{name}};
  {{/props}}

  const {{WidgetName}}({
    super.key,
    {{#props}}
    {{#required}}required {{/required}}this.{{name}},
    {{/props}}
  });

  @override
  Widget build(BuildContext context) {
    return {{content}};
  }
}
```

### StatefulWidget 템플릿

```dart
import 'package:flutter/material.dart';
import 'package:my_app/core/theme/theme.dart';

/// {{description}}
class {{WidgetName}} extends StatefulWidget {
  {{#props}}
  final {{type}} {{name}};
  {{/props}}

  const {{WidgetName}}({
    super.key,
    {{#props}}
    {{#required}}required {{/required}}this.{{name}},
    {{/props}}
  });

  @override
  State<{{WidgetName}}> createState() => _{{WidgetName}}State();
}

class _{{WidgetName}}State extends State<{{WidgetName}}> {
  {{#state}}
  {{type}} {{name}} = {{initial}};
  {{/state}}

  @override
  Widget build(BuildContext context) {
    return {{content}};
  }
}
```

---

## Step 4-3: 페이지 생성

### 페이지 구조

```dart
// lib/features/home/presentation/pages/home_page.dart

import 'package:flutter/material.dart';
import '../widgets/hero_section.dart';
import '../widgets/feature_grid.dart';
import '../widgets/cta_section.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Home'),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          child: Column(
            children: [
              HeroSection(
                title: 'Build faster with AI',
                subtitle: 'Transform your designs into production-ready code.',
                onPrimaryTap: () {},
                onSecondaryTap: () {},
              ),
              FeatureGrid(
                features: [
                  Feature(
                    icon: Icons.flash_on,
                    title: 'Fast',
                    description: 'Lightning fast performance',
                  ),
                  Feature(
                    icon: Icons.security,
                    title: 'Secure',
                    description: 'Enterprise-grade security',
                  ),
                  Feature(
                    icon: Icons.code,
                    title: 'Clean Code',
                    description: 'Well-structured codebase',
                  ),
                ],
              ),
              CTASection(
                title: 'Ready to get started?',
                subtitle: 'Join thousands of developers.',
                onTap: () {},
              ),
            ],
          ),
        ),
      ),
      bottomNavigationBar: NavigationBar(
        destinations: [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.explore_outlined),
            selectedIcon: Icon(Icons.explore),
            label: 'Explore',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outlined),
            selectedIcon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}
```

---

## Step 4-4: 공통 위젯 생성

### Button Variants

```dart
// lib/shared/widgets/buttons/app_button.dart

import 'package:flutter/material.dart';
import 'package:my_app/core/theme/theme.dart';

enum AppButtonVariant { primary, secondary, outline, ghost }
enum AppButtonSize { sm, md, lg }

class AppButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;
  final AppButtonVariant variant;
  final AppButtonSize size;
  final IconData? leadingIcon;
  final IconData? trailingIcon;
  final bool isLoading;
  final bool isExpanded;

  const AppButton({
    super.key,
    required this.label,
    this.onPressed,
    this.variant = AppButtonVariant.primary,
    this.size = AppButtonSize.md,
    this.leadingIcon,
    this.trailingIcon,
    this.isLoading = false,
    this.isExpanded = false,
  });

  @override
  Widget build(BuildContext context) {
    final height = switch (size) {
      AppButtonSize.sm => 36.0,
      AppButtonSize.md => 44.0,
      AppButtonSize.lg => 52.0,
    };

    final padding = switch (size) {
      AppButtonSize.sm => EdgeInsets.symmetric(horizontal: 12),
      AppButtonSize.md => EdgeInsets.symmetric(horizontal: 16),
      AppButtonSize.lg => EdgeInsets.symmetric(horizontal: 24),
    };

    final textStyle = switch (size) {
      AppButtonSize.sm => AppTypography.labelSmall,
      AppButtonSize.md => AppTypography.labelMedium,
      AppButtonSize.lg => AppTypography.labelLarge,
    };

    Widget child = Row(
      mainAxisSize: isExpanded ? MainAxisSize.max : MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        if (isLoading) ...[
          SizedBox(
            width: 16,
            height: 16,
            child: CircularProgressIndicator(strokeWidth: 2),
          ),
          SizedBox(width: 8),
        ] else if (leadingIcon != null) ...[
          Icon(leadingIcon, size: 18),
          SizedBox(width: 8),
        ],
        Text(label, style: textStyle),
        if (trailingIcon != null && !isLoading) ...[
          SizedBox(width: 8),
          Icon(trailingIcon, size: 18),
        ],
      ],
    );

    return switch (variant) {
      AppButtonVariant.primary => ElevatedButton(
          onPressed: isLoading ? null : onPressed,
          style: ElevatedButton.styleFrom(
            minimumSize: Size(isExpanded ? double.infinity : 0, height),
            padding: padding,
          ),
          child: child,
        ),
      AppButtonVariant.secondary => ElevatedButton(
          onPressed: isLoading ? null : onPressed,
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.secondary,
            foregroundColor: AppColors.secondaryForeground,
            minimumSize: Size(isExpanded ? double.infinity : 0, height),
            padding: padding,
          ),
          child: child,
        ),
      AppButtonVariant.outline => OutlinedButton(
          onPressed: isLoading ? null : onPressed,
          style: OutlinedButton.styleFrom(
            minimumSize: Size(isExpanded ? double.infinity : 0, height),
            padding: padding,
          ),
          child: child,
        ),
      AppButtonVariant.ghost => TextButton(
          onPressed: isLoading ? null : onPressed,
          style: TextButton.styleFrom(
            minimumSize: Size(isExpanded ? double.infinity : 0, height),
            padding: padding,
          ),
          child: child,
        ),
    };
  }
}
```

---

## Step 4-5: 반응형 레이아웃

### LayoutBuilder 활용

```dart
class ResponsiveLayout extends StatelessWidget {
  final Widget mobile;
  final Widget? tablet;
  final Widget? desktop;

  const ResponsiveLayout({
    super.key,
    required this.mobile,
    this.tablet,
    this.desktop,
  });

  // Consistent breakpoints across the app (aligned with phase-7)
  static const double mobileBreakpoint = 600;
  static const double tabletBreakpoint = 900;
  static const double desktopBreakpoint = 1200;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth >= desktopBreakpoint && desktop != null) {
          return desktop!;
        }
        if (constraints.maxWidth >= mobileBreakpoint && tablet != null) {
          return tablet!;
        }
        return mobile;
      },
    );
  }
}
```

### 반응형 그리드

```dart
class ResponsiveGrid extends StatelessWidget {
  final List<Widget> children;
  final double spacing;

  const ResponsiveGrid({
    super.key,
    required this.children,
    this.spacing = 16,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final columns = switch (constraints.maxWidth) {
          >= 900 => 3,
          >= 600 => 2,
          _ => 1,
        };

        return Wrap(
          spacing: spacing,
          runSpacing: spacing,
          children: children.map((child) {
            return SizedBox(
              width: (constraints.maxWidth - (spacing * (columns - 1))) / columns,
              child: child,
            );
          }).toList(),
        );
      },
    );
  }
}
```

---

## Step 4-6: 코드 품질 검증

### Dart Analysis

```bash
# 코드 분석 실행
dart analyze lib/

# 포맷팅
dart format lib/

# 린트 검사
flutter analyze
```

### 생성 코드 체크리스트

```markdown
## Code Quality Checklist

### Structure
- [ ] const 생성자 사용
- [ ] super.key 파라미터 포함
- [ ] 불변 위젯 (StatelessWidget 선호)

### Naming
- [ ] UpperCamelCase 클래스명
- [ ] lowerCamelCase 변수/메서드명
- [ ] snake_case 파일명

### Documentation
- [ ] 클래스 설명 주석
- [ ] 복잡한 로직 주석

### Theme
- [ ] 하드코딩 색상 없음
- [ ] AppColors 사용
- [ ] AppTypography 사용
- [ ] AppSpacing 사용
```

---

## 산출물

```markdown
# Code Generate Report

## Files Created
| File | Type | Lines |
|------|------|-------|
| home_page.dart | Page | 85 |
| hero_section.dart | Widget | 62 |
| feature_grid.dart | Widget | 48 |
| cta_section.dart | Widget | 45 |
| app_button.dart | Widget | 98 |

## Code Analysis
- Dart Analyze: No issues
- Flutter Lint: Passed
- Format: Applied

## Widget Tree
```
HomePage
├── AppBar
├── SingleChildScrollView
│   └── Column
│       ├── HeroSection
│       ├── FeatureGrid
│       │   └── ResponsiveGrid
│       │       └── FeatureCard (x3)
│       └── CTASection
└── NavigationBar
```

## Next Phase
Phase 5: Asset Process 진행 가능
```
