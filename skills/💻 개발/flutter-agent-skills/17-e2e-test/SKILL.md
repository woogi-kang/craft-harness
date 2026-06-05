---
name: e2e-test
description: |
  Patrol을 사용한 E2E 통합 테스트를 작성합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# E2E Test Skill

Extends: `../../_shared/e2e-test/SKILL.md` (공통 E2E 테스트 원칙 참조)

Patrol을 사용한 E2E 통합 테스트를 작성합니다.

## Triggers

- "e2e test", "통합 테스트", "patrol"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `flowName` | ✅ | 테스트할 사용자 흐름 |
| `steps` | ✅ | 테스트 단계 |

---

## 설정

Flutter의 공식 `integration_test`는 widget test와 같은 finder/tester API로 앱 전체 사용자 흐름을 검증합니다. Patrol은 권한 다이얼로그, 알림, 네이티브 시스템 UI처럼 Flutter 바깥 상호작용이 필요한 경우 우선 사용합니다.

### pubspec.yaml

```yaml
dev_dependencies:
  patrol: ^4.6.0
```

### patrol.yaml

```yaml
app_name: My App
android:
  package_name: com.example.app
ios:
  bundle_id: com.example.app
```

---

## Test Templates

### 기본 E2E Test

```dart
// integration_test/auth_flow_test.dart
import 'package:patrol/patrol.dart';

void main() {
  patrolTest(
    'User can login and see home page',
    ($) async {
      // 앱 시작
      await $.pumpWidgetAndSettle(const MyApp());

      // 로그인 페이지 확인
      await $('이메일').waitUntilVisible();

      // 이메일 입력
      await $(#emailInput).enterText('test@example.com');

      // 비밀번호 입력
      await $(#passwordInput).enterText('password123');

      // 로그인 버튼 탭
      await $('로그인').tap();

      // 홈 페이지로 이동 확인
      await $('홈').waitUntilVisible();

      // 사용자 정보 확인
      expect($('환영합니다'), findsOneWidget);
    },
  );
}
```

### CRUD Flow Test

```dart
// integration_test/{feature}_crud_test.dart
void main() {
  patrolTest(
    '{Feature} CRUD flow',
    ($) async {
      await $.pumpWidgetAndSettle(const MyApp());

      // 로그인
      await _performLogin($);

      // {Feature} 목록 페이지로 이동
      await $('메뉴').tap();
      await $('{Feature}').tap();

      // CREATE: 새 아이템 생성
      await $(Icons.add).tap();
      await $(#nameInput).enterText('New Item');
      await $(#descriptionInput).enterText('Description');
      await $('저장').tap();

      // 목록에서 확인
      await $('New Item').waitUntilVisible();

      // READ: 상세 페이지
      await $('New Item').tap();
      expect($('Description'), findsOneWidget);

      // UPDATE: 수정
      await $('수정').tap();
      await $(#nameInput).enterText('Updated Item');
      await $('저장').tap();
      await $('Updated Item').waitUntilVisible();

      // DELETE: 삭제
      await $('삭제').tap();
      await $('확인').tap();
      expect($('Updated Item'), findsNothing);
    },
  );

  Future<void> _performLogin(PatrolIntegrationTester $) async {
    await $(#emailInput).enterText('test@example.com');
    await $(#passwordInput).enterText('password');
    await $('로그인').tap();
    await $('홈').waitUntilVisible();
  }
}
```

### 네이티브 상호작용 Test

```dart
// integration_test/permissions_test.dart
void main() {
  patrolTest(
    'Camera permission flow',
    ($) async {
      await $.pumpWidgetAndSettle(const MyApp());
      await _performLogin($);

      // 카메라 버튼 탭
      await $('카메라').tap();

      // 네이티브 권한 다이얼로그 처리
      await $.native.grantPermissionWhenInUse();

      // 카메라 미리보기 확인
      await $(#cameraPreview).waitUntilVisible();
    },
  );

  patrolTest(
    'Location permission flow',
    ($) async {
      await $.pumpWidgetAndSettle(const MyApp());

      // 위치 버튼 탭
      await $('위치 확인').tap();

      // 권한 허용
      await $.native.grantPermissionWhileUsingApp();

      // 위치 정보 표시 확인
      await $('현재 위치').waitUntilVisible();
    },
  );
}
```

### Push Notification Test

```dart
// integration_test/notification_test.dart
void main() {
  patrolTest(
    'Push notification handling',
    ($) async {
      await $.pumpWidgetAndSettle(const MyApp());
      await _performLogin($);

      // 알림 권한 허용
      await $.native.grantPermissionOnlyThisTime();

      // 알림 대기 및 탭
      await $.native.waitForNotification(
        title: 'New Message',
        timeout: const Duration(seconds: 30),
      );
      await $.native.tapOnNotification(title: 'New Message');

      // 메시지 화면 확인
      await $('메시지 상세').waitUntilVisible();
    },
  );
}
```

---

## 테스트 실행

```bash
# 연결된 디바이스에서 실행
patrol test

# 특정 테스트 실행
patrol test integration_test/auth_flow_test.dart

# Hot Restart 개발 모드
patrol develop

# CI 모드
patrol test --ci

# 특정 디바이스
patrol test -d "iPhone 15 Pro"
```

---

## Selector 사용법

```dart
// 텍스트로 찾기
await $('로그인').tap();

// Key로 찾기
await $(#loginButton).tap();

// 타입으로 찾기
await $(ElevatedButton).tap();

// 아이콘으로 찾기
await $(Icons.add).tap();

// 체이닝
await $(Scaffold).$(AppBar).$('Title').tap();

// 인덱스
await $('Item').at(0).tap();
```

## References

- `_references/RECENT-FLUTTER-CHANGES.md`
- `_references/QUALITY-CODE-PATTERN.md`
- `_references/TEST-PATTERN.md`
