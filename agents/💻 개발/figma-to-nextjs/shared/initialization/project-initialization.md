---
name: "Project Initialization Guide"
description: "CLI-based Next.js project creation and setup"
---

# Project Initialization Guide

> CLI-based project creation for token efficiency

---

## Overview

When no existing project is found, use CLI tools instead of manually creating files. This reduces token consumption by ~40x.

```
┌─────────────────────────────────────────────────────────────────┐
│ TOKEN COMPARISON                                                 │
│                                                                  │
│ ❌ Manual Creation (Before)                                      │
│    - package.json:     ~500 tokens                              │
│    - tsconfig.json:    ~300 tokens                              │
│    - next.config.ts:   ~200 tokens                              │
│    - tailwind.config:  ~400 tokens                              │
│    - app/layout.tsx:   ~300 tokens                              │
│    - app/page.tsx:     ~200 tokens                              │
│    - lib/utils.ts:     ~100 tokens                              │
│    ─────────────────────────────                                │
│    Total: ~2000+ tokens                                          │
│                                                                  │
│ ✅ CLI Creation (After)                                          │
│    - npx create-next-app: ~30 tokens                            │
│    - npx shadcn init:     ~20 tokens                            │
│    ─────────────────────────────                                │
│    Total: ~50 tokens (40x savings)                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Next.js Project Initialization

### Phase 0: Project Detection

```typescript
// Check if Next.js project exists
const hasNextProject = await fileExists('package.json') &&
  await Grep({ pattern: '"next"', path: 'package.json' });

if (!hasNextProject) {
  // Initialize new project via CLI
  await initializeNextProject();
}
```

### CLI Commands

```bash
# Step 1: Create Next.js project
npx create-next-app@latest [project-name] \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir \
  --import-alias "@/*" \
  --no-turbopack \
  --yes

# Step 2: Initialize shadcn/ui
npx shadcn@latest init -d

# Step 3: Add commonly used components
npx shadcn@latest add button card input badge avatar
```

### Recommended Flags

| Flag | Purpose | Recommendation |
|------|---------|----------------|
| `--typescript` | TypeScript support | Always |
| `--tailwind` | Tailwind CSS | Always |
| `--eslint` | ESLint setup | Always |
| `--app` | App Router | Always (default) |
| `--src-dir` | Use src/ directory | Recommended |
| `--import-alias "@/*"` | Clean imports | Recommended |
| `--no-turbopack` | Stable bundler | For compatibility |
| `--yes` | Skip prompts | For automation |

### Project Structure (Result)

```
[project-name]/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── components/
│   │   └── ui/           # shadcn components
│   └── lib/
│       └── utils.ts      # cn() utility
├── public/
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.ts
└── components.json       # shadcn config
```

---

## Flutter Project Initialization

### Phase 0: Project Detection

```typescript
// Check if Flutter project exists
const hasFlutterProject = await fileExists('pubspec.yaml') &&
  await Grep({ pattern: 'flutter:', path: 'pubspec.yaml' });

if (!hasFlutterProject) {
  // Initialize new project via CLI
  await initializeFlutterProject();
}
```

### CLI Commands

```bash
# Step 1: Create Flutter project
flutter create [project_name] \
  --org com.example \
  --platforms ios,android,web \
  --description "Figma converted app"

# Step 2: Add common dependencies
cd [project_name]
flutter pub add flutter_riverpod
flutter pub add go_router
flutter pub add freezed_annotation
flutter pub add json_annotation

# Step 3: Add dev dependencies
flutter pub add --dev build_runner
flutter pub add --dev freezed
flutter pub add --dev json_serializable

# Step 4: Create recommended structure
mkdir -p lib/core/theme
mkdir -p lib/core/router
mkdir -p lib/features
mkdir -p lib/shared/widgets
```

### Recommended Packages

| Package | Purpose | Priority |
|---------|---------|----------|
| `flutter_riverpod` | State management | High |
| `go_router` | Navigation | High |
| `freezed` | Immutable models | Medium |
| `cached_network_image` | Image caching | Medium |
| `flutter_svg` | SVG support | Medium |

### Project Structure (Result)

```
[project_name]/
├── lib/
│   ├── main.dart
│   ├── core/
│   │   ├── theme/
│   │   │   ├── app_theme.dart
│   │   │   └── app_colors.dart
│   │   └── router/
│   │       └── app_router.dart
│   ├── features/
│   │   └── [feature_name]/
│   │       ├── presentation/
│   │       ├── domain/
│   │       └── data/
│   └── shared/
│       └── widgets/
├── test/
├── pubspec.yaml
└── analysis_options.yaml
```

---

## Post-Initialization Setup

### Next.js: Additional Configuration

```bash
# Add path aliases to tsconfig.json (if needed)
# Usually handled by create-next-app

# Install additional dev tools (optional)
npm install -D prettier prettier-plugin-tailwindcss

# Create .prettierrc (optional)
echo '{"plugins": ["prettier-plugin-tailwindcss"]}' > .prettierrc
```

### Flutter: Theme Setup

```dart
// lib/core/theme/app_theme.dart
import 'package:flutter/material.dart';

class AppTheme {
  // Will be populated from Figma tokens (Phase 2)
  static ThemeData get light => ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
  );
}
```

---

## Decision Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ PROJECT INITIALIZATION DECISION FLOW                             │
│                                                                  │
│   Start Phase 0                                                  │
│        │                                                         │
│        ▼                                                         │
│   ┌─────────────────┐                                           │
│   │ Project exists? │                                           │
│   └────────┬────────┘                                           │
│            │                                                     │
│      ┌─────┴─────┐                                              │
│      │           │                                              │
│     YES         NO                                              │
│      │           │                                              │
│      ▼           ▼                                              │
│   ┌──────┐   ┌──────────────────────┐                          │
│   │ Scan │   │ Ask: Create project? │                          │
│   │ Only │   └──────────┬───────────┘                          │
│   └──────┘              │                                       │
│                   ┌─────┴─────┐                                 │
│                   │           │                                 │
│                  YES         NO                                 │
│                   │           │                                 │
│                   ▼           ▼                                 │
│            ┌──────────┐   ┌───────┐                            │
│            │ CLI Init │   │ Abort │                            │
│            └──────────┘   └───────┘                            │
│                   │                                             │
│                   ▼                                             │
│            Continue to Phase 1                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Integration with Agents

### Agent Prompt Template

```markdown
## Phase 0: Project Scan & Initialization

### Step 1: Check Existing Project

```bash
# For Next.js
ls package.json 2>/dev/null && grep -q '"next"' package.json && echo "EXISTS" || echo "NOT_FOUND"

# For Flutter
ls pubspec.yaml 2>/dev/null && grep -q 'flutter:' pubspec.yaml && echo "EXISTS" || echo "NOT_FOUND"
```

### Step 2: Initialize if Needed

IF NOT_FOUND:
  - Ask user: "No [Next.js/Flutter] project found. Create one?"
  - If yes: Run CLI initialization commands
  - If no: Abort with message

### Step 3: Scan Project Structure

After initialization or if project exists:
  - Identify existing components
  - Document styling approach
  - List reusable elements
```

---

## Token Savings Summary

| Action | Manual | CLI | Savings |
|--------|--------|-----|---------|
| Next.js setup | ~2000 tokens | ~50 tokens | 97.5% |
| Flutter setup | ~1500 tokens | ~40 tokens | 97.3% |
| shadcn init | ~800 tokens | ~20 tokens | 97.5% |
| Component add | ~200/each | ~10/each | 95% |

### Why CLI is Better

1. **Token Efficiency**: 40x fewer tokens consumed
2. **Consistency**: Official templates, always up-to-date
3. **Best Practices**: Includes recommended configurations
4. **Speed**: Faster than writing each file
5. **Reliability**: Fewer errors from manual typing

---

## Error Handling

### CLI Not Available

```yaml
error: "npx: command not found"
solution:
  - Check Node.js installation
  - Suggest: "Install Node.js from https://nodejs.org"
fallback:
  - Manual creation (last resort)
```

### Network Error

```yaml
error: "npm ERR! network"
solution:
  - Check internet connection
  - Try with --offline flag (if cached)
fallback:
  - Ask user to run CLI manually
```

### Permission Error

```yaml
error: "EACCES: permission denied"
solution:
  - Check directory permissions
  - Suggest: Run in different directory
fallback:
  - Ask user to create project manually
```

---

## Best Practices

### DO

- Always check for existing project first
- Use `--yes` flag to skip prompts
- Initialize UI library (shadcn) immediately
- Add only necessary components

### DON'T

- Manually create package.json
- Write configuration files by hand
- Install all shadcn components upfront
- Skip the project existence check

---

*Version: 1.0.0*
*Last Updated: 2026-01-23*
*Applies To: figma-to-nextjs, figma-to-nextjs-pro, figma-to-flutter, figma-to-flutter-pro*
