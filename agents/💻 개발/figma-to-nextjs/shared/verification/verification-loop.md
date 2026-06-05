---
name: "Verification Loop System"
description: "Iterative verification loop for pixel-perfect accuracy"
---

# Verification Loop System

> Iterative verification and auto-fix system for achieving 95%+ pixel-perfect accuracy

---

## Overview

The Verification Loop is an iterative system that compares generated code against Figma designs, detects differences, and automatically fixes them until reaching the target accuracy (95%+).

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      VERIFICATION LOOP FLOW                              │
│                                                                          │
│   Code Generation (Phase 4)                                              │
│           │                                                              │
│           ▼                                                              │
│   ┌───────────────────────────────────────────────────────────────┐     │
│   │ LOOP START (max_iterations: 5, parallel_agents: 2)            │     │
│   │                                                                │     │
│   │   ┌─────────────────┐     ┌─────────────────┐                 │     │
│   │   │   Agent A       │     │   Agent B       │                 │     │
│   │   │ (Conservative)  │     │ (Experimental)  │                 │     │
│   │   └────────┬────────┘     └────────┬────────┘                 │     │
│   │            │                       │                          │     │
│   │            ▼                       ▼                          │     │
│   │   ┌─────────────────────────────────────────────────────┐    │     │
│   │   │ ① Numeric Comparison (Fast, Accurate)               │    │     │
│   │   │    - spacing, padding, margin                        │    │     │
│   │   │    - font-size, font-weight, line-height            │    │     │
│   │   │    - colors (hex comparison)                        │    │     │
│   │   │    - border-radius, shadow                          │    │     │
│   │   └─────────────────────────────────────────────────────┘    │     │
│   │            │                                                  │     │
│   │            ▼                                                  │     │
│   │   Score >= 95%? ───YES───▶ EXIT LOOP ✅                      │     │
│   │            │                                                  │     │
│   │           NO                                                  │     │
│   │            │                                                  │     │
│   │            ▼                                                  │     │
│   │   ┌─────────────────────────────────────────────────────┐    │     │
│   │   │ ② Visual Comparison (When numeric < 95%)            │    │     │
│   │   │    - Figma get_screenshot                           │    │     │
│   │   │    - Playwright render capture                      │    │     │
│   │   │    - Claude Vision diff analysis                    │    │     │
│   │   └─────────────────────────────────────────────────────┘    │     │
│   │            │                                                  │     │
│   │            ▼                                                  │     │
│   │   ┌─────────────────────────────────────────────────────┐    │     │
│   │   │ ③ Auto Fix (Level 1-2)                              │    │     │
│   │   │    - Tailwind class adjustment                      │    │     │
│   │   │    - CSS variable correction                        │    │     │
│   │   │    - Spacing/typography fixes                       │    │     │
│   │   └─────────────────────────────────────────────────────┘    │     │
│   │            │                                                  │     │
│   │            ▼                                                  │     │
│   │   ④ Re-verification ───────────────▶ LOOP CONTINUE           │     │
│   │                                                                │     │
│   └───────────────────────────────────────────────────────────────┘     │
│           │                                                              │
│           ▼                                                              │
│   Select Best Result (A vs B)                                            │
│           │                                                              │
│           ▼                                                              │
│   Continue to Phase 7 (Responsive)                                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Configuration

```yaml
# verification-loop.yaml
verification_loop:
  enabled: true

  # Iteration settings
  iterations:
    max: 5                    # Maximum iterations per agent
    parallel_agents: 2        # Run 2 agents simultaneously
    total_max: 10             # 2 agents × 5 iterations

  # Target accuracy
  target:
    minimum_score: 95         # Must achieve 95%+ to pass
    perfect_score: 100        # Ideal target

  # Comparison strategy
  comparison:
    primary: numeric          # Fast, accurate number comparison
    fallback: visual          # Vision-based when numeric < 95%

  # Auto-fix levels
  auto_fix:
    level_1: true             # Immediate fix (spacing, colors)
    level_2: true             # Safe fix (typography, shadows)
    level_3: false            # Requires approval (layout changes)

  # Completion marker
  completion:
    marker: "<figma>DONE</figma>"
    require_marker: true
```

---

## Parallel Agent Strategy

### Mode A: Competition (Same Task, Different Approach)

```
┌─────────────────────────────────────────────────────────────────┐
│ COMPETITION MODE                                                 │
│                                                                  │
│   Agent A (Conservative)        Agent B (Experimental)          │
│   ─────────────────────        ──────────────────────           │
│   • Prefer shadcn/ui           • Prefer custom components       │
│   • Strict pattern match       • Optimized generation           │
│   • Stable, predictable        • May find better solutions      │
│                                                                  │
│   Result: 92%                  Result: 96%                       │
│                                                                  │
│   ───────────────────────────────────────────────────────────   │
│   SELECT: Agent B (96%) → Continue with B's approach            │
└─────────────────────────────────────────────────────────────────┘
```

### Mode B: Division (Different Areas)

```
┌─────────────────────────────────────────────────────────────────┐
│ DIVISION MODE                                                    │
│                                                                  │
│   Agent A (Layout Expert)       Agent B (Style Expert)          │
│   ─────────────────────        ──────────────────────           │
│   • Flex/Grid structure        • Colors/Typography              │
│   • Spacing/Padding            • Shadows/Borders                │
│   • Responsive layout          • Animations/Transitions         │
│                                                                  │
│   Layout Score: 98%            Style Score: 94%                 │
│                                                                  │
│   ───────────────────────────────────────────────────────────   │
│   MERGE: Combined Score → 96%                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation

```typescript
// Launch parallel agents in single message
<Task subagent_type="figma-verifier" prompt="
  MODE: conservative
  FOCUS: stability and pattern matching
  TARGET: ${componentPath}
  FIGMA_NODE: ${nodeId}
" />

<Task subagent_type="figma-verifier" prompt="
  MODE: experimental
  FOCUS: optimization and accuracy
  TARGET: ${componentPath}
  FIGMA_NODE: ${nodeId}
" />

// Compare results and select best
const bestResult = selectBestResult(resultA, resultB);
```

---

## Comparison Methods

### 1. Numeric Comparison (Primary)

Fast and accurate comparison of design values.

```typescript
interface NumericComparisonResult {
  category: string;
  figma_value: string;
  generated_value: string;
  match: boolean;
  diff: number;
}

// Comparison categories
const categories = {
  spacing: ['padding', 'margin', 'gap'],
  typography: ['font-size', 'font-weight', 'line-height', 'letter-spacing'],
  colors: ['color', 'background-color', 'border-color'],
  borders: ['border-radius', 'border-width'],
  shadows: ['box-shadow'],
  sizing: ['width', 'height', 'min-width', 'max-width']
};
```

#### Figma → Tailwind Mapping Validation

| Figma (px) | Expected Tailwind | Validation |
|------------|-------------------|------------|
| padding: 24px | p-6 | ✅ 24px = 1.5rem |
| font-size: 16px | text-base | ✅ 16px = 1rem |
| gap: 16px | gap-4 | ✅ 16px = 1rem |
| color: #3B82F6 | text-blue-500 | ✅ Exact match |
| border-radius: 8px | rounded-lg | ✅ 8px |

### 2. Visual Comparison (Fallback)

Used when numeric comparison scores < 95%.

```typescript
// Step 1: Get Figma screenshot
const figmaScreenshot = await mcp__figma__get_screenshot({
  nodeId: targetNodeId
});

// Step 2: Render component with Playwright
const renderedScreenshot = await captureWithPlaywright({
  url: `http://localhost:3000/preview/${componentId}`,
  viewport: { width: 1440, height: 900 },
  fullPage: false
});

// Step 3: Compare with Claude Vision
const diffReport = await compareImages({
  original: figmaScreenshot,
  rendered: renderedScreenshot,
  prompt: `
    Compare these two images:
    1. Original Figma design (left)
    2. Rendered React component (right)

    List specific differences in:
    - Layout alignment
    - Spacing/padding
    - Typography
    - Colors
    - Shadows/borders

    For each difference, specify:
    - Element name
    - What's different
    - Suggested fix (Tailwind class or CSS)
  `
});
```

### Playwright Capture Implementation

```typescript
// Using MCP Playwright
async function captureRenderedComponent(componentPath: string): Promise<string> {
  // 1. Start dev server (if not running)
  await Bash({
    command: "npm run dev &",
    run_in_background: true
  });

  // 2. Wait for server ready
  await waitForServer("http://localhost:3000");

  // 3. Capture screenshot via MCP Playwright
  const screenshot = await mcp__playwright__screenshot({
    url: `http://localhost:3000/preview/${componentPath}`,
    fullPage: false,
    viewport: { width: 1440, height: 900 }
  });

  return screenshot;
}
```

---

## Auto-Fix Levels

### Level 1: Immediate Fix (No Approval)

Safe fixes that don't change structure.

| Category | Example | Fix |
|----------|---------|-----|
| Spacing | padding 24px → 20px | `p-6` → `p-5` |
| Gap | gap 16px → 12px | `gap-4` → `gap-3` |
| Font Size | 18px → 16px | `text-lg` → `text-base` |
| Colors | #3B82F6 → #2563EB | `text-blue-500` → `text-blue-600` |

### Level 2: Safe Fix (Logged)

Fixes that may affect appearance but not structure.

| Category | Example | Fix |
|----------|---------|-----|
| Font Weight | 400 → 500 | `font-normal` → `font-medium` |
| Border Radius | 4px → 8px | `rounded` → `rounded-lg` |
| Shadow | sm → md | `shadow-sm` → `shadow-md` |
| Line Height | 1.5 → 1.75 | `leading-normal` → `leading-relaxed` |

### Level 3: Approval Required

Structural changes that need user confirmation.

| Category | Example | Action |
|----------|---------|--------|
| Layout | flex → grid | Ask user |
| Direction | row → column | Ask user |
| Component | Button → Link | Ask user |
| Nesting | Add wrapper div | Ask user |

### Level 4: Manual Only

Changes too complex for auto-fix.

| Category | Example | Action |
|----------|---------|--------|
| Architecture | Component split | Manual |
| State | Add useState | Manual |
| Logic | Event handlers | Manual |
| API | Data fetching | Manual |

---

## Scoring System

### Category Weights

```yaml
scoring:
  layout:
    weight: 30%
    items:
      - flex/grid structure
      - alignment
      - positioning

  spacing:
    weight: 25%
    items:
      - padding
      - margin
      - gap

  typography:
    weight: 20%
    items:
      - font-size
      - font-weight
      - line-height
      - letter-spacing

  colors:
    weight: 15%
    items:
      - text color
      - background
      - border color

  effects:
    weight: 10%
    items:
      - shadows
      - borders
      - border-radius
```

### Score Calculation

```typescript
interface VerificationScore {
  layout: number;      // 0-100
  spacing: number;     // 0-100
  typography: number;  // 0-100
  colors: number;      // 0-100
  effects: number;     // 0-100

  weighted_total: number;  // Weighted average
  pass: boolean;           // weighted_total >= 95
}

function calculateScore(results: ComparisonResult[]): VerificationScore {
  const weights = {
    layout: 0.30,
    spacing: 0.25,
    typography: 0.20,
    colors: 0.15,
    effects: 0.10
  };

  // Calculate category scores
  const categoryScores = calculateCategoryScores(results);

  // Weighted total
  const weighted_total = Object.entries(weights).reduce(
    (sum, [category, weight]) => sum + categoryScores[category] * weight,
    0
  );

  return {
    ...categoryScores,
    weighted_total,
    pass: weighted_total >= 95
  };
}
```

---

## Completion Conditions

### Exit Criteria

The loop exits when ANY of these conditions are met:

```yaml
exit_conditions:
  # Success conditions
  success:
    - score >= 95 AND all_categories >= 90
    - perfect_score (100)
    - user_approval with score >= 90

  # Stop conditions (not failure)
  stop:
    - max_iterations reached (5 per agent)
    - no_improvement for 2 consecutive iterations
    - user_cancel

  # Failure conditions
  failure:
    - critical_error (MCP failure, render error)
    - score < 50 after 3 iterations
```

### Completion Marker

```markdown
## Verification Complete

Component: HeroSection
Iterations: 3 (Agent A), 4 (Agent B)
Selected: Agent B

### Final Scores
| Category | Score |
|----------|-------|
| Layout | 98% |
| Spacing | 96% |
| Typography | 100% |
| Colors | 100% |
| Effects | 92% |
| **Total** | **97%** |

### Fixes Applied
1. padding: p-5 → p-6 (Level 1)
2. gap: gap-3 → gap-4 (Level 1)
3. shadow: shadow-sm → shadow-md (Level 2)

<figma>DONE</figma>
```

---

## Integration with Phase Contracts

### Phase 6 Contract Update

```yaml
phase_id: 6
phase_name: "Verification Loop"
description: "Iterative verification with auto-fix until 95%+ accuracy"

# NEW: Loop configuration
loop:
  max_iterations: 5
  parallel_agents: 2
  target_score: 95
  auto_fix_levels: [1, 2]

outputs:
  artifacts:
    - verification_report.json
    - iteration_history.json     # NEW
    - selected_result.json       # NEW
    - fix_log.json              # NEW

validation:
  success_criteria:
    - weighted_score >= 95
    - all_categories >= 90
    - completion_marker_present
```

---

## Usage

### For Next.js (figma-to-nextjs)

```typescript
// In agent prompt
const verificationPrompt = `
Execute Verification Loop for component: ${componentPath}

Configuration:
- Target Score: 95%
- Max Iterations: 5
- Parallel Mode: competition
- Auto-Fix: Level 1-2 enabled

Comparison Tools:
- Primary: Numeric (Figma JSON vs Tailwind classes)
- Fallback: Visual (MCP Playwright screenshot)

Exit when score >= 95% and add marker: <figma>DONE</figma>
`;
```

### For Flutter (figma-to-flutter)

```typescript
// Same loop structure, different mapping
const verificationPrompt = `
Execute Verification Loop for widget: ${widgetPath}

Configuration:
- Target Score: 95%
- Max Iterations: 5
- Parallel Mode: competition
- Auto-Fix: Level 1-2 enabled

Comparison Tools:
- Primary: Numeric (Figma JSON vs Flutter properties)
- Fallback: Visual (Flutter test screenshot)

Mapping:
- padding: 24px → EdgeInsets.all(24)
- font-size: 16px → fontSize: 16
- color: #3B82F6 → Color(0xFF3B82F6)

Exit when score >= 95% and add marker: <figma>DONE</figma>
`;
```

---

## Best Practices

### DO

- Run numeric comparison first (faster, more accurate)
- Use parallel agents for better results
- Apply Level 1-2 fixes automatically
- Save iteration history for debugging
- Exit early when 95%+ achieved

### DON'T

- Skip numeric comparison and go straight to visual
- Run more than 5 iterations per agent
- Auto-fix Level 3+ changes
- Continue when score doesn't improve
- Ignore category-specific scores

---

## Troubleshooting

### Score Not Improving

```yaml
problem: Score stuck at 85% after 3 iterations
causes:
  - Layout structure mismatch (Level 3 issue)
  - Missing component mapping
  - Incorrect token extraction
solutions:
  - Check Phase 3 component mapping
  - Review Phase 2 token extraction
  - Request user approval for Level 3 fix
```

### Visual Comparison Fails

```yaml
problem: Playwright screenshot capture fails
causes:
  - Dev server not running
  - Component render error
  - Port conflict
solutions:
  - Ensure `npm run dev` is running
  - Check component for TypeScript errors
  - Try different port (3001)
```

### Parallel Agents Conflict

```yaml
problem: Both agents modify same file simultaneously
causes:
  - Race condition on file write
solutions:
  - Agents work on separate copies
  - Merge only the winning result
  - Use file locking if needed
```

---

*Version: 1.0.0*
*Last Updated: 2026-01-23*
*Applies To: figma-to-nextjs, figma-to-nextjs-pro, figma-to-flutter, figma-to-flutter-pro*
