---
name: view
description: |
  Atomic Design 기반 UI Widget/Page를 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# View Skill

Atomic Design 기반 UI Widget/Page를 구현합니다.

## Triggers

- "화면 구현", "UI 구현", "widget", "page 생성"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `pageName` | ✅ | Page 이름 |
| `featurePath` | ✅ | Feature 경로 |
| `template` | ❌ | 사용할 Template (Main, Auth, List, Detail) |

---

## 구현 원칙

- View/Page는 UI State를 구독하고 하위 위젯에 값과 콜백을 전달한다.
- 재사용 위젯은 API, DB, Repository, Platform Channel을 직접 호출하지 않는다.
- 하위 위젯은 생성자 파라미터로 데이터를 받고 `VoidCallback`, `ValueChanged<T>`, command callback으로 이벤트를 올린다.
- 레이아웃 분기는 고정 기기 크기가 아니라 `MediaQuery.sizeOf` 또는 `LayoutBuilder`의 `BoxConstraints`로 판단한다.
- 독립 위젯은 Widget Previewer, Widgetbook, widget test에서 앱 전체 실행 없이 렌더링 가능해야 한다.

---

## Page Template

### 목록 Page

```dart
// features/{feature}/presentation/pages/{entity}_list_page.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class {Entity}ListPage extends ConsumerWidget {
  const {Entity}ListPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final listState = ref.watch({entity}ListNotifierProvider);

    return MainTemplate(
      title: '{Entity} 목록',
      body: listState.when(
        data: (entities) => entities.isEmpty
            ? const _EmptyView()
            : _ListView(entities: entities),
        loading: () => const Center(child: AppLoading()),
        error: (error, _) => _ErrorView(
          message: error.toString(),
          onRetry: () => ref.invalidate({entity}ListNotifierProvider),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => context.push('/{entity}/create'),
        child: const Icon(Icons.add),
      ),
    );
  }
}

class _ListView extends StatelessWidget {
  const _ListView({required this.entities});

  final List<{Entity}Entity> entities;

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      padding: const EdgeInsets.all(AppSpacing.md),
      itemCount: entities.length,
      itemBuilder: (context, index) {
        final entity = entities[index];
        return {Entity}Card(
          entity: entity,
          onTap: () => context.push('/{entity}/${entity.id}'),
        );
      },
    );
  }
}

class _EmptyView extends StatelessWidget {
  const _EmptyView();

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const AppIcon(Icons.inbox_outlined, size: 64, color: AppColors.textTertiary),
          const AppSpacer.vertical(AppSpacing.md),
          AppText('데이터가 없습니다', color: AppColors.textSecondary),
        ],
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const AppIcon(Icons.error_outline, size: 64, color: AppColors.error),
          const AppSpacer.vertical(AppSpacing.md),
          AppText(message, color: AppColors.error),
          const AppSpacer.vertical(AppSpacing.md),
          AppButton(label: '다시 시도', onPressed: onRetry),
        ],
      ),
    );
  }
}
```

### 상세 Page

```dart
// features/{feature}/presentation/pages/{entity}_detail_page.dart
class {Entity}DetailPage extends ConsumerWidget {
  const {Entity}DetailPage({super.key, required this.{entity}Id});

  final String {entity}Id;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final detailState = ref.watch({entity}DetailNotifierProvider({entity}Id));

    return detailState.when(
      data: (entity) => entity != null
          ? DetailTemplate(
              title: entity.name,
              content: _{Entity}Content(entity: entity),
              actions: [
                AppButton(
                  label: '수정',
                  onPressed: () => context.push('/{entity}/${entity.id}/edit'),
                ),
                AppButton(
                  label: '삭제',
                  variant: AppButtonVariant.destructive,
                  onPressed: () => _showDeleteDialog(context, ref),
                ),
              ],
            )
          : const Center(child: AppText('데이터를 찾을 수 없습니다')),
      loading: () => const Scaffold(
        body: Center(child: AppLoading()),
      ),
      error: (error, _) => Scaffold(
        body: Center(child: AppText('에러: $error')),
      ),
    );
  }

  Future<void> _showDeleteDialog(BuildContext context, WidgetRef ref) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('삭제 확인'),
        content: const Text('정말 삭제하시겠습니까?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('취소'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('삭제'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      await ref.read({entity}ListNotifierProvider.notifier).delete{Entity}({entity}Id);
      if (context.mounted) context.pop();
    }
  }
}
```

### 폼 Page

```dart
// features/{feature}/presentation/pages/{entity}_form_page.dart
class {Entity}FormPage extends ConsumerWidget {
  const {Entity}FormPage({super.key, this.{entity}Id});

  final String? {entity}Id;

  bool get isEditing => {entity}Id != null;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final formState = ref.watch({entity}FormNotifierProvider);
    final formNotifier = ref.read({entity}FormNotifierProvider.notifier);

    // 제출 완료 시 이전 화면으로
    ref.listen({entity}FormNotifierProvider, (_, next) {
      if (next.isSubmitted) {
        context.pop();
      }
    });

    return MainTemplate(
      title: isEditing ? '{Entity} 수정' : '{Entity} 생성',
      showBottomNav: false,
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSpacing.md),
        child: Column(
          children: [
            LabeledInput(
              label: '이름',
              controller: TextEditingController(text: formState.name),
              errorText: formState.errors['name'],
              isRequired: true,
              onChanged: formNotifier.updateName,
            ),
            const AppSpacer.vertical(AppSpacing.md),
            LabeledInput(
              label: '설명',
              controller: TextEditingController(text: formState.description),
              maxLines: 3,
              onChanged: formNotifier.updateDescription,
            ),
            const AppSpacer.vertical(AppSpacing.lg),
            if (formState.submitError != null) ...[
              AppText(formState.submitError!, color: AppColors.error),
              const AppSpacer.vertical(AppSpacing.md),
            ],
            AppButton(
              label: isEditing ? '수정' : '생성',
              onPressed: formNotifier.submit,
              isLoading: formState.isSubmitting,
              isExpanded: true,
            ),
          ],
        ),
      ),
    );
  }
}
```

---

## 상태별 UI 패턴

```dart
asyncState.when(
  data: (data) => DataView(data: data),
  loading: () => const LoadingView(),
  error: (error, stack) => ErrorView(error: error, onRetry: refresh),
);
```

## References

- `_references/RECENT-FLUTTER-CHANGES.md`
- `_references/QUALITY-CODE-PATTERN.md`
- `_references/ATOMIC-DESIGN-PATTERN.md`
- `_references/RIVERPOD-PATTERN.md`
