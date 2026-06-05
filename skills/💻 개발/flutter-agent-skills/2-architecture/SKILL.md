---
name: architecture
description: |
  Clean Architecture 기반 프로젝트 구조를 설계합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Architecture Skill

Extends: `../../_shared/architecture/SKILL.md` (공통 아키텍처 원칙 참조)

Clean Architecture 기반 프로젝트 구조를 설계합니다.

## Triggers

- "아키텍처 설계", "구조 설계", "clean architecture"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | Flutter 프로젝트 경로 |
| `features` | ❌ | 초기 생성할 Feature 목록 |

---

## 레이어 구조

```
┌─────────────────────────────────────┐
│         Presentation Layer          │
│  View (Page) ◄──► ViewModel (Notifier)
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│           Domain Layer              │
│  UseCase → Repository (Interface)   │
│                 │                   │
│              Entity                 │
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│            Data Layer               │
│  Repository (Impl) → DataSource     │
│                 │                   │
│              Model                  │
└─────────────────────────────────────┘
```

## Feature 구조

```
features/{feature}/
├── data/
│   ├── datasources/
│   │   ├── {feature}_remote_datasource.dart
│   │   └── {feature}_local_datasource.dart
│   ├── models/
│   │   └── {feature}_model.dart
│   └── repositories/
│       └── {feature}_repository_impl.dart
├── domain/
│   ├── entities/
│   │   └── {feature}_entity.dart
│   ├── repositories/
│   │   └── {feature}_repository.dart
│   └── usecases/
│       └── {action}_{feature}_usecase.dart
└── presentation/
    ├── notifiers/
    │   └── {feature}_notifier.dart
    └── pages/
        └── {feature}_page.dart
```

## 의존성 방향

- **Domain Layer**: 외부 의존성 없음 (순수 Dart)
- **Data Layer**: Domain Layer에 의존
- **Presentation Layer**: Domain Layer에 의존
- Entity ↔ Model 변환은 Data Layer에서 수행

## References

- `_references/RECENT-FLUTTER-CHANGES.md`
- `_references/QUALITY-CODE-PATTERN.md`
- `_references/ARCHITECTURE-PATTERN.md`
