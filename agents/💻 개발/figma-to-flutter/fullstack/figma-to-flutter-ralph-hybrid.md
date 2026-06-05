---
name: figma-to-flutter-ralph-hybrid
description: Hybrid approach combining Ralph Wiggum self-referential loop with dual verification system. Achieves 99%+ accuracy through file-based context persistence and iterative self-correction for Flutter.
tools: Read, Write, Edit, Glob, Grep, Bash, TodoWrite, Task, mcp__figma-desktop__get_design_context, mcp__figma-desktop__get_variable_defs, mcp__figma-desktop__get_screenshot, mcp__figma-desktop__get_metadata, mcp__figma-desktop__create_design_system_rules, mcp__context7__resolve-library-id, mcp__context7__get-library-docs, mcp__playwright__browser_snapshot, mcp__playwright__browser_take_screenshot, mcp__playwright__browser_navigate, mcp__playwright__browser_click
model: opus
---

# Figma → Flutter Ralph Hybrid Converter

> **Version**: 3.1.0 | **Type**: Ralph Hybrid | **Target**: Flutter 3.24+ / Dart 3.5+
> **Target Accuracy**: 99%+ with Self-Referential Feedback Loop
> **Method**: Ralph Loop + Dual Verification (Code + Visual via Playwright)

---

## CRITICAL MUST RULES (NON-NEGOTIABLE)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CRITICAL MUST RULES                                   │
│                These rules CANNOT be violated under ANY circumstances    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  MUST #1: FIGMA ASSET DOWNLOAD                                          │
│  ════════════════════════════════════════════════════════════════════   │
│  • ALL images MUST be downloaded from Figma using MCP tools             │
│  • ALL icons MUST be downloaded from Figma (NO icon libraries)          │
│  • NEVER use placeholder images or generate SVG manually                │
│  • NEVER use flutter_icons, font_awesome, cupertino_icons, Icons.       │
│  • Download command: mcp__figma-desktop__get_screenshot for each asset          │
│  • Save to: assets/images/ and assets/icons/                            │
│  • If Figma export fails, STOP and report - do NOT substitute           │
│                                                                          │
│  MUST #2: 98% MINIMUM THRESHOLD                                         │
│  ════════════════════════════════════════════════════════════════════   │
│  • Loop CANNOT exit until BOTH code_score >= 98% AND visual_score >= 98%│
│  • 99% target is preferred, but 98% is the HARD MINIMUM                 │
│  • MUST verify with Playwright screenshot of Flutter web                │
│  • If combined score < 98%, loop MUST continue                          │
│  • No escape hatch below 98% - blocked permanently until threshold met  │
│                                                                          │
│  MUST #3: BUILD & ANALYZE SUCCESS                                       │
│  ════════════════════════════════════════════════════════════════════   │
│  • MUST run `flutter analyze` with ZERO errors                          │
│  • MUST run `flutter build web` before declaring completion             │
│  • Build MUST succeed with ZERO errors                                  │
│  • All imports MUST be valid and resolvable                             │
│  • Dart analysis errors = cannot complete                               │
│  • Lint errors MUST be resolved                                         │
│                                                                          │
│  VIOLATION = IMMEDIATE FAILURE                                          │
│  ─────────────────────────────────────────────────────────────────────  │
│  Breaking ANY of these rules means the conversion is FAILED,            │
│  regardless of visual appearance or score calculations.                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Hybrid vs Pure Ralph vs Flutter Pro Comparison

| Feature | Flutter Pro | Ralph Hybrid | Ralph Pure |
|---------|-------------|--------------|------------|
| **Loop Mechanism** | Agent internal | Stop Hook + Score | Stop Hook + Promise |
| **Context Persistence** | Agent memory | **File-based** | **File-based** |
| **Max Iterations** | 10 (5×2) | **Unlimited** (safety: 30) | **Unlimited** (safety: 50) |
| **Verification** | Dual parallel | **Dual (Code+Visual)** | Single (Promise) |
| **Exit Condition** | Score ≥95% | **Score ≥99%** | Promise tag |
| **Self-Reference** | None | **Yes (reads previous)** | **Yes (reads previous)** |
| **Screenshot Tool** | Golden Test | **Playwright MCP** | **Playwright MCP** |
| **Target Accuracy** | 95%+ | **99%+** | 99%+ |

---

## Scoring Weights

```yaml
scoring_weights:
  layout:      25%  # Widget hierarchy, Flex properties, positioning
  spacing:     25%  # Padding, margin, gaps (EdgeInsets, SizedBox)
  typography:  20%  # FontFamily, fontSize, fontWeight, letterSpacing
  colors:      15%  # Fill colors, text colors, gradients
  effects:     15%  # Shadows (BoxShadow), borders, opacity

category_thresholds:
  layout:      95%  # Must achieve
  spacing:     95%  # Must achieve
  typography:  95%  # Must achieve
  colors:      95%  # Must achieve
  effects:     90%  # Slightly lower due to rendering differences
```

---

## L1-L4 Auto-Fix Classification

| Level | Description | Flutter Examples | Auto-Fix |
|-------|-------------|------------------|----------|
| **L1** | Simple value changes | `fontSize: 14→16`, `EdgeInsets.all(16)→all(24)`, `Color(0xFF000000)→Color(0xFF333333)` | ✅ Yes |
| **L2** | Property additions | Add `letterSpacing: 0.5`, add `BoxShadow`, add `BorderRadius.circular(8)` | ✅ Yes |
| **L3** | Widget restructuring | `Row`→`Column`, `Container`→`DecoratedBox`, add `Expanded` wrapper | ⚠️ Approval |
| **L4** | Layout algorithm change | `ListView`→`CustomScrollView`, `Wrap`→`Flow`, add `CustomMultiChildLayout` | ❌ Manual |

---

## Core Philosophy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    RALPH HYBRID: BEST OF BOTH WORLDS                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Ralph Strengths:                     Original System Strengths:        │
│   ─────────────────                    ─────────────────────────         │
│   • File-based infinite context        • Code verification (numeric)    │
│   • Self-referential learning          • Visual verification (Gemini)   │
│   • Stop Hook for auto-repeat          • Weighted scoring system        │
│   • Git history utilization            • Auto-fix levels (L1-L4)        │
│                                                                          │
│   ═══════════════════════════════════════════════════════════════════   │
│                                                                          │
│   HYBRID = Ralph Loop + Dual Verification + Score-based Exit            │
│                                                                          │
│   + Playwright MCP for Flutter Web Screenshot Comparison                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    RALPH HYBRID EXECUTION FLOW                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────────────────────────────────────────────────────┐      │
│   │  /ralph-loop "Convert Figma to Flutter"                      │      │
│   │  --max-iterations 30                                         │      │
│   │  --completion-promise "FLUTTER_PIXEL_PERFECT_99"             │      │
│   └──────────────────────────────────────────────────────────────┘      │
│                              │                                           │
│                              ▼                                           │
│   ┌──────────────────────────────────────────────────────────────┐      │
│   │                    ITERATION N                                │      │
│   │                                                               │      │
│   │   1. Read State Files                                        │      │
│   │      └─ ./ralph-state/verification-report.json               │      │
│   │      └─ ./ralph-state/iteration-history.json                 │      │
│   │      └─ ./ralph-state/fixes-applied.json                     │      │
│   │                                                               │      │
│   │   2. Analyze Previous Failures                               │      │
│   │      └─ What failed? Why? What was tried?                    │      │
│   │                                                               │      │
│   │   3. Apply Targeted Fixes                                    │      │
│   │      └─ Based on previous iteration analysis                 │      │
│   │                                                               │      │
│   │   4. Run Dual Verification                                   │      │
│   │      ├─ Code Verification (Dart/Flutter property diff)       │      │
│   │      └─ Visual Verification (Playwright + Gemini)            │      │
│   │                                                               │      │
│   │   5. Update State Files                                      │      │
│   │      └─ Write results to verification-report.json            │      │
│   │                                                               │      │
│   │   6. Check Exit Condition                                    │      │
│   │      └─ code_score ≥99% AND visual_score ≥99%?              │      │
│   │                                                               │      │
│   └──────────────────────────────────────────────────────────────┘      │
│                              │                                           │
│               ┌──────────────┴──────────────┐                           │
│               ▼                              ▼                           │
│        Score ≥ 99%                    Score < 99%                       │
│               │                              │                           │
│               ▼                              ▼                           │
│   ┌─────────────────────┐      ┌─────────────────────────────┐         │
│   │ Output:             │      │ Stop Hook intercepts exit   │         │
│   │ <promise>           │      │ → Same prompt re-injected   │         │
│   │ FLUTTER_PIXEL_      │      │ → Files preserved           │         │
│   │ PERFECT_99          │      │ → Next iteration starts     │         │
│   │ </promise>          │      │                              │         │
│   │                     │      │                              │         │
│   │ LOOP EXITS          │      │ LOOP CONTINUES              │         │
│   └─────────────────────┘      └─────────────────────────────┘         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## State Files Structure

### ./ralph-state/verification-report.json

```json
{
  "iteration": 12,
  "timestamp": "2024-01-15T10:30:00Z",
  "scores": {
    "code": 97,
    "visual": 96,
    "combined": 96.5
  },
  "categories": {
    "layout": 98,
    "spacing": 96,
    "typography": 100,
    "colors": 99,
    "effects": 92
  },
  "status": "CONTINUE",
  "reason": "visual_score < 99%",
  "fixes_needed": [
    {
      "element": "hero_section",
      "issue": "shadow intensity mismatch",
      "current": "elevation: 2",
      "expected": "elevation: 4",
      "level": "L1",
      "auto_fixable": true
    }
  ],
  "visual_analysis": {
    "pixel_diff_percentage": 3.2,
    "problem_areas": ["header shadow", "button border-radius"],
    "suggested_fix": "elevation: 4, BorderRadius.circular(16)"
  }
}
```

### ./ralph-state/iteration-history.json

```json
{
  "total_iterations": 12,
  "history": [
    {
      "iteration": 1,
      "code": 72,
      "visual": 68,
      "fixes": ["initial generation"]
    },
    {
      "iteration": 5,
      "code": 89,
      "visual": 85,
      "fixes": ["spacing EdgeInsets.all(16)→all(24)", "colors"]
    },
    {
      "iteration": 10,
      "code": 95,
      "visual": 93,
      "fixes": ["typography fontSize 14→16", "layout gap"]
    },
    {
      "iteration": 12,
      "code": 97,
      "visual": 96,
      "fixes": ["effects elevation 2→4"]
    }
  ],
  "trend": "improving",
  "stuck_count": 0,
  "last_improvement": 12
}
```

### ./ralph-state/fixes-applied.json

```json
{
  "total_fixes": 23,
  "by_level": {
    "L1": 15,
    "L2": 6,
    "L3": 2,
    "L4": 0
  },
  "by_category": {
    "spacing": 8,
    "colors": 5,
    "typography": 4,
    "layout": 3,
    "effects": 3
  },
  "fixes": [
    {
      "iteration": 5,
      "file": "lib/features/home/widgets/hero_section.dart",
      "change": "EdgeInsets.all(16) → EdgeInsets.all(24)",
      "result": "spacing +4%"
    }
  ]
}
```

---

## Required Packages

```yaml
# Add to pubspec.yaml
dependencies:
  flutter:
    sdk: flutter
  flutter_svg: ^2.0.10+1      # REQUIRED for Figma SVG icons
  flutter_riverpod: ^2.5.1     # State management (if needed)
  go_router: ^14.2.0           # Routing (if needed)
  cached_network_image: ^3.3.1 # Image caching (optional)

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^4.0.0
```

---

## Pre-execution Checklist

Before starting the Ralph Hybrid loop, verify:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PRE-EXECUTION CHECKLIST                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  [ ] Flutter SDK 3.24+ installed (`flutter --version`)                  │
│  [ ] Dart SDK 3.5+ installed                                            │
│  [ ] Chrome/Chromium available for web testing                          │
│  [ ] Figma file URL/node-id ready                                       │
│  [ ] Figma MCP server connected (mcp__figma-desktop__*)                 │
│  [ ] Playwright MCP server connected (mcp__playwright__*)               │
│  [ ] Context7 MCP server connected (mcp__context7__*)                   │
│  [ ] flutter_svg package added to pubspec.yaml                          │
│  [ ] assets/ directories exist or will be created                       │
│  [ ] Git repository initialized (for checkpoints)                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Execution Command

```bash
# Start Ralph Hybrid Loop
/ralph-loop "
## Figma → Flutter Conversion Task

### Input
- Figma URL: [URL]
- Target: Flutter 3.24+ with Dart 3.5+
- Styling: ThemeData + Custom Theme Extensions
- State: Riverpod 3.x (if needed)

### Verification Requirements (BOTH must pass)
1. **Code Verification**: Flutter widget property comparison ≥99%
2. **Visual Verification**: Playwright screenshot diff ≥99%

### Flutter Web Screenshot Workflow
1. Run `flutter run -d chrome --web-port=3000`
2. Navigate Playwright to http://localhost:3000
3. Take screenshot with mcp__playwright__browser_take_screenshot
4. Compare with Figma screenshot

### On Each Iteration
1. Read ./ralph-state/verification-report.json
2. Read ./ralph-state/iteration-history.json
3. Analyze what failed in previous iteration
4. Apply targeted fixes based on analysis
5. Re-run dual verification
6. Update state files with results

### Self-Correction Protocol
- If same issue persists for 3 iterations → try alternative approach
- If score decreases → revert last change, try different fix
- If stuck for 5 iterations → document blocker, request L3-L4 approval

### Exit Condition
Output <promise>FLUTTER_PIXEL_PERFECT_99</promise> ONLY when:
- code_score >= 99 AND visual_score >= 99
- ALL categories >= 95
- NO pending L3-L4 fixes
- flutter analyze passes
- flutter build web succeeds

This promise may ONLY be declared when conditions are completely and unequivocally TRUE.
" --max-iterations 30 --completion-promise "FLUTTER_PIXEL_PERFECT_99"
```

---

## Iteration Protocol

### Phase 0A: Asset Download (MUST - First Iteration)

```dart
// ═══════════════════════════════════════════════════════════════════════════
// CRITICAL: Download ALL assets from Figma BEFORE any code generation
// This is NON-NEGOTIABLE - never skip this step
// ═══════════════════════════════════════════════════════════════════════════

Future<void> downloadFigmaAssets(String nodeId) async {
  // 1. Create directories
  await Bash(command: "mkdir -p assets/images assets/icons assets/images/2.0x assets/images/3.0x");

  // 2. Get design context to identify all image/icon nodes
  final designContext = await mcp__figma-desktop__get_design_context(nodeId: nodeId);

  // 3. Extract all image and icon node IDs from design context
  final assetNodes = extractAssetNodes(designContext);

  // 4. Track expected assets for later validation
  await Write("./ralph-state/expected-assets.json", jsonEncode(assetNodes));

  // 5. Download EACH asset from Figma - NO EXCEPTIONS
  for (final asset in assetNodes) {
    final savePath = asset.type == "icon"
      ? "assets/icons/${asset.name}.svg"
      : "assets/images/${asset.name}.png";

    try {
      await mcp__figma-desktop__get_screenshot(nodeId: asset.nodeId);

      // For images, also download 2x and 3x versions
      if (asset.type == "image") {
        await mcp__figma-desktop__get_screenshot(nodeId: asset.nodeId, scale: 2);
        await mcp__figma-desktop__get_screenshot(nodeId: asset.nodeId, scale: 3);
      }

      print("Downloaded: $savePath");
    } catch (error) {
      // CRITICAL: If download fails, STOP immediately
      print("FAILED to download asset: ${asset.name}");
      print("STOPPING - Cannot proceed without Figma assets");
      throw Exception("Asset download failed: ${asset.name}");
    }
  }

  // 6. Update pubspec.yaml with assets
  await updatePubspecAssets();

  // 7. Verify all assets exist
  final missingAssets = await verifyAssetsExist(assetNodes);
  if (missingAssets.isNotEmpty) {
    throw Exception("Missing assets: ${missingAssets.join(", ")}");
  }

  print("All ${assetNodes.length} assets downloaded from Figma");
}

// Helper: Extract asset nodes from design context
List<Map<String, dynamic>> extractAssetNodes(dynamic context) {
  final assets = <Map<String, dynamic>>[];

  void traverse(dynamic node) {
    if (node['type'] == 'VECTOR' || node['type'] == 'BOOLEAN_OPERATION') {
      assets.add({
        'nodeId': node['id'],
        'name': sanitizeFilename(node['name']),
        'type': 'icon',
        'path': 'assets/icons/${sanitizeFilename(node["name"])}.svg'
      });
    } else if (node['type'] == 'IMAGE' ||
               (node['type'] == 'RECTANGLE' &&
                node['fills']?.any((f) => f['type'] == 'IMAGE') == true)) {
      assets.add({
        'nodeId': node['id'],
        'name': sanitizeFilename(node['name']),
        'type': 'image',
        'path': 'assets/images/${sanitizeFilename(node["name"])}.png'
      });
    }
    if (node['children'] != null) {
      for (final child in node['children']) {
        traverse(child);
      }
    }
  }

  traverse(context);
  return assets;
}

String sanitizeFilename(String name) {
  return name.toLowerCase().replaceAll(RegExp(r'[^a-z0-9]'), '_').replaceAll(RegExp(r'_+'), '_');
}

// MUST call this before any code generation
await downloadFigmaAssets(FRAME_ID);
```

### Phase 0B: Initialize State (First Iteration Only)

```dart
// Check if this is the first iteration
final stateDir = "./ralph-state";
final stateExists = await Bash(command: "test -d $stateDir && echo 'exists'");

if (!stateExists.contains("exists")) {
  // Create state directory and initial files
  await Bash(command: "mkdir -p $stateDir");
  await Bash(command: "mkdir -p ./comparison");

  // Initialize verification-report.json
  final initialReport = {
    "iteration": 0,
    "timestamp": DateTime.now().toIso8601String(),
    "scores": {"code": 0, "visual": 0, "combined": 0},
    "categories": {"layout": 0, "spacing": 0, "typography": 0, "colors": 0, "effects": 0},
    "status": "STARTING",
    "reason": "Initial iteration",
    "fixes_needed": [],
    "visual_analysis": null
  };
  await Write("./ralph-state/verification-report.json", jsonEncode(initialReport));

  // Initialize iteration-history.json
  final initialHistory = {
    "total_iterations": 0,
    "history": [],
    "trend": "starting",
    "stuck_count": 0,
    "last_improvement": 0
  };
  await Write("./ralph-state/iteration-history.json", jsonEncode(initialHistory));

  // Initialize fixes-applied.json
  final initialFixes = {
    "total_fixes": 0,
    "by_level": {"L1": 0, "L2": 0, "L3": 0, "L4": 0},
    "by_category": {"spacing": 0, "colors": 0, "typography": 0, "layout": 0, "effects": 0},
    "fixes": []
  };
  await Write("./ralph-state/fixes-applied.json", jsonEncode(initialFixes));

  // Git checkpoint for rollback
  await Bash(command: "git checkout -b ralph-flutter-hybrid-checkpoint 2>/dev/null || git checkout ralph-flutter-hybrid-checkpoint");
  await Bash(command: "git add -A && git commit -m 'Ralph Hybrid Flutter: Initial state' --allow-empty");
}
```

### Phase 1: State Read (Every Iteration)

```dart
// MUST read state files at start of every iteration
final state = {
  'report': jsonDecode(await Read("./ralph-state/verification-report.json")),
  'history': jsonDecode(await Read("./ralph-state/iteration-history.json")),
  'fixes': jsonDecode(await Read("./ralph-state/fixes-applied.json"))
};

// Analyze previous iteration
if (state['report']['iteration'] > 0) {
  print("Previous: Code ${state['report']['scores']['code']}%, Visual ${state['report']['scores']['visual']}%");
  print("Fixes needed: ${state['report']['fixes_needed'].length}");
}
```

### Phase 2: Analysis & Fix

```dart
// Identify what to fix based on state
final prioritizedFixes = (state['report']['fixes_needed'] as List)
  .where((f) => f['auto_fixable'] == true)
  .toList()
  ..sort((a, b) => getLevelPriority(a['level']) - getLevelPriority(b['level']));

// Check if we're stuck
final history = state['history']['history'] as List;
final lastThree = history.length >= 3 ? history.sublist(history.length - 3) : history;
final isStuck = lastThree.every((h) => h['code'] == lastThree[0]['code']);

if (isStuck) {
  // Try alternative approach
  print("Stuck detected - trying alternative approach");
}

// Apply fixes
for (final fix in prioritizedFixes) {
  await applyFix(fix);
}
```

### Phase 3: Dual Verification with Playwright

```dart
// 1. Code Verification
final codeScore = await runCodeVerification(
  figmaContext: await mcp__figma-desktop__get_design_context(nodeId: FRAME_ID),
  generatedCode: await Read("lib/features/[feature]/widgets/[widget].dart")
);

// 2. Visual Verification via Playwright
// Get Figma screenshot
await mcp__figma-desktop__get_screenshot(nodeId: FRAME_ID);
// Saves to ./comparison/figma.png

// Start Flutter web server (if not running)
final serverRunning = await Bash(command: "lsof -i :3000 | grep LISTEN || echo 'not running'");
if (serverRunning.contains('not running')) {
  await Bash(
    command: "flutter run -d chrome --web-port=3000 &",
    run_in_background: true
  );
  await Future.delayed(Duration(seconds: 8)); // Wait for server startup
}

// Navigate and screenshot with Playwright
await mcp__playwright__browser_navigate(url: "http://localhost:3000");
await Future.delayed(Duration(seconds: 2)); // Wait for render
await mcp__playwright__browser_take_screenshot();
// Saves to ./comparison/current.png

// 3. Compare screenshots using Gemini CLI
final visualResult = await Bash(
  command: '''gemini -p "Compare these two UI screenshots. Return JSON with:
  - visual_score (0-100): pixel-perfect accuracy percentage
  - categories: {layout, spacing, typography, colors, effects} each 0-100
  - differences: array of specific issues found
  - fixes: array of suggested CSS/styling fixes
  Be STRICT - small differences should reduce score." ./comparison/figma.png ./comparison/current.png'''
);

final visualScore = jsonDecode(visualResult)['visual_score'];
```

### Phase 4: State Update

```dart
// Track applied fixes from this iteration
final appliedFixes = <String>[];
for (final fix in prioritizedFixes) {
  appliedFixes.add("${fix['current']} → ${fix['expected']}");
}

// Calculate category scores from visual analysis
final visualAnalysis = jsonDecode(visualResult);
final categories = visualAnalysis['categories'] ?? {
  'layout': 0, 'spacing': 0, 'typography': 0, 'colors': 0, 'effects': 0
};

// Update verification report
final newReport = {
  'iteration': state['report']['iteration'] + 1,
  'timestamp': DateTime.now().toIso8601String(),
  'scores': {
    'code': codeScore,
    'visual': visualScore,
    'combined': (codeScore + visualScore) / 2
  },
  'categories': categories,
  'status': (codeScore >= 99 && visualScore >= 99) ? 'COMPLETE' : 'CONTINUE',
  'reason': codeScore < 99 ? 'code_score < 99%' : visualScore < 99 ? 'visual_score < 99%' : 'Checking categories',
  'fixes_needed': visualAnalysis['fixes'] ?? [],
  'visual_analysis': visualAnalysis
};

await Write("./ralph-state/verification-report.json", jsonEncode(newReport));

// Update history
(state['history']['history'] as List).add({
  'iteration': newReport['iteration'],
  'code': codeScore,
  'visual': visualScore,
  'fixes': appliedFixes
});
state['history']['total_iterations'] = newReport['iteration'];

await Write("./ralph-state/iteration-history.json", jsonEncode(state['history']));

// Create git checkpoint every 5 iterations
await createGitCheckpoint(newReport['iteration']);

// Check for regression and handle
await handleRegression(state['history']);
```

### Phase 5: Exit Check (WITH MUST VALIDATIONS)

```dart
// ═══════════════════════════════════════════════════════════════════════════
// MUST VALIDATION #1: Verify all assets are from Figma (not generated/library)
// ═══════════════════════════════════════════════════════════════════════════
Future<ValidationResult> validateFigmaAssets() async {
  final issues = <String>[];

  // Check for forbidden icon library imports
  final dartFiles = await Glob("lib/**/*.dart");
  for (final file in dartFiles) {
    final content = await Read(file);

    // FORBIDDEN: Icon library imports
    if (content.contains("flutter_icons") ||
        content.contains("font_awesome_flutter") ||
        content.contains("material_design_icons") ||
        content.contains("cupertino_icons")) {
      issues.add("$file: Uses forbidden icon library - MUST use Figma assets");
    }

    // FORBIDDEN: Material Icons (except specific approved ones)
    final iconMatches = RegExp(r'Icons\.\w+').allMatches(content);
    if (iconMatches.isNotEmpty) {
      issues.add("$file: Uses Material Icons - MUST use Figma assets");
    }

    // Check for placeholder images
    if (content.contains("placeholder") || content.contains("via.placeholder")) {
      issues.add("$file: Contains placeholder image - MUST use Figma assets");
    }
  }

  // Verify expected assets from Phase 0A exist
  try {
    final expectedAssets = jsonDecode(await Read("./ralph-state/expected-assets.json")) as List;
    for (final asset in expectedAssets) {
      final exists = await Bash(command: "test -f '${asset['path']}' && echo 'exists'");
      if (!exists.contains("exists")) {
        issues.add("Missing Figma asset: ${asset['path']}");
      }
    }
  } catch (_) {
    issues.add("Cannot verify assets - expected-assets.json missing");
  }

  return ValidationResult(valid: issues.isEmpty, issues: issues);
}

// ═══════════════════════════════════════════════════════════════════════════
// MUST VALIDATION #3: Build and Analyze must succeed
// ═══════════════════════════════════════════════════════════════════════════
Future<ValidationResult> validateBuildAndAnalyze() async {
  final errors = <String>[];

  print("Running flutter analyze...");
  final analyzeResult = await Bash(
    command: "flutter analyze 2>&1",
    timeout: 120000
  );

  if (analyzeResult.contains("error") ||
      analyzeResult.contains("Error") ||
      !analyzeResult.contains("No issues found")) {
    errors.add("Flutter analyze failed");
    final errorLines = analyzeResult.split("\n")
      .where((line) => line.contains("error") || line.contains("Error"))
      .take(10)
      .toList();
    errors.addAll(errorLines);
  }

  print("Running flutter build web...");
  final buildResult = await Bash(
    command: "flutter build web 2>&1",
    timeout: 180000 // 3 minute timeout
  );

  // Check for common error patterns
  final hasErrors = buildResult.contains("Error:") ||
                    buildResult.contains("error:") ||
                    buildResult.contains("Could not") ||
                    buildResult.contains("Failed to compile");

  if (hasErrors) {
    errors.add("Flutter build web failed");
    final errorLines = buildResult.split("\n")
      .where((line) =>
        line.contains("error") ||
        line.contains("Error") ||
        line.contains("Could not"))
      .take(10)
      .toList();
    errors.addAll(errorLines);
  }

  return ValidationResult(success: errors.isEmpty, errors: errors);
}

// Helper: Check if fix level requires approval (L3 or L4)
bool isHighLevelFix(String level) {
  return level == "L3" || level == "L4";
}

// ═══════════════════════════════════════════════════════════════════════════
// EXIT CONDITION CHECK (ALL THREE MUST RULES REQUIRED)
// ═══════════════════════════════════════════════════════════════════════════

// MUST #2: Check 98% MINIMUM threshold (99% target, 98% hard minimum)
const HARD_MINIMUM = 98;
const TARGET = 99;

if (codeScore < HARD_MINIMUM || visualScore < HARD_MINIMUM) {
  // CANNOT exit - below hard minimum
  print("MUST #2 FAILED: Scores below 98% minimum");
  print("   Code: $codeScore% (need >= $HARD_MINIMUM%)");
  print("   Visual: $visualScore% (need >= $HARD_MINIMUM%)");
  print("Loop MUST continue - no escape below 98%");
  // Do NOT output promise - loop continues
} else if (codeScore >= TARGET && visualScore >= TARGET) {
  // Target achieved - check remaining conditions
  print("MUST #2 PASSED: Both scores >= $TARGET%");

  final allCategoriesPass = (newReport['categories'] as Map).values.every((v) => v >= 95);
  final noPendingL3L4 = (newReport['fixes_needed'] as List)
    .where((f) => isHighLevelFix(f['level']))
    .isEmpty;

  if (allCategoriesPass && noPendingL3L4) {
    // Check MUST #1: Asset validation
    final assetCheck = await validateFigmaAssets();
    if (!assetCheck.valid) {
      print("MUST #1 FAILED: Asset validation");
      for (final issue in assetCheck.issues) {
        print("  - $issue");
      }
      print("Cannot complete - fix asset issues first");
      // Do NOT output promise - loop continues
    } else {
      print("MUST #1 PASSED: All assets from Figma");

      // Check MUST #3: Build and Analyze validation
      final buildCheck = await validateBuildAndAnalyze();
      if (!buildCheck.success) {
        print("MUST #3 FAILED: Build/Analyze errors");
        for (final err in buildCheck.errors) {
          print("  - $err");
        }
        print("Cannot complete - fix build errors first");
        // Do NOT output promise - loop continues

        // Add build errors to fixes_needed for next iteration
        (newReport['fixes_needed'] as List).add({
          'element': 'build',
          'issue': 'Build/Analyze failed',
          'current': 'Errors present',
          'expected': 'Build success',
          'level': 'L1',
          'auto_fixable': true,
          'errors': buildCheck.errors
        });
        await Write("./ralph-state/verification-report.json", jsonEncode(newReport));
      } else {
        print("MUST #3 PASSED: Build and Analyze successful");

        // ALL THREE MUST RULES PASSED - NOW CAN COMPLETE
        print("ALL MUST RULES PASSED - Conversion complete!");
        print("<promise>FLUTTER_PIXEL_PERFECT_99</promise>");

        // Generate final report
        await generateFinalReport();
      }
    }
  } else {
    print("Category or L3/L4 checks failed - continuing...");
    if (!allCategoriesPass) {
      final failingCategories = (newReport['categories'] as Map).entries
        .where((e) => e.value < 95)
        .map((e) => "${e.key}: ${e.value}%")
        .toList();
      print("  Failing categories: ${failingCategories.join(", ")}");
    }
  }
} else {
  // Between 98-99% - acceptable but continue for target
  print("Scores at $codeScore%/$visualScore% - above minimum but below target");
  print("Continuing to reach 99% target...");
  // Continue loop for improvement
}

// If not exiting, Stop Hook will intercept and restart
```

---

## Stuck Detection & Recovery

```yaml
stuck_detection:
  # Same score for N iterations
  score_plateau:
    threshold: 3
    action: try_alternative_approach

  # Score decreasing
  score_regression:
    threshold: 2
    action: revert_and_retry

  # No improvement for N iterations
  no_progress:
    threshold: 5
    action: escalate_to_user

alternative_approaches:
  spacing_stuck:
    - Try arbitrary values (EdgeInsets.only(left: 17))
    - Use MediaQuery-based spacing

  visual_stuck:
    - Request higher resolution Figma export
    - Check for responsive breakpoint mismatch

  layout_stuck:
    - Switch Row ↔ Column
    - Try Stack for specific elements
    - Use CustomMultiChildLayout
```

---

## Safety Mechanisms

```yaml
safety:
  max_iterations: 30

  # Auto-stop conditions
  auto_stop:
    - stuck_for: 10 iterations
    - score_below: 70 for 5 iterations
    - regression_count: 5 times

  # Escalation
  escalation:
    L3_fixes: require_approval
    L4_fixes: halt_and_report

  # Rollback
  rollback:
    enabled: true
    checkpoint_every: 5 iterations
    git_branch: ralph-flutter-hybrid-checkpoint
```

### Git Checkpoint & Rollback Implementation

```dart
// Create checkpoint every 5 iterations
Future<void> createGitCheckpoint(int iteration) async {
  if (iteration % 5 == 0) {
    await Bash(command: "git add -A && git commit -m 'Ralph Hybrid Flutter: Checkpoint iteration $iteration' --allow-empty");
    print("Git checkpoint created at iteration $iteration");
  }
}

// Rollback to previous checkpoint when regression detected
Future<void> rollbackToLastCheckpoint(int currentIteration) async {
  final checkpointIter = ((currentIteration - 1) ~/ 5) * 5;
  if (checkpointIter <= 0) {
    print("No previous checkpoint to rollback to");
    return;
  }

  // Find the checkpoint commit
  final result = await Bash(
    command: "git log --oneline --all | grep 'Checkpoint iteration $checkpointIter' | head -1 | cut -d' ' -f1"
  );

  final commitHash = result.trim();
  if (commitHash.isNotEmpty) {
    await Bash(command: "git reset --soft $commitHash");
    print("Rolled back to checkpoint at iteration $checkpointIter ($commitHash)");
  }
}

// Detect regression and trigger rollback
Future<bool> handleRegression(Map<String, dynamic> history) async {
  final historyList = history['history'] as List;
  if (historyList.length < 2) return false;

  final prev = historyList[historyList.length - 2];
  final curr = historyList[historyList.length - 1];

  if (curr['code'] < prev['code'] || curr['visual'] < prev['visual']) {
    print("Regression detected: Code ${prev['code']}→${curr['code']}, Visual ${prev['visual']}→${curr['visual']}");
    await rollbackToLastCheckpoint(curr['iteration']);
    return true;
  }
  return false;
}

// Helper functions
int getLevelPriority(String level) {
  const priorities = {'L1': 1, 'L2': 2, 'L3': 3, 'L4': 4};
  return priorities[level] ?? 99;
}

Future<void> applyFix(Map<String, dynamic> fix) async {
  await Edit(
    file_path: fix['file'] ?? "lib/features/unknown/widget.dart",
    old_string: fix['current'],
    new_string: fix['expected']
  );
  print("Applied fix: ${fix['current']} → ${fix['expected']}");
}
```

---

## Exit Conditions

```yaml
success:
  - code_score >= 99%
  - visual_score >= 99%
  - all_categories >= 95%
  - no_pending_L3_L4_fixes
  - flutter_analyze: pass
  - flutter_build_web: success
  - completion_marker: "<promise>FLUTTER_PIXEL_PERFECT_99</promise>"

stop:
  - max_iterations (30) reached
  - stuck_for 10 consecutive iterations
  - user_cancellation (/cancel-ralph)
```

---

## Output Structure

```
project/
├── lib/
│   ├── core/
│   │   ├── theme/
│   │   │   ├── app_theme.dart
│   │   │   ├── app_colors.dart
│   │   │   ├── app_typography.dart
│   │   │   ├── app_spacing.dart
│   │   │   └── app_shadows.dart
│   │   └── constants/
│   │       └── assets.dart
│   ├── features/
│   │   └── [feature]/
│   │       └── presentation/
│   │           ├── pages/
│   │           └── widgets/
│   └── shared/
│       └── widgets/
├── assets/
│   ├── images/           # Downloaded from Figma
│   │   ├── 2.0x/
│   │   └── 3.0x/
│   └── icons/            # Downloaded from Figma (SVG)
├── ralph-state/          # State files for self-reference
│   ├── verification-report.json
│   ├── iteration-history.json
│   ├── fixes-applied.json
│   └── expected-assets.json
├── comparison/           # Verification images
│   ├── figma.png
│   └── current.png
└── reports/
    └── final-report.md   # Generated on completion
```

---

## Final Report Template

```markdown
# Ralph Hybrid Flutter Conversion Report

## Summary
- **Figma File**: [name]
- **Total Iterations**: 15
- **Final Score**: Code 99.2% | Visual 99.1%
- **Time Elapsed**: 45 minutes

## Iteration Journey
| Iteration | Code | Visual | Key Fixes |
|-----------|------|--------|-----------|
| 1 | 72% | 68% | Initial generation |
| 5 | 89% | 85% | Spacing, colors |
| 10 | 95% | 93% | Typography, layout |
| 15 | 99.2% | 99.1% | Final effects |

## Self-Correction Highlights
- **Stuck at iteration 8**: Spacing issue, resolved by trying arbitrary value
- **Regression at iteration 11**: Reverted shadow change, tried alternative

## Widgets Generated
- lib/features/home/widgets/hero_section.dart (99% match)
- lib/shared/widgets/feature_card.dart (99% match)
- lib/shared/widgets/cta_button.dart (100% match)

## Validation Results
- flutter analyze: No issues found
- flutter build web: Success

## <promise>FLUTTER_PIXEL_PERFECT_99</promise>
```

---

## ThemeData Integration Patterns

```dart
// lib/core/theme/app_theme.dart
import 'package:flutter/material.dart';
import 'app_colors.dart';
import 'app_typography.dart';
import 'app_spacing.dart';

class AppTheme {
  static ThemeData get lightTheme => ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: AppColors.primary,
      brightness: Brightness.light,
    ),
    textTheme: AppTypography.textTheme,
    extensions: [
      AppSpacing.standard,
      AppShadows.standard,
    ],
  );
}

// lib/core/theme/app_spacing.dart
@immutable
class AppSpacing extends ThemeExtension<AppSpacing> {
  final double xs;
  final double sm;
  final double md;
  final double lg;
  final double xl;

  const AppSpacing({
    required this.xs,
    required this.sm,
    required this.md,
    required this.lg,
    required this.xl,
  });

  static const standard = AppSpacing(
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
  );

  @override
  ThemeExtension<AppSpacing> copyWith({...}) => ...;

  @override
  ThemeExtension<AppSpacing> lerp(...) => ...;
}

// Usage in widgets
final spacing = Theme.of(context).extension<AppSpacing>()!;
Padding(padding: EdgeInsets.all(spacing.md), child: ...);
```

---

## Riverpod 3.x State Management Pattern

```dart
// lib/features/home/providers/home_provider.dart
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'home_provider.g.dart';
part 'home_provider.freezed.dart';

// Freezed state class for immutability
@freezed
class HomeState with _$HomeState {
  const factory HomeState({
    @Default('') String data,
    @Default(false) bool isLoading,
  }) = _HomeState;

  factory HomeState.initial() => const HomeState();
}

// Riverpod 3.x Notifier (replaces StateNotifier)
@riverpod
class HomeNotifier extends _$HomeNotifier {
  @override
  HomeState build() => HomeState.initial();

  void updateData(String data) {
    state = state.copyWith(data: data);
  }

  Future<void> loadData() async {
    state = state.copyWith(isLoading: true);
    try {
      final result = await ref.read(userRepositoryProvider).getData();
      state = state.copyWith(data: result, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false);
    }
  }
}

// Simple sync provider with @riverpod annotation
@riverpod
int counter(CounterRef ref) => 0;

// Async provider
@riverpod
Future<User> user(UserRef ref) async {
  return await ref.read(userRepositoryProvider).getUser();
}

// Usage in widget (ConsumerWidget)
class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(homeNotifierProvider);
    final notifier = ref.read(homeNotifierProvider.notifier);

    return Column(
      children: [
        Text(state.data),
        if (state.isLoading) const CircularProgressIndicator(),
        ElevatedButton(
          onPressed: () => notifier.loadData(),
          child: const Text('Load'),
        ),
      ],
    );
  }
}
```

### Riverpod 3.x Required Packages

```yaml
# pubspec.yaml - REQUIRED for Riverpod 3.x code generation
dependencies:
  flutter_riverpod: ^2.5.1
  riverpod_annotation: ^2.3.5       # For @riverpod annotation

dev_dependencies:
  riverpod_generator: ^2.4.0        # REQUIRED for code generation
  build_runner: ^2.4.9
  freezed: ^2.5.2                   # For state classes
  freezed_annotation: ^2.4.1
```

```bash
# Generate code after adding providers
dart run build_runner build --delete-conflicting-outputs
```

---

## Troubleshooting

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| **SVG not rendering** | Missing flutter_svg | Add `flutter_svg: ^2.0.10+1` to pubspec.yaml |
| **Asset not found** | Path mismatch | Check pubspec.yaml assets section matches actual paths |
| **2x/3x images not loading** | Directory structure | Ensure `assets/images/2.0x/` and `assets/images/3.0x/` exist |
| **Playwright connection failed** | MCP not running | Start Playwright MCP server |
| **Flutter web port conflict** | Port 3000 in use | Kill existing process or use different port |
| **Analyze errors** | Import issues | Run `flutter pub get` first |
| **Build timeout** | Large project | Increase timeout to 300000ms |
| **Score stuck at ~95%** | Fine-tuning needed | Try L2 fixes (letterSpacing, shadows) |

### Flutter Web Server Commands

```bash
# Start Flutter web with specific port
flutter run -d chrome --web-port=3000

# Build web for production test
flutter build web

# Run analyze
flutter analyze --no-fatal-infos

# Clean and rebuild
flutter clean && flutter pub get && flutter build web
```

---

## Version

- Agent Version: 3.1.0
- Method: Ralph Hybrid (Loop + Dual Verification)
- Max Iterations: 30
- Target Accuracy: 99%+
- Flutter Target: 3.24+
- Dart Target: 3.5+

---

*Version: 3.1.0 | Last Updated: 2026-01-24 | Ralph Hybrid with MUST Rules (Asset/98%/Build) + Playwright + ThemeData + Riverpod*
