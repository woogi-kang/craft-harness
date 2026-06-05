---
name: "Phase 4: Asset Lock"
phase_id: 4
description: "Download and verify all Figma assets before code generation"
---

# Phase 4: Asset Lock

## Purpose

All images, icons, logos, masks, and rasterized unsupported layers must come from Figma.

## Steps

1. Build asset inventory from `design-spec.json` and Figma metadata.
2. Download each asset with `get_screenshot` in the required format.
3. Save assets under `public/figma-assets/{session_id}/`.
4. Record dimensions, format, node id, and checksum.
5. Verify every code reference points to the manifest.

## Required Artifact

```json
{
  "assets": [
    {
      "nodeId": "123:789",
      "name": "Logo",
      "kind": "svg",
      "path": "public/figma-assets/session/logo.svg",
      "width": 128,
      "height": 32,
      "downloaded": true,
      "checksum": "sha256:..."
    }
  ]
}
```

## Hard Failures

- Missing asset.
- Placeholder image.
- Icon library import.
- Manually drawn replacement SVG.
- AI-generated substitute.
- Similar but non-Figma asset.

