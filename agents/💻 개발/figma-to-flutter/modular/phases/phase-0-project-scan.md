---
name: "Phase 0: Project Scan"
description: "Flutter project structure analysis"
---

# Phase 0: Project Scan

> Flutter 프로젝트 구조 분석

---

## 실행 조건

- Flutter 프로젝트 루트에서 실행
- `pubspec.yaml` 존재 확인

---

## Step 0-1: 프로젝트 감지

```bash
# Flutter 프로젝트 확인
flutter --version
cat pubspec.yaml
```

### 필수 파일 체크

```
[project_root]/
├── pubspec.yaml          # 필수
├── lib/
│   └── main.dart         # 필수
├── assets/               # 권장
└── test/                 # 권장
```

---

## Step 0-2: 의존성 확인

### pubspec.yaml 분석

```yaml
# 필수 의존성
dependencies:
  flutter:
    sdk: flutter

# 권장 의존성
  flutter_svg: ^2.0.0      # SVG 지원
  cached_network_image: ^3.3.0  # 이미지 캐싱
  google_fonts: ^6.0.0     # 구글 폰트
```

### 권장 dev 의존성

```yaml
dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^4.0.0
  build_runner: ^2.4.0
```

---

## Step 0-3: 디렉토리 구조 확인

### Clean Architecture 구조

```
lib/
├── core/                 # 앱 핵심 설정
│   ├── theme/           # 테마 관련
│   ├── utils/           # 유틸리티
│   └── widgets/         # 공통 위젯
│
├── features/            # 기능별 모듈
│   └── [feature_name]/
│       ├── data/
│       ├── domain/
│       └── presentation/
│           ├── pages/
│           └── widgets/
│
├── shared/              # 공유 리소스
│   └── widgets/
│
└── main.dart
```

### 심플 구조 (소규모 프로젝트)

```
lib/
├── models/
├── screens/
├── widgets/
├── theme/
├── utils/
└── main.dart
```

---

## Step 0-4: 테마 설정 확인

### 기존 테마 파일 검색

```bash
# 테마 관련 파일 검색
find lib -name "*theme*" -o -name "*color*" -o -name "*style*"
```

### ThemeData 패턴 확인

```dart
// lib/core/theme/app_theme.dart
class AppTheme {
  static ThemeData get light => ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: AppColors.primary,
    ),
    // ...
  );

  static ThemeData get dark => ThemeData.dark().copyWith(
    // ...
  );
}
```

---

## Step 0-5: 에셋 설정 확인

### pubspec.yaml 에셋 섹션

```yaml
flutter:
  assets:
    - assets/images/
    - assets/icons/
    - assets/fonts/

  fonts:
    - family: Pretendard
      fonts:
        - asset: assets/fonts/Pretendard-Regular.otf
        - asset: assets/fonts/Pretendard-Bold.otf
          weight: 700
```

---

## 산출물

```markdown
# Project Scan Report

## Project Info
- Name: my_app
- Flutter Version: 3.24.0
- Dart Version: 3.5.0

## Structure
- Architecture: Clean Architecture
- State Management: Riverpod (detected)
- Routing: go_router (detected)

## Theme Status
- [x] ThemeData 설정됨
- [x] ColorScheme 정의됨
- [ ] TextTheme 커스터마이징 필요
- [ ] 간격 상수 정의 필요

## Assets Status
- [x] assets/images/ 존재
- [x] assets/icons/ 존재
- [ ] 폰트 설정 필요

## Dependencies to Add
- flutter_svg: ^2.0.0
- cached_network_image: ^3.3.0

## Next Phase
Phase 1: Design Scan 진행 가능
```
