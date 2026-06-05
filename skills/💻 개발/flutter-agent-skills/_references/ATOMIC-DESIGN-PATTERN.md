# Atomic Design Pattern Reference

Flutter Atomic Design 위젯 구조 패턴 및 샘플 코드 레퍼런스입니다.

## 계층 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                         PAGES                                    │
│    실제 콘텐츠가 적용된 최종 화면 (ConsumerWidget)                  │
├─────────────────────────────────────────────────────────────────┤
│                       TEMPLATES                                  │
│    페이지 레이아웃 뼈대, 슬롯 구조 (StatelessWidget)               │
├─────────────────────────────────────────────────────────────────┤
│                       ORGANISMS                                  │
│    복잡한 UI 섹션 (StatefulWidget 가능)                           │
├─────────────────────────────────────────────────────────────────┤
│                       MOLECULES                                  │
│    Atoms 조합, 단일 기능 (StatelessWidget)                        │
├─────────────────────────────────────────────────────────────────┤
│                         ATOMS                                    │
│    최소 단위 위젯 (StatelessWidget)                               │
├─────────────────────────────────────────────────────────────────┤
│                        TOKENS                                    │
│    디자인 시스템 원시값 (Colors, Typography, Spacing 등)           │
└─────────────────────────────────────────────────────────────────┘
```

## 위젯 순수성 계약

Atomic Design 계층의 재사용 위젯은 값과 콜백으로만 동작한다.

- Atoms/Molecules/Organisms는 HTTP, DB, Repository, Platform Channel을 직접 호출하지 않는다.
- 재사용 위젯은 `ref.watch` 같은 상태관리 구현을 직접 알지 않는다. 필요한 값은 생성자로 받고, 사용자 이벤트는 콜백으로 올린다.
- Pages는 ViewModel/Notifier를 연결하는 조립 계층이다. 하위 위젯에는 UI State와 command callback만 전달한다.
- Preview, widget test, golden test에서 앱 전체 실행 없이 렌더링할 수 있어야 재사용 가능한 위젯으로 본다.

```dart
class UserCard extends StatelessWidget {
  const UserCard({
    super.key,
    required this.user,
    required this.onTap,
  });

  final UserEntity user;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      title: Text(user.name),
      subtitle: Text(user.email),
      onTap: onTap,
    );
  }
}
```

## Constraints 기반 반응형 규칙

- 화면 전체 크기 판단은 `MediaQuery.sizeOf(context)`를 사용한다.
- 컴포넌트가 놓인 로컬 영역의 가용 공간은 `LayoutBuilder`의 `BoxConstraints`로 판단한다.
- `width: 360`, `height: 812` 같은 기기 기준 고정값으로 레이아웃을 분기하지 않는다.
- 작은 화면과 큰 화면에서 정보 구조가 달라지면 하나의 위젯을 억지로 늘리지 말고 다른 레이아웃 위젯을 반환한다.

---

## 디렉토리 구조

```
lib/
├── core/
│   ├── design_system/
│   │   ├── tokens/
│   │   │   ├── app_colors.dart
│   │   │   ├── app_typography.dart
│   │   │   ├── app_spacing.dart
│   │   │   ├── app_radius.dart
│   │   │   ├── app_shadows.dart
│   │   │   └── index.dart              # barrel export
│   │   │
│   │   ├── atoms/
│   │   │   ├── app_text.dart
│   │   │   ├── app_button.dart
│   │   │   ├── app_input.dart
│   │   │   ├── app_icon.dart
│   │   │   ├── app_image.dart
│   │   │   ├── app_spacer.dart
│   │   │   ├── app_divider.dart
│   │   │   ├── app_loading.dart
│   │   │   └── index.dart
│   │   │
│   │   ├── molecules/
│   │   │   ├── search_bar.dart
│   │   │   ├── labeled_input.dart
│   │   │   ├── avatar_with_name.dart
│   │   │   ├── icon_text_row.dart
│   │   │   ├── rating_stars.dart
│   │   │   ├── tag_chip.dart
│   │   │   └── index.dart
│   │   │
│   │   ├── organisms/
│   │   │   ├── app_header.dart
│   │   │   ├── app_bottom_nav.dart
│   │   │   ├── app_drawer.dart
│   │   │   ├── login_form.dart
│   │   │   ├── product_card.dart
│   │   │   ├── comment_section.dart
│   │   │   └── index.dart
│   │   │
│   │   └── templates/
│   │       ├── main_template.dart
│   │       ├── auth_template.dart
│   │       ├── list_template.dart
│   │       ├── detail_template.dart
│   │       └── index.dart
│   │
│   └── theme/
│       ├── app_theme.dart
│       ├── light_theme.dart
│       └── dark_theme.dart
│
└── features/
    └── {feature}/
        └── presentation/
            └── pages/                  # Pages 계층
                └── {feature}_page.dart
```

---

## Tokens (디자인 토큰)

### Colors

```dart
// tokens/app_colors.dart
import 'package:flutter/material.dart';

abstract class AppColors {
  // Primary
  static const Color primary = Color(0xFF6366F1);
  static const Color primaryLight = Color(0xFF818CF8);
  static const Color primaryDark = Color(0xFF4F46E5);
  static const Color onPrimary = Color(0xFFFFFFFF);

  // Secondary
  static const Color secondary = Color(0xFF10B981);
  static const Color secondaryLight = Color(0xFF34D399);
  static const Color secondaryDark = Color(0xFF059669);
  static const Color onSecondary = Color(0xFFFFFFFF);

  // Neutral
  static const Color background = Color(0xFFFAFAFA);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color surfaceVariant = Color(0xFFF4F4F5);
  static const Color border = Color(0xFFE4E4E7);

  // Text
  static const Color textPrimary = Color(0xFF18181B);
  static const Color textSecondary = Color(0xFF71717A);
  static const Color textTertiary = Color(0xFFA1A1AA);
  static const Color textDisabled = Color(0xFFD4D4D8);

  // Semantic
  static const Color success = Color(0xFF10B981);
  static const Color warning = Color(0xFFF59E0B);
  static const Color error = Color(0xFFEF4444);
  static const Color info = Color(0xFF3B82F6);

  // Dark Mode
  static const Color darkBackground = Color(0xFF18181B);
  static const Color darkSurface = Color(0xFF27272A);
  static const Color darkSurfaceVariant = Color(0xFF3F3F46);
  static const Color darkBorder = Color(0xFF52525B);
  static const Color darkTextPrimary = Color(0xFFFAFAFA);
  static const Color darkTextSecondary = Color(0xFFA1A1AA);
}
```

### Typography

```dart
// tokens/app_typography.dart
import 'package:flutter/material.dart';

abstract class AppTypography {
  static const String fontFamily = 'Pretendard';

  // Display
  static const TextStyle displayLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 57,
    fontWeight: FontWeight.w400,
    letterSpacing: -0.25,
    height: 1.12,
  );

  static const TextStyle displayMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 45,
    fontWeight: FontWeight.w400,
    height: 1.16,
  );

  static const TextStyle displaySmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 36,
    fontWeight: FontWeight.w400,
    height: 1.22,
  );

  // Headline
  static const TextStyle headlineLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 32,
    fontWeight: FontWeight.w600,
    height: 1.25,
  );

  static const TextStyle headlineMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 28,
    fontWeight: FontWeight.w600,
    height: 1.29,
  );

  static const TextStyle headlineSmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 24,
    fontWeight: FontWeight.w600,
    height: 1.33,
  );

  // Title
  static const TextStyle titleLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 22,
    fontWeight: FontWeight.w500,
    height: 1.27,
  );

  static const TextStyle titleMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.15,
    height: 1.50,
  );

  static const TextStyle titleSmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.1,
    height: 1.43,
  );

  // Body
  static const TextStyle bodyLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w400,
    letterSpacing: 0.5,
    height: 1.50,
  );

  static const TextStyle bodyMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w400,
    letterSpacing: 0.25,
    height: 1.43,
  );

  static const TextStyle bodySmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    fontWeight: FontWeight.w400,
    letterSpacing: 0.4,
    height: 1.33,
  );

  // Label
  static const TextStyle labelLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.1,
    height: 1.43,
  );

  static const TextStyle labelMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.5,
    height: 1.33,
  );

  static const TextStyle labelSmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 11,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.5,
    height: 1.45,
  );
}
```

### Spacing

```dart
// tokens/app_spacing.dart
abstract class AppSpacing {
  static const double xxs = 2.0;
  static const double xs = 4.0;
  static const double sm = 8.0;
  static const double md = 16.0;
  static const double lg = 24.0;
  static const double xl = 32.0;
  static const double xxl = 48.0;
  static const double xxxl = 64.0;

  // Semantic spacing
  static const double pagePadding = md;
  static const double cardPadding = md;
  static const double sectionGap = lg;
  static const double itemGap = sm;
}
```

### Radius

```dart
// tokens/app_radius.dart
import 'package:flutter/material.dart';

abstract class AppRadius {
  static const double none = 0;
  static const double xs = 2.0;
  static const double sm = 4.0;
  static const double md = 8.0;
  static const double lg = 12.0;
  static const double xl = 16.0;
  static const double xxl = 24.0;
  static const double full = 9999.0;

  // BorderRadius
  static const BorderRadius noneBorder = BorderRadius.zero;
  static const BorderRadius smBorder = BorderRadius.all(Radius.circular(sm));
  static const BorderRadius mdBorder = BorderRadius.all(Radius.circular(md));
  static const BorderRadius lgBorder = BorderRadius.all(Radius.circular(lg));
  static const BorderRadius xlBorder = BorderRadius.all(Radius.circular(xl));
  static const BorderRadius fullBorder = BorderRadius.all(Radius.circular(full));
}
```

### Shadows

```dart
// tokens/app_shadows.dart
import 'package:flutter/material.dart';

abstract class AppShadows {
  static const List<BoxShadow> none = [];

  static const List<BoxShadow> sm = [
    BoxShadow(
      color: Color(0x0D000000),
      offset: Offset(0, 1),
      blurRadius: 2,
    ),
  ];

  static const List<BoxShadow> md = [
    BoxShadow(
      color: Color(0x1A000000),
      offset: Offset(0, 4),
      blurRadius: 6,
      spreadRadius: -1,
    ),
  ];

  static const List<BoxShadow> lg = [
    BoxShadow(
      color: Color(0x1A000000),
      offset: Offset(0, 10),
      blurRadius: 15,
      spreadRadius: -3,
    ),
  ];

  static const List<BoxShadow> xl = [
    BoxShadow(
      color: Color(0x26000000),
      offset: Offset(0, 20),
      blurRadius: 25,
      spreadRadius: -5,
    ),
  ];
}
```

---

## Atoms (최소 단위 위젯)

### AppText

```dart
// atoms/app_text.dart
import 'package:flutter/material.dart';

enum AppTextVariant {
  displayLarge,
  displayMedium,
  displaySmall,
  headlineLarge,
  headlineMedium,
  headlineSmall,
  titleLarge,
  titleMedium,
  titleSmall,
  bodyLarge,
  bodyMedium,
  bodySmall,
  labelLarge,
  labelMedium,
  labelSmall,
}

class AppText extends StatelessWidget {
  const AppText(
    this.text, {
    super.key,
    this.variant = AppTextVariant.bodyMedium,
    this.color,
    this.maxLines,
    this.overflow,
    this.textAlign,
  });

  final String text;
  final AppTextVariant variant;
  final Color? color;
  final int? maxLines;
  final TextOverflow? overflow;
  final TextAlign? textAlign;

  @override
  Widget build(BuildContext context) {
    return Text(
      text,
      style: _getTextStyle().copyWith(color: color),
      maxLines: maxLines,
      overflow: overflow,
      textAlign: textAlign,
    );
  }

  TextStyle _getTextStyle() => switch (variant) {
        AppTextVariant.displayLarge => AppTypography.displayLarge,
        AppTextVariant.displayMedium => AppTypography.displayMedium,
        AppTextVariant.displaySmall => AppTypography.displaySmall,
        AppTextVariant.headlineLarge => AppTypography.headlineLarge,
        AppTextVariant.headlineMedium => AppTypography.headlineMedium,
        AppTextVariant.headlineSmall => AppTypography.headlineSmall,
        AppTextVariant.titleLarge => AppTypography.titleLarge,
        AppTextVariant.titleMedium => AppTypography.titleMedium,
        AppTextVariant.titleSmall => AppTypography.titleSmall,
        AppTextVariant.bodyLarge => AppTypography.bodyLarge,
        AppTextVariant.bodyMedium => AppTypography.bodyMedium,
        AppTextVariant.bodySmall => AppTypography.bodySmall,
        AppTextVariant.labelLarge => AppTypography.labelLarge,
        AppTextVariant.labelMedium => AppTypography.labelMedium,
        AppTextVariant.labelSmall => AppTypography.labelSmall,
      };
}
```

### AppButton

```dart
// atoms/app_button.dart
import 'package:flutter/material.dart';

enum AppButtonVariant { primary, secondary, outline, ghost, destructive }
enum AppButtonSize { sm, md, lg }

class AppButton extends StatelessWidget {
  const AppButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.variant = AppButtonVariant.primary,
    this.size = AppButtonSize.md,
    this.icon,
    this.iconPosition = IconPosition.leading,
    this.isLoading = false,
    this.isDisabled = false,
    this.isExpanded = false,
  });

  final String label;
  final VoidCallback? onPressed;
  final AppButtonVariant variant;
  final AppButtonSize size;
  final IconData? icon;
  final IconPosition iconPosition;
  final bool isLoading;
  final bool isDisabled;
  final bool isExpanded;

  @override
  Widget build(BuildContext context) {
    final effectiveOnPressed = isDisabled || isLoading ? null : onPressed;

    return SizedBox(
      height: _height,
      width: isExpanded ? double.infinity : null,
      child: _buildButton(effectiveOnPressed),
    );
  }

  Widget _buildButton(VoidCallback? onPressed) {
    final child = _buildChild();

    return switch (variant) {
      AppButtonVariant.primary => ElevatedButton(
          onPressed: onPressed,
          style: _primaryStyle,
          child: child,
        ),
      AppButtonVariant.secondary => ElevatedButton(
          onPressed: onPressed,
          style: _secondaryStyle,
          child: child,
        ),
      AppButtonVariant.outline => OutlinedButton(
          onPressed: onPressed,
          style: _outlineStyle,
          child: child,
        ),
      AppButtonVariant.ghost => TextButton(
          onPressed: onPressed,
          style: _ghostStyle,
          child: child,
        ),
      AppButtonVariant.destructive => ElevatedButton(
          onPressed: onPressed,
          style: _destructiveStyle,
          child: child,
        ),
    };
  }

  Widget _buildChild() {
    if (isLoading) {
      return SizedBox(
        width: _iconSize,
        height: _iconSize,
        child: CircularProgressIndicator(
          strokeWidth: 2,
          valueColor: AlwaysStoppedAnimation(_loadingColor),
        ),
      );
    }

    final textWidget = Text(label, style: _textStyle);

    if (icon == null) return textWidget;

    final iconWidget = Icon(icon, size: _iconSize);

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: iconPosition == IconPosition.leading
          ? [iconWidget, SizedBox(width: AppSpacing.sm), textWidget]
          : [textWidget, SizedBox(width: AppSpacing.sm), iconWidget],
    );
  }

  double get _height => switch (size) {
        AppButtonSize.sm => 32,
        AppButtonSize.md => 40,
        AppButtonSize.lg => 48,
      };

  double get _iconSize => switch (size) {
        AppButtonSize.sm => 16,
        AppButtonSize.md => 20,
        AppButtonSize.lg => 24,
      };

  TextStyle get _textStyle => switch (size) {
        AppButtonSize.sm => AppTypography.labelSmall,
        AppButtonSize.md => AppTypography.labelMedium,
        AppButtonSize.lg => AppTypography.labelLarge,
      };

  Color get _loadingColor => switch (variant) {
        AppButtonVariant.primary => AppColors.onPrimary,
        AppButtonVariant.secondary => AppColors.onSecondary,
        AppButtonVariant.outline => AppColors.primary,
        AppButtonVariant.ghost => AppColors.primary,
        AppButtonVariant.destructive => AppColors.onPrimary,
      };

  ButtonStyle get _primaryStyle => ElevatedButton.styleFrom(
        backgroundColor: AppColors.primary,
        foregroundColor: AppColors.onPrimary,
        shape: RoundedRectangleBorder(borderRadius: AppRadius.mdBorder),
      );

  ButtonStyle get _secondaryStyle => ElevatedButton.styleFrom(
        backgroundColor: AppColors.secondary,
        foregroundColor: AppColors.onSecondary,
        shape: RoundedRectangleBorder(borderRadius: AppRadius.mdBorder),
      );

  ButtonStyle get _outlineStyle => OutlinedButton.styleFrom(
        foregroundColor: AppColors.primary,
        side: BorderSide(color: AppColors.border),
        shape: RoundedRectangleBorder(borderRadius: AppRadius.mdBorder),
      );

  ButtonStyle get _ghostStyle => TextButton.styleFrom(
        foregroundColor: AppColors.primary,
        shape: RoundedRectangleBorder(borderRadius: AppRadius.mdBorder),
      );

  ButtonStyle get _destructiveStyle => ElevatedButton.styleFrom(
        backgroundColor: AppColors.error,
        foregroundColor: AppColors.onPrimary,
        shape: RoundedRectangleBorder(borderRadius: AppRadius.mdBorder),
      );
}

enum IconPosition { leading, trailing }
```

### AppInput

```dart
// atoms/app_input.dart
import 'package:flutter/material.dart';

class AppInput extends StatelessWidget {
  const AppInput({
    super.key,
    this.controller,
    this.hintText,
    this.labelText,
    this.errorText,
    this.prefixIcon,
    this.suffixIcon,
    this.obscureText = false,
    this.enabled = true,
    this.readOnly = false,
    this.maxLines = 1,
    this.keyboardType,
    this.textInputAction,
    this.onChanged,
    this.onSubmitted,
    this.validator,
    this.autofocus = false,
  });

  final TextEditingController? controller;
  final String? hintText;
  final String? labelText;
  final String? errorText;
  final IconData? prefixIcon;
  final Widget? suffixIcon;
  final bool obscureText;
  final bool enabled;
  final bool readOnly;
  final int maxLines;
  final TextInputType? keyboardType;
  final TextInputAction? textInputAction;
  final ValueChanged<String>? onChanged;
  final ValueChanged<String>? onSubmitted;
  final String? Function(String?)? validator;
  final bool autofocus;

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      obscureText: obscureText,
      enabled: enabled,
      readOnly: readOnly,
      maxLines: maxLines,
      keyboardType: keyboardType,
      textInputAction: textInputAction,
      onChanged: onChanged,
      onFieldSubmitted: onSubmitted,
      validator: validator,
      autofocus: autofocus,
      style: AppTypography.bodyMedium.copyWith(
        color: AppColors.textPrimary,
      ),
      decoration: InputDecoration(
        hintText: hintText,
        labelText: labelText,
        errorText: errorText,
        hintStyle: AppTypography.bodyMedium.copyWith(
          color: AppColors.textTertiary,
        ),
        labelStyle: AppTypography.bodyMedium.copyWith(
          color: AppColors.textSecondary,
        ),
        errorStyle: AppTypography.bodySmall.copyWith(
          color: AppColors.error,
        ),
        prefixIcon: prefixIcon != null ? Icon(prefixIcon) : null,
        suffixIcon: suffixIcon,
        filled: true,
        fillColor: enabled ? AppColors.surface : AppColors.surfaceVariant,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.md,
          vertical: AppSpacing.sm,
        ),
        border: OutlineInputBorder(
          borderRadius: AppRadius.mdBorder,
          borderSide: BorderSide(color: AppColors.border),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: AppRadius.mdBorder,
          borderSide: BorderSide(color: AppColors.border),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: AppRadius.mdBorder,
          borderSide: BorderSide(color: AppColors.primary, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: AppRadius.mdBorder,
          borderSide: BorderSide(color: AppColors.error),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: AppRadius.mdBorder,
          borderSide: BorderSide(color: AppColors.error, width: 2),
        ),
        disabledBorder: OutlineInputBorder(
          borderRadius: AppRadius.mdBorder,
          borderSide: BorderSide(color: AppColors.border.withOpacity(0.5)),
        ),
      ),
    );
  }
}
```

### AppIcon / AppImage / AppSpacer / AppDivider / AppLoading

```dart
// atoms/app_icon.dart
class AppIcon extends StatelessWidget {
  const AppIcon(
    this.icon, {
    super.key,
    this.size = 24,
    this.color,
  });

  final IconData icon;
  final double size;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    return Icon(icon, size: size, color: color ?? AppColors.textPrimary);
  }
}

// atoms/app_image.dart
class AppImage extends StatelessWidget {
  const AppImage({
    super.key,
    required this.src,
    this.width,
    this.height,
    this.fit = BoxFit.cover,
    this.borderRadius,
    this.placeholder,
    this.errorWidget,
  });

  final String src;
  final double? width;
  final double? height;
  final BoxFit fit;
  final BorderRadius? borderRadius;
  final Widget? placeholder;
  final Widget? errorWidget;

  @override
  Widget build(BuildContext context) {
    Widget image;

    if (src.startsWith('http')) {
      image = Image.network(
        src,
        width: width,
        height: height,
        fit: fit,
        loadingBuilder: (_, child, progress) =>
            progress == null ? child : (placeholder ?? const AppLoading()),
        errorBuilder: (_, __, ___) =>
            errorWidget ?? const Icon(Icons.broken_image),
      );
    } else {
      image = Image.asset(
        src,
        width: width,
        height: height,
        fit: fit,
      );
    }

    if (borderRadius != null) {
      return ClipRRect(borderRadius: borderRadius!, child: image);
    }

    return image;
  }
}

// atoms/app_spacer.dart
class AppSpacer extends StatelessWidget {
  const AppSpacer({super.key, this.width, this.height});

  final double? width;
  final double? height;

  const AppSpacer.horizontal(double size, {super.key})
      : width = size,
        height = null;

  const AppSpacer.vertical(double size, {super.key})
      : width = null,
        height = size;

  @override
  Widget build(BuildContext context) {
    return SizedBox(width: width, height: height);
  }
}

// atoms/app_divider.dart
class AppDivider extends StatelessWidget {
  const AppDivider({
    super.key,
    this.color,
    this.thickness = 1,
    this.indent = 0,
    this.endIndent = 0,
  });

  final Color? color;
  final double thickness;
  final double indent;
  final double endIndent;

  @override
  Widget build(BuildContext context) {
    return Divider(
      color: color ?? AppColors.border,
      thickness: thickness,
      indent: indent,
      endIndent: endIndent,
    );
  }
}

// atoms/app_loading.dart
class AppLoading extends StatelessWidget {
  const AppLoading({
    super.key,
    this.size = 24,
    this.color,
    this.strokeWidth = 2,
  });

  final double size;
  final Color? color;
  final double strokeWidth;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: CircularProgressIndicator(
        strokeWidth: strokeWidth,
        valueColor: AlwaysStoppedAnimation(color ?? AppColors.primary),
      ),
    );
  }
}
```

---

## Molecules (Atoms 조합)

### SearchBar

```dart
// molecules/search_bar.dart
class AppSearchBar extends StatelessWidget {
  const AppSearchBar({
    super.key,
    required this.controller,
    this.hintText = '검색어를 입력하세요',
    this.onChanged,
    this.onSubmitted,
    this.onClear,
  });

  final TextEditingController controller;
  final String hintText;
  final ValueChanged<String>? onChanged;
  final ValueChanged<String>? onSubmitted;
  final VoidCallback? onClear;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        const AppIcon(Icons.search, color: AppColors.textSecondary),
        const AppSpacer.horizontal(AppSpacing.sm),
        Expanded(
          child: AppInput(
            controller: controller,
            hintText: hintText,
            onChanged: onChanged,
            onSubmitted: onSubmitted,
          ),
        ),
        if (controller.text.isNotEmpty)
          IconButton(
            icon: const AppIcon(Icons.close, size: 20),
            onPressed: () {
              controller.clear();
              onClear?.call();
            },
          ),
      ],
    );
  }
}
```

### LabeledInput

```dart
// molecules/labeled_input.dart
class LabeledInput extends StatelessWidget {
  const LabeledInput({
    super.key,
    required this.label,
    required this.controller,
    this.hintText,
    this.errorText,
    this.isRequired = false,
    this.obscureText = false,
    this.keyboardType,
    this.onChanged,
  });

  final String label;
  final TextEditingController controller;
  final String? hintText;
  final String? errorText;
  final bool isRequired;
  final bool obscureText;
  final TextInputType? keyboardType;
  final ValueChanged<String>? onChanged;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Label Row (Atoms: AppText)
        Row(
          children: [
            AppText(label, variant: AppTextVariant.labelMedium),
            if (isRequired)
              AppText(' *', variant: AppTextVariant.labelMedium, color: AppColors.error),
          ],
        ),
        const AppSpacer.vertical(AppSpacing.xs),

        // Input (Atom: AppInput)
        AppInput(
          controller: controller,
          hintText: hintText,
          errorText: errorText,
          obscureText: obscureText,
          keyboardType: keyboardType,
          onChanged: onChanged,
        ),
      ],
    );
  }
}
```

### AvatarWithName

```dart
// molecules/avatar_with_name.dart
class AvatarWithName extends StatelessWidget {
  const AvatarWithName({
    super.key,
    required this.name,
    this.imageUrl,
    this.subtitle,
    this.size = 40,
    this.onTap,
  });

  final String name;
  final String? imageUrl;
  final String? subtitle;
  final double size;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Row(
        children: [
          // Avatar (Atom: AppImage or placeholder)
          ClipOval(
            child: imageUrl != null
                ? AppImage(
                    src: imageUrl!,
                    width: size,
                    height: size,
                  )
                : Container(
                    width: size,
                    height: size,
                    color: AppColors.primary,
                    child: Center(
                      child: AppText(
                        name[0].toUpperCase(),
                        variant: AppTextVariant.titleMedium,
                        color: AppColors.onPrimary,
                      ),
                    ),
                  ),
          ),
          const AppSpacer.horizontal(AppSpacing.sm),

          // Name & Subtitle (Atoms: AppText)
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              AppText(name, variant: AppTextVariant.titleSmall),
              if (subtitle != null)
                AppText(
                  subtitle!,
                  variant: AppTextVariant.bodySmall,
                  color: AppColors.textSecondary,
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

## Organisms (복합 기능)

### LoginForm

```dart
// organisms/login_form.dart
class LoginForm extends StatefulWidget {
  const LoginForm({
    super.key,
    required this.onSubmit,
    this.isLoading = false,
  });

  final void Function(String email, String password) onSubmit;
  final bool isLoading;

  @override
  State<LoginForm> createState() => _LoginFormState();
}

class _LoginFormState extends State<LoginForm> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  String? _emailError;
  String? _passwordError;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Molecule: LabeledInput (Email)
          LabeledInput(
            label: '이메일',
            controller: _emailController,
            hintText: 'example@email.com',
            errorText: _emailError,
            isRequired: true,
            keyboardType: TextInputType.emailAddress,
          ),
          const AppSpacer.vertical(AppSpacing.md),

          // Molecule: LabeledInput (Password)
          LabeledInput(
            label: '비밀번호',
            controller: _passwordController,
            hintText: '비밀번호를 입력하세요',
            errorText: _passwordError,
            isRequired: true,
            obscureText: true,
          ),
          const AppSpacer.vertical(AppSpacing.lg),

          // Atom: AppButton
          AppButton(
            label: '로그인',
            onPressed: _handleSubmit,
            isLoading: widget.isLoading,
            isExpanded: true,
          ),
          const AppSpacer.vertical(AppSpacing.md),

          // Atom: AppButton (Ghost)
          AppButton(
            label: '비밀번호를 잊으셨나요?',
            onPressed: () {},
            variant: AppButtonVariant.ghost,
          ),
        ],
      ),
    );
  }

  void _handleSubmit() {
    setState(() {
      _emailError = _validateEmail(_emailController.text);
      _passwordError = _validatePassword(_passwordController.text);
    });

    if (_emailError == null && _passwordError == null) {
      widget.onSubmit(_emailController.text, _passwordController.text);
    }
  }

  String? _validateEmail(String value) {
    if (value.isEmpty) return '이메일을 입력해주세요';
    if (!value.contains('@')) return '올바른 이메일 형식이 아닙니다';
    return null;
  }

  String? _validatePassword(String value) {
    if (value.isEmpty) return '비밀번호를 입력해주세요';
    if (value.length < 6) return '비밀번호는 6자 이상이어야 합니다';
    return null;
  }
}
```

### AppHeader

```dart
// organisms/app_header.dart
class AppHeader extends StatelessWidget {
  const AppHeader({
    super.key,
    required this.title,
    this.showBackButton = false,
    this.actions = const [],
    this.onBack,
  });

  final String title;
  final bool showBackButton;
  final List<Widget> actions;
  final VoidCallback? onBack;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.md,
        vertical: AppSpacing.sm,
      ),
      decoration: BoxDecoration(
        color: AppColors.surface,
        boxShadow: AppShadows.sm,
      ),
      child: SafeArea(
        bottom: false,
        child: Row(
          children: [
            // Atom: Back Button
            if (showBackButton)
              IconButton(
                icon: const AppIcon(Icons.arrow_back),
                onPressed: onBack ?? () => Navigator.pop(context),
              ),

            // Atom: Title
            Expanded(
              child: AppText(
                title,
                variant: AppTextVariant.titleLarge,
                textAlign: showBackButton ? TextAlign.center : TextAlign.start,
              ),
            ),

            // Actions
            ...actions,
          ],
        ),
      ),
    );
  }
}
```

---

## Templates (레이아웃 뼈대)

### MainTemplate

```dart
// templates/main_template.dart
class MainTemplate extends StatelessWidget {
  const MainTemplate({
    super.key,
    required this.body,
    this.title,
    this.showHeader = true,
    this.showBottomNav = true,
    this.headerActions = const [],
    this.floatingActionButton,
    this.onBack,
  });

  final Widget body;
  final String? title;
  final bool showHeader;
  final bool showBottomNav;
  final List<Widget> headerActions;
  final Widget? floatingActionButton;
  final VoidCallback? onBack;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Column(
        children: [
          // Organism: Header
          if (showHeader && title != null)
            AppHeader(
              title: title!,
              showBackButton: Navigator.canPop(context),
              actions: headerActions,
              onBack: onBack,
            ),

          // Body Slot
          Expanded(child: body),
        ],
      ),

      // Organism: Bottom Navigation
      bottomNavigationBar: showBottomNav ? const AppBottomNav() : null,

      floatingActionButton: floatingActionButton,
    );
  }
}
```

### AuthTemplate

```dart
// templates/auth_template.dart
class AuthTemplate extends StatelessWidget {
  const AuthTemplate({
    super.key,
    required this.child,
    this.title,
    this.subtitle,
  });

  final Widget child;
  final String? title;
  final String? subtitle;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const AppSpacer.vertical(AppSpacing.xxl),

              // Atom: Logo
              Center(
                child: AppImage(
                  src: 'assets/images/logo.png',
                  width: 80,
                  height: 80,
                ),
              ),
              const AppSpacer.vertical(AppSpacing.xl),

              // Atoms: Title & Subtitle
              if (title != null) ...[
                AppText(
                  title!,
                  variant: AppTextVariant.headlineMedium,
                  textAlign: TextAlign.center,
                ),
                const AppSpacer.vertical(AppSpacing.sm),
              ],
              if (subtitle != null) ...[
                AppText(
                  subtitle!,
                  variant: AppTextVariant.bodyMedium,
                  color: AppColors.textSecondary,
                  textAlign: TextAlign.center,
                ),
                const AppSpacer.vertical(AppSpacing.xl),
              ],

              // Content Slot
              child,
            ],
          ),
        ),
      ),
    );
  }
}
```

---

## Pages (최종 화면)

### LoginPage

```dart
// features/auth/presentation/pages/login_page.dart
class LoginPage extends ConsumerWidget {
  const LoginPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authNotifierProvider);

    // 에러 처리
    ref.listen(authNotifierProvider, (_, next) {
      next.whenOrNull(
        error: (error, _) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('로그인 실패: $error')),
          );
        },
      );
    });

    return AuthTemplate(
      title: '로그인',
      subtitle: '계정에 로그인하세요',
      child: LoginForm(
        onSubmit: (email, password) {
          ref.read(authNotifierProvider.notifier).login(email, password);
        },
        isLoading: authState.isLoading,
      ),
    );
  }
}
```

---

## 분류 가이드라인

| 질문 | Yes → | No → |
|------|-------|------|
| 더 쪼갤 수 있나? | 상위 계층으로 | Atom |
| 단일 책임인가? | Molecule | Organism |
| 레이아웃 구조인가? | Template | Organism |
| 실제 데이터/상태 연동? | Page | Template |
| 재사용 가능한가? | 공통 폴더 | Feature 내부 |

## 네이밍 규칙

| 계층 | 규칙 | 예시 |
|------|------|------|
| **Tokens** | `App` 접두사 + 복수형 | `AppColors`, `AppTypography` |
| **Atoms** | `App` 접두사 | `AppButton`, `AppText`, `AppInput` |
| **Molecules** | 기능 설명 | `SearchBar`, `LabeledInput` |
| **Organisms** | 컴포넌트명 | `LoginForm`, `ProductCard`, `AppHeader` |
| **Templates** | `Template` 접미사 | `MainTemplate`, `AuthTemplate` |
| **Pages** | `Page` 접미사 | `HomePage`, `LoginPage`, `ProfilePage` |
