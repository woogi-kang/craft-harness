---
name: "Phase 2: Source Spec"
phase_id: 2
description: "Create design-spec.json as the source of truth before code generation"
---

# Phase 2: Source Spec

## Purpose

Do not treat generated React from `get_design_context` as the source of truth. Build a structured spec first.

## Required Fields

For every relevant node, record:

```json
{
  "id": "123:456",
  "name": "CTA Button",
  "type": "INSTANCE",
  "bounds": { "x": 120, "y": 48, "width": 160, "height": 48 },
  "layout": {
    "mode": "HORIZONTAL",
    "gap": 8,
    "padding": { "top": 12, "right": 24, "bottom": 12, "left": 24 },
    "sizing": { "horizontal": "FIXED", "vertical": "FIXED" }
  },
  "style": {
    "fills": [],
    "strokes": [],
    "radius": 12,
    "effects": [],
    "opacity": 1
  },
  "text": {
    "fontFamily": "Inter",
    "fontSize": 16,
    "fontWeight": 600,
    "lineHeight": 24,
    "letterSpacing": 0
  }
}
```

## Required Artifacts

```text
design-spec.json
token-spec.json
node-order.json
unsupported-effects.json
```

## Quality Gate

If a visual property cannot be represented in CSS and cannot be faithfully decomposed, mark it as a blocker or rasterize that exact layer from Figma as an asset. Do not approximate silently.

