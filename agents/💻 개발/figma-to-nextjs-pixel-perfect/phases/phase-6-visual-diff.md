---
name: "Phase 6: Visual Diff"
phase_id: 6
description: "Run deterministic screenshot comparison against Figma reference"
---

# Phase 6: Visual Diff

## Purpose

Pass/fail is determined by deterministic image diff, not LLM judgment.

## Steps

1. Start or reuse the Next.js dev server.
2. Open the preview route in Chromium.
3. Set viewport to the exact Figma frame dimensions.
4. Capture a screenshot with fixed `deviceScaleFactor`.
5. Compare against `figma-reference.png` using deterministic diff tooling.
6. Save diff image and grouped mismatch regions.

## Recommended Diff Tools

Use what exists in the project. If absent, install or script one of:

- `pixelmatch`
- `looks-same`
- Playwright screenshot comparison

## Diff Policy

Load `references/diff-policy.md`.

## Required Artifacts

```text
implemented-screenshot.png
diff-mask.png
diff-report.json
```

## Quality Gate

Fail on:

- Missing or extra visible element.
- Element position shift beyond tolerance.
- Color mismatch beyond tolerance.
- Text metric mismatch beyond tolerance.
- Diff budget exceeded.

