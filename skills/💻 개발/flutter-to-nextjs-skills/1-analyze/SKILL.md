---
name: analyze
description: |
  Flutter 프로젝트를 분석하여 마이그레이션에 필요한 정보를 추출합니다.
  프로젝트 구조, 위젯, 상태관리, API 엔드포인트를 파악합니다.
triggers:
  - "flutter 분석"
  - "프로젝트 분석"
  - "analyze"
---

# Flutter Project Analysis Skill

Flutter 프로젝트를 분석하여 마이그레이션 계획 수립에 필요한 정보를 추출합니다.

## 입력

- Flutter 프로젝트 경로

## 출력

- `workspace/flutter-migration/{project-name}/analysis/flutter-analysis.md`

---

## 분석 항목

### 1. 프로젝트 구조 분석

```
lib/
├── main.dart              # 진입점
├── app.dart               # 앱 설정
├── features/              # Feature 기반 구조
│   ├── auth/
│   ├── home/
│   └── settings/
├── core/                  # 공통 코드
│   ├── api/
│   ├── models/
│   └── utils/
└── shared/                # 공유 위젯
```

분석 결과:
- 아키텍처 패턴 (Feature-based, Clean Architecture, MVVM 등)
- 디렉토리 깊이 및 구조
- 파일 수 및 코드 라인 수

### 2. 위젯 분석

#### 화면(Screen/Page) 목록

```dart
// 패턴 검색
class *Screen extends StatelessWidget
class *Page extends StatefulWidget
@RoutePage()
```

추출 정보:
- 화면 이름
- 파일 경로
- StatelessWidget / StatefulWidget 구분
- 의존하는 위젯 목록

#### 커스텀 위젯 목록

```dart
// 패턴 검색
class Custom* extends StatelessWidget
class *Widget extends StatefulWidget
```

추출 정보:
- 위젯 이름
- 재사용 빈도
- Props (생성자 파라미터)

### 3. 상태관리 분석

#### BLoC 패턴

```dart
// 검색 패턴
class *Bloc extends Bloc<*, *>
class *Cubit extends Cubit<*>
class *Event
class *State
```

추출 정보:
- BLoC/Cubit 목록
- Event 목록
- State 목록
- 의존성 관계

#### Riverpod 패턴

```dart
// 검색 패턴
final *Provider = Provider<*>
final *Provider = StateNotifierProvider<*, *>
final *Provider = FutureProvider<*>
@riverpod
```

추출 정보:
- Provider 목록
- Provider 타입 (State, Future, Stream 등)
- 의존성 관계

#### Provider 패턴

```dart
// 검색 패턴
class * extends ChangeNotifier
ChangeNotifierProvider<*>
```

#### GetX 패턴

```dart
// 검색 패턴
class *Controller extends GetxController
Get.put<*>
```

### 4. API 분석

#### 엔드포인트 추출

```dart
// 검색 패턴
dio.get('*')
dio.post('*')
http.get(Uri.parse('*'))
@GET('*')
@POST('*')
```

추출 정보:
- HTTP 메서드
- 엔드포인트 URL
- 요청/응답 모델
- 인증 필요 여부

#### Repository 패턴

```dart
// 검색 패턴
abstract class *Repository
class *RepositoryImpl implements *Repository
```

### 5. 모델 분석

```dart
// 검색 패턴
class * {
  final String *;
  factory *.fromJson(Map<String, dynamic> json)
  Map<String, dynamic> toJson()
}

@freezed
class * with _$*
```

추출 정보:
- 모델 이름
- 필드 목록 (이름, 타입)
- JSON 직렬화 여부
- Freezed/JsonSerializable 사용 여부

### 6. 라우팅 분석

#### GoRouter

```dart
// 검색 패턴
GoRoute(
  path: '*',
  builder: (context, state) => *Screen(),
)
```

#### Auto Route

```dart
// 검색 패턴
@RoutePage()
AutoRoute(page: *Route.page)
```

#### Navigator 1.0

```dart
// 검색 패턴
Navigator.push(context, MaterialPageRoute(builder: (*) => *Screen()))
Navigator.pushNamed(context, '/*')
```

추출 정보:
- 라우트 경로
- 대상 화면
- 파라미터
- 중첩 라우트 구조

### 7. 의존성 분석

```yaml
# pubspec.yaml 분석
dependencies:
  flutter_bloc: ^8.0.0
  dio: ^5.0.0
  go_router: ^12.0.0
```

추출 정보:
- 상태관리 라이브러리
- HTTP 클라이언트
- 라우팅 라이브러리
- UI 라이브러리
- 유틸리티 라이브러리

---

## 분석 프로세스

### Step 1: 프로젝트 경로 확인

```
입력된 경로에 pubspec.yaml이 있는지 확인
lib/ 디렉토리 존재 확인
```

### Step 2: pubspec.yaml 분석

```
프로젝트 이름, 버전 추출
의존성 목록 추출
상태관리/라우팅 라이브러리 식별
```

### Step 3: 디렉토리 구조 스캔

```
lib/ 하위 모든 .dart 파일 목록화
디렉토리 구조 파악
아키텍처 패턴 추론
```

### Step 4: 코드 분석

```
각 .dart 파일 파싱
클래스, 함수, 변수 추출
패턴 매칭으로 위젯/상태/API 분류
```

### Step 5: 의존성 그래프 생성

```
import 문 분석
위젯 간 의존성 파악
상태 의존성 파악
```

### Step 6: 리포트 생성

```
분석 결과를 markdown으로 정리
통계 정보 포함
변환 복잡도 예측
```

---

## 출력 형식

### flutter-analysis.md

```markdown
# Flutter Project Analysis: {project-name}

## 개요

| 항목 | 값 |
|------|-----|
| 프로젝트 이름 | {name} |
| Flutter 버전 | {version} |
| Dart 버전 | {dart-version} |
| 총 파일 수 | {file-count} |
| 총 코드 라인 | {loc} |

## 아키텍처

- **패턴**: {architecture-pattern}
- **상태관리**: {state-management}
- **라우팅**: {routing-library}

## 화면 목록 ({count}개)

| # | 화면 | 경로 | 타입 | 복잡도 |
|---|------|------|------|--------|
| 1 | HomeScreen | lib/features/home/home_screen.dart | Stateful | 중 |
| 2 | LoginScreen | lib/features/auth/login_screen.dart | Stateless | 저 |
| ... |

## 위젯 목록 ({count}개)

| # | 위젯 | 경로 | 재사용 | 복잡도 |
|---|------|------|--------|--------|
| 1 | CustomButton | lib/shared/custom_button.dart | 15회 | 저 |
| ... |

## 상태관리 ({type})

### BLoC/Cubit 목록

| # | 이름 | Events | States | 복잡도 |
|---|------|--------|--------|--------|
| 1 | AuthBloc | 5 | 4 | 중 |
| ... |

## API 엔드포인트 ({count}개)

| # | 메서드 | 엔드포인트 | 인증 | 사용처 |
|---|--------|-----------|------|--------|
| 1 | GET | /api/users | ✓ | UserRepository |
| 2 | POST | /api/auth/login | ✗ | AuthRepository |
| ... |

## 모델 ({count}개)

| # | 모델 | 필드 수 | JSON | Freezed |
|---|------|--------|------|---------|
| 1 | User | 8 | ✓ | ✓ |
| ... |

## 라우트 ({count}개)

| # | 경로 | 화면 | 파라미터 |
|---|------|------|---------|
| 1 | / | HomeScreen | - |
| 2 | /user/:id | UserDetailScreen | id: String |
| ... |

## 의존성

### 핵심 의존성

| 패키지 | 버전 | 용도 | Next.js 대응 |
|--------|------|------|-------------|
| flutter_bloc | ^8.0.0 | 상태관리 | Zustand |
| dio | ^5.0.0 | HTTP | fetch/axios |
| go_router | ^12.0.0 | 라우팅 | App Router |
| ... |

## 변환 복잡도 예측

| 영역 | 복잡도 | 예상 작업량 |
|------|--------|------------|
| UI 컴포넌트 | 중 | {count}개 위젯 변환 |
| 상태관리 | 고 | {count}개 BLoC → Zustand |
| 라우팅 | 저 | {count}개 라우트 변환 |
| API | 저 | 구조 유지 |

## 권장 변환 순서

1. 공통 컴포넌트 (Button, Input, Card)
2. 레이아웃 (AppBar, Drawer)
3. 인증 상태 (AuthBloc → authStore)
4. 로그인 화면
5. 홈 화면
6. ...
```

---

## 복잡도 기준

### 위젯 복잡도

| 복잡도 | 기준 |
|--------|------|
| 저 | 단순 표시, props < 5개 |
| 중 | 상태 있음, 이벤트 핸들링 |
| 고 | 애니메이션, 복잡한 레이아웃, 제스처 |

### BLoC 복잡도

| 복잡도 | 기준 |
|--------|------|
| 저 | Events < 3, 단순 상태 |
| 중 | Events 3-7, 비동기 처리 |
| 고 | Events > 7, 복잡한 상태 머신 |

---

## 주의사항

1. **플랫폼 전용 코드**: `dart:io`, `MethodChannel` 사용 부분 표시
2. **네이티브 플러그인**: 웹 대안이 필요한 플러그인 목록화
3. **애니메이션**: 복잡한 애니메이션은 별도 표시
4. **로컬 저장소**: SharedPreferences, Hive 사용 부분 표시
