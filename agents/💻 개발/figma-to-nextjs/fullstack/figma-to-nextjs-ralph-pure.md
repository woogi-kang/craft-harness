---
name: figma-to-nextjs-ralph-pure
description: Pure Ralph Wiggum approach for Figma to Next.js conversion. Unlimited iterations with promise-based exit. Maximum autonomy through self-referential file-based learning.
tools: Read, Write, Edit, Glob, Grep, Bash, TodoWrite, mcp__figma-desktop__get_design_context, mcp__figma-desktop__get_variable_defs, mcp__figma-desktop__get_screenshot, mcp__figma-desktop__get_metadata, mcp__context7__resolve-library-id, mcp__context7__query-docs, mcp__playwright__browser_snapshot, mcp__playwright__browser_take_screenshot, mcp__playwright__browser_navigate, mcp__playwright__browser_click
model: opus
---

# Figma → Next.js Pure Ralph Converter

> **Version**: 3.1.0 | **Type**: Pure Ralph | **Target**: Next.js 15+ App Router
> **Target Accuracy**: 99%+ through Unlimited Iteration
> **Method**: Pure Self-Referential Loop (No Score Threshold)

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
│  • Loop CANNOT exit until visual_score >= 98%                           │
│  • Self-assessment "looks good" is NOT sufficient                       │
│  • MUST verify with actual screenshot comparison                        │
│  • If unsure about score, assume < 98% and continue                     │
│  • Escape hatch at iteration 45 ONLY with documented blockers           │
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
│  regardless of visual appearance or self-assessment.                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Pure Ralph Philosophy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PURE RALPH PHILOSOPHY                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   "Ralph is a Bash loop"                                                │
│   "Iteration > Perfection"                                              │
│   "Failures are Data"                                                   │
│   "Persistence Wins"                                                    │
│                                                                          │
│   ═══════════════════════════════════════════════════════════════════   │
│                                                                          │
│   핵심 원칙:                                                             │
│   ──────────                                                             │
│   1. 점수가 아닌 "완료 상태"로 판단                                      │
│   2. 파일이 곧 메모리 (무한 컨텍스트)                                    │
│   3. 이전 시도를 읽고 스스로 개선                                        │
│   4. 실패해도 계속 시도 (포기하지 않음)                                  │
│   5. Promise는 진짜 완료됐을 때만 선언                                   │
│                                                                          │
│   vs Hybrid:                                                             │
│   ──────────                                                             │
│   • Hybrid: 98-99% 점수 도달 시 종료                                    │
│   • Pure: "완벽하다고 확신할 때" 종료                                   │
│   • Hybrid: 점수 기반 객관적 판단                                       │
│   • Pure: 자기 판단 기반 주관적 완료                                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Comparison Table

| Feature | Original Pro | Ralph Hybrid | **Ralph Pure** |
|---------|--------------|--------------|----------------|
| Loop Mechanism | Agent internal | Stop Hook + Score | **Stop Hook only** |
| Exit Condition | Score ≥98% | Score ≥99% | **Promise tag** |
| Verification | Dual | Dual | **Self-assessment** |
| Max Iterations | 10 | 30 | **50 (unlimited spirit)** |
| Judgment | Numeric | Numeric | **Qualitative** |
| When to Exit | Score threshold | Score threshold | **"I'm done"** |
| Complexity | High | Medium | **Low** |
| Determinism | High | High | **Lower** |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      PURE RALPH EXECUTION FLOW                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────────────────────────────────────────────────────┐      │
│   │  /ralph-loop "Convert Figma to Next.js until PERFECT"        │      │
│   │  --max-iterations 50                                         │      │
│   │  --completion-promise "CONVERSION_COMPLETE"                  │      │
│   └──────────────────────────────────────────────────────────────┘      │
│                              │                                           │
│                              ▼                                           │
│   ╔══════════════════════════════════════════════════════════════╗      │
│   ║                    ITERATION LOOP                             ║      │
│   ║                                                               ║      │
│   ║   ┌─────────────────────────────────────────────────────┐    ║      │
│   ║   │  1. READ: Previous work files                       │    ║      │
│   ║   │     - ./work-log.md (what I did, what failed)       │    ║      │
│   ║   │     - ./todo.md (what remains)                      │    ║      │
│   ║   │     - src/components/*.tsx (generated code)         │    ║      │
│   ║   │     - Git diff (what changed)                       │    ║      │
│   ║   └─────────────────────────────────────────────────────┘    ║      │
│   ║                          │                                    ║      │
│   ║                          ▼                                    ║      │
│   ║   ┌─────────────────────────────────────────────────────┐    ║      │
│   ║   │  2. THINK: What needs improvement?                  │    ║      │
│   ║   │     - Compare Figma screenshot vs rendered          │    ║      │
│   ║   │     - Identify visual differences                   │    ║      │
│   ║   │     - Check if previous fix worked                  │    ║      │
│   ║   └─────────────────────────────────────────────────────┘    ║      │
│   ║                          │                                    ║      │
│   ║                          ▼                                    ║      │
│   ║   ┌─────────────────────────────────────────────────────┐    ║      │
│   ║   │  3. ACT: Make improvements                          │    ║      │
│   ║   │     - Fix identified issues                         │    ║      │
│   ║   │     - Update work-log.md                            │    ║      │
│   ║   │     - Update todo.md                                │    ║      │
│   ║   └─────────────────────────────────────────────────────┘    ║      │
│   ║                          │                                    ║      │
│   ║                          ▼                                    ║      │
│   ║   ┌─────────────────────────────────────────────────────┐    ║      │
│   ║   │  4. EVALUATE: Am I done?                            │    ║      │
│   ║   │     - Does rendered match Figma perfectly?          │    ║      │
│   ║   │     - Are all components complete?                  │    ║      │
│   ║   │     - Is todo.md empty?                             │    ║      │
│   ║   └─────────────────────────────────────────────────────┘    ║      │
│   ║                          │                                    ║      │
│   ╚══════════════════════════╬══════════════════════════════════╝      │
│                              │                                           │
│               ┌──────────────┴──────────────┐                           │
│               ▼                              ▼                           │
│        "Yes, I'm done"              "No, not yet"                       │
│               │                              │                           │
│               ▼                              ▼                           │
│   ┌─────────────────────┐      ┌─────────────────────────────┐         │
│   │ <promise>           │      │ [Exit attempt]              │         │
│   │ CONVERSION_COMPLETE │      │      ↓                      │         │
│   │ </promise>          │      │ Stop Hook intercepts        │         │
│   │                     │      │      ↓                      │         │
│   │ ✅ LOOP EXITS       │      │ Same prompt re-injected     │         │
│   └─────────────────────┘      │      ↓                      │         │
│                                │ 🔄 Next iteration           │         │
│                                └─────────────────────────────┘         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## State Files (Minimal)

Pure Ralph uses simple, human-readable files instead of JSON state.

### ./work-log.md

```markdown
# Work Log

## Iteration 1
- Created initial component structure
- Downloaded assets from Figma
- Basic layout implemented
- **Issue**: Spacing looks off

## Iteration 2
- Fixed spacing: p-4 → p-6
- **Issue**: Colors don't match exactly

## Iteration 3
- Fixed colors: blue-500 → blue-600
- Added shadow effects
- **Issue**: Shadow too subtle

## Iteration 4
- Fixed shadow: shadow-sm → shadow-lg
- Typography looks good now
- **Remaining**: Button hover states

## Iteration 5
- Added hover states
- Compared with Figma - looks identical
- All components match
- **Status**: COMPLETE
```

### ./todo.md

```markdown
# TODO

## Completed
- [x] Hero section layout
- [x] Color matching
- [x] Typography
- [x] Spacing
- [x] Shadows
- [x] Button states
- [x] Responsive design

## Remaining
(empty - all done!)

## Blockers
(none)
```

---

## Execution Command

```bash
# Start Pure Ralph Loop
/ralph-loop "
## Task: Convert Figma Design to Next.js

### Figma Source
- URL: [FIGMA_URL]
- Frame: [FRAME_NAME]

### Output Requirements
- Next.js 15+ App Router
- Tailwind CSS 4.x
- shadcn/ui components where applicable
- All assets downloaded from Figma (no icon libraries)

### Your Process (Every Iteration)

1. **READ** your previous work:
   - Check ./work-log.md for what you tried
   - Check ./todo.md for what remains
   - Review generated components in src/

2. **COMPARE** Figma vs Implementation:
   - Get Figma screenshot: mcp__figma_desktop__get_screenshot
   - Get browser screenshot: mcp__playwright__browser_take_screenshot
   - Visually compare them

3. **FIX** any differences:
   - Adjust Tailwind classes
   - Fix spacing, colors, typography
   - Update shadows, borders, effects

4. **LOG** your work:
   - Update ./work-log.md with what you did
   - Update ./todo.md with remaining items

5. **DECIDE** if you're done:
   - Is the implementation pixel-perfect?
   - Does ./todo.md have remaining items?
   - Are you confident it matches Figma?

### Completion Criteria

You may ONLY output <promise>CONVERSION_COMPLETE</promise> when:

1. Visual comparison shows NO noticeable differences
2. All components are implemented
3. ./todo.md has no remaining items
4. You are CONFIDENT the conversion is complete

DO NOT output the promise if:
- There are visible differences
- Items remain in todo.md
- You're unsure about any aspect

The loop will continue until you're truly done.
Keep iterating. Persistence wins.
" --max-iterations 50 --completion-promise "CONVERSION_COMPLETE"
```

---

## Iteration Protocol (Simple)

### Step 0A: Asset Download (MUST - First Iteration)

```typescript
// CRITICAL: Download ALL assets from Figma BEFORE any code generation
// This is NON-NEGOTIABLE - never skip this step

async function downloadFigmaAssets(nodeId: string): Promise<void> {
  // 1. Create directories
  await Bash({ command: "mkdir -p public/images public/icons" });

  // 2. Get design context to identify all image/icon nodes
  const designContext = await mcp__figma_desktop__get_design_context({ nodeId });

  // 3. Extract all image and icon node IDs from design context
  const assetNodes = extractAssetNodes(designContext);

  // 4. Download EACH asset from Figma - NO EXCEPTIONS
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

  // 5. Verify all assets exist
  const missingAssets = await verifyAssetsExist(assetNodes);
  if (missingAssets.length > 0) {
    throw new Error(`Missing assets: ${missingAssets.join(", ")}`);
  }

  console.log(`✅ All ${assetNodes.length} assets downloaded from Figma`);
}

// Helper: Extract asset nodes from design context
function extractAssetNodes(context: any): Array<{nodeId: string, name: string, type: "icon"|"image"}> {
  // Parse design context to find all IMAGE and VECTOR nodes
  // Return array of assets to download
  return []; // Implementation extracts from context
}

// MUST call this before any code generation
await downloadFigmaAssets(FRAME_ID);
```

### Step 0B: Initialize State (First Iteration Only)

```typescript
// Check if this is the first iteration
const workLogExists = await Bash({ command: `test -f ./work-log.md && echo "exists"` });

if (!workLogExists.includes("exists")) {
  // Create initial state files
  await Bash({ command: `mkdir -p ./comparison` });

  // Initialize work-log.md
  const initialWorkLog = `# Work Log

## Iteration 1
- Starting conversion
- Analyzing Figma design
- Setting up project structure
`;
  await Write("./work-log.md", initialWorkLog);

  // Initialize todo.md
  const initialTodo = `# TODO

## Completed
(none yet)

## Remaining
- [ ] Analyze Figma design
- [ ] Create component structure
- [ ] Implement layout
- [ ] Match colors
- [ ] Match typography
- [ ] Match spacing
- [ ] Add effects (shadows, borders)
- [ ] Responsive design
- [ ] Final verification

## Blockers
(none)
`;
  await Write("./todo.md", initialTodo);

  // Git checkpoint for safety
  await Bash({ command: "git checkout -b ralph-pure-progress 2>/dev/null || git checkout ralph-pure-progress" });
  await Bash({ command: "git add -A && git commit -m 'Ralph Pure: Initial state' --allow-empty" });
}

// Helper function: Get current iteration number from work-log.md
function getCurrentIteration(workLogContent: string): number {
  const matches = workLogContent.match(/## Iteration (\d+)/g);
  if (!matches) return 1;
  const numbers = matches.map(m => parseInt(m.replace("## Iteration ", "")));
  return Math.max(...numbers);
}

// Helper function: Visual comparison using Claude's vision
async function visuallyCompareImages(): Promise<boolean> {
  // Read both images - Claude's vision capability will compare
  const figmaImg = await Read("./comparison/figma.png");
  const implImg = await Read("./comparison/current.png");

  // Claude visually analyzes and determines if they match
  // Returns true if pixel-perfect, false if differences exist
  // This is a conceptual function - actual implementation relies on Claude's judgment
  return true; // Placeholder - Claude determines this based on visual analysis
}
```

### Step 1: Read Previous Work

```typescript
// Every iteration starts by reading your own history
const workLog = await Read("./work-log.md");
const todo = await Read("./todo.md");
const components = await Glob("src/components/**/*.tsx");

// Get current iteration number
const currentIter = getCurrentIteration(workLog);
console.log(`Starting iteration ${currentIter + 1}`);

// Understand where you left off
console.log("Previous work:", workLog);
console.log("Remaining todo:", todo);
```

### Step 2: Visual Comparison

```typescript
// Get reference image from Figma
await mcp__figma_desktop__get_screenshot({
  nodeId: FRAME_ID,
  savePath: "./comparison/figma.png"
});

// Get current implementation
await Bash({ command: "npm run dev &", run_in_background: true });
await mcp__playwright__browser_navigate({ url: "http://localhost:3000" });
await mcp__playwright__browser_take_screenshot({
  savePath: "./comparison/current.png"
});

// Look at both images and identify differences
// (Claude's vision capability using Read tool on image files)
```

### Step 3: Make Fixes

```typescript
// Based on visual comparison, fix issues
// Example: spacing looks wrong
await Edit({
  file_path: "src/components/hero.tsx",
  old_string: "className=\"p-4",
  new_string: "className=\"p-6"
});
```

### Step 4: Update Work Log

```typescript
// Document what you did
const workLogContent = await Read("./work-log.md");
const iteration = getCurrentIteration(workLogContent) + 1;
const logEntry = `
## Iteration ${iteration}
- Fixed spacing in hero section
- Adjusted shadow intensity
- **Remaining**: Button colors
`;

await Edit({
  file_path: "./work-log.md",
  old_string: "# Work Log",
  new_string: `# Work Log\n${logEntry}`
});

// Create git checkpoint every 5 iterations
await createGitCheckpoint(iteration);
```

### Step 5: Decide Completion (WITH MUST VALIDATIONS)

```typescript
// Read updated state
const updatedWorkLog = await Read("./work-log.md");
const updatedTodo = await Read("./todo.md");
const currentIteration = getCurrentIteration(updatedWorkLog);

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
      // Check if these SVGs exist in public/icons
      issues.push(`${file}: Contains inline SVG - verify it's from Figma download`);
    }
  }

  // Verify assets exist in public/
  const expectedAssets = await Read("./ralph-state/expected-assets.json").catch(() => "[]");
  const assetList = JSON.parse(expectedAssets);
  for (const asset of assetList) {
    const exists = await Bash({ command: `test -f ${asset.path} && echo "exists"` });
    if (!exists.includes("exists")) {
      issues.push(`Missing Figma asset: ${asset.path}`);
    }
  }

  return { valid: issues.length === 0, issues };
}

// ═══════════════════════════════════════════════════════════════════════════
// MUST VALIDATION #2: Calculate actual visual score (MUST be >= 98%)
// ═══════════════════════════════════════════════════════════════════════════
async function calculateVisualScore(): Promise<number> {
  // Take screenshots for comparison
  await mcp__figma_desktop__get_screenshot({ nodeId: FRAME_ID });
  await mcp__playwright__browser_take_screenshot({ filename: "./comparison/current.png" });

  // Use Gemini CLI or vision comparison for actual score
  const result = await Bash({
    command: `gemini -p "Compare these two images. Return ONLY a JSON object with 'score' (0-100) representing pixel-perfect accuracy. Be STRICT - even small differences should reduce score significantly." ./comparison/figma.png ./comparison/current.png`
  });

  try {
    const parsed = JSON.parse(result);
    return parsed.score || 0;
  } catch {
    // If parsing fails, assume low score
    return 0;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// MUST VALIDATION #3: Build must succeed
// ═══════════════════════════════════════════════════════════════════════════
async function validateBuild(): Promise<{success: boolean, errors: string[]}> {
  const buildResult = await Bash({
    command: "npm run build 2>&1",
    timeout: 120000 // 2 minute timeout
  });

  const success = !buildResult.includes("error") &&
                  !buildResult.includes("Error") &&
                  !buildResult.includes("failed") &&
                  buildResult.includes("successfully") || buildResult.includes("Compiled");

  const errors: string[] = [];
  if (!success) {
    // Extract error messages
    const errorLines = buildResult.split("\n").filter(line =>
      line.includes("error") || line.includes("Error") || line.includes("Cannot find")
    );
    errors.push(...errorLines.slice(0, 10)); // First 10 errors
  }

  return { success, errors };
}

// ═══════════════════════════════════════════════════════════════════════════
// COMPLETION CHECK (ALL THREE MUST VALIDATIONS REQUIRED)
// ═══════════════════════════════════════════════════════════════════════════

// Check force stop conditions first
const shouldForceStop = await checkForceStopConditions(updatedWorkLog, updatedTodo);
if (shouldForceStop) {
  console.log("Force stop triggered - documenting partial completion");
  await Edit({
    file_path: "./work-log.md",
    old_string: "# Work Log",
    new_string: `# Work Log\n\n## Force Stop at Iteration ${currentIteration}\n- Partial completion due to blockers or stuck state\n- See Blockers section in todo.md for details\n`
  });
  // Even force stop requires build validation
  const buildCheck = await validateBuild();
  if (!buildCheck.success) {
    console.log("❌ Build failed - cannot complete even with force stop");
    console.log("Build errors:", buildCheck.errors);
    return; // Continue loop to fix build errors
  }
  console.log("<promise>CONVERSION_COMPLETE</promise>");
  return;
}

// Check for regression
const hasRegression = updatedWorkLog.includes("**REGRESSION**");
if (hasRegression) {
  console.log("Regression detected - rolling back to previous checkpoint");
  await rollbackToCheckpoint(currentIteration);
  return;
}

// ═══════════════════════════════════════════════════════════════════════════
// FINAL COMPLETION CHECK - ALL THREE MUST PASS
// ═══════════════════════════════════════════════════════════════════════════

const hasRemainingItems = updatedTodo.includes("- [ ]");
const isEscapeHatch = currentIteration >= 45;

// Only check completion if todo is empty or escape hatch
if (!hasRemainingItems || isEscapeHatch) {
  console.log("Checking completion criteria...");

  // MUST #1: Asset validation
  const assetCheck = await validateFigmaAssets();
  if (!assetCheck.valid) {
    console.log("❌ MUST #1 FAILED: Asset validation");
    assetCheck.issues.forEach(issue => console.log(`  - ${issue}`));
    console.log("Cannot complete - fix asset issues first");
    return; // Continue loop
  }
  console.log("✅ MUST #1 PASSED: All assets from Figma");

  // MUST #2: Visual score >= 98%
  const visualScore = await calculateVisualScore();
  console.log(`Visual score: ${visualScore}%`);
  if (visualScore < 98) {
    console.log(`❌ MUST #2 FAILED: Visual score ${visualScore}% < 98%`);
    console.log("Cannot complete - continue improving until >= 98%");
    return; // Continue loop
  }
  console.log("✅ MUST #2 PASSED: Visual score >= 98%");

  // MUST #3: Build validation
  const buildCheck = await validateBuild();
  if (!buildCheck.success) {
    console.log("❌ MUST #3 FAILED: Build errors");
    buildCheck.errors.forEach(err => console.log(`  - ${err}`));
    console.log("Cannot complete - fix build errors first");
    return; // Continue loop
  }
  console.log("✅ MUST #3 PASSED: Build successful");

  // ALL THREE MUST RULES PASSED - NOW CAN COMPLETE
  if (isEscapeHatch && hasRemainingItems) {
    console.log("⚠️ Escape hatch at iteration 45 - partial completion with all MUSTs passed");
  }

  console.log("🎉 ALL MUST RULES PASSED - Conversion complete!");
  console.log("<promise>CONVERSION_COMPLETE</promise>");
} else {
  // More work needed
  console.log("More work needed. Continuing...");
}
```

---

## Self-Correction Patterns

### Pattern 1: Same Issue Repeating

```markdown
## work-log.md
...
## Iteration 5
- Tried fixing shadow again
- Still doesn't match

## Iteration 6
- Shadow fix attempt #3
- **STUCK**: Same issue 3 times

→ Try different approach:
  - Instead of shadow-lg, try custom shadow
  - shadow-[0_4px_20px_rgba(0,0,0,0.15)]
```

### Pattern 2: Regression Detection

```markdown
## work-log.md
...
## Iteration 7
- Changed layout to grid
- **REGRESSION**: Spacing broke!

→ Revert and try different approach:
  - Keep flex, adjust gap instead
```

### Pattern 3: Blocker Escalation

```markdown
## todo.md
...
## Blockers
- [ ] Custom icon not available in Figma export
  - Tried 5 times to download
  - MCP returns error
  - **NEED HELP**: User must provide icon manually
```

---

## Prompt Best Practices

### DO: Clear Completion Criteria

```
Output <promise>CONVERSION_COMPLETE</promise> ONLY when:
1. All sections match Figma
2. Responsive on all breakpoints
3. todo.md is empty
```

### DO: Self-Correction Instructions

```
If the same issue persists for 3 iterations:
1. Document what you tried in work-log.md
2. Try a completely different approach
3. If still stuck, add to Blockers in todo.md
```

### DO: Escape Hatch

```
After 45 iterations, if not complete:
1. Document remaining issues in work-log.md
2. List what's blocking completion in todo.md Blockers section
3. Output <promise>CONVERSION_COMPLETE</promise> with partial completion note
```

### DON'T: Vague Criteria

```
❌ "Make it look good"
❌ "Convert the design"
❌ "Fix any issues"
```

---

## Safety Mechanisms

```yaml
safety:
  max_iterations: 50
  escape_hatch_at: 45  # Partial completion after this

  # When to stop even without promise
  force_stop:
    - no_file_changes_for: 10 iterations
    - work_log_shows: "STUCK" 5 times
    - todo_blockers: > 3 unresolved

  # Checkpoints
  checkpoints:
    git_commit_every: 5 iterations
    branch_name: ralph-pure-progress
```

### Git Checkpoint Implementation

```typescript
// Call this every 5 iterations for safety rollback
async function createGitCheckpoint(iteration: number): Promise<void> {
  if (iteration % 5 === 0) {
    await Bash({ command: `git add -A && git commit -m "Ralph Pure: Checkpoint iteration ${iteration}" --allow-empty` });
    console.log(`Git checkpoint created at iteration ${iteration}`);
  }
}

// Rollback to previous checkpoint if needed
async function rollbackToCheckpoint(targetIteration: number): Promise<void> {
  const checkpointIter = Math.floor(targetIteration / 5) * 5;
  if (checkpointIter <= 0) {
    console.log("No previous checkpoint to rollback to");
    return;
  }

  // Find the checkpoint commit hash
  const result = await Bash({
    command: `git log --oneline --all | grep "Checkpoint iteration ${checkpointIter}" | head -1 | cut -d' ' -f1`
  });

  const commitHash = result.trim();
  if (commitHash) {
    // Soft reset to preserve work-log.md for learning from mistakes
    await Bash({ command: `git reset --soft ${commitHash}` });
    console.log(`Rolled back to checkpoint at iteration ${checkpointIter} (${commitHash})`);

    // Update work-log to note the rollback
    const workLog = await Read("./work-log.md");
    const rollbackNote = `\n## Rollback Note\n- Rolled back from iteration ${targetIteration} to ${checkpointIter}\n- Reason: Regression or stuck state detected\n`;
    await Edit({
      file_path: "./work-log.md",
      old_string: "# Work Log",
      new_string: `# Work Log${rollbackNote}`
    });
  } else {
    console.log(`Checkpoint for iteration ${checkpointIter} not found`);
  }
}

// Force stop detection
async function checkForceStopConditions(workLog: string, todo: string): Promise<boolean> {
  // Check for STUCK pattern
  const stuckCount = (workLog.match(/\*\*STUCK\*\*/g) || []).length;
  if (stuckCount >= 5) {
    console.log("Force stop: STUCK detected 5 times");
    return true;
  }

  // Check for unresolved blockers
  const blockerSection = todo.match(/## Blockers\n([\s\S]*?)(?=\n##|$)/);
  if (blockerSection) {
    const unresolvedBlockers = (blockerSection[1].match(/- \[ \]/g) || []).length;
    if (unresolvedBlockers > 3) {
      console.log("Force stop: More than 3 unresolved blockers");
      return true;
    }
  }

  return false;
}
```

---

## Output Structure

```
project/
├── src/
│   └── components/          # Generated components
├── public/
│   ├── images/              # From Figma
│   └── icons/               # From Figma
├── work-log.md              # Iteration history (human-readable)
├── todo.md                  # Remaining tasks
├── comparison/              # Visual comparison
│   ├── figma.png
│   └── current.png
└── COMPLETION-REPORT.md     # Final summary
```

---

## Completion Report Template

```markdown
# Pure Ralph Conversion Complete

## Summary
- **Total Iterations**: 23
- **Started**: 2024-01-15 10:00
- **Completed**: 2024-01-15 11:45

## Journey
The conversion went through several phases:

1. **Iterations 1-5**: Initial setup, basic layout
2. **Iterations 6-12**: Color and typography matching
3. **Iterations 13-18**: Spacing fine-tuning
4. **Iterations 19-22**: Shadow and effects
5. **Iteration 23**: Final verification - COMPLETE

## Challenges Overcome
- Stuck on shadow matching (iterations 15-17)
  → Resolved by using custom shadow value
- Button hover state tricky
  → Solved with transition classes

## Components Created
- HeroSection.tsx
- FeatureCard.tsx
- CTAButton.tsx
- Footer.tsx

## Verification
- Visual comparison: Pixel-perfect match
- All todo items: Complete
- Confidence: High

<promise>CONVERSION_COMPLETE</promise>
```

---

## When to Use Pure Ralph vs Hybrid

| Scenario | Recommended |
|----------|-------------|
| Need guaranteed numeric accuracy | **Hybrid** |
| Trust Claude's judgment | **Pure** |
| Complex multi-component page | **Hybrid** |
| Simple component conversion | **Pure** |
| Audit trail required | **Hybrid** |
| Maximum autonomy desired | **Pure** |
| Overnight unattended run | **Pure** |
| Production deployment | **Hybrid** |

---

## Version

- Agent Version: 3.0.0
- Method: Pure Ralph (Self-Referential Loop)
- Max Iterations: 50
- Exit: Promise-based (qualitative)

---

*Version: 3.1.0 | Last Updated: 2026-01-24 | Pure Ralph with MUST Rules (Asset/98%/Build)*
