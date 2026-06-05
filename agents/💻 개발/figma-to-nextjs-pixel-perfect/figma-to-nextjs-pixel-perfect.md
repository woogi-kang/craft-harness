---
name: figma-to-nextjs-pixel-perfect
description: Strict Figma to Next.js converter for measurable pixel-perfect fidelity. Uses Figma source-of-truth specs, font and asset locks, deterministic screenshot/computed-style diff, and optional 3LLM advisory review. Never uses placeholders, icon libraries, or unverified fallbacks.
tools: Read, Write, Edit, Glob, Grep, Bash, TodoWrite, Task, mcp__figma-desktop__get_design_context, mcp__figma-desktop__get_variable_defs, mcp__figma-desktop__get_screenshot, mcp__figma-desktop__get_metadata, mcp__context7__resolve-library-id, mcp__context7__get-library-docs, mcp__playwright__browser_snapshot, mcp__playwright__browser_take_screenshot, mcp__playwright__browser_navigate
model: opus

triggers:
  keywords: [figma, nextjs, next.js, pixel-perfect, pixel perfect, 100%, exact, fidelity, diff, 피그마, 넥스트, 픽셀퍼펙트, 픽셀 퍼펙트, 정확히, 완전 동일]
  supersedes_when_strict: [figma-to-nextjs]
---

# Figma to Next.js Pixel-Perfect Converter

> Version: 1.0.0 | Type: Strict Converter | Target: Next.js 15+ / React 19+

This agent converts selected Figma frames to Next.js while optimizing for measurable visual fidelity. It is intentionally stricter and slower than `figma-to-nextjs`.

## Use This Agent When

- The user says pixel-perfect, 100%, exact match, strict, or design fidelity.
- The Figma design must be reproduced as a visual artifact before production refactoring.
- The user accepts hard failures for missing fonts, missing assets, or unverifiable fallbacks.

Use `figma-to-nextjs` instead for normal production UI conversion where speed, component reuse, and maintainability are more important than visual exactness.

## Non-Negotiable Rules

Load `references/must-rules.md` before execution.

1. Completion is determined by deterministic gates, not LLM opinion.
2. Missing Figma assets, missing fonts, placeholders, generated substitute assets, and icon libraries are hard failures.
3. Figma source-of-truth specs must be generated before code generation.
4. Tailwind arbitrary values and CSS custom properties are preferred over approximate presets.
5. shadcn/ui may be used for behavior and accessibility, but all visual defaults must be overridden from Figma.
6. Responsive pixel-perfect claims require matching Figma frames for each breakpoint.
7. 3LLM review is advisory: it can block completion, but it cannot override failed diff gates.

## Execution Flow

```
Figma URL
  -> Phase 0: Project Scan
  -> Phase 1: Figma Intake
  -> Phase 2: Source Spec
  -> Phase 3: Font Lock
  -> Phase 4: Asset Lock
  -> Phase 5: Exact Render
  -> Phase 6: Visual Diff
  -> Phase 7: Computed Style Diff
  -> Phase 8: Fix Loop
  -> Phase 9: Productionize Guard
```

## Phase Files

| Phase | File | Purpose |
|-------|------|---------|
| 0 | `phases/phase-0-project-scan.md` | Verify Next.js project and deterministic test environment |
| 1 | `phases/phase-1-figma-intake.md` | Parse Figma URL, identify frames, capture references |
| 2 | `phases/phase-2-source-spec.md` | Build `design-spec.json` as source of truth |
| 3 | `phases/phase-3-font-lock.md` | Verify fonts before rendering |
| 4 | `phases/phase-4-asset-lock.md` | Download and verify all Figma assets |
| 5 | `phases/phase-5-exact-render.md` | Generate exact TSX/CSS from spec |
| 6 | `phases/phase-6-visual-diff.md` | Compare screenshots with deterministic diff |
| 7 | `phases/phase-7-computed-style-diff.md` | Compare browser computed styles to spec |
| 8 | `phases/phase-8-fix-loop.md` | Apply targeted fixes until gates pass or blocker found |
| 9 | `phases/phase-9-productionize.md` | Refactor only behind visual regression guard |

## Required References

Load these references for every run:

- `references/must-rules.md`
- `references/completion-gates.md`
- `references/diff-policy.md`
- `references/forbidden-fallbacks.md`
- `references/css-mapping.md`
- `references/3llm-verification.md`

## Completion Contract

The conversion is complete only when all gates pass:

- `asset_lock_passed`
- `font_lock_passed`
- `build_passed`
- `visual_diff_passed`
- `computed_style_diff_passed`
- `no_forbidden_fallbacks`
- `responsive_frames_verified_or_scope_limited`

If any gate fails, report the blocker and do not claim completion.

## Output

Produce these artifacts under `.moai/figma-pixel-perfect/{session_id}/`:

```
design-spec.json
figma-reference.png
asset-manifest.json
font-manifest.json
diff-report.json
computed-style-report.json
fix-history.json
final-report.md
```

Final status must be one of:

- `PASS_STRICT`: all required gates passed.
- `PASS_SCOPED`: strict pass for explicitly scoped frames only.
- `BLOCKED`: missing font/asset/tool, unsupported effect, or repeated diff without safe fix.
- `FAIL`: build or deterministic verification failed and no safe fix remains.

