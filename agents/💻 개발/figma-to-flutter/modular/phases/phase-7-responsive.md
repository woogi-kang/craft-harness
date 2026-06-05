---
name: "Phase 7: Responsive Validation"
description: "Responsive layout validation for Flutter"
---

# Phase 7: Responsive Validation

> 다양한 화면 크기에서 반응형 검증

---

## 실행 조건

- Phase 6 완료
- 기본 레이아웃 검증 완료

---

## Step 7-1: Flutter 브레이크포인트

### 권장 브레이크포인트

| Type | Width | 용도 |
|------|-------|------|
| Mobile | < 600dp | 스마트폰 |
| Tablet | 600-900dp | 태블릿 |
| Desktop | >= 900dp | 데스크톱/웹 |

### 디바이스 크기 상수

```dart
// lib/core/constants/breakpoints.dart

abstract class Breakpoints {
  static const double mobile = 600;
  static const double tablet = 900;
  static const double desktop = 1200;
}

extension BreakpointExtension on BoxConstraints {
  bool get isMobile => maxWidth < Breakpoints.mobile;
  bool get isTablet => maxWidth >= Breakpoints.mobile && maxWidth < Breakpoints.desktop;
  bool get isDesktop => maxWidth >= Breakpoints.desktop;  // Uses 1200, aligned with phase-4
}
```

---

## Step 7-2: 반응형 레이아웃 패턴

### ResponsiveBuilder

```dart
// lib/shared/widgets/responsive_builder.dart

class ResponsiveBuilder extends StatelessWidget {
  final Widget mobile;
  final Widget? tablet;
  final Widget? desktop;

  const ResponsiveBuilder({
    super.key,
    required this.mobile,
    this.tablet,
    this.desktop,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.isDesktop && desktop != null) {
          return desktop!;
        }
        if (constraints.isTablet && tablet != null) {
          return tablet!;
        }
        return mobile;
      },
    );
  }
}
```

### ResponsiveValue

```dart
// lib/core/utils/responsive.dart

T responsiveValue<T>(
  BuildContext context, {
  required T mobile,
  T? tablet,
  T? desktop,
}) {
  final width = MediaQuery.of(context).size.width;

  if (width >= Breakpoints.tablet && desktop != null) {
    return desktop;
  }
  if (width >= Breakpoints.mobile && tablet != null) {
    return tablet;
  }
  return mobile;
}

// 사용 예
final columns = responsiveValue(
  context,
  mobile: 1,
  tablet: 2,
  desktop: 3,
);
```

---

## Step 7-3: 반응형 그리드

### GridView 활용

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
        final columns = responsiveValue(
          context,
          mobile: 1,
          tablet: 2,
          desktop: 3,
        );

        return GridView.builder(
          shrinkWrap: true,
          physics: NeverScrollableScrollPhysics(),
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: columns,
            crossAxisSpacing: spacing,
            mainAxisSpacing: spacing,
            childAspectRatio: 1.2,
          ),
          itemCount: children.length,
          itemBuilder: (context, index) => children[index],
        );
      },
    );
  }
}
```

### Wrap 활용

```dart
class FlexibleGrid extends StatelessWidget {
  final List<Widget> children;
  final double spacing;
  final double minChildWidth;

  const FlexibleGrid({
    super.key,
    required this.children,
    this.spacing = 16,
    this.minChildWidth = 280,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final columns = (constraints.maxWidth / minChildWidth).floor().clamp(1, 4);
        final childWidth = (constraints.maxWidth - (spacing * (columns - 1))) / columns;

        return Wrap(
          spacing: spacing,
          runSpacing: spacing,
          children: children.map((child) {
            return SizedBox(
              width: childWidth,
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

## Step 7-4: 반응형 네비게이션

### NavigationRail (Tablet/Desktop)

```dart
/// Adaptive navigation that switches between NavigationBar and NavigationRail
/// based on screen width.
///
/// Note: This widget is intentionally StatelessWidget because navigation state
/// (selectedIndex) is managed by the parent widget. The parent should be a
/// StatefulWidget that holds the selectedIndex state.
///
/// Example usage:
/// ```dart
/// class MyHomePage extends StatefulWidget { ... }
/// class _MyHomePageState extends State<MyHomePage> {
///   int _selectedIndex = 0;
///   @override
///   Widget build(BuildContext context) {
///     return AdaptiveNavigation(
///       selectedIndex: _selectedIndex,
///       onDestinationSelected: (index) => setState(() => _selectedIndex = index),
///       child: _pages[_selectedIndex],
///     );
///   }
/// }
/// ```
class AdaptiveNavigation extends StatelessWidget {
  final int selectedIndex;
  final ValueChanged<int> onDestinationSelected;
  final Widget child;

  const AdaptiveNavigation({
    super.key,
    required this.selectedIndex,
    required this.onDestinationSelected,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.isDesktop) {
          return Row(
            children: [
              NavigationRail(
                extended: true,
                selectedIndex: selectedIndex,
                onDestinationSelected: onDestinationSelected,
                destinations: _buildRailDestinations(),
              ),
              Expanded(child: child),
            ],
          );
        }

        if (constraints.isTablet) {
          return Row(
            children: [
              NavigationRail(
                selectedIndex: selectedIndex,
                onDestinationSelected: onDestinationSelected,
                destinations: _buildRailDestinations(),
              ),
              Expanded(child: child),
            ],
          );
        }

        return Scaffold(
          body: child,
          bottomNavigationBar: NavigationBar(
            selectedIndex: selectedIndex,
            onDestinationSelected: onDestinationSelected,
            destinations: _buildBarDestinations(),
          ),
        );
      },
    );
  }

  List<NavigationRailDestination> _buildRailDestinations() => [
    NavigationRailDestination(
      icon: Icon(Icons.home_outlined),
      selectedIcon: Icon(Icons.home),
      label: Text('Home'),
    ),
    // ...
  ];

  List<NavigationDestination> _buildBarDestinations() => [
    NavigationDestination(
      icon: Icon(Icons.home_outlined),
      selectedIcon: Icon(Icons.home),
      label: 'Home',
    ),
    // ...
  ];
}
```

---

## Step 7-5: 반응형 Hero Section

```dart
class HeroSection extends StatelessWidget {
  final String title;
  final String subtitle;
  final Widget? image;
  final VoidCallback onPrimaryTap;
  final VoidCallback? onSecondaryTap;

  const HeroSection({
    super.key,
    required this.title,
    required this.subtitle,
    this.image,
    required this.onPrimaryTap,
    this.onSecondaryTap,
  });

  @override
  Widget build(BuildContext context) {
    return ResponsiveBuilder(
      mobile: _buildMobile(context),
      tablet: _buildTablet(context),
      desktop: _buildDesktop(context),
    );
  }

  Widget _buildMobile(BuildContext context) {
    return Padding(
      padding: AppPadding.section,
      child: Column(
        children: [
          if (image != null) ...[
            image!,
            SizedBox(height: AppSpacing.xl),
          ],
          _buildContent(context, TextAlign.center),
        ],
      ),
    );
  }

  Widget _buildTablet(BuildContext context) {
    return Padding(
      padding: AppPadding.section,
      child: Row(
        children: [
          Expanded(child: _buildContent(context, TextAlign.left)),
          if (image != null) ...[
            SizedBox(width: AppSpacing.xl),
            Expanded(child: image!),
          ],
        ],
      ),
    );
  }

  Widget _buildDesktop(BuildContext context) {
    return Container(
      constraints: BoxConstraints(maxWidth: 1200),
      padding: EdgeInsets.symmetric(
        horizontal: AppSpacing.xxxl,
        vertical: AppSpacing.xxxl,
      ),
      child: Row(
        children: [
          Expanded(child: _buildContent(context, TextAlign.left)),
          if (image != null) ...[
            SizedBox(width: AppSpacing.xxxl),
            Expanded(child: image!),
          ],
        ],
      ),
    );
  }

  Widget _buildContent(BuildContext context, TextAlign align) {
    return Column(
      crossAxisAlignment: align == TextAlign.center
          ? CrossAxisAlignment.center
          : CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: Theme.of(context).textTheme.headlineLarge,
          textAlign: align,
        ),
        SizedBox(height: AppSpacing.lg),
        Text(
          subtitle,
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
            color: AppColors.mutedForeground,
          ),
          textAlign: align,
        ),
        SizedBox(height: AppSpacing.xl),
        Wrap(
          spacing: AppSpacing.lg,
          runSpacing: AppSpacing.md,
          alignment: align == TextAlign.center
              ? WrapAlignment.center
              : WrapAlignment.start,
          children: [
            AppButton(
              label: 'Get Started',
              onPressed: onPrimaryTap,
            ),
            if (onSecondaryTap != null)
              AppButton(
                label: 'Learn More',
                variant: AppButtonVariant.outline,
                onPressed: onSecondaryTap,
              ),
          ],
        ),
      ],
    );
  }
}
```

---

## Step 7-6: 검증 체크리스트

### Mobile (< 600dp)

```markdown
## Mobile Checklist

### Layout
- [ ] 단일 컬럼 레이아웃
- [ ] 전체 너비 사용
- [ ] 적절한 패딩 (16dp)

### Navigation
- [ ] BottomNavigationBar 표시
- [ ] 터치 영역 48dp 이상
- [ ] FAB 접근 가능 (있는 경우)

### Typography
- [ ] 제목 크기 적절 (24-28sp)
- [ ] 본문 가독성 (14-16sp)

### Interactions
- [ ] 터치 타겟 48x48dp
- [ ] 스와이프 제스처 동작
```

### Tablet (600-900dp)

```markdown
## Tablet Checklist

### Layout
- [ ] 2컬럼 그리드
- [ ] NavigationRail 표시
- [ ] 적절한 여백

### Content
- [ ] 카드 2열 배치
- [ ] Hero 가로 레이아웃
- [ ] 텍스트 줄바꿈 확인
```

### Desktop (>= 900dp)

```markdown
## Desktop Checklist

### Layout
- [ ] 3-4컬럼 그리드
- [ ] Extended NavigationRail
- [ ] 최대 너비 제한 (1200dp)
- [ ] 중앙 정렬

### Interactions
- [ ] 호버 상태 표시
- [ ] 키보드 네비게이션
- [ ] 커서 변경
```

---

## Step 7-7: 테스트 디바이스

### 주요 테스트 크기

```dart
// test/responsive_test.dart

void main() {
  final testSizes = [
    Size(375, 667),   // iPhone SE
    Size(390, 844),   // iPhone 14
    Size(768, 1024),  // iPad
    Size(1024, 768),  // iPad Landscape
    Size(1440, 900),  // Desktop
  ];

  for (final size in testSizes) {
    testWidgets('Responsive layout at ${size.width}x${size.height}', (tester) async {
      tester.view.physicalSize = size;
      tester.view.devicePixelRatio = 1.0;

      await tester.pumpWidget(MyApp());
      await tester.pumpAndSettle();

      // 레이아웃 검증
      if (size.width < 600) {
        expect(find.byType(NavigationBar), findsOneWidget);
        expect(find.byType(NavigationRail), findsNothing);
      } else {
        expect(find.byType(NavigationRail), findsOneWidget);
        expect(find.byType(NavigationBar), findsNothing);
      }

      addTearDown(tester.view.resetPhysicalSize);
    });
  }
}
```

---

## 산출물

```markdown
# Responsive Validation Report

## Test Summary
| Breakpoint | Size | Status | Issues |
|------------|------|--------|--------|
| Mobile (375px) | iPhone SE | Pass | 0 |
| Mobile (390px) | iPhone 14 | Pass | 0 |
| Tablet (768px) | iPad | Pass | 1 minor |
| Desktop (1024px) | iPad Pro | Pass | 0 |
| Desktop (1440px) | Laptop | Pass | 0 |

## Component Results

### HeroSection
- Mobile: Pass (stacked layout)
- Tablet: Pass (side-by-side)
- Desktop: Pass (wide layout)

### FeatureGrid
- Mobile: Pass (1 column)
- Tablet: Pass (2 columns)
- Desktop: Pass (3 columns)

### Navigation
- Mobile: Pass (BottomNavigationBar)
- Tablet: Pass (NavigationRail)
- Desktop: Pass (Extended NavigationRail)

## Issues Found
1. Tablet: Grid item overflow at 768px
   - **Fix**: Adjusted aspect ratio

## Final Status: APPROVED

---

## Conversion Complete

### Summary
- Total Phases: 8 (0-7)
- Widgets Created: 12
- Assets Processed: 17
- Pixel-Perfect Score: 97.5%
- Responsive Score: 100%

### Files Created
- 12 widget files
- 6 theme files
- 1 constants file
- 17 asset files

### Next Steps
1. Code review
2. Accessibility audit (a11y)
3. Performance profiling
4. Deploy to TestFlight/Play Console
```
