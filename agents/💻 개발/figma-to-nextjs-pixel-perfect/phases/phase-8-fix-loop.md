---
name: "Phase 8: Fix Loop"
phase_id: 8
description: "Apply targeted fixes based on deterministic diff and optional 3LLM advisory review"
---

# Phase 8: Fix Loop

## Purpose

Iterate only on measured differences. Avoid speculative rewrites.

## Loop Protocol

1. Read `diff-report.json` and `computed-style-report.json`.
2. Classify each issue by cause: layout, text metrics, color, asset, effect, browser default, unsupported Figma feature.
3. Apply smallest safe patch.
4. Re-run Phase 6 and Phase 7.
5. Record fix in `fix-history.json`.

## Escalation

Use `references/3llm-verification.md` when:

- The same diff remains after two targeted fixes.
- Pixel diff fails but computed style appears correct.
- A CSS specificity or layout interaction is unclear.
- Build passes but hydration/rendering changes the layout.

## Stop Conditions

Stop and report `BLOCKED` when:

- Required asset or font is unavailable.
- Unsupported effect cannot be represented or rasterized.
- Three targeted fixes regress another passed area.
- The user-requested scope lacks necessary Figma frames.

