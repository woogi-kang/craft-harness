---
name: performance
description: |
  성능 최적화를 분석하고 적용합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Performance Skill

Extends: `../../_shared/performance/SKILL.md` (공통 성능 최적화 원칙 참조)

성능 최적화를 분석하고 적용합니다.

## Triggers

- "성능 최적화", "performance", "렌더링 최적화"

---

## 최적화 영역

### 1. Widget 리빌드 최적화

```dart
// ❌ Bad: 전체 상태 watch
final state = ref.watch(userNotifierProvider);
Text(state.value?.name ?? '');

// ✅ Good: select로 필요한 값만 watch
final name = ref.watch(
  userNotifierProvider.select((s) => s.value?.name),
);
Text(name ?? '');

// ✅ Good: Consumer로 부분 리빌드
Consumer(
  builder: (context, ref, child) {
    final name = ref.watch(userNotifierProvider.select((s) => s.value?.name));
    return Text(name ?? '');
  },
);
```

### 2. const 위젯 활용

```dart
// ❌ Bad: 매번 새 인스턴스
Container(
  padding: EdgeInsets.all(16),
  child: Icon(Icons.home),
);

// ✅ Good: const 활용
const Padding(
  padding: EdgeInsets.all(16),
  child: Icon(Icons.home),
);
```

### 3. ListView 최적화

```dart
// ❌ Bad: 모든 아이템 한번에 빌드
ListView(
  children: items.map((item) => ItemWidget(item: item)).toList(),
);

// ✅ Good: 보이는 아이템만 빌드
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) => ItemWidget(item: items[index]),
);

// ✅ Better: cacheExtent 설정
ListView.builder(
  itemCount: items.length,
  cacheExtent: 500, // 픽셀 단위 캐시 영역
  itemBuilder: (context, index) => ItemWidget(item: items[index]),
);

// ✅ Best: itemExtent로 고정 높이 (스크롤 성능 향상)
ListView.builder(
  itemCount: items.length,
  itemExtent: 80,
  itemBuilder: (context, index) => ItemWidget(item: items[index]),
);
```

### 4. 이미지 최적화

```dart
// 캐시된 네트워크 이미지
CachedNetworkImage(
  imageUrl: url,
  placeholder: (context, url) => const Shimmer(),
  errorWidget: (context, url, error) => const Icon(Icons.error),
  memCacheWidth: 200, // 메모리 캐시 크기 제한
);

// 적절한 해상도
Image.asset(
  'assets/image.png',
  cacheWidth: 200, // 렌더링 크기에 맞게 디코딩
  cacheHeight: 200,
);
```

### 5. 무거운 연산 분리

```dart
// ❌ Bad: UI 스레드에서 무거운 연산
final result = heavyComputation(data);

// ✅ Good: Isolate로 분리
final result = await compute(heavyComputation, data);

// ✅ Good: Future.microtask로 프레임 분할
for (final item in largeList) {
  await Future.microtask(() => processItem(item));
}
```

### 6. 애니메이션 최적화

```dart
// RepaintBoundary로 리페인트 영역 분리
RepaintBoundary(
  child: AnimatedWidget(),
);

// AnimatedBuilder 활용
AnimatedBuilder(
  animation: controller,
  builder: (context, child) {
    return Transform.rotate(
      angle: controller.value * 2 * pi,
      child: child, // child는 리빌드 안됨
    );
  },
  child: const ExpensiveWidget(), // 한번만 빌드
);
```

---

## 성능 측정

### DevTools

```bash
# Performance 탭 열기
flutter run --profile
# DevTools에서 Timeline 분석
```

### Layout 진단

레이아웃 오버플로우나 의도치 않은 리빌드는 추측으로 수치를 바꾸기 전에 DevTools에서 확인합니다.

- Inspector에서 문제 위젯의 `constraints`, `size`, 부모/자식 관계를 확인
- 노란색 overflow stripe가 나온 경우 정확한 Row/Column/Flex 지점을 먼저 식별
- `LayoutBuilder`로 분기하는 위젯은 작은/큰 제약 조건을 widget test나 preview로 재현
- Dart and Flutter MCP server가 연결되어 있으면 runtime errors, analyzer 결과, pub.dev 문서, running app introspection을 확인한 뒤 수정

### 프레임 분석

```dart
// 프레임 시간 로깅
WidgetsBinding.instance.addTimingsCallback((timings) {
  for (final timing in timings) {
    if (timing.totalSpan.inMilliseconds > 16) {
      print('Slow frame: ${timing.totalSpan.inMilliseconds}ms');
    }
  }
});
```

---

## 체크리스트

- [ ] 불필요한 리빌드 제거 (select, Consumer)
- [ ] const 위젯 활용
- [ ] ListView.builder 사용
- [ ] 이미지 캐싱 및 크기 최적화
- [ ] 무거운 연산 Isolate 분리
- [ ] RepaintBoundary 적용
- [ ] 프레임 드롭 확인 (16ms 이내)
- [ ] DevTools Inspector/Performance 또는 MCP 기반으로 원인 확인 후 수정

## References

- `_references/RECENT-FLUTTER-CHANGES.md`
- `_references/QUALITY-CODE-PATTERN.md`
