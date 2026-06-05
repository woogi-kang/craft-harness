---
name: refactor
description: |
  코드 리팩토링을 수행합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Refactor Skill

코드 리팩토링을 수행합니다.

## Triggers

- "리팩토링", "refactor", "코드 정리"

---

## 리팩토링 원칙

### 1. DRY (Don't Repeat Yourself)

```dart
// ❌ Bad: 중복 코드
Widget buildUserCard(User user) {
  return Card(
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Text(user.name, style: const TextStyle(fontSize: 18)),
          Text(user.email),
        ],
      ),
    ),
  );
}

Widget buildAdminCard(Admin admin) {
  return Card(
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Text(admin.name, style: const TextStyle(fontSize: 18)),
          Text(admin.email),
          Text('Admin'),
        ],
      ),
    ),
  );
}

// ✅ Good: 공통 컴포넌트 추출
class PersonCard extends StatelessWidget {
  final String name;
  final String email;
  final Widget? badge;

  const PersonCard({
    required this.name,
    required this.email,
    this.badge,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Text(name, style: const TextStyle(fontSize: 18)),
            Text(email),
            if (badge != null) badge!,
          ],
        ),
      ),
    );
  }
}
```

### 2. 함수/메서드 추출

```dart
// ❌ Bad: 긴 함수
Future<void> processOrder() async {
  // 검증 로직 (20줄)
  // 결제 로직 (30줄)
  // 알림 로직 (15줄)
}

// ✅ Good: 단일 책임 함수
Future<void> processOrder() async {
  await _validateOrder();
  await _processPayment();
  await _sendNotifications();
}

Future<void> _validateOrder() async { ... }
Future<void> _processPayment() async { ... }
Future<void> _sendNotifications() async { ... }
```

### 3. 네이밍 개선

```dart
// ❌ Bad: 불명확한 이름
var d = DateTime.now();
var l = <String>[];
void fn(int x) { ... }

// ✅ Good: 명확한 이름
var currentDateTime = DateTime.now();
var userNames = <String>[];
void calculateTotalPrice(int quantity) { ... }
```

### 4. 조건문 단순화

```dart
// ❌ Bad: 중첩 조건문
if (user != null) {
  if (user.isActive) {
    if (user.hasPermission) {
      return true;
    }
  }
}
return false;

// ✅ Good: Guard clause
if (user == null) return false;
if (!user.isActive) return false;
if (!user.hasPermission) return false;
return true;

// ✅ Better: 조건 결합
if (user == null || !user.isActive || !user.hasPermission) {
  return false;
}
return true;
```

### 5. Extension 활용

```dart
// ❌ Bad: 유틸리티 함수
String formatPrice(int price) => '${price.toString().replaceAllMapped(
  RegExp(r'(\d)(?=(\d{3})+(?!\d))'),
  (m) => '${m[1]},',
)}원';

// ✅ Good: Extension
extension IntX on int {
  String get formattedPrice => '${toString().replaceAllMapped(
    RegExp(r'(\d)(?=(\d{3})+(?!\d))'),
    (m) => '${m[1]},',
  )}원';
}

// 사용
final price = 10000.formattedPrice; // "10,000원"
```

---

## 리팩토링 체크리스트

### 코드 품질
- [ ] 중복 코드 제거
- [ ] 긴 함수 분리 (20줄 이하)
- [ ] 네이밍 명확화
- [ ] 매직 넘버 상수화
- [ ] 조건문 단순화

### 아키텍처
- [ ] 단일 책임 원칙 준수
- [ ] 의존성 방향 확인
- [ ] 불필요한 추상화 제거
- [ ] 레이어 경계 명확화

### 테스트
- [ ] 테스트 커버리지 유지
- [ ] 테스트 통과 확인
