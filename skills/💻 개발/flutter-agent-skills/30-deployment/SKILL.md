---
name: deployment
description: |
  Fastlane을 활용한 자동 배포 파이프라인을 구성합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Deployment Skill

Fastlane을 활용한 자동 배포 파이프라인을 구성합니다.

## Triggers

- "배포", "deployment", "fastlane", "release", "앱 출시"

---

## SDK 기준

- 배포 워크플로우의 Flutter 버전은 앱 `pubspec.yaml`과 CI 설정에 맞춘다. 최신 신규 프로젝트 기본값은 Flutter `3.44.0`이다.
- Android 배포는 Java 17 이상과 min SDK API 24 이상을 기본값으로 검토한다.
- iOS/macOS 네이티브 의존성은 Swift Package Manager 우선, CocoaPods fallback 순서로 점검한다.

---

## 배포 파이프라인

```
┌─────────────────────────────────────────────────────────────┐
│                    Deployment Pipeline                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐  │
│  │  Build   │ → │  Test    │ → │  Sign    │ → │  Deploy  │  │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘  │
│       ↓              ↓              ↓              ↓        │
│   Flutter       Unit/Widget    Certificates    App Store    │
│   Build         Golden/E2E     Provisioning    Play Store   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Fastlane 설치

```bash
# macOS
brew install fastlane

# 또는 Ruby gem
gem install fastlane

# 프로젝트에서 초기화
cd ios && fastlane init
cd android && fastlane init
```

---

## 2. iOS Fastlane 설정

### Fastfile

```ruby
# ios/fastlane/Fastfile
default_platform(:ios)

platform :ios do

  # 환경 변수
  APP_IDENTIFIER = ENV['APP_IDENTIFIER'] || 'com.example.myapp'
  TEAM_ID = ENV['TEAM_ID']

  desc "Sync certificates and profiles"
  lane :sync_certs do
    match(
      type: "appstore",
      app_identifier: APP_IDENTIFIER,
      readonly: true
    )
    match(
      type: "development",
      app_identifier: APP_IDENTIFIER,
      readonly: true
    )
  end

  desc "Build and upload to TestFlight (Dev)"
  lane :beta_dev do
    sync_certs

    # Increment build number
    increment_build_number(
      build_number: ENV['BUILD_NUMBER'] || latest_testflight_build_number + 1
    )

    # Build Flutter
    sh("cd .. && flutter build ipa --flavor dev -t lib/main_dev.dart --release --export-options-plist=ios/ExportOptions.plist")

    # Upload to TestFlight
    upload_to_testflight(
      skip_waiting_for_build_processing: true,
      ipa: "../build/ios/ipa/MyApp-Dev.ipa"
    )

    # Slack notification
    slack(
      message: "🚀 Dev build uploaded to TestFlight!",
      slack_url: ENV['SLACK_WEBHOOK_URL']
    )
  end

  desc "Build and upload to TestFlight (Staging)"
  lane :beta_staging do
    sync_certs

    increment_build_number(
      build_number: ENV['BUILD_NUMBER'] || latest_testflight_build_number + 1
    )

    sh("cd .. && flutter build ipa --flavor staging -t lib/main_staging.dart --release --obfuscate --split-debug-info=build/debug-info --export-options-plist=ios/ExportOptions.plist")

    upload_to_testflight(
      skip_waiting_for_build_processing: true,
      ipa: "../build/ios/ipa/MyApp-Staging.ipa"
    )

    slack(
      message: "🎯 Staging build uploaded to TestFlight!",
      slack_url: ENV['SLACK_WEBHOOK_URL']
    )
  end

  desc "Build and upload to App Store (Production)"
  lane :release do
    sync_certs

    # Version bump
    version = prompt(text: "Enter version number (e.g., 1.2.0): ")
    increment_version_number(version_number: version)
    increment_build_number(build_number: 1)

    sh("cd .. && flutter build ipa --flavor prod -t lib/main_prod.dart --release --obfuscate --split-debug-info=build/debug-info --export-options-plist=ios/ExportOptions.plist")

    # Upload to App Store Connect
    upload_to_app_store(
      submit_for_review: false,
      automatic_release: false,
      ipa: "../build/ios/ipa/MyApp.ipa",
      precheck_include_in_app_purchases: false
    )

    slack(
      message: "🎉 Production build uploaded to App Store Connect!",
      slack_url: ENV['SLACK_WEBHOOK_URL']
    )
  end
end
```

### Matchfile

```ruby
# ios/fastlane/Matchfile
git_url(ENV['MATCH_GIT_URL'])
storage_mode("git")

type("appstore")
app_identifier(["com.example.myapp", "com.example.myapp.dev", "com.example.myapp.staging"])
username(ENV['APPLE_ID'])
team_id(ENV['TEAM_ID'])
```

### Appfile

```ruby
# ios/fastlane/Appfile
app_identifier(ENV['APP_IDENTIFIER'] || "com.example.myapp")
apple_id(ENV['APPLE_ID'])
team_id(ENV['TEAM_ID'])

for_platform :ios do
  for_lane :beta_dev do
    app_identifier("com.example.myapp.dev")
  end

  for_lane :beta_staging do
    app_identifier("com.example.myapp.staging")
  end
end
```

---

## 3. Android Fastlane 설정

### Fastfile

```ruby
# android/fastlane/Fastfile
default_platform(:android)

platform :android do

  desc "Build and upload to Play Store Internal Track (Dev)"
  lane :beta_dev do
    # Build Flutter AAB
    sh("cd .. && flutter build appbundle --flavor dev -t lib/main_dev.dart --release")

    upload_to_play_store(
      track: 'internal',
      aab: '../build/app/outputs/bundle/devRelease/app-dev-release.aab',
      skip_upload_metadata: true,
      skip_upload_images: true,
      skip_upload_screenshots: true
    )

    slack(
      message: "🚀 Dev build uploaded to Play Store Internal!",
      slack_url: ENV['SLACK_WEBHOOK_URL']
    )
  end

  desc "Build and upload to Play Store Beta Track (Staging)"
  lane :beta_staging do
    sh("cd .. && flutter build appbundle --flavor staging -t lib/main_staging.dart --release --obfuscate --split-debug-info=build/debug-info")

    upload_to_play_store(
      track: 'beta',
      aab: '../build/app/outputs/bundle/stagingRelease/app-staging-release.aab',
      skip_upload_metadata: true,
      skip_upload_images: true,
      skip_upload_screenshots: true
    )

    slack(
      message: "🎯 Staging build uploaded to Play Store Beta!",
      slack_url: ENV['SLACK_WEBHOOK_URL']
    )
  end

  desc "Build and upload to Play Store Production"
  lane :release do
    # Version code from CI or increment
    version_code = ENV['VERSION_CODE'] || (google_play_track_version_codes(track: 'production').first + 1)

    sh("cd .. && flutter build appbundle --flavor prod -t lib/main_prod.dart --release --obfuscate --split-debug-info=build/debug-info --build-number=#{version_code}")

    upload_to_play_store(
      track: 'production',
      aab: '../build/app/outputs/bundle/prodRelease/app-prod-release.aab',
      rollout: '0.1'  # 10% staged rollout
    )

    slack(
      message: "🎉 Production build uploaded to Play Store (10% rollout)!",
      slack_url: ENV['SLACK_WEBHOOK_URL']
    )
  end

  desc "Promote beta to production"
  lane :promote_to_production do
    upload_to_play_store(
      track: 'beta',
      track_promote_to: 'production',
      rollout: '0.2'  # 20% staged rollout
    )
  end
end
```

### Appfile

```ruby
# android/fastlane/Appfile
json_key_file(ENV['GOOGLE_PLAY_JSON_KEY'])
package_name(ENV['PACKAGE_NAME'] || "com.example.myapp")
```

---

## 4. GitHub Actions Integration

### Deploy Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    tags:
      - 'v*.*.*'
  workflow_dispatch:
    inputs:
      platform:
        description: 'Platform (ios/android/both)'
        required: true
        default: 'both'
      track:
        description: 'Track (dev/staging/production)'
        required: true
        default: 'staging'

jobs:
  deploy-ios:
    if: ${{ github.event.inputs.platform == 'ios' || github.event.inputs.platform == 'both' || github.event_name == 'push' }}
    runs-on: macos-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.44.0'
          channel: 'stable'
          cache: true

      - name: Install dependencies
        run: flutter pub get

      - name: Setup Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.2'
          bundler-cache: true
          working-directory: ios

      - name: Setup Fastlane Match
        env:
          MATCH_PASSWORD: ${{ secrets.MATCH_PASSWORD }}
          MATCH_GIT_URL: ${{ secrets.MATCH_GIT_URL }}
          MATCH_GIT_BASIC_AUTHORIZATION: ${{ secrets.MATCH_GIT_BASIC_AUTHORIZATION }}
        run: |
          cd ios
          bundle exec fastlane sync_certs

      - name: Deploy to TestFlight
        env:
          APP_STORE_CONNECT_API_KEY_ID: ${{ secrets.APP_STORE_CONNECT_API_KEY_ID }}
          APP_STORE_CONNECT_API_ISSUER_ID: ${{ secrets.APP_STORE_CONNECT_API_ISSUER_ID }}
          APP_STORE_CONNECT_API_KEY: ${{ secrets.APP_STORE_CONNECT_API_KEY }}
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
          BUILD_NUMBER: ${{ github.run_number }}
        run: |
          cd ios
          bundle exec fastlane beta_${{ github.event.inputs.track || 'staging' }}

  deploy-android:
    if: ${{ github.event.inputs.platform == 'android' || github.event.inputs.platform == 'both' || github.event_name == 'push' }}
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
          channel: 'stable'
          cache: true

      - name: Install dependencies
        run: flutter pub get

      - name: Setup Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.2'
          bundler-cache: true
          working-directory: android

      - name: Decode Keystore
        env:
          KEYSTORE_BASE64: ${{ secrets.KEYSTORE_BASE64 }}
        run: |
          echo $KEYSTORE_BASE64 | base64 --decode > android/app/upload-keystore.jks

      - name: Setup key.properties
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        run: |
          cat > android/key.properties << EOF
          storePassword=$KEYSTORE_PASSWORD
          keyPassword=$KEY_PASSWORD
          keyAlias=$KEY_ALIAS
          storeFile=upload-keystore.jks
          EOF

      - name: Decode Google Play Service Account
        env:
          GOOGLE_PLAY_JSON_KEY_BASE64: ${{ secrets.GOOGLE_PLAY_JSON_KEY_BASE64 }}
        run: |
          echo $GOOGLE_PLAY_JSON_KEY_BASE64 | base64 --decode > android/google-play-key.json

      - name: Deploy to Play Store
        env:
          GOOGLE_PLAY_JSON_KEY: android/google-play-key.json
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
          VERSION_CODE: ${{ github.run_number }}
        run: |
          cd android
          bundle exec fastlane beta_${{ github.event.inputs.track || 'staging' }}
```

---

## 5. Shorebird (OTA Updates)

```bash
# Shorebird CLI 설치
curl --proto '=https' --tlsv1.2 https://raw.githubusercontent.com/shorebirdtech/install/main/install.sh -sSf | bash

# 프로젝트 초기화
shorebird init

# 릴리스 빌드
shorebird release android --flavor prod
shorebird release ios --flavor prod

# 패치 배포 (코드 변경만, 네이티브 변경 불가)
shorebird patch android --flavor prod
shorebird patch ios --flavor prod
```

### Shorebird Configuration

```yaml
# shorebird.yaml
app_id: your-app-id
flavors:
  dev:
    app_id: your-dev-app-id
  staging:
    app_id: your-staging-app-id
  prod:
    app_id: your-prod-app-id
```

---

## 6. Release Checklist

### Pre-Release
- [ ] 버전 번호 업데이트 (pubspec.yaml)
- [ ] Changelog 작성
- [ ] 모든 테스트 통과 확인
- [ ] 난독화 빌드 테스트
- [ ] 스크린샷/영상 업데이트 (필요시)

### iOS Checklist
- [ ] Xcode 아카이브 빌드 성공
- [ ] 인증서/프로비저닝 프로파일 유효성
- [ ] App Store Connect 앱 정보 업데이트
- [ ] 심사 정보 작성 (테스트 계정 등)

### Android Checklist
- [ ] AAB 빌드 성공
- [ ] 서명 키 확인
- [ ] Play Console 앱 정보 업데이트
- [ ] 릴리스 노트 작성

### Post-Release
- [ ] 배포 확인
- [ ] Crashlytics 모니터링
- [ ] 사용자 피드백 모니터링
- [ ] Rollout 비율 조정 (단계적 배포)

---

## 7. Version Management

```dart
// lib/core/config/version_info.dart
class VersionInfo {
  static const String appVersion = '1.0.0';
  static const int buildNumber = 1;

  static String get fullVersion => '$appVersion+$buildNumber';

  // 버전 체크 (서버에서 최소 버전 받아오기)
  static Future<bool> isUpdateRequired() async {
    final minVersion = await _fetchMinVersion();
    return _compareVersions(appVersion, minVersion) < 0;
  }

  static int _compareVersions(String v1, String v2) {
    final parts1 = v1.split('.').map(int.parse).toList();
    final parts2 = v2.split('.').map(int.parse).toList();

    for (var i = 0; i < 3; i++) {
      if (parts1[i] > parts2[i]) return 1;
      if (parts1[i] < parts2[i]) return -1;
    }
    return 0;
  }
}
```

---

## References

- `_references/RECENT-FLUTTER-CHANGES.md`
- `25-flavor/SKILL.md`
- `22-cicd/SKILL.md`
