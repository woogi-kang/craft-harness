---
name: flutter-tokens
description: Figma design tokens to Flutter ThemeData conversion
version: 1.0.0
progressive_disclosure:
  level_1_tokens: 50
  level_2_tokens: 3500
triggers:
  keywords: ["token", "color", "spacing", "typography", "theme", "ThemeData"]
  phases: ["phase:2"]
  agents: ["figma-to-flutter-pro"]
---

# Skill: Flutter Tokens

> Figma 디자인 토큰을 Flutter ThemeData로 변환

---

## Overview

이 스킬은 Figma의 디자인 토큰(Variables)을 추출하여 Flutter의 ThemeData와 상수 클래스로 변환합니다.

---

## Token Types

| Figma Type | Dart Type | Output |
|------------|-----------|--------|
| COLOR | Color | app_colors.dart |
| FLOAT | double | app_spacing.dart |
| STRING | String | app_typography.dart |
| BOOLEAN | bool | - |
| ALIAS | Reference | 참조 |

---

## Extraction Workflow

### Step 1: Get Variable Definitions

```typescript
// MCP Call
get_variable_defs({
  fileKey: "ABC123"
})
```

### Step 2: Token Classification

```dart
class TokenCollection {
  final List<ColorToken> colors;
  final List<SpacingToken> spacing;
  final List<TypographyToken> typography;
  final List<RadiusToken> radius;
  final List<ShadowToken> shadows;
}
```

### Step 3: Generate Dart Files

---

## Color Tokens

### Figma → Flutter Color Conversion

```dart
// lib/core/theme/app_colors.dart

import 'package:flutter/material.dart';

/// App color palette extracted from Figma design tokens
abstract class AppColors {
  // Primary
  static const Color primary = Color(0xFF3B82F6);
  static const Color primaryForeground = Color(0xFFFFFFFF);

  // Secondary
  static const Color secondary = Color(0xFF6B7280);
  static const Color secondaryForeground = Color(0xFFFFFFFF);

  // Background
  static const Color background = Color(0xFFFFFFFF);
  static const Color foreground = Color(0xFF1F2937);

  // Surface
  static const Color surface = Color(0xFFF9FAFB);
  static const Color surfaceForeground = Color(0xFF1F2937);

  // Muted
  static const Color muted = Color(0xFFF3F4F6);
  static const Color mutedForeground = Color(0xFF6B7280);

  // Border
  static const Color border = Color(0xFFE5E7EB);

  // Destructive
  static const Color destructive = Color(0xFFEF4444);
  static const Color destructiveForeground = Color(0xFFFFFFFF);

  // Success
  static const Color success = Color(0xFF22C55E);
  static const Color successForeground = Color(0xFFFFFFFF);

  // Warning
  static const Color warning = Color(0xFFF59E0B);
  static const Color warningForeground = Color(0xFF1F2937);

  // Info
  static const Color info = Color(0xFF3B82F6);
  static const Color infoForeground = Color(0xFFFFFFFF);
}

/// Dark theme color palette
abstract class AppColorsDark {
  static const Color primary = Color(0xFF60A5FA);
  static const Color primaryForeground = Color(0xFF1F2937);

  static const Color secondary = Color(0xFF9CA3AF);
  static const Color secondaryForeground = Color(0xFF1F2937);

  static const Color background = Color(0xFF1F2937);
  static const Color foreground = Color(0xFFF9FAFB);

  static const Color surface = Color(0xFF374151);
  static const Color surfaceForeground = Color(0xFFF9FAFB);

  static const Color muted = Color(0xFF4B5563);
  static const Color mutedForeground = Color(0xFF9CA3AF);

  static const Color border = Color(0xFF4B5563);

  static const Color destructive = Color(0xFFF87171);
  static const Color destructiveForeground = Color(0xFF1F2937);
}
```

### Hex to Flutter Color Conversion

```dart
/// Convert hex string to Flutter Color
Color hexToColor(String hex) {
  hex = hex.replaceFirst('#', '');
  if (hex.length == 6) {
    hex = 'FF$hex'; // Add alpha
  }
  return Color(int.parse(hex, radix: 16));
}

/// Validate color format
bool validateColorToken(String value) {
  return RegExp(r'^#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?$').hasMatch(value) ||
         value.startsWith('rgba(') ||
         value.startsWith('hsla(');
}
```

---

## Spacing Tokens

### Figma px → Flutter double

```dart
// lib/core/theme/app_spacing.dart

/// Spacing constants extracted from Figma
abstract class AppSpacing {
  // Base scale
  static const double xs = 4.0;    // 4px
  static const double sm = 8.0;    // 8px
  static const double md = 12.0;   // 12px
  static const double lg = 16.0;   // 16px
  static const double xl = 24.0;   // 24px
  static const double xxl = 32.0;  // 32px
  static const double xxxl = 48.0; // 48px

  // Numeric scale (Tailwind-like)
  static const double s0 = 0.0;
  static const double s1 = 4.0;
  static const double s2 = 8.0;
  static const double s3 = 12.0;
  static const double s4 = 16.0;
  static const double s5 = 20.0;
  static const double s6 = 24.0;
  static const double s7 = 28.0;
  static const double s8 = 32.0;
  static const double s9 = 36.0;
  static const double s10 = 40.0;
  static const double s11 = 44.0;
  static const double s12 = 48.0;
  static const double s14 = 56.0;
  static const double s16 = 64.0;
  static const double s20 = 80.0;
  static const double s24 = 96.0;

  // Semantic spacing
  static const double screenPadding = 16.0;
  static const double cardPadding = 16.0;
  static const double sectionGap = 24.0;
  static const double itemGap = 12.0;
}

/// Common EdgeInsets presets
abstract class AppPadding {
  static const EdgeInsets screen = EdgeInsets.symmetric(
    horizontal: AppSpacing.screenPadding,
  );

  static const EdgeInsets screenAll = EdgeInsets.all(
    AppSpacing.screenPadding,
  );

  static const EdgeInsets card = EdgeInsets.all(AppSpacing.cardPadding);

  static const EdgeInsets section = EdgeInsets.symmetric(
    vertical: AppSpacing.sectionGap,
    horizontal: AppSpacing.screenPadding,
  );

  static const EdgeInsets buttonPadding = EdgeInsets.symmetric(
    horizontal: AppSpacing.lg,
    vertical: AppSpacing.md,
  );
}
```

---

## Typography Tokens

### Figma → Flutter TextStyle

```dart
// lib/core/theme/app_typography.dart

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Typography styles extracted from Figma
abstract class AppTypography {
  // Null-safe font family with fallback to system font
  static String get _fontFamily => GoogleFonts.inter().fontFamily ?? 'Inter';

  // Display styles
  static TextStyle get displayLarge => TextStyle(
    fontFamily: _fontFamily,
    fontSize: 48,
    fontWeight: FontWeight.w700,
    height: 1.2,
    letterSpacing: -0.5,
  );

  static TextStyle get displayMedium => TextStyle(
    fontFamily: _fontFamily,
    fontSize: 40,
    fontWeight: FontWeight.w700,
    height: 1.2,
    letterSpacing: -0.25,
  );

  static TextStyle get displaySmall => TextStyle(
    fontFamily: _fontFamily,
    fontSize: 36,
    fontWeight: FontWeight.w700,
    height: 1.2,
  );

  // Headline styles
  static TextStyle get headlineLarge => TextStyle(
    fontFamily: _fontFamily,
    fontSize: 32,
    fontWeight: FontWeight.w700,
    height: 1.25,
  );

  static TextStyle get headlineMedium => TextStyle(
    fontFamily: _fontFamily,
    fontSize: 24,
    fontWeight: FontWeight.w600,
    height: 1.3,
  );

  static TextStyle get headlineSmall => TextStyle(
    fontFamily: _fontFamily,
    fontSize: 20,
    fontWeight: FontWeight.w600,
    height: 1.35,
  );

  // Title styles
  static TextStyle get titleLarge => TextStyle(
    fontFamily: _fontFamily,
    fontSize: 18,
    fontWeight: FontWeight.w600,
    height: 1.4,
  );

  static TextStyle get titleMedium => TextStyle(
    fontFamily: _fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w500,
    height: 1.4,
  );

  static TextStyle get titleSmall => TextStyle(
    fontFamily: _fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w500,
    height: 1.4,
  );

  // Body styles
  static TextStyle get bodyLarge => TextStyle(
    fontFamily: _fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w400,
    height: 1.5,
  );

  static TextStyle get bodyMedium => TextStyle(
    fontFamily: _fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w400,
    height: 1.5,
  );

  static TextStyle get bodySmall => TextStyle(
    fontFamily: _fontFamily,
    fontSize: 12,
    fontWeight: FontWeight.w400,
    height: 1.5,
  );

  // Label styles
  static TextStyle get labelLarge => TextStyle(
    fontFamily: _fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w500,
    height: 1.4,
    letterSpacing: 0.1,
  );

  static TextStyle get labelMedium => TextStyle(
    fontFamily: _fontFamily,
    fontSize: 12,
    fontWeight: FontWeight.w500,
    height: 1.4,
    letterSpacing: 0.5,
  );

  static TextStyle get labelSmall => TextStyle(
    fontFamily: _fontFamily,
    fontSize: 10,
    fontWeight: FontWeight.w500,
    height: 1.4,
    letterSpacing: 0.5,
  );
}
```

### Line Height Conversion

```dart
// Figma line height (%) → Flutter height (ratio)
double lineHeightToRatio(double percentage) {
  return percentage / 100;
}

// Figma: lineHeight 150% → Flutter: height 1.5
```

---

## Border Radius Tokens

```dart
// lib/core/theme/app_radius.dart

import 'package:flutter/material.dart';

/// Border radius constants
abstract class AppRadius {
  static const double none = 0.0;
  static const double xs = 4.0;
  static const double sm = 8.0;
  static const double md = 12.0;
  static const double lg = 16.0;
  static const double xl = 24.0;
  static const double xxl = 32.0;
  static const double full = 999.0;

  // BorderRadius presets
  static BorderRadius get xsAll => BorderRadius.circular(xs);
  static BorderRadius get smAll => BorderRadius.circular(sm);
  static BorderRadius get mdAll => BorderRadius.circular(md);
  static BorderRadius get lgAll => BorderRadius.circular(lg);
  static BorderRadius get xlAll => BorderRadius.circular(xl);
  static BorderRadius get circular => BorderRadius.circular(full);

  // Top only
  static BorderRadius get smTop => BorderRadius.vertical(
    top: Radius.circular(sm),
  );
  static BorderRadius get mdTop => BorderRadius.vertical(
    top: Radius.circular(md),
  );

  // Bottom only
  static BorderRadius get smBottom => BorderRadius.vertical(
    bottom: Radius.circular(sm),
  );
  static BorderRadius get mdBottom => BorderRadius.vertical(
    bottom: Radius.circular(md),
  );
}
```

---

## Shadow Tokens

```dart
// lib/core/theme/app_shadows.dart

import 'package:flutter/material.dart';

/// Box shadow presets
abstract class AppShadows {
  static List<BoxShadow> get none => [];

  // Flutter 3.27+: Use Color constructor instead of deprecated withOpacity()
  static List<BoxShadow> get sm => [
    const BoxShadow(
      color: Color(0x0D000000), // black with 5% opacity
      blurRadius: 4,
      offset: Offset(0, 1),
    ),
  ];

  static List<BoxShadow> get md => [
    const BoxShadow(
      color: Color(0x1A000000), // black with 10% opacity
      blurRadius: 8,
      offset: Offset(0, 4),
    ),
  ];

  static List<BoxShadow> get lg => [
    const BoxShadow(
      color: Color(0x1A000000), // black with 10% opacity
      blurRadius: 16,
      offset: Offset(0, 8),
    ),
  ];

  static List<BoxShadow> get xl => [
    const BoxShadow(
      color: Color(0x26000000), // black with 15% opacity
      blurRadius: 24,
      offset: Offset(0, 12),
    ),
  ];

  static List<BoxShadow> get xxl => [
    const BoxShadow(
      color: Color(0x33000000), // black with 20% opacity
      blurRadius: 32,
      offset: Offset(0, 16),
    ),
  ];
}
```

---

## Theme Integration

```dart
// lib/core/theme/app_theme.dart

import 'package:flutter/material.dart';
import 'app_colors.dart';
import 'app_typography.dart';
import 'app_spacing.dart';

class AppTheme {
  static ThemeData get light => ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    colorScheme: ColorScheme.light(
      primary: AppColors.primary,
      onPrimary: AppColors.primaryForeground,
      secondary: AppColors.secondary,
      onSecondary: AppColors.secondaryForeground,
      surface: AppColors.surface,
      onSurface: AppColors.surfaceForeground,
      error: AppColors.destructive,
      onError: AppColors.destructiveForeground,
    ),
    scaffoldBackgroundColor: AppColors.background,
    textTheme: _textTheme,
    elevatedButtonTheme: _elevatedButtonTheme,
    outlinedButtonTheme: _outlinedButtonTheme,
    inputDecorationTheme: _inputDecorationTheme,
    cardTheme: _cardTheme,
    dividerTheme: _dividerTheme,
  );

  static ThemeData get dark => ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    colorScheme: ColorScheme.dark(
      primary: AppColorsDark.primary,
      onPrimary: AppColorsDark.primaryForeground,
      secondary: AppColorsDark.secondary,
      onSecondary: AppColorsDark.secondaryForeground,
      surface: AppColorsDark.surface,
      onSurface: AppColorsDark.surfaceForeground,
      error: AppColorsDark.destructive,
      onError: AppColorsDark.destructiveForeground,
    ),
    scaffoldBackgroundColor: AppColorsDark.background,
    textTheme: _textTheme,
  );

  static TextTheme get _textTheme => TextTheme(
    displayLarge: AppTypography.displayLarge,
    displayMedium: AppTypography.displayMedium,
    displaySmall: AppTypography.displaySmall,
    headlineLarge: AppTypography.headlineLarge,
    headlineMedium: AppTypography.headlineMedium,
    headlineSmall: AppTypography.headlineSmall,
    titleLarge: AppTypography.titleLarge,
    titleMedium: AppTypography.titleMedium,
    titleSmall: AppTypography.titleSmall,
    bodyLarge: AppTypography.bodyLarge,
    bodyMedium: AppTypography.bodyMedium,
    bodySmall: AppTypography.bodySmall,
    labelLarge: AppTypography.labelLarge,
    labelMedium: AppTypography.labelMedium,
    labelSmall: AppTypography.labelSmall,
  );

  static ElevatedButtonThemeData get _elevatedButtonTheme =>
    ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: AppColors.primary,
        foregroundColor: AppColors.primaryForeground,
        padding: AppPadding.buttonPadding,
        minimumSize: const Size(0, 48),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    );

  static OutlinedButtonThemeData get _outlinedButtonTheme =>
    OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: AppColors.foreground,
        side: BorderSide(color: AppColors.border),
        padding: AppPadding.buttonPadding,
        minimumSize: const Size(0, 48),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    );

  static InputDecorationTheme get _inputDecorationTheme =>
    InputDecorationTheme(
      filled: true,
      fillColor: AppColors.surface,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide(color: AppColors.border),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide(color: AppColors.border),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide(color: AppColors.primary, width: 2),
      ),
      contentPadding: AppPadding.buttonPadding,
    );

  static CardTheme get _cardTheme => CardTheme(
    elevation: 0,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(12),
      side: BorderSide(color: AppColors.border),
    ),
    color: AppColors.surface,
  );

  static DividerThemeData get _dividerTheme => DividerThemeData(
    color: AppColors.border,
    thickness: 1,
  );
}
```

---

## Output Files

```
lib/
└── core/
    └── theme/
        ├── app_theme.dart       # ThemeData 통합
        ├── app_colors.dart      # 색상 팔레트
        ├── app_typography.dart  # 텍스트 스타일
        ├── app_spacing.dart     # 간격 상수
        ├── app_radius.dart      # Border radius
        └── app_shadows.dart     # Box shadows
```
