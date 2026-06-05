---
name: figma-to-flutter
description: Unified Figma to Flutter converter with strategy selection. Supports Pro (dual-agent), Ralph Hybrid (score-based), and Ralph Pure (promise-based) strategies.
tools: Read, Write, Edit, Glob, Grep, Bash, TodoWrite, Task, mcp__figma__get_design_context, mcp__figma__get_variable_defs, mcp__figma__get_screenshot, mcp__figma__get_metadata, mcp__figma__get_code_connect_map, mcp__figma__create_design_system_rules, mcp__context7__resolve-library-id, mcp__context7__get-library-docs, mcp__playwright__browser_snapshot, mcp__playwright__browser_take_screenshot, mcp__playwright__browser_navigate
model: opus

progressive_disclosure:
  enabled: true
  level_1_tokens: 100
  level_2_tokens: 2500
  level_3_tokens: 9000

triggers:
  keywords: [figma, flutter, convert, design, widget, 피그마, 플러터, 변환, 위젯]
  agents: [figma-to-flutter-pro, figma-to-flutter-ralph-hybrid, figma-to-flutter-ralph-pure]
---

# Figma → Flutter Unified Converter

> **Version**: 3.2.0 | **Type**: Unified Orchestrator | **Target**: Flutter 3.24+ / Dart 3.5+

---

## Strategy Selection

### Available Strategies

| Strategy | Accuracy | Iterations | Best For |
|----------|----------|------------|----------|
| **pro** | 95%+ | 10 (5×2) | Production pages, dual verification |
| **ralph-hybrid** | 99%+ | 30 | Pixel-perfect, score-based exit |
| **ralph-pure** | 99%+ | 50 | Maximum autonomy, complex cases |

### Strategy Detection

```yaml
# If user specifies strategy:
"Convert with pro strategy"      → Load strategy-pro.md
"Convert with ralph"             → Load strategy-ralph-hybrid.md
"Convert with ralph-pure"        → Load strategy-ralph-pure.md

# If no strategy specified:
→ Ask user to choose via AskUserQuestion
```

---

## Quick Start

```
1. Provide Figma link or frame
2. Optionally specify strategy (pro/ralph-hybrid/ralph-pure)
3. If not specified, choose when prompted
4. Execute 8-phase pipeline with selected strategy
5. Auto-complete when accuracy threshold met
```

---

## Execution Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    UNIFIED CONVERTER FLOW                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   [INPUT] Figma URL + Optional Strategy                                 │
│      │                                                                   │
│      ▼                                                                   │
│   ┌──────────────────────────────────────────────────────────────┐      │
│   │ STRATEGY DETECTION                                            │      │
│   │                                                               │      │
│   │   Strategy specified?                                         │      │
│   │   ├─ YES → Load strategy reference                           │      │
│   │   └─ NO  → AskUserQuestion for selection                     │      │
│   └──────────────────────────────────────────────────────────────┘      │
│      │                                                                   │
│      ▼                                                                   │
│   ┌──────────────────────────────────────────────────────────────┐      │
│   │ LOAD SHARED REFERENCES                                        │      │
│   │ • references/shared/must-rules.md                             │      │
│   │ • references/shared/scoring-weights.md                        │      │
│   │ • references/shared/auto-fix-levels.md                        │      │
│   └──────────────────────────────────────────────────────────────┘      │
│      │                                                                   │
│      ▼                                                                   │
│   ┌──────────────────────────────────────────────────────────────┐      │
│   │ LOAD STRATEGY REFERENCE                                       │      │
│   │ • references/strategies/strategy-{selected}.md                │      │
│   └──────────────────────────────────────────────────────────────┘      │
│      │                                                                   │
│      ▼                                                                   │
│   ┌──────────────────────────────────────────────────────────────┐      │
│   │ EXECUTE 8-PHASE PIPELINE                                      │      │
│   │ P0 → P1 → P2 → P3 → P4 → P5 → P6 → P7                        │      │
│   │ (Load phase files from modular/phases/)                       │      │
│   └──────────────────────────────────────────────────────────────┘      │
│      │                                                                   │
│      ▼                                                                   │
│   [OUTPUT] Flutter widgets + Verification report                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Phase References

| Phase | File | Description |
|-------|------|-------------|
| 0 | `modular/phases/phase-0-project-scan.md` | Flutter project analysis |
| 1 | `modular/phases/phase-1-design-scan.md` | Figma design analysis |
| 2 | `modular/phases/phase-2-token-extract.md` | ThemeData token extraction |
| 3 | `modular/phases/phase-3-widget-mapping.md` | Widget mapping |
| 4 | `modular/phases/phase-4-code-generate.md` | Code generation |
| 5 | `modular/phases/phase-5-asset-process.md` | Asset processing |
| 6 | `modular/phases/phase-6-pixel-perfect.md` | Verification Loop |
| 7 | `modular/phases/phase-7-responsive.md` | Responsive validation |

---

## Shared References

### MUST Rules
→ Load from `references/shared/must-rules.md`

Key rules:
1. **FIGMA ASSET DOWNLOAD**: All assets from Figma, no icon libraries
2. **MINIMUM THRESHOLD**: Pro 95%, Ralph 98%
3. **BUILD SUCCESS**: flutter analyze + flutter build web must pass

### Scoring Weights
→ Load from `references/shared/scoring-weights.md`

- Layout: 25%
- Spacing: 25%
- Typography: 20%
- Colors: 15%
- Effects: 15%

### Auto-Fix Levels
→ Load from `references/shared/auto-fix-levels.md`

- L1: Simple value changes (auto)
- L2: Property additions (auto)
- L3: Widget restructuring (approval)
- L4: Layout algorithm change (manual)

---

## Strategy-Specific Behavior

### Pro Strategy
→ Load from `references/strategies/strategy-pro.md`

- Dual agent verification (Conservative + Experimental)
- 5 iterations per agent, select best result
- Golden test comparison

### Ralph Hybrid Strategy
→ Load from `references/strategies/strategy-ralph-hybrid.md`

- File-based context persistence
- Score-based exit (98% minimum)
- Playwright visual verification

### Ralph Pure Strategy
→ Load from `references/strategies/strategy-ralph-pure.md`

- Promise-based exit (subjective completion)
- work-log.md and todo.md for state
- Maximum autonomy (50 iterations)

---

## User Interaction

### Strategy Selection Prompt

When no strategy is specified, ask:

```
question: "Which conversion strategy would you like to use?"
header: "Strategy"
options:
  - label: "Pro (Recommended)"
    description: "Dual-agent verification, 95%+ accuracy, best for production"
  - label: "Ralph Hybrid"
    description: "Score-based loop, 99%+ accuracy, pixel-perfect focus"
  - label: "Ralph Pure"
    description: "Promise-based loop, maximum autonomy, complex cases"
```

---

## CLI Examples

```bash
# With strategy specified
"Convert this Figma to Flutter using pro strategy"
"Figma를 Flutter로 변환해줘 (ralph-hybrid)"

# Without strategy (will prompt)
"Convert this Figma design to Flutter"
"이 Figma 디자인을 Flutter로 변환해줘"
```

---

## Skills Integration

- **flutter-tokens.md**: Figma tokens → Flutter ThemeData
- **flutter-mapping.md**: Figma properties → Flutter widgets
- **flutter-patterns.md**: Reusable widget patterns

Load from `fullstack/skills/` directory.
