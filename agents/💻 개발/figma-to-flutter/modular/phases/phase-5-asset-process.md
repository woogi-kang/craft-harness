---
name: "Phase 5: Asset Process"
description: "Image and icon asset processing for Flutter"
---

# Phase 5: Asset Process

> 이미지, 아이콘, 폰트 에셋 처리

---

## 실행 조건

- Phase 4 완료
- 코드 생성 완료

---

## Step 5-1: 에셋 식별

### Figma 에셋 유형

| Type | Export Format | Flutter Usage |
|------|---------------|---------------|
| Vector/Icon | SVG | flutter_svg |
| Photo/Image | PNG/WebP | Image.asset |
| Logo | SVG or PNG | SvgPicture / Image |
| Illustration | SVG | flutter_svg |

### MCP로 에셋 목록 추출

```typescript
// 노드에서 이미지 에셋 식별
get_design_context({
  fileKey: "ABC123",
  nodeId: "123-456"
})

// 응답에서 fills 분석
{
  "fills": [
    {
      "type": "IMAGE",
      "imageRef": "abc123"
    }
  ]
}
```

---

## Step 5-2: 이미지 에셋 처리

### 다중 해상도 지원

```
assets/
└── images/
    ├── hero_image.png          # 1x (base)
    ├── 2.0x/
    │   └── hero_image.png      # 2x
    └── 3.0x/
        └── hero_image.png      # 3x
```

### pubspec.yaml 설정

```yaml
flutter:
  assets:
    - assets/images/
    - assets/images/2.0x/
    - assets/images/3.0x/
```

### 이미지 사용

```dart
// 자동 해상도 선택
Image.asset(
  'assets/images/hero_image.png',
  width: 300,
  height: 200,
  fit: BoxFit.cover,
)

// 네트워크 이미지 (캐싱)
CachedNetworkImage(
  imageUrl: 'https://example.com/image.jpg',
  placeholder: (context, url) => CircularProgressIndicator(),
  errorWidget: (context, url, error) => Icon(Icons.error),
  width: 300,
  height: 200,
  fit: BoxFit.cover,
)
```

---

## Step 5-3: SVG 아이콘 처리

### 아이콘 디렉토리 구조

```
assets/
└── icons/
    ├── home.svg
    ├── search.svg
    ├── profile.svg
    ├── settings.svg
    └── arrow_right.svg
```

### SVG 색상 처리

```dart
// 단색 아이콘 (colorFilter 사용)
SvgPicture.asset(
  'assets/icons/home.svg',
  width: 24,
  height: 24,
  colorFilter: ColorFilter.mode(
    AppColors.primary,
    BlendMode.srcIn,
  ),
)

// 다색 아이콘 (원본 유지)
SvgPicture.asset(
  'assets/icons/logo.svg',
  width: 120,
  height: 40,
)
```

### 아이콘 위젯 래퍼

```dart
// lib/shared/widgets/app_icon.dart

class AppIcon extends StatelessWidget {
  final String name;
  final double size;
  final Color? color;

  const AppIcon({
    super.key,
    required this.name,
    this.size = 24,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return SvgPicture.asset(
      'assets/icons/$name.svg',
      width: size,
      height: size,
      colorFilter: color != null
          ? ColorFilter.mode(color!, BlendMode.srcIn)
          : null,
    );
  }
}

// 사용
AppIcon(name: 'home', size: 24, color: AppColors.primary)
```

---

## Step 5-4: 폰트 처리

### 커스텀 폰트 구조

```
assets/
└── fonts/
    ├── Pretendard-Regular.otf
    ├── Pretendard-Medium.otf
    ├── Pretendard-SemiBold.otf
    └── Pretendard-Bold.otf
```

### pubspec.yaml 폰트 설정

```yaml
flutter:
  fonts:
    - family: Pretendard
      fonts:
        - asset: assets/fonts/Pretendard-Regular.otf
          weight: 400
        - asset: assets/fonts/Pretendard-Medium.otf
          weight: 500
        - asset: assets/fonts/Pretendard-SemiBold.otf
          weight: 600
        - asset: assets/fonts/Pretendard-Bold.otf
          weight: 700
```

### Google Fonts 사용 (권장)

```dart
// pubspec.yaml
dependencies:
  google_fonts: ^6.0.0

// 코드에서 사용
import 'package:google_fonts/google_fonts.dart';

Text(
  'Hello',
  style: GoogleFonts.inter(
    fontSize: 16,
    fontWeight: FontWeight.w500,
  ),
)

// 또는 TextTheme 전체 적용
ThemeData(
  textTheme: GoogleFonts.interTextTheme(),
)
```

---

## Step 5-5: 에셋 최적화

### 이미지 최적화

```bash
# PNG 최적화
pngquant --quality=65-80 assets/images/*.png

# WebP 변환 (더 작은 파일 크기)
cwebp -q 80 input.png -o output.webp
```

### SVG 최적화

```bash
# SVGO 사용
npx svgo assets/icons/*.svg --multipass
```

### 에셋 사전 로드

```dart
// 중요 이미지 사전 로드
Future<void> precacheAssets(BuildContext context) async {
  await Future.wait([
    precacheImage(AssetImage('assets/images/hero.png'), context),
    precacheImage(AssetImage('assets/images/logo.png'), context),
  ]);
}
```

---

## Step 5-6: 에셋 접근 유틸리티

### 에셋 경로 상수

```dart
// lib/core/constants/assets.dart

abstract class AppAssets {
  // Images
  static const String heroImage = 'assets/images/hero.png';
  static const String logo = 'assets/images/logo.png';
  static const String placeholder = 'assets/images/placeholder.png';

  // Icons
  static const String iconHome = 'assets/icons/home.svg';
  static const String iconSearch = 'assets/icons/search.svg';
  static const String iconProfile = 'assets/icons/profile.svg';

  // Lottie (if used)
  static const String loadingAnimation = 'assets/animations/loading.json';
}
```

### 에셋 사용 예시

```dart
Image.asset(AppAssets.heroImage)

SvgPicture.asset(AppAssets.iconHome)
```

---

## Step 5-7: 에셋 생성 스크립트

### flutter_gen 사용 (선택)

```yaml
# pubspec.yaml
dev_dependencies:
  flutter_gen_runner: ^5.3.0
  build_runner: ^2.4.0

flutter_gen:
  output: lib/gen/
  integrations:
    flutter_svg: true
```

```bash
# 에셋 코드 생성
flutter pub run build_runner build
```

```dart
// 생성된 코드 사용
import 'package:my_app/gen/assets.gen.dart';

Image.asset(Assets.images.hero.path)
Assets.icons.home.svg(width: 24)
```

---

## 산출물

```markdown
# Asset Process Report

## Images Processed
| File | Size | Optimized | Format |
|------|------|-----------|--------|
| hero.png | 245KB | 180KB | PNG |
| logo.png | 12KB | 8KB | PNG |

## Icons Processed
| Icon | Size | Optimized |
|------|------|-----------|
| home.svg | 1.2KB | 0.8KB |
| search.svg | 0.9KB | 0.6KB |
| profile.svg | 1.1KB | 0.7KB |

## Fonts
| Family | Weights | Source |
|--------|---------|--------|
| Inter | 400, 500, 600, 700 | Google Fonts |

## pubspec.yaml Updates
```yaml
flutter:
  assets:
    - assets/images/
    - assets/images/2.0x/
    - assets/images/3.0x/
    - assets/icons/
```

## Files Created
- lib/core/constants/assets.dart
- lib/shared/widgets/app_icon.dart

## Total Assets
- Images: 5
- Icons: 12
- Fonts: 1 family (4 weights)

## Next Phase
Phase 6: Pixel-Perfect 진행 가능
```
