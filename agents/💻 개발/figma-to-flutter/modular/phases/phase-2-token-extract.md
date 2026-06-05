---
name: "Phase 2: Token Extract"
description: "Design token extraction for Flutter theming"
---

# Phase 2: Token Extract

> Figma 디자인 토큰을 Flutter ThemeData로 변환

---

## 실행 조건

- Phase 1 완료
- 디자인 분석 데이터 확보

---

## Step 2-1: 변수 정의 조회

### MCP 호출

```typescript
get_variable_defs({
  fileKey: "ABC123"
})
```

### 응답 구조

```json
{
  "variables": [
    {
      "id": "var:123",
      "name": "colors/primary",
      "resolvedType": "COLOR",
      "valuesByMode": {
        "light": "#3B82F6",
        "dark": "#60A5FA"
      }
    }
  ]
}
```

---

## Step 2-2: 색상 토큰 추출

### Figma → Flutter 색상 변환

```dart
// lib/core/theme/app_colors.dart

import 'package:flutter/material.dart';

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
}

// Dark theme colors
abstract class AppColorsDark {
  static const Color primary = Color(0xFF60A5FA);
  static const Color primaryForeground = Color(0xFF1F2937);

  static const Color background = Color(0xFF1F2937);
  static const Color foreground = Color(0xFFF9FAFB);

  // ... etc
}
```

---

## Step 2-3: 간격 토큰 추출

### Figma px → Flutter 상수

```dart
// lib/core/theme/app_spacing.dart

abstract class AppSpacing {
  static const double xs = 4.0;    // 4px
  static const double sm = 8.0;    // 8px
  static const double md = 12.0;   // 12px
  static const double lg = 16.0;   // 16px
  static const double xl = 24.0;   // 24px
  static const double xxl = 32.0;  // 32px
  static const double xxxl = 48.0; // 48px

  // Semantic spacing
  static const double cardPadding = 16.0;
  static const double sectionGap = 24.0;
  static const double screenPadding = 16.0;
  static const double itemGap = 12.0;
}

// EdgeInsets helpers
abstract class AppPadding {
  static const EdgeInsets screen = EdgeInsets.symmetric(
    horizontal: AppSpacing.screenPadding,
  );

  static const EdgeInsets card = EdgeInsets.all(AppSpacing.cardPadding);

  static const EdgeInsets section = EdgeInsets.symmetric(
    vertical: AppSpacing.sectionGap,
    horizontal: AppSpacing.screenPadding,
  );
}
```

---

## Step 2-4: 타이포그래피 토큰 추출

### Figma → Flutter TextStyle

```dart
// lib/core/theme/app_typography.dart

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

abstract class AppTypography {
  static String get _fontFamily => GoogleFonts.inter().fontFamily!;

  // Display
  static TextStyle get displayLarge => TextStyle(
    fontFamily: _fontFamily,
    fontSize: 48,
    fontWeight: FontWeight.w700,
    height: 1.2,
    letterSpacing: -0.5,
  );

  // Headings
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

  // Titles
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

  // Body
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

  // Labels
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

---

## Step 2-5: Border Radius 토큰 추출

```dart
// lib/core/theme/app_radius.dart

abstract class AppRadius {
  static const double xs = 4.0;
  static const double sm = 8.0;
  static const double md = 12.0;
  static const double lg = 16.0;
  static const double xl = 24.0;
  static const double full = 999.0;

  // BorderRadius helpers
  static BorderRadius get xsAll => BorderRadius.circular(xs);
  static BorderRadius get smAll => BorderRadius.circular(sm);
  static BorderRadius get mdAll => BorderRadius.circular(md);
  static BorderRadius get lgAll => BorderRadius.circular(lg);
  static BorderRadius get xlAll => BorderRadius.circular(xl);
  static BorderRadius get circular => BorderRadius.circular(full);
}
```

---

## Step 2-6: 그림자 토큰 추출

```dart
// lib/core/theme/app_shadows.dart

abstract class AppShadows {
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
}
```

---

## Step 2-7: ThemeData 통합

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
    textTheme: TextTheme(
      displayLarge: AppTypography.displayLarge,
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
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: AppColors.primary,
        foregroundColor: AppColors.primaryForeground,
        padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.lg,
          vertical: AppSpacing.md,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: AppColors.foreground,
        side: BorderSide(color: AppColors.border),
        padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.lg,
          vertical: AppSpacing.md,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
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
      contentPadding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.lg,
        vertical: AppSpacing.md,
      ),
    ),
    cardTheme: CardTheme(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: AppColors.border),
      ),
      color: AppColors.surface,
    ),
    dividerTheme: DividerThemeData(
      color: AppColors.border,
      thickness: 1,
    ),
  );

  static ThemeData get dark => ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    colorScheme: ColorScheme.dark(
      primary: AppColorsDark.primary,
      onPrimary: AppColorsDark.primaryForeground,
      surface: AppColorsDark.background,
      onSurface: AppColorsDark.foreground,
    ),
    // ... similar structure
  );
}
```

---

## 산출물

```markdown
# Token Extract Report

## Files Created
- lib/core/theme/app_colors.dart
- lib/core/theme/app_typography.dart
- lib/core/theme/app_spacing.dart
- lib/core/theme/app_radius.dart
- lib/core/theme/app_shadows.dart
- lib/core/theme/app_theme.dart

## Color Tokens
| Token | Light | Dark |
|-------|-------|------|
| primary | #3B82F6 | #60A5FA |
| background | #FFFFFF | #1F2937 |
| foreground | #1F2937 | #F9FAFB |

## Typography Tokens
| Style | Size | Weight | Line Height |
|-------|------|--------|-------------|
| headlineLarge | 32px | 700 | 1.25 |
| bodyLarge | 16px | 400 | 1.5 |

## Spacing Tokens
| Token | Value |
|-------|-------|
| xs | 4px |
| sm | 8px |
| md | 12px |
| lg | 16px |
| xl | 24px |

## Next Phase
Phase 3: Widget Mapping 진행 가능
```
