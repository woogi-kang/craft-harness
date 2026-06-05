---
name: flutter-patterns
description: Reusable Flutter widget patterns for Figma components
version: 1.0.0
progressive_disclosure:
  level_1_tokens: 50
  level_2_tokens: 5000
triggers:
  keywords: ["pattern", "widget", "button", "card", "section", "navigation", "responsive"]
  phases: ["phase:4", "phase:5"]
  agents: ["figma-to-flutter-pro"]
---

# Skill: Flutter Patterns

> 재사용 가능한 Flutter 위젯 패턴

---

## Overview

이 스킬은 Figma에서 추출된 컴포넌트를 Flutter 위젯으로 변환하는 패턴을 제공합니다.

---

## Button Patterns

### AppButton

```dart
import 'package:flutter/material.dart';
import 'package:my_app/core/theme/theme.dart';

enum AppButtonVariant { primary, secondary, outline, ghost, destructive }
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
    final theme = Theme.of(context);

    final height = switch (size) {
      AppButtonSize.sm => 36.0,
      AppButtonSize.md => 44.0,
      AppButtonSize.lg => 52.0,
    };

    final horizontalPadding = switch (size) {
      AppButtonSize.sm => 12.0,
      AppButtonSize.md => 16.0,
      AppButtonSize.lg => 24.0,
    };

    final textStyle = switch (size) {
      AppButtonSize.sm => AppTypography.labelSmall,
      AppButtonSize.md => AppTypography.labelMedium,
      AppButtonSize.lg => AppTypography.labelLarge,
    };

    final iconSize = switch (size) {
      AppButtonSize.sm => 16.0,
      AppButtonSize.md => 18.0,
      AppButtonSize.lg => 20.0,
    };

    Widget child = Row(
      mainAxisSize: isExpanded ? MainAxisSize.max : MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        if (isLoading) ...[
          SizedBox(
            width: iconSize,
            height: iconSize,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation(_getForegroundColor()),
            ),
          ),
          const SizedBox(width: 8),
        ] else if (leadingIcon != null) ...[
          Icon(leadingIcon, size: iconSize),
          const SizedBox(width: 8),
        ],
        Text(label, style: textStyle),
        if (trailingIcon != null && !isLoading) ...[
          const SizedBox(width: 8),
          Icon(trailingIcon, size: iconSize),
        ],
      ],
    );

    final style = _getButtonStyle(height, horizontalPadding);

    return switch (variant) {
      AppButtonVariant.primary ||
      AppButtonVariant.secondary ||
      AppButtonVariant.destructive => ElevatedButton(
          onPressed: isLoading ? null : onPressed,
          style: style,
          child: child,
        ),
      AppButtonVariant.outline => OutlinedButton(
          onPressed: isLoading ? null : onPressed,
          style: style,
          child: child,
        ),
      AppButtonVariant.ghost => TextButton(
          onPressed: isLoading ? null : onPressed,
          style: style,
          child: child,
        ),
    };
  }

  ButtonStyle _getButtonStyle(double height, double horizontalPadding) {
    final backgroundColor = switch (variant) {
      AppButtonVariant.primary => AppColors.primary,
      AppButtonVariant.secondary => AppColors.secondary,
      AppButtonVariant.destructive => AppColors.destructive,
      _ => Colors.transparent,
    };

    final foregroundColor = switch (variant) {
      AppButtonVariant.primary => AppColors.primaryForeground,
      AppButtonVariant.secondary => AppColors.secondaryForeground,
      AppButtonVariant.destructive => AppColors.destructiveForeground,
      AppButtonVariant.outline => AppColors.foreground,
      AppButtonVariant.ghost => AppColors.foreground,
    };

    final side = variant == AppButtonVariant.outline
        ? BorderSide(color: AppColors.border)
        : BorderSide.none;

    return ButtonStyle(
      backgroundColor: WidgetStatePropertyAll(backgroundColor),
      foregroundColor: WidgetStatePropertyAll(foregroundColor),
      minimumSize: WidgetStatePropertyAll(
        Size(isExpanded ? double.infinity : 0, height),
      ),
      padding: WidgetStatePropertyAll(
        EdgeInsets.symmetric(horizontal: horizontalPadding),
      ),
      shape: WidgetStatePropertyAll(
        RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
          side: side,
        ),
      ),
    );
  }

  Color _getForegroundColor() {
    return switch (variant) {
      AppButtonVariant.primary => AppColors.primaryForeground,
      AppButtonVariant.secondary => AppColors.secondaryForeground,
      AppButtonVariant.destructive => AppColors.destructiveForeground,
      _ => AppColors.foreground,
    };
  }
}
```

### IconButton Pattern

```dart
class AppIconButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback? onPressed;
  final double size;
  final Color? color;
  final Color? backgroundColor;

  const AppIconButton({
    super.key,
    required this.icon,
    this.onPressed,
    this.size = 44,
    this.color,
    this.backgroundColor,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: backgroundColor ?? Colors.transparent,
      borderRadius: BorderRadius.circular(size / 2),
      child: InkWell(
        onTap: onPressed,
        borderRadius: BorderRadius.circular(size / 2),
        child: SizedBox(
          width: size,
          height: size,
          child: Center(
            child: Icon(
              icon,
              size: size * 0.5,
              color: color ?? AppColors.foreground,
            ),
          ),
        ),
      ),
    );
  }
}
```

---

## Card Patterns

### Feature Card

```dart
class FeatureCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;
  final VoidCallback? onTap;

  const FeatureCard({
    super.key,
    required this.icon,
    required this.title,
    required this.description,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    // Use Material + InkWell for proper Material ripple effect
    return Material(
      color: Theme.of(context).colorScheme.surface,
      borderRadius: AppRadius.mdAll,
      child: InkWell(
        onTap: onTap,
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

### Product Card

```dart
class ProductCard extends StatelessWidget {
  final String imageUrl;
  final String title;
  final String price;
  final String? originalPrice;
  final VoidCallback? onTap;

  const ProductCard({
    super.key,
    required this.imageUrl,
    required this.title,
    required this.price,
    this.originalPrice,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    // Use Material + InkWell for proper Material ripple effect
    return Material(
      color: Theme.of(context).colorScheme.surface,
      borderRadius: AppRadius.mdAll,
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Container(
          decoration: BoxDecoration(
            borderRadius: AppRadius.mdAll,
            border: Border.all(color: AppColors.border),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ClipRRect(
                borderRadius: AppRadius.mdTop,
                child: AspectRatio(
                  aspectRatio: 1,
                  child: Image.network(
                    imageUrl,
                    fit: BoxFit.cover,
                  ),
                ),
              ),
              Padding(
                padding: EdgeInsets.all(AppSpacing.md),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: AppTypography.titleMedium,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: AppSpacing.sm),
                    Row(
                      children: [
                        Text(
                          price,
                          style: AppTypography.titleLarge.copyWith(
                            color: AppColors.primary,
                          ),
                        ),
                        if (originalPrice != null) ...[
                          const SizedBox(width: AppSpacing.sm),
                          Text(
                            originalPrice!,
                            style: AppTypography.bodySmall.copyWith(
                              color: AppColors.mutedForeground,
                              decoration: TextDecoration.lineThrough,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ],
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

---

## Section Patterns

### Hero Section

```dart
class HeroSection extends StatelessWidget {
  final String? badge;
  final String title;
  final String subtitle;
  final VoidCallback onPrimaryTap;
  final VoidCallback? onSecondaryTap;
  final Widget? image;

  const HeroSection({
    super.key,
    this.badge,
    required this.title,
    required this.subtitle,
    required this.onPrimaryTap,
    this.onSecondaryTap,
    this.image,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isWide = constraints.maxWidth >= 768;

        if (isWide) {
          return _buildWideLayout(context);
        }
        return _buildNarrowLayout(context);
      },
    );
  }

  Widget _buildWideLayout(BuildContext context) {
    return Padding(
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

  Widget _buildNarrowLayout(BuildContext context) {
    return Padding(
      padding: AppPadding.section,
      child: Column(
        children: [
          if (image != null) ...[
            image!,
            const SizedBox(height: AppSpacing.xl),
          ],
          _buildContent(context, TextAlign.center),
        ],
      ),
    );
  }

  Widget _buildContent(BuildContext context, TextAlign align) {
    final crossAlignment = align == TextAlign.center
        ? CrossAxisAlignment.center
        : CrossAxisAlignment.start;

    return Column(
      crossAxisAlignment: crossAlignment,
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
          const SizedBox(height: AppSpacing.lg),
        ],
        Text(
          title,
          style: AppTypography.headlineLarge,
          textAlign: align,
        ),
        const SizedBox(height: AppSpacing.lg),
        Text(
          subtitle,
          style: AppTypography.bodyLarge.copyWith(
            color: AppColors.mutedForeground,
          ),
          textAlign: align,
        ),
        const SizedBox(height: AppSpacing.xl),
        Wrap(
          spacing: AppSpacing.lg,
          runSpacing: AppSpacing.md,
          alignment: align == TextAlign.center
              ? WrapAlignment.center
              : WrapAlignment.start,
          children: [
            AppButton(
              label: 'Get Started',
              size: AppButtonSize.lg,
              onPressed: onPrimaryTap,
            ),
            if (onSecondaryTap != null)
              AppButton(
                label: 'Learn More',
                variant: AppButtonVariant.outline,
                size: AppButtonSize.lg,
                onPressed: onSecondaryTap,
              ),
          ],
        ),
      ],
    );
  }
}
```

### CTA Section

```dart
class CTASection extends StatelessWidget {
  final String title;
  final String subtitle;
  final VoidCallback onPrimaryTap;
  final VoidCallback? onSecondaryTap;
  final bool isPrimary;

  const CTASection({
    super.key,
    required this.title,
    required this.subtitle,
    required this.onPrimaryTap,
    this.onSecondaryTap,
    this.isPrimary = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: AppSpacing.screenPadding,
        vertical: AppSpacing.xxxl,
      ),
      color: isPrimary ? AppColors.primary : AppColors.muted,
      child: Column(
        children: [
          Text(
            title,
            style: AppTypography.headlineMedium.copyWith(
              color: isPrimary ? AppColors.primaryForeground : null,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: AppSpacing.lg),
          Text(
            subtitle,
            style: AppTypography.bodyLarge.copyWith(
              color: isPrimary
                  ? AppColors.primaryForeground.withValues(alpha: 0.9)
                  : AppColors.mutedForeground,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: AppSpacing.xl),
          Wrap(
            spacing: AppSpacing.lg,
            runSpacing: AppSpacing.md,
            alignment: WrapAlignment.center,
            children: [
              AppButton(
                label: 'Start Free Trial',
                variant: isPrimary
                    ? AppButtonVariant.secondary
                    : AppButtonVariant.primary,
                size: AppButtonSize.lg,
                onPressed: onPrimaryTap,
              ),
              if (onSecondaryTap != null)
                AppButton(
                  label: 'Contact Sales',
                  variant: AppButtonVariant.outline,
                  size: AppButtonSize.lg,
                  onPressed: onSecondaryTap,
                ),
            ],
          ),
        ],
      ),
    );
  }
}
```

---

## Navigation Patterns

### Adaptive Navigation

```dart
/// Adaptive navigation that switches between NavigationBar and NavigationRail
/// based on screen width.
///
/// Note: This widget is intentionally StatelessWidget because navigation state
/// (selectedIndex) is managed by the parent widget. The parent should be a
/// StatefulWidget that holds the selectedIndex state.
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
        if (constraints.maxWidth >= 900) {
          return _buildDesktop(context);
        }
        if (constraints.maxWidth >= 600) {
          return _buildTablet(context);
        }
        return _buildMobile(context);
      },
    );
  }

  Widget _buildDesktop(BuildContext context) {
    return Row(
      children: [
        NavigationRail(
          extended: true,
          selectedIndex: selectedIndex,
          onDestinationSelected: onDestinationSelected,
          destinations: _buildRailDestinations(),
        ),
        VerticalDivider(thickness: 1, width: 1),
        Expanded(child: child),
      ],
    );
  }

  Widget _buildTablet(BuildContext context) {
    return Row(
      children: [
        NavigationRail(
          selectedIndex: selectedIndex,
          onDestinationSelected: onDestinationSelected,
          destinations: _buildRailDestinations(),
        ),
        VerticalDivider(thickness: 1, width: 1),
        Expanded(child: child),
      ],
    );
  }

  Widget _buildMobile(BuildContext context) {
    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: selectedIndex,
        onDestinationSelected: onDestinationSelected,
        destinations: _buildBarDestinations(),
      ),
    );
  }

  List<NavigationRailDestination> _buildRailDestinations() => [
        NavigationRailDestination(
          icon: Icon(Icons.home_outlined),
          selectedIcon: Icon(Icons.home),
          label: Text('Home'),
        ),
        NavigationRailDestination(
          icon: Icon(Icons.explore_outlined),
          selectedIcon: Icon(Icons.explore),
          label: Text('Explore'),
        ),
        NavigationRailDestination(
          icon: Icon(Icons.favorite_outline),
          selectedIcon: Icon(Icons.favorite),
          label: Text('Favorites'),
        ),
        NavigationRailDestination(
          icon: Icon(Icons.person_outline),
          selectedIcon: Icon(Icons.person),
          label: Text('Profile'),
        ),
      ];

  List<NavigationDestination> _buildBarDestinations() => [
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
          icon: Icon(Icons.favorite_outline),
          selectedIcon: Icon(Icons.favorite),
          label: 'Favorites',
        ),
        NavigationDestination(
          icon: Icon(Icons.person_outline),
          selectedIcon: Icon(Icons.person),
          label: 'Profile',
        ),
      ];
}
```

---

## Form Patterns

### AppTextField

```dart
class AppTextField extends StatelessWidget {
  final String? label;
  final String? hint;
  final String? errorText;
  final TextEditingController? controller;
  final bool obscureText;
  final TextInputType? keyboardType;
  final IconData? prefixIcon;
  final Widget? suffixIcon;
  final ValueChanged<String>? onChanged;

  const AppTextField({
    super.key,
    this.label,
    this.hint,
    this.errorText,
    this.controller,
    this.obscureText = false,
    this.keyboardType,
    this.prefixIcon,
    this.suffixIcon,
    this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (label != null) ...[
          Text(
            label!,
            style: AppTypography.labelMedium,
          ),
          SizedBox(height: AppSpacing.sm),
        ],
        TextField(
          controller: controller,
          obscureText: obscureText,
          keyboardType: keyboardType,
          onChanged: onChanged,
          decoration: InputDecoration(
            hintText: hint,
            errorText: errorText,
            prefixIcon: prefixIcon != null ? Icon(prefixIcon) : null,
            suffixIcon: suffixIcon,
          ),
        ),
      ],
    );
  }
}
```

---

## Responsive Patterns

### ResponsiveBuilder

```dart
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

  static const double mobileBreakpoint = 600;
  static const double tabletBreakpoint = 900;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth >= tabletBreakpoint && desktop != null) {
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

### ResponsiveGrid

```dart
class ResponsiveGrid extends StatelessWidget {
  final List<Widget> children;
  final double spacing;
  final double minChildWidth;

  const ResponsiveGrid({
    super.key,
    required this.children,
    this.spacing = 16,
    this.minChildWidth = 280,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final columns = (constraints.maxWidth / minChildWidth)
            .floor()
            .clamp(1, 4);
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

## Footer Pattern

```dart
class AppFooter extends StatelessWidget {
  const AppFooter({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: AppSpacing.screenPadding,
        vertical: AppSpacing.xl,
      ),
      decoration: BoxDecoration(
        border: Border(top: BorderSide(color: AppColors.border)),
      ),
      child: ResponsiveBuilder(
        mobile: _buildMobile(),
        desktop: _buildDesktop(),
      ),
    );
  }

  Widget _buildMobile() {
    return Column(
      children: [
        _buildLogo(),
        SizedBox(height: AppSpacing.xl),
        _buildLinks(),
        SizedBox(height: AppSpacing.xl),
        _buildCopyright(),
      ],
    );
  }

  Widget _buildDesktop() {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(flex: 2, child: _buildLogo()),
        Expanded(flex: 3, child: _buildLinks()),
        Expanded(child: _buildCopyright()),
      ],
    );
  }

  Widget _buildLogo() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('AppName', style: AppTypography.titleLarge),
        SizedBox(height: AppSpacing.sm),
        Text(
          'Building the future.',
          style: AppTypography.bodyMedium.copyWith(
            color: AppColors.mutedForeground,
          ),
        ),
      ],
    );
  }

  Widget _buildLinks() {
    return Wrap(
      spacing: AppSpacing.xxxl,
      runSpacing: AppSpacing.xl,
      children: [
        _buildLinkColumn('Product', ['Features', 'Pricing', 'Security']),
        _buildLinkColumn('Company', ['About', 'Blog', 'Careers']),
        _buildLinkColumn('Support', ['Help', 'Contact', 'Status']),
      ],
    );
  }

  Widget _buildLinkColumn(String title, List<String> links) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: AppTypography.titleSmall),
        SizedBox(height: AppSpacing.md),
        ...links.map((link) => Padding(
              padding: EdgeInsets.only(bottom: AppSpacing.sm),
              child: Text(
                link,
                style: AppTypography.bodyMedium.copyWith(
                  color: AppColors.mutedForeground,
                ),
              ),
            )),
      ],
    );
  }

  Widget _buildCopyright() {
    return Text(
      '© ${DateTime.now().year} Company. All rights reserved.',
      style: AppTypography.bodySmall.copyWith(
        color: AppColors.mutedForeground,
      ),
    );
  }
}
```

---

## Checklist

```markdown
## Flutter Patterns Checklist

### Buttons
- [ ] AppButton with variants
- [ ] AppIconButton
- [ ] Loading states

### Cards
- [ ] FeatureCard
- [ ] ProductCard
- [ ] Interactive states

### Sections
- [ ] HeroSection (responsive)
- [ ] CTASection
- [ ] Feature grid

### Navigation
- [ ] AdaptiveNavigation
- [ ] AppBar patterns

### Forms
- [ ] AppTextField
- [ ] Form validation

### Layout
- [ ] ResponsiveBuilder
- [ ] ResponsiveGrid
- [ ] Footer
```
