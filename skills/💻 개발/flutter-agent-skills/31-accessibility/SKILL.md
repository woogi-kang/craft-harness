---
name: accessibility
description: |
  앱 접근성(a11y) 설정 및 베스트 프랙티스를 적용합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Accessibility Skill

앱 접근성(a11y) 설정 및 베스트 프랙티스를 적용합니다.

## Triggers

- "접근성", "accessibility", "a11y", "스크린리더", "semantics"

---

## 접근성 영역

```
┌─────────────────────────────────────────────────────────────┐
│                    Accessibility Areas                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────────┐  ┌───────────────┐  ┌─────────────────┐  │
│  │ Visual        │  │ Motor         │  │ Cognitive       │  │
│  ├───────────────┤  ├───────────────┤  ├─────────────────┤  │
│  │ • Screen      │  │ • Touch       │  │ • Simple        │  │
│  │   Reader      │  │   Target      │  │   Navigation    │  │
│  │ • Color       │  │ • Gesture     │  │ • Clear         │  │
│  │   Contrast    │  │   Alternatives│  │   Feedback      │  │
│  │ • Text        │  │ • Timeouts    │  │ • Predictable   │  │
│  │   Scaling     │  │               │  │   Behavior      │  │
│  └───────────────┘  └───────────────┘  └─────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Semantics Widget

### 기본 Semantics

```dart
// 이미지에 설명 추가
Semantics(
  label: '프로필 이미지: 홍길동님',
  child: CircleAvatar(
    backgroundImage: NetworkImage(user.profileUrl),
  ),
);

// 버튼에 설명 추가
Semantics(
  button: true,
  label: '장바구니에 추가',
  hint: '탭하여 이 상품을 장바구니에 추가합니다',
  child: IconButton(
    icon: const Icon(Icons.add_shopping_cart),
    onPressed: onAddToCart,
  ),
);

// 토글 상태 알림
Semantics(
  toggled: isEnabled,
  label: '알림',
  hint: isEnabled ? '알림이 켜져 있습니다' : '알림이 꺼져 있습니다',
  child: Switch(
    value: isEnabled,
    onChanged: onChanged,
  ),
);
```

### 복합 Semantics

```dart
// 카드 전체를 하나의 의미 단위로
Semantics(
  container: true,
  label: '상품: ${product.name}, 가격: ${product.price}원, 평점: ${product.rating}점',
  child: ProductCard(product: product),
);

// 리스트 아이템
Semantics(
  label: '${index + 1}번째 항목, ${item.title}',
  child: ListTile(title: Text(item.title)),
);
```

### Semantics 제외

```dart
// 장식용 요소 제외
ExcludeSemantics(
  child: DecorativeImage(),
);

// 또는 Semantics로 명시적 제외
Semantics(
  excludeSemantics: true,
  child: DecorativeIcon(),
);
```

---

## 2. 포커스 관리

### Focus Management

```dart
// 포커스 순서 지정
FocusTraversalGroup(
  policy: OrderedTraversalPolicy(),
  child: Column(
    children: [
      FocusTraversalOrder(
        order: const NumericFocusOrder(1),
        child: TextField(decoration: const InputDecoration(labelText: '이메일')),
      ),
      FocusTraversalOrder(
        order: const NumericFocusOrder(2),
        child: TextField(decoration: const InputDecoration(labelText: '비밀번호')),
      ),
      FocusTraversalOrder(
        order: const NumericFocusOrder(3),
        child: ElevatedButton(
          onPressed: onLogin,
          child: const Text('로그인'),
        ),
      ),
    ],
  ),
);
```

### Autofocus & Focus Request

```dart
class LoginForm extends StatefulWidget {
  @override
  State<LoginForm> createState() => _LoginFormState();
}

class _LoginFormState extends State<LoginForm> {
  final _emailFocusNode = FocusNode();
  final _passwordFocusNode = FocusNode();

  @override
  void dispose() {
    _emailFocusNode.dispose();
    _passwordFocusNode.dispose();
    super.dispose();
  }

  void _onEmailSubmitted(String value) {
    // 다음 필드로 포커스 이동
    _passwordFocusNode.requestFocus();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        TextField(
          focusNode: _emailFocusNode,
          autofocus: true, // 페이지 로드시 자동 포커스
          onSubmitted: _onEmailSubmitted,
          decoration: const InputDecoration(labelText: '이메일'),
        ),
        TextField(
          focusNode: _passwordFocusNode,
          decoration: const InputDecoration(labelText: '비밀번호'),
        ),
      ],
    );
  }
}
```

---

## 3. 색상 대비

### 대비율 계산

```dart
// lib/core/design_system/accessibility/contrast_checker.dart
class ContrastChecker {
  /// WCAG 2.1 대비율 계산
  static double calculateContrastRatio(Color foreground, Color background) {
    final l1 = _calculateRelativeLuminance(foreground);
    final l2 = _calculateRelativeLuminance(background);

    final lighter = l1 > l2 ? l1 : l2;
    final darker = l1 > l2 ? l2 : l1;

    return (lighter + 0.05) / (darker + 0.05);
  }

  static double _calculateRelativeLuminance(Color color) {
    final r = _linearize(color.red / 255);
    final g = _linearize(color.green / 255);
    final b = _linearize(color.blue / 255);

    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  }

  static double _linearize(double value) {
    return value <= 0.03928
        ? value / 12.92
        : pow((value + 0.055) / 1.055, 2.4).toDouble();
  }

  /// WCAG AA 기준 (4.5:1 for normal text, 3:1 for large text)
  static bool meetsAA(Color foreground, Color background, {bool isLargeText = false}) {
    final ratio = calculateContrastRatio(foreground, background);
    return isLargeText ? ratio >= 3.0 : ratio >= 4.5;
  }

  /// WCAG AAA 기준 (7:1 for normal text, 4.5:1 for large text)
  static bool meetsAAA(Color foreground, Color background, {bool isLargeText = false}) {
    final ratio = calculateContrastRatio(foreground, background);
    return isLargeText ? ratio >= 4.5 : ratio >= 7.0;
  }
}
```

### 접근성 친화적 색상 토큰

```dart
// lib/core/design_system/tokens/accessible_colors.dart
class AccessibleColors {
  // 배경에 따른 접근성 텍스트 색상
  static Color getAccessibleTextColor(Color background) {
    final luminance = background.computeLuminance();
    return luminance > 0.5 ? Colors.black87 : Colors.white;
  }

  // Primary 색상 팔레트 (대비율 보장)
  static const primary = Color(0xFF1A5FB4); // AA 통과
  static const onPrimary = Colors.white;

  static const error = Color(0xFFC01C28); // AA 통과
  static const onError = Colors.white;

  // 링크 색상 (배경과 구분되면서 충분한 대비)
  static const link = Color(0xFF1C71D8);
}
```

---

## 4. 텍스트 크기 조절

### MediaQuery 활용

```dart
// 시스템 텍스트 크기 반영
class AccessibleText extends StatelessWidget {
  final String text;
  final TextStyle? style;

  const AccessibleText(this.text, {this.style, super.key});

  @override
  Widget build(BuildContext context) {
    final textScaleFactor = MediaQuery.textScaleFactorOf(context);

    return Text(
      text,
      style: style,
      // 텍스트 스케일 제한 (레이아웃 깨짐 방지)
      textScaler: TextScaler.linear(textScaleFactor.clamp(0.8, 1.5)),
    );
  }
}
```

### 반응형 레이아웃

```dart
// 텍스트 크기 증가시에도 레이아웃 유지
class AccessibleCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final textScaleFactor = MediaQuery.textScaleFactorOf(context);
    final isLargeText = textScaleFactor > 1.3;

    return Card(
      child: isLargeText
          // 큰 텍스트일 때 세로 레이아웃
          ? Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildIcon(),
                const SizedBox(height: 8),
                _buildContent(),
              ],
            )
          // 기본 가로 레이아웃
          : Row(
              children: [
                _buildIcon(),
                const SizedBox(width: 16),
                Expanded(child: _buildContent()),
              ],
            ),
    );
  }
}
```

---

## 5. 터치 타겟 크기

```dart
// 최소 48x48dp 터치 영역 보장
class AccessibleIconButton extends StatelessWidget {
  final VoidCallback onPressed;
  final IconData icon;
  final String semanticLabel;

  const AccessibleIconButton({
    required this.onPressed,
    required this.icon,
    required this.semanticLabel,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      label: semanticLabel,
      child: InkWell(
        onTap: onPressed,
        customBorder: const CircleBorder(),
        child: Padding(
          // 최소 48dp 터치 영역
          padding: const EdgeInsets.all(12),
          child: Icon(icon, size: 24),
        ),
      ),
    );
  }
}

// 버튼 최소 높이 보장
class AccessibleButton extends StatelessWidget {
  final VoidCallback onPressed;
  final String label;

  const AccessibleButton({
    required this.onPressed,
    required this.label,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return ConstrainedBox(
      constraints: const BoxConstraints(
        minHeight: 48,
        minWidth: 48,
      ),
      child: ElevatedButton(
        onPressed: onPressed,
        child: Text(label),
      ),
    );
  }
}
```

---

## 6. 애니메이션 설정

```dart
// 모션 감소 설정 확인
class AccessibleAnimatedWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final reduceMotion = MediaQuery.disableAnimationsOf(context);

    if (reduceMotion) {
      // 애니메이션 없이 즉시 전환
      return _buildStaticWidget();
    }

    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      child: _buildContent(),
    );
  }
}

// 페이지 전환 애니메이션 조정
GoRouter(
  routes: [...],
  // 모션 감소시 즉시 전환
  pageBuilder: (context, state, child) {
    final reduceMotion = MediaQuery.disableAnimationsOf(context);

    if (reduceMotion) {
      return NoTransitionPage(child: child);
    }

    return CustomTransitionPage(
      child: child,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        return FadeTransition(opacity: animation, child: child);
      },
    );
  },
);
```

---

## 7. 스크린 리더 지원

### Live Region (동적 콘텐츠 알림)

```dart
// 상태 변경시 스크린 리더에 알림
Semantics(
  liveRegion: true, // 변경시 자동 읽기
  child: Text('장바구니에 ${itemCount}개 상품이 있습니다'),
);

// 중요 알림
Semantics(
  liveRegion: true,
  child: SnackBar(
    content: Text('저장되었습니다'),
  ),
);
```

### 커스텀 액션

```dart
Semantics(
  customSemanticsActions: {
    CustomSemanticsAction(label: '삭제'): () => _deleteItem(),
    CustomSemanticsAction(label: '편집'): () => _editItem(),
    CustomSemanticsAction(label: '공유'): () => _shareItem(),
  },
  child: ListTile(
    title: Text(item.title),
    trailing: PopupMenuButton(...),
  ),
);
```

---

## 8. 접근성 테스트

### Widget Test

```dart
// test/widget/accessibility_test.dart
void main() {
  testWidgets('button has semantic label', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: AccessibleIconButton(
          icon: Icons.add,
          onPressed: () {},
          semanticLabel: '추가',
        ),
      ),
    );

    // Semantics 확인
    expect(
      find.bySemanticsLabel('추가'),
      findsOneWidget,
    );
  });

  testWidgets('meets minimum tap target size', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: AccessibleButton(
          onPressed: () {},
          label: '제출',
        ),
      ),
    );

    final button = tester.getSize(find.byType(AccessibleButton));
    expect(button.width, greaterThanOrEqualTo(48));
    expect(button.height, greaterThanOrEqualTo(48));
  });
}
```

### 자동화된 접근성 검사

```dart
// integration_test/accessibility_test.dart
void main() {
  testWidgets('home page accessibility', (tester) async {
    await tester.pumpWidget(const MyApp());

    // Semantics 덤프로 접근성 트리 확인
    final semantics = tester.getSemantics(find.byType(HomePage));
    debugPrint(semantics.toStringDeep());

    // 접근성 검사
    await expectLater(tester, meetsGuideline(textContrastGuideline));
    await expectLater(tester, meetsGuideline(labeledTapTargetGuideline));
    await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
  });
}
```

---

## 9. Accessibility Checklist

### Visual
- [ ] 색상 대비율 4.5:1 이상 (일반 텍스트)
- [ ] 색상 대비율 3:1 이상 (큰 텍스트)
- [ ] 색상만으로 정보 전달하지 않음
- [ ] 텍스트 크기 조절 200%까지 지원
- [ ] 이미지에 대체 텍스트 제공

### Motor
- [ ] 터치 타겟 최소 48x48dp
- [ ] 충분한 터치 타겟 간격 (8dp+)
- [ ] 스와이프 외 대체 조작 제공
- [ ] 타임아웃 조절 가능

### Cognitive
- [ ] 명확한 레이블과 지시문
- [ ] 예측 가능한 네비게이션
- [ ] 오류 메시지 명확
- [ ] 입력 도움말 제공

### Screen Reader
- [ ] 모든 인터랙티브 요소에 label
- [ ] 논리적인 포커스 순서
- [ ] 동적 콘텐츠 변경 알림
- [ ] 헤딩 구조 적절

---

## References

- `5-design-system/SKILL.md`
