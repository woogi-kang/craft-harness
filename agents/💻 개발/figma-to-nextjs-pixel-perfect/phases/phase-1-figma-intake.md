---
name: "Phase 1: Figma Intake"
phase_id: 1
description: "Parse Figma URL, identify target frames, and capture reference screenshots"
---

# Phase 1: Figma Intake

## Purpose

Identify exactly which Figma nodes are in scope.

## Steps

1. Parse `fileKey` and `nodeId` from the Figma URL.
2. Use `get_metadata` to read frame hierarchy and bounds.
3. Confirm the target node is a frame/component suitable for rendering.
4. Capture `figma-reference.png` using `get_screenshot` at comparison scale.
5. Record all responsive frames if provided.

## Required Artifacts

```text
figma-intake.json
figma-reference.png
frame-map.json
```

`frame-map.json` must include:

```json
{
  "desktop": { "nodeId": "123:456", "width": 1440, "height": 900 },
  "tablet": null,
  "mobile": null
}
```

## Quality Gate

If the user asks for responsive pixel-perfect output but only one Figma frame exists, continue only with explicit scope: `desktop exact, responsive approximation not claimed`.

