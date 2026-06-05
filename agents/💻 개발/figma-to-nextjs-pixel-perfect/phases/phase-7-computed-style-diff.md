---
name: "Phase 7: Computed Style Diff"
phase_id: 7
description: "Compare browser DOM bounds and computed styles against design-spec.json"
---

# Phase 7: Computed Style Diff

## Purpose

Image diff tells where pixels differ. Computed-style diff explains why.

## Steps

Use Playwright in the preview route to collect:

- `getBoundingClientRect()`
- `getComputedStyle()`
- text content and rendered line boxes where possible
- image natural/rendered dimensions

Compare to `design-spec.json`.

## Required Checks

```json
{
  "bounds": ["x", "y", "width", "height"],
  "typography": ["fontFamily", "fontSize", "fontWeight", "lineHeight", "letterSpacing"],
  "box": ["padding", "margin", "borderWidth", "borderRadius"],
  "paint": ["color", "backgroundColor", "opacity", "boxShadow", "filter"],
  "assets": ["src", "naturalWidth", "naturalHeight", "objectFit"]
}
```

## Required Artifact

```text
computed-style-report.json
```

## Quality Gate

If computed styles differ while screenshot diff passes, document the discrepancy. If the difference is likely to break another browser/viewport, block productionize mode.

