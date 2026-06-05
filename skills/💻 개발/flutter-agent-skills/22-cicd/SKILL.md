---
name: cicd
description: |
  GitHub Actions 기반 Flutter CI/CD 파이프라인을 구성합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# CI/CD Skill

Extends: `../../_shared/cicd/SKILL.md` (공통 CI/CD 원칙 참조)

GitHub Actions 기반 Flutter CI/CD 파이프라인을 구성합니다.

## Triggers

- "ci/cd", "github actions", "배포 자동화", "ci 설정"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `platforms` | ✅ | 대상 플랫폼 (android, ios, web) |
| `coverageThreshold` | ❌ | 최소 커버리지 (기본 60%) |

---

## SDK 기준

- CI의 Flutter 버전은 `pubspec.yaml` SDK constraint와 맞춘다. 최신 신규 프로젝트 기본값은 Flutter `3.44.0`이다.
- Android 빌드는 Java 17 이상을 기본값으로 둔다.
- 최신 패키지 세트를 쓰는 경우 최소 Flutter `3.38.1`, Dart `3.10.0` 이상을 확인한다.

---

## Output Templates

### 1. 기본 CI Workflow

```yaml
# .github/workflows/ci.yml
name: Flutter CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  analyze:
    name: Analyze & Test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.44.0'
          cache: true

      - name: Get dependencies
        run: flutter pub get

      - name: Generate code
        run: dart run build_runner build --delete-conflicting-outputs

      - name: Analyze code
        run: flutter analyze --fatal-infos

      - name: Format check
        run: dart format --set-exit-if-changed .

      - name: Run tests
        run: flutter test --coverage

      - name: Check coverage threshold
        run: |
          COVERAGE=$(lcov --summary coverage/lcov.info 2>/dev/null | grep 'lines' | cut -d':' -f2 | cut -d'%' -f1 | tr -d ' ')
          echo "Coverage: $COVERAGE%"
          if (( $(echo "$COVERAGE < 60" | bc -l) )); then
            echo "Coverage is below 60%"
            exit 1
          fi

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: coverage/lcov.info
          fail_ci_if_error: true

  golden-test:
    name: Golden Tests
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.44.0'
          cache: true

      - name: Get dependencies
        run: flutter pub get

      - name: Generate code
        run: dart run build_runner build --delete-conflicting-outputs

      - name: Run golden tests
        run: flutter test --tags=golden

      - name: Upload golden failures
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: golden-failures
          path: test/**/failures/
```

### 2. Android Build & Release

```yaml
# .github/workflows/android-release.yml
name: Android Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-android:
    name: Build Android
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Setup Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.44.0'
          cache: true

      - name: Get dependencies
        run: flutter pub get

      - name: Generate code
        run: dart run build_runner build --delete-conflicting-outputs

      - name: Decode keystore
        run: |
          echo "${{ secrets.ANDROID_KEYSTORE_BASE64 }}" | base64 --decode > android/app/upload-keystore.jks

      - name: Create key.properties
        run: |
          cat > android/key.properties << EOF
          storePassword=${{ secrets.ANDROID_KEYSTORE_PASSWORD }}
          keyPassword=${{ secrets.ANDROID_KEY_PASSWORD }}
          keyAlias=${{ secrets.ANDROID_KEY_ALIAS }}
          storeFile=upload-keystore.jks
          EOF

      - name: Build APK
        run: flutter build apk --release

      - name: Build App Bundle
        run: flutter build appbundle --release

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: android-apk
          path: build/app/outputs/flutter-apk/app-release.apk

      - name: Upload AAB
        uses: actions/upload-artifact@v4
        with:
          name: android-aab
          path: build/app/outputs/bundle/release/app-release.aab

      - name: Upload to Play Store
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.GOOGLE_PLAY_SERVICE_ACCOUNT }}
          packageName: com.example.app
          releaseFiles: build/app/outputs/bundle/release/app-release.aab
          track: internal
```

### 3. iOS Build & Release

```yaml
# .github/workflows/ios-release.yml
name: iOS Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-ios:
    name: Build iOS
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.44.0'
          cache: true

      - name: Get dependencies
        run: flutter pub get

      - name: Generate code
        run: dart run build_runner build --delete-conflicting-outputs

      - name: Install Apple certificate
        env:
          CERTIFICATE_BASE64: ${{ secrets.IOS_CERTIFICATE_BASE64 }}
          CERTIFICATE_PASSWORD: ${{ secrets.IOS_CERTIFICATE_PASSWORD }}
          PROVISIONING_PROFILE_BASE64: ${{ secrets.IOS_PROVISIONING_PROFILE_BASE64 }}
        run: |
          # Create temp keychain
          KEYCHAIN_PATH=$RUNNER_TEMP/app-signing.keychain-db
          KEYCHAIN_PASSWORD=$(openssl rand -base64 32)

          security create-keychain -p "$KEYCHAIN_PASSWORD" $KEYCHAIN_PATH
          security set-keychain-settings -lut 21600 $KEYCHAIN_PATH
          security unlock-keychain -p "$KEYCHAIN_PASSWORD" $KEYCHAIN_PATH

          # Import certificate
          echo "$CERTIFICATE_BASE64" | base64 --decode > $RUNNER_TEMP/certificate.p12
          security import $RUNNER_TEMP/certificate.p12 -P "$CERTIFICATE_PASSWORD" -A -t cert -f pkcs12 -k $KEYCHAIN_PATH
          security list-keychain -d user -s $KEYCHAIN_PATH

          # Install provisioning profile
          mkdir -p ~/Library/MobileDevice/Provisioning\ Profiles
          echo "$PROVISIONING_PROFILE_BASE64" | base64 --decode > ~/Library/MobileDevice/Provisioning\ Profiles/profile.mobileprovision

      - name: Build iOS
        run: flutter build ipa --release --export-options-plist=ios/ExportOptions.plist

      - name: Upload IPA
        uses: actions/upload-artifact@v4
        with:
          name: ios-ipa
          path: build/ios/ipa/*.ipa

      - name: Upload to App Store Connect
        env:
          APPLE_API_KEY_ID: ${{ secrets.APPLE_API_KEY_ID }}
          APPLE_ISSUER_ID: ${{ secrets.APPLE_ISSUER_ID }}
          APPLE_API_KEY_BASE64: ${{ secrets.APPLE_API_KEY_BASE64 }}
        run: |
          mkdir -p ~/.appstoreconnect/private_keys
          echo "$APPLE_API_KEY_BASE64" | base64 --decode > ~/.appstoreconnect/private_keys/AuthKey_$APPLE_API_KEY_ID.p8
          xcrun altool --upload-app -f build/ios/ipa/*.ipa -t ios --apiKey $APPLE_API_KEY_ID --apiIssuer $APPLE_ISSUER_ID
```

### 4. Web Build & Deploy (Firebase Hosting)

```yaml
# .github/workflows/web-deploy.yml
name: Web Deploy

on:
  push:
    branches: [main]

jobs:
  build-web:
    name: Build & Deploy Web
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.44.0'
          cache: true

      - name: Get dependencies
        run: flutter pub get

      - name: Generate code
        run: dart run build_runner build --delete-conflicting-outputs

      - name: Build web
        run: flutter build web --release --web-renderer canvaskit

      - name: Deploy to Firebase Hosting
        uses: FirebaseExtended/action-hosting-deploy@v0
        with:
          repoToken: ${{ secrets.GITHUB_TOKEN }}
          firebaseServiceAccount: ${{ secrets.FIREBASE_SERVICE_ACCOUNT }}
          channelId: live
          projectId: your-project-id
```

---

## Secrets 설정 가이드

### Android

| Secret | 설명 |
|--------|------|
| `ANDROID_KEYSTORE_BASE64` | `base64 -i upload-keystore.jks` |
| `ANDROID_KEYSTORE_PASSWORD` | Keystore 비밀번호 |
| `ANDROID_KEY_PASSWORD` | Key 비밀번호 |
| `ANDROID_KEY_ALIAS` | Key alias |
| `GOOGLE_PLAY_SERVICE_ACCOUNT` | Play Console API JSON |

### iOS

| Secret | 설명 |
|--------|------|
| `IOS_CERTIFICATE_BASE64` | Distribution 인증서 (.p12) |
| `IOS_CERTIFICATE_PASSWORD` | 인증서 비밀번호 |
| `IOS_PROVISIONING_PROFILE_BASE64` | Provisioning Profile |
| `APPLE_API_KEY_ID` | App Store Connect API Key ID |
| `APPLE_ISSUER_ID` | App Store Connect Issuer ID |
| `APPLE_API_KEY_BASE64` | API Key (.p8) |

---

## Fastlane 대안 (선택)

```ruby
# ios/fastlane/Fastfile
default_platform(:ios)

platform :ios do
  desc "Push to TestFlight"
  lane :beta do
    build_app(
      workspace: "Runner.xcworkspace",
      scheme: "Runner",
      export_options: {
        method: "app-store"
      }
    )
    upload_to_testflight
  end
end
```

```ruby
# android/fastlane/Fastfile
default_platform(:android)

platform :android do
  desc "Deploy to Play Store Internal"
  lane :internal do
    upload_to_play_store(
      track: 'internal',
      aab: '../build/app/outputs/bundle/release/app-release.aab'
    )
  end
end
```

---

## 버전 관리

```yaml
# pubspec.yaml 버전 자동화
- name: Bump version
  run: |
    VERSION=${GITHUB_REF#refs/tags/v}
    sed -i "s/version: .*/version: $VERSION/" pubspec.yaml
```

## References

- `_references/RECENT-FLUTTER-CHANGES.md`
- `_references/TEST-PATTERN.md`
