---
name: "Phase 3: Widget Mapping"
description: "Figma components to Flutter widgets mapping"
---

# Phase 3: Widget Mapping

> Figma 컴포넌트를 Flutter 위젯으로 매핑

---

## 실행 조건

- Phase 2 완료
- ThemeData 토큰 생성됨

---

## Step 3-1: 레이아웃 매핑

### Figma Auto Layout → Flutter

| Figma | Flutter | 설명 |
|-------|---------|------|
| Auto Layout (Vertical) | Column | 세로 배치 |
| Auto Layout (Horizontal) | Row | 가로 배치 |
| Auto Layout (Wrap) | Wrap | 줄바꿈 |
| Fixed Position | Positioned (in Stack) | 절대 위치 |
| Fill Container | Expanded | 남은 공간 채움 |
| Hug Contents | 기본값 | 콘텐츠 크기 |

### Gap/Spacing 변환

```dart
// Figma: itemSpacing: 16
Column(
  children: [
    Widget1(),
    SizedBox(height: 16),  // or use spacing extension
    Widget2(),
  ],
)

// 또는 MainAxisAlignment 사용
Row(
  mainAxisAlignment: MainAxisAlignment.spaceBetween,
  children: [...],
)
```

### Padding 변환

```dart
// Figma: padding 16 24 16 24
Container(
  padding: EdgeInsets.symmetric(
    horizontal: 24,
    vertical: 16,
  ),
  child: ...,
)
```

---

## Step 3-2: 기본 위젯 매핑

### Text

| Figma Property | Flutter Property |
|----------------|------------------|
| fontSize | fontSize |
| fontWeight | fontWeight |
| fontFamily | fontFamily |
| lineHeight (%) | height (ratio) |
| letterSpacing (px) | letterSpacing |
| textAlign | textAlign |
| fill | color |

```dart
// Figma: Inter, 16px, 400, 150% line height
Text(
  'Hello World',
  style: TextStyle(
    fontFamily: 'Inter',
    fontSize: 16,
    fontWeight: FontWeight.w400,
    height: 1.5,  // 150% = 1.5
  ),
)
```

### Container/Frame

| Figma Property | Flutter Property |
|----------------|------------------|
| width | width |
| height | height |
| fills | color / gradient |
| cornerRadius | borderRadius |
| stroke | border |
| effects (shadow) | boxShadow |

```dart
// Figma Frame: 200x100, radius 12, fill #FFFFFF, shadow
Container(
  width: 200,
  height: 100,
  decoration: BoxDecoration(
    color: const Color(0xFFFFFFFF),
    borderRadius: BorderRadius.circular(12),
    boxShadow: const [
      BoxShadow(
        color: Color(0x1A000000), // black with 10% opacity
        blurRadius: 8,
        offset: Offset(0, 4),
      ),
    ],
  ),
)
```

### Image

| Figma Type | Flutter Widget |
|------------|----------------|
| Rectangle with Image Fill | Image.asset / Image.network |
| Vector | SvgPicture |
| Exported PNG | Image.asset |

```dart
// Image with aspect ratio
AspectRatio(
  aspectRatio: 16 / 9,
  child: Image.network(
    'https://example.com/image.jpg',
    fit: BoxFit.cover,
  ),
)

// SVG
SvgPicture.asset(
  'assets/icons/icon.svg',
  width: 24,
  height: 24,
  colorFilter: ColorFilter.mode(
    AppColors.primary,
    BlendMode.srcIn,
  ),
)
```

---

## Step 3-3: 컴포넌트 매핑

### Button

| Figma Variant | Flutter Widget |
|---------------|----------------|
| Primary / Filled | ElevatedButton |
| Secondary | ElevatedButton.styleFrom |
| Outline | OutlinedButton |
| Ghost / Text | TextButton |
| Icon | IconButton |

```dart
// Primary Button
ElevatedButton(
  onPressed: () {},
  style: ElevatedButton.styleFrom(
    backgroundColor: AppColors.primary,
    foregroundColor: AppColors.primaryForeground,
    minimumSize: Size(double.infinity, 48),
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(8),
    ),
  ),
  child: Text('Button'),
)

// Outline Button
OutlinedButton(
  onPressed: () {},
  style: OutlinedButton.styleFrom(
    side: BorderSide(color: AppColors.border),
    minimumSize: Size(double.infinity, 48),
  ),
  child: Text('Button'),
)
```

### Card

```dart
// Feature Card
class FeatureCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;

  const FeatureCard({
    super.key,
    required this.icon,
    required this.title,
    required this.description,
  });

  @override
  Widget build(BuildContext context) {
    // Use Material + InkWell for proper Material ripple effect
    return Material(
      color: Theme.of(context).colorScheme.surface,
      borderRadius: AppRadius.mdAll,
      child: InkWell(
        onTap: () {}, // Add onTap callback as needed
        borderRadius: AppRadius.mdAll,
        child: Container(
          padding: EdgeInsets.all(AppSpacing.lg),
          decoration: BoxDecoration(
            borderRadius: AppRadius.mdAll,
            border: Border.all(color: AppColors.border),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: AppColors.primary.withValues(alpha: 0.1),
                  borderRadius: AppRadius.smAll,
                ),
                child: Icon(
                  icon,
                  color: AppColors.primary,
                  size: 24,
                ),
              ),
              const SizedBox(height: AppSpacing.lg),
              Text(
                title,
                style: AppTypography.titleLarge,
              ),
              const SizedBox(height: AppSpacing.sm),
              Text(
                description,
                style: AppTypography.bodyMedium.copyWith(
                  color: AppColors.mutedForeground,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

### TextField

```dart
// Standard TextField
TextField(
  decoration: InputDecoration(
    labelText: 'Email',
    hintText: 'Enter your email',
    prefixIcon: Icon(Icons.email_outlined),
  ),
)

// Password Field
TextField(
  obscureText: true,
  decoration: InputDecoration(
    labelText: 'Password',
    hintText: 'Enter your password',
    prefixIcon: Icon(Icons.lock_outlined),
    suffixIcon: IconButton(
      icon: Icon(Icons.visibility_outlined),
      onPressed: () {},
    ),
  ),
)
```

---

## Step 3-4: 네비게이션 매핑

### AppBar

```dart
AppBar(
  title: Text('Home'),
  centerTitle: true,
  backgroundColor: AppColors.background,
  foregroundColor: AppColors.foreground,
  elevation: 0,
  actions: [
    IconButton(
      icon: Icon(Icons.notifications_outlined),
      onPressed: () {},
    ),
  ],
)
```

### BottomNavigationBar

```dart
NavigationBar(
  selectedIndex: currentIndex,
  onDestinationSelected: (index) => setState(() => currentIndex = index),
  destinations: [
    NavigationDestination(
      icon: Icon(Icons.home_outlined),
      selectedIcon: Icon(Icons.home),
      label: 'Home',
    ),
    NavigationDestination(
      icon: Icon(Icons.search_outlined),
      selectedIcon: Icon(Icons.search),
      label: 'Search',
    ),
    NavigationDestination(
      icon: Icon(Icons.person_outlined),
      selectedIcon: Icon(Icons.person),
      label: 'Profile',
    ),
  ],
)
```

---

## Step 3-5: 섹션 매핑

### Hero Section

```dart
class HeroSection extends StatelessWidget {
  final String? badge;
  final String title;
  final String subtitle;
  final VoidCallback onPrimaryTap;
  final VoidCallback? onSecondaryTap;

  const HeroSection({
    super.key,
    this.badge,
    required this.title,
    required this.subtitle,
    required this.onPrimaryTap,
    this.onSecondaryTap,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: AppPadding.section,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          if (badge != null) ...[
            Container(
              padding: EdgeInsets.symmetric(
                horizontal: AppSpacing.md,
                vertical: AppSpacing.xs,
              ),
              decoration: BoxDecoration(
                color: AppColors.primary.withValues(alpha: 0.1),
                borderRadius: AppRadius.circular,
              ),
              child: Text(
                badge!,
                style: AppTypography.labelMedium.copyWith(
                  color: AppColors.primary,
                ),
              ),
            ),
            SizedBox(height: AppSpacing.lg),
          ],
          Text(
            title,
            style: AppTypography.headlineLarge,
            textAlign: TextAlign.center,
          ),
          SizedBox(height: AppSpacing.lg),
          Text(
            subtitle,
            style: AppTypography.bodyLarge.copyWith(
              color: AppColors.mutedForeground,
            ),
            textAlign: TextAlign.center,
          ),
          SizedBox(height: AppSpacing.xl),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              ElevatedButton(
                onPressed: onPrimaryTap,
                child: Text('Get Started'),
              ),
              if (onSecondaryTap != null) ...[
                const SizedBox(width: AppSpacing.lg),
                OutlinedButton(
                  onPressed: onSecondaryTap,
                  child: Text('Learn More'),
                ),
              ],
            ],
          ),
        ],
      ),
    );
  }
}
```

---

## 산출물

```markdown
# Widget Mapping Report

## Layout Mappings
| Figma | Flutter | Count |
|-------|---------|-------|
| Auto Layout (V) | Column | 15 |
| Auto Layout (H) | Row | 12 |
| Fixed | Stack + Positioned | 3 |

## Component Mappings
| Component | Widget Class | File |
|-----------|--------------|------|
| PrimaryButton | ElevatedButton | buttons.dart |
| FeatureCard | FeatureCard | feature_card.dart |
| HeroSection | HeroSection | hero_section.dart |

## Mapping Coverage
- Layouts: 100%
- Components: 100%
- Styles: 100%

## Next Phase
Phase 4: Code Generate 진행 가능
```
