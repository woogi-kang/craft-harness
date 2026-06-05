---
name: routing
description: |
  GoRouter 라우팅을 설정합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Routing Skill

GoRouter 라우팅을 설정합니다.

## Triggers

- "라우팅 설정", "go_router", "네비게이션"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `routes` | ✅ | 라우트 목록 |

---

## Output Template

### AppRouter

```dart
// routes/app_router.dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'app_router.g.dart';

@riverpod
GoRouter appRouter(Ref ref) {
  final authState = ref.watch(authNotifierProvider);

  return GoRouter(
    initialLocation: '/',
    debugLogDiagnostics: true,
    redirect: (context, state) {
      final isLoggedIn = authState.valueOrNull != null;
      final isAuthRoute = state.matchedLocation.startsWith('/auth');

      if (!isLoggedIn && !isAuthRoute) {
        return '/auth/login';
      }
      if (isLoggedIn && isAuthRoute) {
        return '/';
      }
      return null;
    },
    routes: [
      // Auth Routes
      GoRoute(
        path: '/auth/login',
        builder: (context, state) => const LoginPage(),
      ),
      GoRoute(
        path: '/auth/register',
        builder: (context, state) => const RegisterPage(),
      ),

      // Main Routes (with Bottom Navigation)
      StatefulShellRoute.indexedStack(
        builder: (context, state, navigationShell) {
          return MainShell(navigationShell: navigationShell);
        },
        branches: [
          // Home
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/',
                builder: (context, state) => const HomePage(),
              ),
            ],
          ),

          // {Feature} List
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/{feature}',
                builder: (context, state) => const {Feature}ListPage(),
                routes: [
                  // Create
                  GoRoute(
                    path: 'create',
                    builder: (context, state) => const {Feature}FormPage(),
                  ),
                  // Detail
                  GoRoute(
                    path: ':id',
                    builder: (context, state) {
                      final id = state.pathParameters['id']!;
                      return {Feature}DetailPage({feature}Id: id);
                    },
                    routes: [
                      // Edit
                      GoRoute(
                        path: 'edit',
                        builder: (context, state) {
                          final id = state.pathParameters['id']!;
                          return {Feature}FormPage({feature}Id: id);
                        },
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),

          // Profile
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/profile',
                builder: (context, state) => const ProfilePage(),
              ),
            ],
          ),
        ],
      ),
    ],
    errorBuilder: (context, state) => ErrorPage(error: state.error),
  );
}
```

### MainShell (Bottom Navigation)

```dart
// routes/main_shell.dart
class MainShell extends StatelessWidget {
  const MainShell({super.key, required this.navigationShell});

  final StatefulNavigationShell navigationShell;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: navigationShell,
      bottomNavigationBar: NavigationBar(
        selectedIndex: navigationShell.currentIndex,
        onDestinationSelected: (index) {
          navigationShell.goBranch(
            index,
            initialLocation: index == navigationShell.currentIndex,
          );
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home),
            label: '홈',
          ),
          NavigationDestination(
            icon: Icon(Icons.list_outlined),
            selectedIcon: Icon(Icons.list),
            label: '{Feature}',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person),
            label: '프로필',
          ),
        ],
      ),
    );
  }
}
```

### Type-Safe Routes (go_router_builder)

```dart
// routes/app_routes.dart
import 'package:go_router/go_router.dart';

part 'app_routes.g.dart';

@TypedGoRoute<HomeRoute>(path: '/')
class HomeRoute extends GoRouteData {
  const HomeRoute();
}

@TypedGoRoute<{Feature}ListRoute>(
  path: '/{feature}',
  routes: [
    TypedGoRoute<{Feature}CreateRoute>(path: 'create'),
    TypedGoRoute<{Feature}DetailRoute>(
      path: ':id',
      routes: [
        TypedGoRoute<{Feature}EditRoute>(path: 'edit'),
      ],
    ),
  ],
)
class {Feature}ListRoute extends GoRouteData {
  const {Feature}ListRoute();
}

class {Feature}CreateRoute extends GoRouteData {
  const {Feature}CreateRoute();
}

class {Feature}DetailRoute extends GoRouteData {
  const {Feature}DetailRoute({required this.id});
  final String id;
}

class {Feature}EditRoute extends GoRouteData {
  const {Feature}EditRoute({required this.id});
  final String id;
}

// 사용
const HomeRoute().go(context);
{Feature}DetailRoute(id: '123').push(context);
```

---

## 네비게이션 사용

```dart
// push (스택에 추가)
context.push('/{feature}/123');

// go (스택 교체)
context.go('/');

// pop (뒤로가기)
context.pop();

// pushReplacement
context.pushReplacement('/{feature}');
```

## References

- `_references/ARCHITECTURE-PATTERN.md`
