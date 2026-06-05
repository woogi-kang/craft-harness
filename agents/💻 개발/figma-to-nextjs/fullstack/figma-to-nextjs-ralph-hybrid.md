---
name: figma-to-nextjs-ralph-hybrid
description: Hybrid approach combining Ralph Wiggum self-referential loop with dual verification system. Achieves 99%+ accuracy through file-based context persistence and iterative self-correction.
tools: Read, Write, Edit, Glob, Grep, Bash, TodoWrite, Task, mcp__figma-desktop__get_design_context, mcp__figma-desktop__get_variable_defs, mcp__figma-desktop__get_screenshot, mcp__figma-desktop__get_metadata, mcp__figma-desktop__create_design_system_rules, mcp__context7__resolve-library-id, mcp__context7__query-docs, mcp__playwright__browser_snapshot, mcp__playwright__browser_take_screenshot, mcp__playwright__browser_navigate, mcp__playwright__browser_click
model: opus
---

# Figma → Next.js Ralph Hybrid Converter

> **Version**: 3.1.0 | **Type**: Ralph Hybrid | **Target**: Next.js 15+ App Router
> **Target Accuracy**: 99%+ with Self-Referential Feedback Loop
> **Method**: Ralph Loop + Dual Verification (Code + Visual)

---

## ⚠️ CRITICAL MUST RULES (NON-NEGOTIABLE)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    🚨 CRITICAL MUST RULES 🚨                             │
│                These rules CANNOT be violated under ANY circumstances    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  MUST #1: FIGMA ASSET DOWNLOAD                                          │
│  ════════════════════════════════════════════════════════════════════   │
│  • ALL images MUST be downloaded from Figma using MCP tools             │
│  • ALL icons MUST be downloaded from Figma (NO icon libraries)          │
│  • NEVER use placeholder images or generate SVG manually                │
│  • NEVER use lucide-react, heroicons, or any icon library               │
│  • Download command: mcp__figma-desktop__get_screenshot for each asset  │
│  • Save to: public/images/ and public/icons/                            │
│  • If Figma export fails, STOP and report - do NOT substitute           │
│                                                                          │
│  MUST #2: 98% MINIMUM THRESHOLD                                         │
│  ════════════════════════════════════════════════════════════════════   │
│  • Loop CANNOT exit until BOTH code_score >= 98% AND visual_score >= 98%│
│  • 99% target is preferred, but 98% is the HARD MINIMUM                 │
│  • MUST verify with actual screenshot comparison (Gemini CLI)           │
│  • If combined score < 98%, loop MUST continue                          │
│  • No escape hatch below 98% - blocked permanently until threshold met  │
│                                                                          │
│  MUST #3: BUILD SUCCESS VALIDATION                                      │
│  ════════════════════════════════════════════════════════════════════   │
│  • MUST run `npm run build` before declaring completion                 │
│  • Build MUST succeed with ZERO errors                                  │
│  • All imports MUST be valid and resolvable                             │
│  • TypeScript errors = build failure = cannot complete                  │
│  • ESLint errors (if configured) MUST be resolved                       │
│                                                                          │
│  VIOLATION = IMMEDIATE FAILURE                                          │
│  ─────────────────────────────────────────────────────────────────────  │
│  Breaking ANY of these rules means the conversion is FAILED,            │
│  regardless of visual appearance or score calculations.                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Hybrid vs Pure Ralph vs Original Comparison

| Feature | Original Pro | Ralph Hybrid | Ralph Pure |
|---------|--------------|--------------|------------|
| **Loop Mechanism** | Agent internal | Stop Hook + Score | Stop Hook + Promise |
| **Context Persistence** | Agent memory | **File-based** | **File-based** |
| **Max Iterations** | 10 (5×2) | **Unlimited** (safety: 30) | **Unlimited** (safety: 50) |
| **Verification** | Dual (Code+Visual) | **Dual (Code+Visual)** | Single (Promise) |
| **Exit Condition** | Score ≥98% | **Score ≥99%** | Promise tag |
| **Self-Reference** | None | **Yes (reads previous)** | **Yes (reads previous)** |
| **Parallel Agents** | 2 agents | **1 agent** | **1 agent** |
| **Target Accuracy** | 98%+ | **99%+** | 99%+ |

---

## Core Philosophy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    RALPH HYBRID: BEST OF BOTH WORLDS                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Ralph의 강점:                      기존 시스템의 강점:                 │
│   ─────────────                      ─────────────────                   │
│   • 파일 기반 무한 컨텍스트           • Code 검증 (수치 비교)            │
│   • 자기 참조적 학습                  • Visual 검증 (Gemini CLI)         │
│   • Stop Hook으로 자동 반복          • 가중치 기반 점수 체계             │
│   • Git 히스토리 활용                 • 자동 수정 레벨 (L1-L4)           │
│                                                                          │
│   ═══════════════════════════════════════════════════════════════════   │
│                                                                          │
│   HYBRID = Ralph Loop + Dual Verification + Score-based Exit            │
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
│   │  /ralph-loop "Convert Figma to Next.js"                      │      │
│   │  --max-iterations 30                                         │      │
│   │  --completion-promise "PIXEL_PERFECT_99"                     │      │
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
│   │      ├─ Code Verification (Tailwind class diff)              │      │
│   │      └─ Visual Verification (Gemini CLI image diff)          │      │
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
│   │ PIXEL_PERFECT_99    │      │ → Files preserved           │         │
│   │ </promise>          │      │ → Next iteration starts     │         │
│   │                     │      │                              │         │
│   │ ✅ LOOP EXITS       │      │ 🔄 LOOP CONTINUES           │         │
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
      "element": ".hero-section",
      "issue": "shadow intensity mismatch",
      "current": "shadow-md",
      "expected": "shadow-lg",
      "level": "L1",
      "auto_fixable": true
    }
  ],
  "gemini_analysis": {
    "pixel_diff_percentage": 3.2,
    "problem_areas": ["header shadow", "button border-radius"],
    "suggested_css": "shadow-lg rounded-xl"
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
      "fixes": ["spacing p-4→p-6", "colors blue-500→blue-600"]
    },
    {
      "iteration": 10,
      "code": 95,
      "visual": 93,
      "fixes": ["typography text-lg→text-xl", "layout gap-3→gap-4"]
    },
    {
      "iteration": 12,
      "code": 97,
      "visual": 96,
      "fixes": ["effects shadow-sm→shadow-md"]
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
      "file": "src/components/hero.tsx",
      "change": "p-4 → p-6",
      "result": "spacing +4%"
    }
  ]
}
```

---

## Execution Command

```bash
# Start Ralph Hybrid Loop
/ralph-loop "
## Figma → Next.js Conversion Task

### Input
- Figma URL: [URL]
- Target: Next.js 15+ with App Router
- Styling: Tailwind CSS 4.x + shadcn/ui

### Verification Requirements (BOTH must pass)
1. **Code Verification**: Tailwind class comparison ≥99%
2. **Visual Verification**: Gemini CLI image diff ≥99%

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
Output <promise>PIXEL_PERFECT_99</promise> ONLY when:
- code_score >= 99 AND visual_score >= 99
- ALL categories >= 95
- NO pending L3-L4 fixes

This promise may ONLY be declared when conditions are completely and unequivocally TRUE.
" --max-iterations 30 --completion-promise "PIXEL_PERFECT_99"
```

---

## Iteration Protocol

### Phase 0A: Asset Download (MUST - First Iteration)

```typescript
// ═══════════════════════════════════════════════════════════════════════════
// CRITICAL: Download ALL assets from Figma BEFORE any code generation
// This is NON-NEGOTIABLE - never skip this step
// ═══════════════════════════════════════════════════════════════════════════

async function downloadFigmaAssets(nodeId: string): Promise<void> {
  // 1. Create directories
  await Bash({ command: "mkdir -p public/images public/icons" });

  // 2. Get design context to identify all image/icon nodes
  const designContext = await mcp__figma_desktop__get_design_context({ nodeId });

  // 3. Extract all image and icon node IDs from design context
  const assetNodes = extractAssetNodes(designContext);

  // 4. Track expected assets for later validation
  await Write("./ralph-state/expected-assets.json", JSON.stringify(assetNodes, null, 2));

  // 5. Download EACH asset from Figma - NO EXCEPTIONS
  for (const asset of assetNodes) {
    const savePath = asset.type === "icon"
      ? `public/icons/${asset.name}.svg`
      : `public/images/${asset.name}.png`;

    try {
      await mcp__figma_desktop__get_screenshot({
        nodeId: asset.nodeId,
        // Export as SVG for icons, PNG for images
      });
      console.log(`✅ Downloaded: ${savePath}`);
    } catch (error) {
      // CRITICAL: If download fails, STOP immediately
      console.error(`❌ FAILED to download asset: ${asset.name}`);
      console.error("STOPPING - Cannot proceed without Figma assets");
      throw new Error(`Asset download failed: ${asset.name}`);
    }
  }

  // 6. Verify all assets exist
  const missingAssets = await verifyAssetsExist(assetNodes);
  if (missingAssets.length > 0) {
    throw new Error(`Missing assets: ${missingAssets.join(", ")}`);
  }

  console.log(`✅ All ${assetNodes.length} assets downloaded from Figma`);
}

// Helper: Extract asset nodes from design context
function extractAssetNodes(context: any): Array<{nodeId: string, name: string, type: "icon"|"image", path: string}> {
  // Parse design context to find all IMAGE and VECTOR nodes
  // Icons are typically VECTOR or small IMAGE nodes
  // Images are larger IMAGE nodes or RECTANGLE with fills
  const assets: Array<{nodeId: string, name: string, type: "icon"|"image", path: string}> = [];

  // Recursively traverse design context
  function traverse(node: any) {
    if (node.type === "VECTOR" || node.type === "BOOLEAN_OPERATION") {
      assets.push({
        nodeId: node.id,
        name: sanitizeFilename(node.name),
        type: "icon",
        path: `public/icons/${sanitizeFilename(node.name)}.svg`
      });
    } else if (node.type === "IMAGE" || (node.type === "RECTANGLE" && node.fills?.some((f: any) => f.type === "IMAGE"))) {
      assets.push({
        nodeId: node.id,
        name: sanitizeFilename(node.name),
        type: "image",
        path: `public/images/${sanitizeFilename(node.name)}.png`
      });
    }
    if (node.children) {
      node.children.forEach(traverse);
    }
  }

  traverse(context);
  return assets;
}

function sanitizeFilename(name: string): string {
  return name.toLowerCase().replace(/[^a-z0-9]/g, "-").replace(/-+/g, "-");
}

// MUST call this before any code generation
await downloadFigmaAssets(FRAME_ID);
```

### Phase 0B: Initialize State (First Iteration Only)

```typescript
// Check if this is the first iteration
const stateDir = "./ralph-state";
const stateExists = await Bash({ command: `test -d ${stateDir} && echo "exists"` });

if (!stateExists.includes("exists")) {
  // Create state directory and initial files
  await Bash({ command: `mkdir -p ${stateDir}` });
  await Bash({ command: `mkdir -p ./comparison` });

  // Initialize verification-report.json
  const initialReport = {
    iteration: 0,
    timestamp: new Date().toISOString(),
    scores: { code: 0, visual: 0, combined: 0 },
    categories: { layout: 0, spacing: 0, typography: 0, colors: 0, effects: 0 },
    status: "STARTING",
    reason: "Initial iteration",
    fixes_needed: [],
    gemini_analysis: null
  };
  await Write("./ralph-state/verification-report.json", JSON.stringify(initialReport, null, 2));

  // Initialize iteration-history.json
  const initialHistory = {
    total_iterations: 0,
    history: [],
    trend: "starting",
    stuck_count: 0,
    last_improvement: 0
  };
  await Write("./ralph-state/iteration-history.json", JSON.stringify(initialHistory, null, 2));

  // Initialize fixes-applied.json
  const initialFixes = {
    total_fixes: 0,
    by_level: { L1: 0, L2: 0, L3: 0, L4: 0 },
    by_category: { spacing: 0, colors: 0, typography: 0, layout: 0, effects: 0 },
    fixes: []
  };
  await Write("./ralph-state/fixes-applied.json", JSON.stringify(initialFixes, null, 2));

  // Git checkpoint for rollback
  await Bash({ command: "git checkout -b ralph-hybrid-checkpoint 2>/dev/null || git checkout ralph-hybrid-checkpoint" });
  await Bash({ command: "git add -A && git commit -m 'Ralph Hybrid: Initial state' --allow-empty" });
}
```

### Phase 1: State Read (Every Iteration)

```typescript
// MUST read state files at start of every iteration
const state = {
  report: JSON.parse(await Read("./ralph-state/verification-report.json")),
  history: JSON.parse(await Read("./ralph-state/iteration-history.json")),
  fixes: JSON.parse(await Read("./ralph-state/fixes-applied.json"))
};

// Analyze previous iteration
if (state.report.iteration > 0) {
  console.log(`Previous: Code ${state.report.scores.code}%, Visual ${state.report.scores.visual}%`);
  console.log(`Fixes needed: ${state.report.fixes_needed.length}`);
}
```

### Phase 2: Analysis & Fix

```typescript
// Identify what to fix based on state
const prioritizedFixes = state.report.fixes_needed
  .filter(f => f.auto_fixable)
  .sort((a, b) => getLevelPriority(a.level) - getLevelPriority(b.level));

// Check if we're stuck
const history = state.history.history;
const lastThree = history.slice(-3);
const isStuck = lastThree.every(h => h.code === lastThree[0].code);

if (isStuck) {
  // Try alternative approach
  console.log("Stuck detected - trying alternative approach");
}

// Apply fixes
for (const fix of prioritizedFixes) {
  await applyFix(fix);
}
```

### Phase 3: Dual Verification

```typescript
// 1. Code Verification
const codeScore = await runCodeVerification({
  figmaContext: await mcp__figma_desktop__get_design_context({ nodeId }),
  generatedCode: await Read("src/components/[component].tsx")
});

// 2. Visual Verification (Gemini CLI)
await mcp__figma_desktop__get_screenshot({ nodeId, savePath: "./comparison/figma.png" });
await mcp__playwright__browser_take_screenshot({ savePath: "./comparison/impl.png" });

const visualResult = await Bash({
  command: `gemini -p "Compare images, output JSON with visual_score (0-100), differences, fixes" ./comparison/figma.png ./comparison/impl.png`
});

const visualScore = JSON.parse(visualResult).visual_score;
```

### Phase 4: State Update

```typescript
// Track applied fixes from this iteration
const appliedFixes: string[] = [];
for (const fix of prioritizedFixes) {
  appliedFixes.push(`${fix.current} → ${fix.expected}`);
}

// Calculate category scores from Gemini analysis
const categories = {
  layout: calculateCategoryScore("layout", visualResult),
  spacing: calculateCategoryScore("spacing", visualResult),
  typography: calculateCategoryScore("typography", visualResult),
  colors: calculateCategoryScore("colors", visualResult),
  effects: calculateCategoryScore("effects", visualResult)
};

// Update verification report
const newReport = {
  iteration: state.report.iteration + 1,
  timestamp: new Date().toISOString(),
  scores: { code: codeScore, visual: visualScore, combined: (codeScore + visualScore) / 2 },
  categories,
  status: (codeScore >= 99 && visualScore >= 99) ? "COMPLETE" : "CONTINUE",
  reason: codeScore < 99 ? "code_score < 99%" : visualScore < 99 ? "visual_score < 99%" : "Checking categories",
  fixes_needed: JSON.parse(visualResult).fixes || [],
  gemini_analysis: JSON.parse(visualResult)
};

await Write("./ralph-state/verification-report.json", JSON.stringify(newReport, null, 2));

// Update history
state.history.history.push({
  iteration: newReport.iteration,
  code: codeScore,
  visual: visualScore,
  fixes: appliedFixes
});
state.history.total_iterations = newReport.iteration;

await Write("./ralph-state/iteration-history.json", JSON.stringify(state.history, null, 2));

// Create git checkpoint every 5 iterations
await createGitCheckpoint(newReport.iteration);

// Check for regression and handle
await handleRegression(state.history);
```

### Phase 5: Exit Check (WITH MUST VALIDATIONS)

```typescript
// ═══════════════════════════════════════════════════════════════════════════
// MUST VALIDATION #1: Verify all assets are from Figma (not generated/library)
// ═══════════════════════════════════════════════════════════════════════════
async function validateFigmaAssets(): Promise<{valid: boolean, issues: string[]}> {
  const issues: string[] = [];

  // Check for forbidden icon library imports
  const components = await Glob("src/**/*.tsx");
  for (const file of components) {
    const content = await Read(file);

    // FORBIDDEN: Icon library imports
    if (content.includes("lucide-react") ||
        content.includes("@heroicons") ||
        content.includes("react-icons") ||
        content.includes("@radix-ui/react-icons")) {
      issues.push(`${file}: Uses forbidden icon library - MUST use Figma assets`);
    }

    // FORBIDDEN: Inline SVG that wasn't downloaded
    const inlineSvgMatch = content.match(/<svg[^>]*>[\s\S]*?<\/svg>/g);
    if (inlineSvgMatch && inlineSvgMatch.length > 0) {
      issues.push(`${file}: Contains inline SVG - verify it's from Figma download`);
    }

    // Check for placeholder images
    if (content.includes("placeholder") || content.includes("via.placeholder")) {
      issues.push(`${file}: Contains placeholder image - MUST use Figma assets`);
    }
  }

  // Verify expected assets from Phase 0A exist
  try {
    const expectedAssets = JSON.parse(await Read("./ralph-state/expected-assets.json"));
    for (const asset of expectedAssets) {
      const exists = await Bash({ command: `test -f "${asset.path}" && echo "exists"` });
      if (!exists.includes("exists")) {
        issues.push(`Missing Figma asset: ${asset.path}`);
      }
    }
  } catch {
    issues.push("Cannot verify assets - expected-assets.json missing");
  }

  return { valid: issues.length === 0, issues };
}

// ═══════════════════════════════════════════════════════════════════════════
// MUST VALIDATION #3: Build must succeed
// ═══════════════════════════════════════════════════════════════════════════
async function validateBuild(): Promise<{success: boolean, errors: string[]}> {
  console.log("Running build validation...");

  const buildResult = await Bash({
    command: "npm run build 2>&1",
    timeout: 180000 // 3 minute timeout
  });

  // Check for common error patterns
  const hasErrors = buildResult.includes("error TS") ||
                    buildResult.includes("Error:") ||
                    buildResult.includes("Cannot find module") ||
                    buildResult.includes("Module not found") ||
                    buildResult.includes("SyntaxError") ||
                    buildResult.includes("TypeError") ||
                    buildResult.includes("failed to compile") ||
                    buildResult.includes("Build failed");

  const success = !hasErrors;

  const errors: string[] = [];
  if (!success) {
    // Extract error messages
    const lines = buildResult.split("\n");
    for (const line of lines) {
      if (line.includes("error") || line.includes("Error") ||
          line.includes("Cannot find") || line.includes("Module not found")) {
        errors.push(line.trim());
      }
    }
  }

  return { success, errors: errors.slice(0, 10) };
}

// Helper: Check if fix level requires approval (L3 or L4)
function isHighLevelFix(level: string): boolean {
  return level === "L3" || level === "L4";
}

// ═══════════════════════════════════════════════════════════════════════════
// EXIT CONDITION CHECK (ALL THREE MUST RULES REQUIRED)
// ═══════════════════════════════════════════════════════════════════════════

// MUST #2: Check 98% MINIMUM threshold (99% target, 98% hard minimum)
const HARD_MINIMUM = 98;
const TARGET = 99;

if (codeScore < HARD_MINIMUM || visualScore < HARD_MINIMUM) {
  // CANNOT exit - below hard minimum
  console.log(`❌ MUST #2 FAILED: Scores below 98% minimum`);
  console.log(`   Code: ${codeScore}% (need >= ${HARD_MINIMUM}%)`);
  console.log(`   Visual: ${visualScore}% (need >= ${HARD_MINIMUM}%)`);
  console.log("Loop MUST continue - no escape below 98%");
  // Do NOT output promise - loop continues
} else if (codeScore >= TARGET && visualScore >= TARGET) {
  // Target achieved - check remaining conditions
  console.log(`✅ MUST #2 PASSED: Both scores >= ${TARGET}%`);

  const allCategoriesPass = Object.values(newReport.categories).every(v => v >= 95);
  const noPendingL3L4 = newReport.fixes_needed.filter(f => isHighLevelFix(f.level)).length === 0;

  if (allCategoriesPass && noPendingL3L4) {
    // Check MUST #1: Asset validation
    const assetCheck = await validateFigmaAssets();
    if (!assetCheck.valid) {
      console.log("❌ MUST #1 FAILED: Asset validation");
      assetCheck.issues.forEach(issue => console.log(`  - ${issue}`));
      console.log("Cannot complete - fix asset issues first");
      // Do NOT output promise - loop continues
    } else {
      console.log("✅ MUST #1 PASSED: All assets from Figma");

      // Check MUST #3: Build validation
      const buildCheck = await validateBuild();
      if (!buildCheck.success) {
        console.log("❌ MUST #3 FAILED: Build errors");
        buildCheck.errors.forEach(err => console.log(`  - ${err}`));
        console.log("Cannot complete - fix build errors first");
        // Do NOT output promise - loop continues

        // Add build errors to fixes_needed for next iteration
        newReport.fixes_needed.push({
          element: "build",
          issue: "Build compilation failed",
          current: "Build errors present",
          expected: "Build success",
          level: "L1",
          auto_fixable: true,
          errors: buildCheck.errors
        });
        await Write("./ralph-state/verification-report.json", JSON.stringify(newReport, null, 2));
      } else {
        console.log("✅ MUST #3 PASSED: Build successful");

        // ALL THREE MUST RULES PASSED - NOW CAN COMPLETE
        console.log("🎉 ALL MUST RULES PASSED - Conversion complete!");
        console.log("<promise>PIXEL_PERFECT_99</promise>");

        // Generate final report
        await generateFinalReport();
      }
    }
  } else {
    console.log("Category or L3/L4 checks failed - continuing...");
    if (!allCategoriesPass) {
      const failingCategories = Object.entries(newReport.categories)
        .filter(([_, v]) => v < 95)
        .map(([k, v]) => `${k}: ${v}%`);
      console.log(`  Failing categories: ${failingCategories.join(", ")}`);
    }
  }
} else {
  // Between 98-99% - acceptable but continue for target
  console.log(`⚠️ Scores at ${codeScore}%/${visualScore}% - above minimum but below target`);
  console.log("Continuing to reach 99% target...");
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
    - Try arbitrary values (p-[17px])
    - Use CSS variables instead of Tailwind

  visual_stuck:
    - Request higher resolution Figma export
    - Check for responsive breakpoint mismatch

  layout_stuck:
    - Switch flex ↔ grid
    - Try absolute positioning for specific elements
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
    git_branch: ralph-hybrid-checkpoint
```

### Git Checkpoint & Rollback Implementation

```typescript
// Create checkpoint every 5 iterations
async function createGitCheckpoint(iteration: number): Promise<void> {
  if (iteration % 5 === 0) {
    await Bash({ command: `git add -A && git commit -m "Ralph Hybrid: Checkpoint iteration ${iteration}" --allow-empty` });
    console.log(`Git checkpoint created at iteration ${iteration}`);
  }
}

// Rollback to previous checkpoint when regression detected
async function rollbackToLastCheckpoint(currentIteration: number): Promise<void> {
  const checkpointIter = Math.floor((currentIteration - 1) / 5) * 5;
  if (checkpointIter <= 0) {
    console.log("No previous checkpoint to rollback to");
    return;
  }

  // Find the checkpoint commit
  const result = await Bash({
    command: `git log --oneline --all | grep "Checkpoint iteration ${checkpointIter}" | head -1 | cut -d' ' -f1`
  });

  const commitHash = result.trim();
  if (commitHash) {
    // Soft reset to preserve changes in working directory for analysis
    await Bash({ command: `git reset --soft ${commitHash}` });
    console.log(`Rolled back to checkpoint at iteration ${checkpointIter} (${commitHash})`);
  }
}

// Detect regression and trigger rollback
async function handleRegression(history: IterationHistory): Promise<boolean> {
  const recent = history.history.slice(-2);
  if (recent.length < 2) return false;

  const [prev, curr] = recent;
  if (curr.code < prev.code || curr.visual < prev.visual) {
    console.log(`Regression detected: Code ${prev.code}→${curr.code}, Visual ${prev.visual}→${curr.visual}`);
    await rollbackToLastCheckpoint(curr.iteration);
    return true;
  }
  return false;
}

// Helper functions for fix management
function getLevelPriority(level: string): number {
  const priorities: Record<string, number> = { L1: 1, L2: 2, L3: 3, L4: 4 };
  return priorities[level] || 99;
}

async function applyFix(fix: Fix): Promise<void> {
  // Apply the fix based on fix specification
  await Edit({
    file_path: fix.file || "src/components/unknown.tsx",
    old_string: fix.current,
    new_string: fix.expected
  });
  console.log(`Applied fix: ${fix.current} → ${fix.expected}`);
}

// Conceptual functions - implemented by Claude during execution
async function runCodeVerification(params: { figmaContext: any; generatedCode: string }): Promise<number> {
  // Compare Tailwind classes between Figma design tokens and generated code
  // Returns score 0-100 based on class matching percentage
  // Actual implementation uses Claude's analysis capability
  return 0; // Placeholder
}

async function generateFinalReport(): Promise<void> {
  // Read all state files and generate final markdown report
  const report = await Read("./ralph-state/verification-report.json");
  const history = await Read("./ralph-state/iteration-history.json");
  // Generate comprehensive report in ./reports/final-report.md
}

function calculateCategoryScore(category: string, geminiResult: string): number {
  // Extract category-specific score from Gemini analysis
  // Returns 0-100 based on how well that category matches
  const analysis = JSON.parse(geminiResult);
  return analysis.categories?.[category] || 0;
}

// Type definitions
interface Fix {
  element: string;
  issue: string;
  current: string;
  expected: string;
  level: string;
  auto_fixable: boolean;
  file?: string;
}

interface IterationHistory {
  total_iterations: number;
  history: Array<{ iteration: number; code: number; visual: number; fixes: string[] }>;
  trend: string;
  stuck_count: number;
  last_improvement: number;
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
  - completion_marker: "<promise>PIXEL_PERFECT_99</promise>"

stop:
  - max_iterations (30) reached
  - stuck_for 10 consecutive iterations
  - user_cancellation (/cancel-ralph)
```

---

## Output Structure

```
project/
├── src/
│   └── components/          # Generated components
├── public/
│   ├── images/              # Downloaded from Figma
│   └── icons/               # Downloaded from Figma
├── ralph-state/             # State files for self-reference
│   ├── verification-report.json
│   ├── iteration-history.json
│   └── fixes-applied.json
├── comparison/              # Verification images
│   ├── figma.png
│   └── impl.png
└── reports/
    └── final-report.md      # Generated on completion
```

---

## Final Report Template

```markdown
# Ralph Hybrid Conversion Report

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

## Components Generated
- HeroSection (99% match)
- FeatureCard (99% match)
- CTAButton (100% match)

## <promise>PIXEL_PERFECT_99</promise>
```

---

## Version

- Agent Version: 3.0.0
- Method: Ralph Hybrid (Loop + Dual Verification)
- Max Iterations: 30
- Target Accuracy: 99%+

---

*Version: 3.1.0 | Last Updated: 2026-01-24 | Ralph Hybrid with MUST Rules (Asset/98%/Build)*
