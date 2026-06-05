---
name: feature-design
description: |
  Feature 단위 도메인 설계를 수행합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Feature Design Skill

Feature 단위 도메인 설계를 수행합니다.

## Triggers

- "기능 설계", "feature 설계", "도메인 설계", "화면 설계"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `featureName` | ✅ | 기능 이름 (snake_case) |
| `description` | ✅ | 기능 설명 |
| `requirements` | ❌ | 요구사항 목록 |

---

## Workflow

```
1. 요구사항 분석
   └─ 사용자 스토리 정의

2. Entity 설계
   └─ 핵심 도메인 모델 정의

3. UseCase 도출
   └─ 비즈니스 로직 정의

4. Repository Interface 설계
   └─ 데이터 접근 추상화

5. UI 흐름 설계
   └─ 화면/상태 흐름도

6. API/DB 스키마 설계
   └─ Model, Table 정의
```

---

## Output: Feature Design Document

```markdown
# {Feature Name} 설계

## 1. 개요
- **기능명**: {feature_name}
- **설명**: {description}

## 2. 요구사항
- [ ] {requirement_1}
- [ ] {requirement_2}

## 3. Entity 설계

### {EntityName}Entity
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| id | String | ✅ | 고유 식별자 |
| ... | ... | ... | ... |

## 4. UseCase 목록
| UseCase | 설명 | Input | Output |
|---------|------|-------|--------|
| Get{Entity} | 조회 | id | Entity |
| Create{Entity} | 생성 | Params | Entity |
| Update{Entity} | 수정 | Entity | Entity |
| Delete{Entity} | 삭제 | id | void |

## 5. Repository Interface

```dart
abstract class {Feature}Repository {
  Future<Either<Failure, {Entity}Entity>> get{Entity}(String id);
  Future<Either<Failure, List<{Entity}Entity>>> get{Entity}List();
  Future<Either<Failure, {Entity}Entity>> create{Entity}({Entity}Entity entity);
  Future<Either<Failure, {Entity}Entity>> update{Entity}({Entity}Entity entity);
  Future<Either<Failure, void>> delete{Entity}(String id);
}
```

## 6. UI 흐름

```
[시작] → [목록 화면] → [상세 화면]
              ↓
         [생성/수정 화면]
```

## 7. 상태 설계

| 상태 | 설명 |
|------|------|
| Initial | 초기 상태 |
| Loading | 로딩 중 |
| Loaded | 데이터 로드 완료 |
| Error | 에러 발생 |

## 8. API 엔드포인트
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | /api/{feature} | 목록 조회 |
| GET | /api/{feature}/{id} | 상세 조회 |
| POST | /api/{feature} | 생성 |
| PUT | /api/{feature}/{id} | 수정 |
| DELETE | /api/{feature}/{id} | 삭제 |
```

---

## 생성 파일 체크리스트

### Domain Layer
- [ ] `entities/{feature}_entity.dart`
- [ ] `repositories/{feature}_repository.dart`
- [ ] `usecases/get_{feature}_usecase.dart`
- [ ] `usecases/create_{feature}_usecase.dart`
- [ ] `usecases/update_{feature}_usecase.dart`
- [ ] `usecases/delete_{feature}_usecase.dart`

### Data Layer
- [ ] `models/{feature}_model.dart`
- [ ] `datasources/{feature}_remote_datasource.dart`
- [ ] `datasources/{feature}_local_datasource.dart`
- [ ] `repositories/{feature}_repository_impl.dart`

### Presentation Layer
- [ ] `notifiers/{feature}_notifier.dart`
- [ ] `pages/{feature}_list_page.dart`
- [ ] `pages/{feature}_detail_page.dart`
- [ ] `pages/{feature}_form_page.dart`

## References

- `_references/ARCHITECTURE-PATTERN.md`
