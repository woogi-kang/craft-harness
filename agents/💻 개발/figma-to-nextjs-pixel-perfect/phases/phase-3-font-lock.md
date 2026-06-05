---
name: "Phase 3: Font Lock"
phase_id: 3
description: "Verify all Figma fonts before rendering"
---

# Phase 3: Font Lock

## Purpose

Text metrics drive layout. Missing fonts must block strict completion.

## Steps

1. Extract all font families, weights, styles, sizes, line heights, and letter spacing from `design-spec.json`.
2. Check project font setup: `next/font`, local assets, CSS imports, or system availability.
3. Prefer `next/font/local` for exact local font files when available.
4. Record fallback risk explicitly.

## Required Artifact

```json
{
  "fonts": [
    {
      "family": "Inter",
      "weights": [400, 500, 600, 700],
      "source": "next/font/google",
      "available": true,
      "strictPass": true
    }
  ]
}
```

## Quality Gate

If any required font or weight is missing, stop with `BLOCKED: missing_font`. Do not use browser default fallback and claim pixel-perfect output.

