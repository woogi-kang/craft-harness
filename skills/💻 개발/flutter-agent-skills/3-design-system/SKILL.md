---
name: design-system
description: |
  Atomic Design 기반 디자인 시스템과 Constraints 기반 반응형 UI를 구축합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Design System Skill

Extends: `../../../design-system/SKILL.md` (공통 디자인 시스템 토큰 아키텍처 참조)

Atomic Design 기반 디자인 시스템과 Constraints 기반 반응형 UI를 구축합니다.

## Triggers

- "디자인 시스템", "atomic design", "design tokens", "위젯 구조"
- "반응형 레이아웃", "responsive", "constraints", "LayoutBuilder"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectName` | ✅ | 프로젝트 이름 |
| `brandColors` | ❌ | 브랜드 컬러 (primary, secondary) |

---

## Atomic Design 계층

```
Pages      ← 실제 데이터 연동 (ConsumerWidget)
Templates  ← 레이아웃 뼈대, 슬롯
Organisms  ← 복잡한 UI 컴포넌트 (StatefulWidget 가능)
Molecules  ← Atoms 조합, 단일 책임
Atoms      ← 최소 단위 위젯
Tokens     ← 디자인 원시값 (Colors, Typography, Spacing)
```

---

## 디렉토리 구조

### Core Design System (앱 전역 공유)

```
lib/core/design_system/
├── tokens/
│   ├── app_colors.dart
│   ├── app_typography.dart
│   ├── app_spacing.dart
│   ├── app_radius.dart
│   └── app_shadows.dart
├── atoms/
│   ├── app_text.dart
│   ├── app_button.dart
│   ├── app_input.dart
│   ├── app_icon.dart
│   ├── app_image.dart
│   └── app_loading.dart
├── molecules/
│   ├── search_bar.dart
│   ├── labeled_input.dart
│   ├── avatar_with_name.dart
│   └── icon_text_row.dart
├── organisms/
│   ├── app_header.dart
│   ├── app_bottom_nav.dart
│   └── app_drawer.dart
└── templates/
    ├── main_template.dart
    ├── auth_template.dart
    └── detail_template.dart
```

### Feature-specific Widgets (Feature 전용)

```
lib/features/{feature}/presentation/
├── pages/
│   ├── {feature}_list_page.dart
│   └── {feature}_detail_page.dart
└── widgets/
    └── atomic/
        ├── atoms/           # Feature 전용 Atoms
        │   └── {feature}_badge.dart
        ├── molecules/       # Feature 전용 Molecules
        │   └── {feature}_list_tile.dart
        └── organisms/       # Feature 전용 Organisms
            ├── {feature}_card.dart
            └── {feature}_form.dart
```

---

## 배치 기준

| 위젯 | Core | Feature |
|------|------|---------|
| AppButton, AppText, AppInput | ✅ | - |
| SearchBar, LabeledInput | ✅ | - |
| AppHeader, AppBottomNav | ✅ | - |
| MainTemplate, AuthTemplate | ✅ | - |
| ProductCard, ProductForm | - | ✅ (product) |
| OrderListTile, OrderBadge | - | ✅ (order) |
| UserAvatar (특화) | - | ✅ (user) |

**기준**: 2개 이상의 Feature에서 사용되면 Core로 승격

---

## 반응형 레이아웃 원칙

디자인 시스템은 고정 화면 크기가 아니라 Flutter 제약 조건 모델을 기준으로 설계합니다.

- 앱 전체 창 크기 기준 분기: `MediaQuery.sizeOf(context)`
- 위젯이 배치된 로컬 영역 기준 분기: `LayoutBuilder`
- 디자인 토큰은 간격/반경/타이포그래피의 일관성을 제공하고, 레이아웃 분기 자체는 `BoxConstraints`로 판단
- `flutter_screenutil`은 기존 프로젝트가 채택한 경우 스케일 보조 도구로만 사용하며, 레이아웃 의사결정의 1차 기준으로 사용하지 않음

```dart
class ResponsiveShell extends StatelessWidget {
  const ResponsiveShell({
    super.key,
    required this.navigation,
    required this.content,
  });

  final Widget navigation;
  final Widget content;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth >= 840) {
          return Row(
            children: [
              SizedBox(width: 280, child: navigation),
              Expanded(child: content),
            ],
          );
        }

        return Column(
          children: [
            Expanded(child: content),
            navigation,
          ],
        );
      },
    );
  }
}
```

---

## Output Templates

### 1. Design Tokens

```dart
// lib/core/design_system/tokens/app_colors.dart
import 'package:flutter/material.dart';

abstract final class AppColors {
  // Brand
  static const Color primary = Color(0xFF6366F1);
  static const Color primaryLight = Color(0xFF818CF8);
  static const Color primaryDark = Color(0xFF4F46E5);
  static const Color secondary = Color(0xFF22D3EE);

  // Semantic
  static const Color success = Color(0xFF22C55E);
  static const Color warning = Color(0xFFF59E0B);
  static const Color error = Color(0xFFEF4444);
  static const Color info = Color(0xFF3B82F6);

  // Neutral
  static const Color background = Color(0xFFFAFAFA);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color border = Color(0xFFE5E7EB);
  static const Color disabled = Color(0xFF9CA3AF);

  // Text
  static const Color textPrimary = Color(0xFF111827);
  static const Color textSecondary = Color(0xFF6B7280);
  static const Color textTertiary = Color(0xFF9CA3AF);
  static const Color textOnPrimary = Color(0xFFFFFFFF);

  // Dark Theme
  static const Color backgroundDark = Color(0xFF111827);
  static const Color surfaceDark = Color(0xFF1F2937);
  static const Color textPrimaryDark = Color(0xFFF9FAFB);
}
```

```dart
// lib/core/design_system/tokens/app_typography.dart
import 'package:flutter/material.dart';

abstract final class AppTypography {
  static const String fontFamily = 'Pretendard';

  // Display
  static const TextStyle displayLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 57,
    fontWeight: FontWeight.w400,
    letterSpacing: -0.25,
    height: 1.12,
  );

  // Headline
  static const TextStyle headlineLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 32,
    fontWeight: FontWeight.w700,
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
    fontWeight: FontWeight.w600,
    height: 1.27,
  );

  static const TextStyle titleMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w600,
    letterSpacing: 0.15,
    height: 1.5,
  );

  static const TextStyle titleSmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w600,
    letterSpacing: 0.1,
    height: 1.43,
  );

  // Body
  static const TextStyle bodyLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w400,
    letterSpacing: 0.5,
    height: 1.5,
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

```dart
// lib/core/design_system/tokens/app_spacing.dart
import 'package:flutter_screenutil/flutter_screenutil.dart';

abstract final class AppSpacing {
  // 기본 값 (디자인 기준)
  static const double xxs = 2;
  static const double xs = 4;
  static const double sm = 8;
  static const double md = 12;
  static const double lg = 16;
  static const double xl = 24;
  static const double xxl = 32;
  static const double xxxl = 48;

  // 반응형 값 (ScreenUtil 적용)
  static double get xxsR => xxs.w;
  static double get xsR => xs.w;
  static double get smR => sm.w;
  static double get mdR => md.w;
  static double get lgR => lg.w;
  static double get xlR => xl.w;
  static double get xxlR => xxl.w;
  static double get xxxlR => xxxl.w;

  // SizedBox 헬퍼
  static SizedBox get verticalXxs => SizedBox(height: xxs.h);
  static SizedBox get verticalXs => SizedBox(height: xs.h);
  static SizedBox get verticalSm => SizedBox(height: sm.h);
  static SizedBox get verticalMd => SizedBox(height: md.h);
  static SizedBox get verticalLg => SizedBox(height: lg.h);
  static SizedBox get verticalXl => SizedBox(height: xl.h);
  static SizedBox get verticalXxl => SizedBox(height: xxl.h);

  static SizedBox get horizontalXxs => SizedBox(width: xxs.w);
  static SizedBox get horizontalXs => SizedBox(width: xs.w);
  static SizedBox get horizontalSm => SizedBox(width: sm.w);
  static SizedBox get horizontalMd => SizedBox(width: md.w);
  static SizedBox get horizontalLg => SizedBox(width: lg.w);
  static SizedBox get horizontalXl => SizedBox(width: xl.w);
  static SizedBox get horizontalXxl => SizedBox(width: xxl.w);
}
```

```dart
// lib/core/design_system/tokens/app_radius.dart
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

abstract final class AppRadius {
  // 기본 값
  static const double xs = 4;
  static const double sm = 8;
  static const double md = 12;
  static const double lg = 16;
  static const double xl = 24;
  static const double full = 9999;

  // 반응형 값
  static double get xsR => xs.r;
  static double get smR => sm.r;
  static double get mdR => md.r;
  static double get lgR => lg.r;
  static double get xlR => xl.r;

  // 반응형 BorderRadius
  static BorderRadius get xsAllR => BorderRadius.circular(xs.r);
  static BorderRadius get smAllR => BorderRadius.circular(sm.r);
  static BorderRadius get mdAllR => BorderRadius.circular(md.r);
  static BorderRadius get lgAllR => BorderRadius.circular(lg.r);
  static BorderRadius get xlAllR => BorderRadius.circular(xl.r);

  // 정적 BorderRadius (const 필요 시)
  static const BorderRadius xsAll = BorderRadius.all(Radius.circular(xs));
  static const BorderRadius smAll = BorderRadius.all(Radius.circular(sm));
  static const BorderRadius mdAll = BorderRadius.all(Radius.circular(md));
  static const BorderRadius lgAll = BorderRadius.all(Radius.circular(lg));
  static const BorderRadius xlAll = BorderRadius.all(Radius.circular(xl));
}
```

### ScreenUtil 초기화 (선택, main.dart)

`ScreenUtil`은 기존 프로젝트에서 이미 사용 중이거나 디자인 토큰 스케일 보정이 필요한 경우에만 추가합니다. 신규 반응형 레이아웃 분기는 `MediaQuery.sizeOf`와 `LayoutBuilder`를 우선합니다.

```dart
// lib/main.dart
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:easy_localization/easy_localization.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await EasyLocalization.ensureInitialized();

  runApp(
    EasyLocalization(
      supportedLocales: const [Locale('ko'), Locale('en')],
      path: 'assets/translations',
      fallbackLocale: const Locale('ko'),
      child: const ProviderScope(
        child: MyApp(),
      ),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ScreenUtilInit(
      // 디자인 기준 사이즈 (Figma/XD 기준)
      designSize: const Size(375, 812), // iPhone 13 기준
      minTextAdapt: true,
      splitScreenMode: true,
      builder: (context, child) {
        return MaterialApp(
          debugShowCheckedModeBanner: false,
          localizationsDelegates: context.localizationDelegates,
          supportedLocales: context.supportedLocales,
          locale: context.locale,
          theme: ThemeData(
            colorScheme: ColorScheme.fromSeed(seedColor: AppColors.primary),
            useMaterial3: true,
          ),
          home: child,
        );
      },
      child: const HomePage(),
    );
  }
}
```

### ScreenUtil 사용법 (선택)

```dart
import 'package:flutter_screenutil/flutter_screenutil.dart';

// 너비 기준 스케일링 (가장 많이 사용)
Container(
  width: 200.w,        // 너비 기준 반응형
  height: 100.h,       // 높이 기준 반응형 (주의: 비율 깨질 수 있음)
  padding: EdgeInsets.all(16.w),
)

// 정사각형은 .w 또는 .r 사용
Container(
  width: 100.w,
  height: 100.w,  // 정사각형 유지
)

// 또는 .r (min(width, height) 기준)
Container(
  width: 100.r,
  height: 100.r,
)

// 폰트 사이즈
Text(
  'Hello',
  style: TextStyle(fontSize: 16.sp),
)

// 간격
Column(
  children: [
    Text('Title'),
    AppSpacing.verticalLg,  // 16.h SizedBox
    Text('Content'),
  ],
)

// 화면 비율
Container(
  width: 0.8.sw,   // 화면 너비의 80%
  height: 0.3.sh,  // 화면 높이의 30%
)
```

### 권장 사용 패턴

| 요소 | 권장 | 비고 |
|------|------|------|
| **너비** | `.w` | 기본 스케일링 |
| **높이** | `.w` 또는 `.h` | 정사각형은 `.w`, 비율 유지 필요시 `.h` |
| **폰트** | `.sp` | 시스템 접근성 설정 반영 |
| **패딩/마진** | `.w` | 일관성 유지 |
| **아이콘** | `.r` | min 기준으로 균형 |
| **Border Radius** | `.r` | 균형잡힌 곡률 |

### 2. Core Atom 예시

```dart
// lib/core/design_system/atoms/app_button.dart
import 'package:flutter/material.dart';
import '../tokens/app_colors.dart';
import '../tokens/app_typography.dart';
import '../tokens/app_spacing.dart';
import '../tokens/app_radius.dart';

enum ButtonVariant { primary, secondary, outline, text }
enum ButtonSize { small, medium, large }
enum IconPosition { left, right }

class AppButton extends StatelessWidget {
  const AppButton({
    super.key,
    required this.label,
    this.onPressed,
    this.variant = ButtonVariant.primary,
    this.size = ButtonSize.medium,
    this.icon,
    this.iconPosition = IconPosition.left,
    this.isLoading = false,
    this.isFullWidth = false,
  });

  final String label;
  final VoidCallback? onPressed;
  final ButtonVariant variant;
  final ButtonSize size;
  final IconData? icon;
  final IconPosition iconPosition;
  final bool isLoading;
  final bool isFullWidth;

  @override
  Widget build(BuildContext context) {
    final isEnabled = onPressed != null && !isLoading;

    return SizedBox(
      width: isFullWidth ? double.infinity : null,
      height: _height,
      child: switch (variant) {
        ButtonVariant.primary => ElevatedButton(
            onPressed: isEnabled ? onPressed : null,
            style: _primaryStyle,
            child: _buildChild(),
          ),
        ButtonVariant.secondary => ElevatedButton(
            onPressed: isEnabled ? onPressed : null,
            style: _secondaryStyle,
            child: _buildChild(),
          ),
        ButtonVariant.outline => OutlinedButton(
            onPressed: isEnabled ? onPressed : null,
            style: _outlineStyle,
            child: _buildChild(),
          ),
        ButtonVariant.text => TextButton(
            onPressed: isEnabled ? onPressed : null,
            style: _textButtonStyle,
            child: _buildChild(),
          ),
      },
    );
  }

  Widget _buildChild() {
    if (isLoading) {
      return SizedBox(
        width: 20,
        height: 20,
        child: CircularProgressIndicator(
          strokeWidth: 2,
          color: variant == ButtonVariant.primary
              ? AppColors.textOnPrimary
              : AppColors.primary,
        ),
      );
    }

    if (icon == null) {
      return Text(label, style: _textStyle);
    }

    final iconWidget = Icon(icon, size: _iconSize);
    final spacing = SizedBox(width: AppSpacing.sm);

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: iconPosition == IconPosition.left
          ? [iconWidget, spacing, Text(label)]
          : [Text(label), spacing, iconWidget],
    );
  }

  double get _height => switch (size) {
        ButtonSize.small => 36,
        ButtonSize.medium => 44,
        ButtonSize.large => 52,
      };

  double get _iconSize => switch (size) {
        ButtonSize.small => 16,
        ButtonSize.medium => 20,
        ButtonSize.large => 24,
      };

  TextStyle get _textStyle => switch (size) {
        ButtonSize.small => AppTypography.labelMedium,
        ButtonSize.medium => AppTypography.labelLarge,
        ButtonSize.large => AppTypography.titleSmall,
      };

  ButtonStyle get _primaryStyle => ElevatedButton.styleFrom(
        backgroundColor: AppColors.primary,
        foregroundColor: AppColors.textOnPrimary,
        disabledBackgroundColor: AppColors.disabled,
        shape: RoundedRectangleBorder(borderRadius: AppRadius.smAll),
        padding: _padding,
      );

  ButtonStyle get _secondaryStyle => ElevatedButton.styleFrom(
        backgroundColor: AppColors.primaryLight.withOpacity(0.1),
        foregroundColor: AppColors.primary,
        shape: RoundedRectangleBorder(borderRadius: AppRadius.smAll),
        padding: _padding,
        elevation: 0,
      );

  ButtonStyle get _outlineStyle => OutlinedButton.styleFrom(
        foregroundColor: AppColors.primary,
        side: const BorderSide(color: AppColors.primary),
        shape: RoundedRectangleBorder(borderRadius: AppRadius.smAll),
        padding: _padding,
      );

  ButtonStyle get _textButtonStyle => TextButton.styleFrom(
        foregroundColor: AppColors.primary,
        padding: _padding,
      );

  EdgeInsets get _padding => switch (size) {
        ButtonSize.small => const EdgeInsets.symmetric(horizontal: 12),
        ButtonSize.medium => const EdgeInsets.symmetric(horizontal: 16),
        ButtonSize.large => const EdgeInsets.symmetric(horizontal: 24),
      };
}
```

### 3. Feature Atomic 예시

```dart
// lib/features/product/presentation/widgets/atomic/organisms/product_card.dart
import 'package:flutter/material.dart';
import 'package:{app}/core/design_system/atoms/app_text.dart';
import 'package:{app}/core/design_system/atoms/app_button.dart';
import 'package:{app}/core/design_system/atoms/app_image.dart';
import 'package:{app}/core/design_system/tokens/app_colors.dart';
import 'package:{app}/core/design_system/tokens/app_spacing.dart';
import 'package:{app}/core/design_system/tokens/app_radius.dart';
import '../../../domain/entities/product_entity.dart';
import '../molecules/product_price_tag.dart';

/// Product Feature 전용 Organism
/// Core의 Atoms/Molecules를 조합하여 Feature 특화 컴포넌트 구성
class ProductCard extends StatelessWidget {
  const ProductCard({
    super.key,
    required this.product,
    required this.onTap,
    this.onAddToCart,
  });

  final ProductEntity product;
  final VoidCallback onTap;
  final VoidCallback? onAddToCart;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: AppRadius.mdAll,
          boxShadow: [
            BoxShadow(
              color: AppColors.textPrimary.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 이미지 (Core Atom)
            ClipRRect(
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(AppRadius.md),
              ),
              child: AppImage(
                url: product.imageUrl,
                height: 160,
                width: double.infinity,
                fit: BoxFit.cover,
              ),
            ),

            Padding(
              padding: const EdgeInsets.all(AppSpacing.md),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 제목 (Core Atom)
                  AppText(
                    product.name,
                    variant: TextVariant.titleSmall,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),

                  const SizedBox(height: AppSpacing.xs),

                  // 가격 태그 (Feature Molecule)
                  ProductPriceTag(
                    price: product.price,
                    originalPrice: product.originalPrice,
                  ),

                  const SizedBox(height: AppSpacing.sm),

                  // 장바구니 버튼 (Core Atom)
                  if (onAddToCart != null)
                    AppButton(
                      label: '장바구니 담기',
                      onPressed: onAddToCart,
                      size: ButtonSize.small,
                      isFullWidth: true,
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

```dart
// lib/features/product/presentation/widgets/atomic/molecules/product_price_tag.dart
import 'package:flutter/material.dart';
import 'package:{app}/core/design_system/atoms/app_text.dart';
import 'package:{app}/core/design_system/tokens/app_colors.dart';
import 'package:{app}/core/design_system/tokens/app_spacing.dart';
import 'package:intl/intl.dart';

/// Product Feature 전용 Molecule
class ProductPriceTag extends StatelessWidget {
  const ProductPriceTag({
    super.key,
    required this.price,
    this.originalPrice,
  });

  final int price;
  final int? originalPrice;

  @override
  Widget build(BuildContext context) {
    final formatter = NumberFormat('#,###');
    final hasDiscount = originalPrice != null && originalPrice! > price;

    return Row(
      children: [
        // 할인가
        AppText(
          '${formatter.format(price)}원',
          variant: TextVariant.titleMedium,
          color: AppColors.primary,
        ),

        if (hasDiscount) ...[
          const SizedBox(width: AppSpacing.sm),

          // 원가 (취소선)
          AppText(
            '${formatter.format(originalPrice)}원',
            variant: TextVariant.bodySmall,
            color: AppColors.textTertiary,
            decoration: TextDecoration.lineThrough,
          ),

          const SizedBox(width: AppSpacing.xs),

          // 할인율
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: AppSpacing.xs,
              vertical: 2,
            ),
            decoration: BoxDecoration(
              color: AppColors.error.withOpacity(0.1),
              borderRadius: BorderRadius.circular(4),
            ),
            child: AppText(
              '${_discountPercent}%',
              variant: TextVariant.labelSmall,
              color: AppColors.error,
            ),
          ),
        ],
      ],
    );
  }

  int get _discountPercent {
    if (originalPrice == null || originalPrice! <= price) return 0;
    return ((originalPrice! - price) / originalPrice! * 100).round();
  }
}
```

---

## 네이밍 규칙

| 계층 | Core | Feature |
|------|------|---------|
| Tokens | `App{Name}` | - |
| Atoms | `App{Name}` | `{Feature}{Name}` |
| Molecules | 기능 설명 | `{Feature}{Name}` |
| Organisms | `App{Name}` | `{Feature}{Name}` |
| Templates | `{Name}Template` | `{Feature}Template` |
| Pages | - | `{Feature}{Name}Page` |

---

## 분류 기준

| 질문 | Yes | No |
|------|-----|-----|
| 더 쪼갤 수 있나? | 상위 계층 | Atom |
| 단일 책임인가? | Molecule | Organism |
| 레이아웃 구조인가? | Template | Organism |
| 데이터/상태 연동? | Page | Template |
| 2개+ Feature에서 사용? | Core | Feature |

---

## Core 승격 체크리스트

Feature 위젯을 Core로 승격할 때:

- [ ] 2개 이상의 Feature에서 사용됨
- [ ] Feature 특화 로직 제거 완료
- [ ] 범용적인 Props 설계
- [ ] 기존 Feature 사용처 import 수정
- [ ] Widgetbook에 Use Case 추가

## References

- `_references/RECENT-FLUTTER-CHANGES.md`
- `_references/QUALITY-CODE-PATTERN.md`
- `_references/ATOMIC-DESIGN-PATTERN.md`
