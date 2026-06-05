# Flutter Quality Code Pattern Reference

Flutter 고품질 코드 작성을 위한 공통 기준입니다. Flutter 공식 "How to write really good Flutter code" 세션과 공식 문서의 아키텍처, 적응형 UI, DevTools, Widget Previewer, MCP, 테스트 가이드를 기준으로 정리합니다.

최신 SDK/패키지 기준은 [RECENT-FLUTTER-CHANGES.md](RECENT-FLUTTER-CHANGES.md)를 먼저 확인합니다.

## 1. Constraints 기반 UI

Flutter 레이아웃은 "부모가 제약을 내려주고, 자식이 크기를 올려보내며, 부모가 위치를 정한다"는 모델을 따른다.

- 고정 `width`/`height`는 터치 타깃, 아이콘, 아바타, 명시적 디자인 토큰처럼 의도가 명확할 때만 사용한다.
- 전체 앱 창 크기 기준 분기는 `MediaQuery.sizeOf(context)`를 사용한다.
- 특정 영역의 실제 가용 공간 기준 분기는 `LayoutBuilder`의 `BoxConstraints`를 사용한다.
- 반응형 위젯은 `abstract -> measure -> branch` 순서로 설계한다.
  - `abstract`: 화면 크기에 따라 바뀌는 UI 조각과 공통 데이터를 분리한다.
  - `measure`: 앱 전체 크기인지, 로컬 영역 제약인지 결정한다.
  - `branch`: 작은 화면과 큰 화면에서 필요한 경우 완전히 다른 레이아웃 위젯을 반환한다.

```dart
class ProductPane extends StatelessWidget {
  const ProductPane({
    super.key,
    required this.products,
    required this.onProductTap,
  });

  final List<Product> products;
  final ValueChanged<Product> onProductTap;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth >= 720) {
          return ProductGrid(
            products: products,
            onProductTap: onProductTap,
          );
        }

        return ProductList(
          products: products,
          onProductTap: onProductTap,
        );
      },
    );
  }
}
```

## 2. DevTools와 MCP 기반 진단

추측으로 숫자를 바꾸며 hot reload를 반복하지 않는다.

- 레이아웃 오버플로우는 DevTools Inspector에서 원인 위젯, `size`, `constraints`를 먼저 확인한다.
- 성능 문제는 profile 모드와 DevTools Timeline/Performance 탭으로 측정한 뒤 수정한다.
- Dart and Flutter MCP server는 선택적 DX 도구다. 사용 가능하면 AI 어시스턴트가 analyzer, runtime errors, running app introspection, pub.dev 검색, 테스트 실행 결과를 확인하도록 연결한다.
- MCP와 Widget Previewer는 실험적 기능일 수 있으므로 프로젝트 Flutter/Dart 버전을 먼저 확인한다.

## 3. 재사용 가능한 순수 위젯

재사용 가능한 위젯은 데이터를 받아 렌더링하고 사용자 이벤트를 콜백으로 올려보낸다.

- 위젯 내부에서 HTTP 클라이언트, DB, platform channel, repository를 직접 호출하지 않는다.
- atoms/molecules/organisms에는 `ref.watch`와 전역 싱글턴 접근을 넣지 않는다.
- Page/View 계층에서 ViewModel/Notifier를 연결하고, 하위 위젯에는 값과 콜백만 전달한다.
- 위젯 생성자는 상태별 preview/test를 만들 수 있을 만큼 명시적이어야 한다.

```dart
class PaymentButton extends StatelessWidget {
  const PaymentButton({
    super.key,
    required this.label,
    required this.isLoading,
    required this.onPressed,
  });

  final String label;
  final bool isLoading;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    return FilledButton(
      onPressed: isLoading ? null : onPressed,
      child: isLoading ? const CircularProgressIndicator() : Text(label),
    );
  }
}
```

## 4. MVVM + Clean Architecture 매핑

Flutter 공식 아키텍처는 MVVM을 권장한다. 이 하니스의 Clean Architecture 용어와 다음처럼 매핑한다.

| 공식 용어 | 하니스 용어 | 책임 |
|----------|-------------|------|
| View | Page/Widget | UI 렌더링, 입력 수신, 이벤트 전달 |
| ViewModel | Riverpod Notifier | UI 상태 생성, 사용자 액션 처리, Repository/UseCase 호출 |
| Repository | Repository | 앱 데이터의 단일 진실 공급원 |
| Service | DataSource/API/Platform Service | 외부 API, DB, 디바이스 기능 접근 |
| Domain layer | UseCase/Interactor | 복잡하거나 재사용되는 비즈니스 로직 |

UseCase는 모든 기능에 기계적으로 만들지 않는다. 여러 Repository를 조합하거나, 로직이 복잡하거나, 여러 ViewModel에서 재사용될 때 추가한다.

## 5. Repository 데이터 추상화

Repository는 앱 데이터의 단일 진실 공급원이다.

- ViewModel은 DataSource, API client, DB, platform plugin을 직접 알지 않는다.
- 캐싱, retry, polling, offline fallback, 에러 변환은 Repository 책임으로 둔다.
- Repository끼리 직접 의존하지 않는다. 여러 Repository 조합은 ViewModel 또는 UseCase에서 수행한다.
- 외부 데이터 형태(Model/DTO)는 Data layer에서 Domain Entity로 변환한다.

## 6. 네이티브 기능 추상화

플랫폼 기능은 직접 Kotlin/Swift부터 작성하지 않는다.

1. pub.dev에서 공식/활성 패키지와 플랫폼 지원 범위를 먼저 확인한다.
2. 패키지가 요구사항, 보안, 플랫폼 범위, 유지보수 기준을 충족하면 Dart 인터페이스 뒤에 감싼다.
3. 패키지가 없거나 요구사항을 충족하지 못할 때 Pigeon 기반 Platform Channel을 사용한다.
4. 플랫폼 접근 코드는 Service/DataSource에 격리하고, UI와 ViewModel에는 Repository/UseCase 인터페이스만 노출한다.

## 7. 테스트 가능한 구조

좋은 구조는 테스트하기 쉽다. 레이어 분리가 테스트 작성 비용을 낮춰야 한다.

- Unit test: ViewModel/Notifier, UseCase, Repository의 분기와 실패 처리를 빠르게 검증한다.
- Widget test: 독립 위젯의 텍스트, 콜백, 상태별 렌더링, 작은/큰 제약 조건 분기를 검증한다.
- Golden test: 디자인 시스템 컴포넌트와 핵심 화면의 시각적 회귀를 검증한다.
- Integration/E2E test: 실제 앱에서 핵심 사용자 여정을 검증한다.
- `checks`는 타입 지향 assertion을 작성할 때 선택적으로 사용한다. 프로젝트 안정성이 더 중요하면 기존 `expect`/matcher와 혼합 도입한다.

## 품질 체크리스트

- [ ] UI 분기가 고정 픽셀이 아니라 `MediaQuery.sizeOf` 또는 `LayoutBuilder` 제약 조건에 기반한다.
- [ ] 재사용 위젯이 외부 I/O와 상태관리 구현을 직접 알지 않는다.
- [ ] Page/View는 ViewModel을 연결하고 하위 위젯에는 값과 콜백만 전달한다.
- [ ] Repository가 데이터 접근, 캐싱, 에러 변환의 단일 진실 공급원이다.
- [ ] 플랫폼 기능은 pub.dev 패키지 우선 검토 후 필요할 때만 Pigeon으로 구현한다.
- [ ] DevTools 또는 MCP로 실제 오류/성능 데이터를 확인한 뒤 수정한다.
- [ ] Unit, widget, golden, integration/E2E 테스트 중 변경 위험에 맞는 수준을 작성한다.

## References

- Flutter architecture guide: https://docs.flutter.dev/app-architecture/guide
- Adaptive and responsive design: https://docs.flutter.dev/ui/adaptive-responsive/general
- Understanding constraints: https://docs.flutter.dev/development/ui/layout/constraints
- Flutter Inspector: https://docs.flutter.dev/tools/devtools/inspector
- Widget Previewer: https://docs.flutter.dev/tools/widget-previewer
- Dart and Flutter MCP server: https://docs.flutter.dev/ai/mcp-server
- `checks` package: https://pub.dev/packages/checks
