---
name: "Phase 0: Project Scan"
phase_id: 0
description: "Verify Next.js project and deterministic verification environment"
---

# Phase 0: Project Scan

## Purpose

Confirm the target project can render and verify pixel-perfect output repeatably.

## Required Checks

```bash
test -f package.json
grep -q '"next"' package.json
```

Check:

- Next.js version and App Router or Pages Router.
- TypeScript availability.
- Tailwind availability.
- Existing `src/app` or `pages` structure.
- `npm run build` script.
- Existing Playwright setup or ability to run browser screenshots.
- Existing image/font handling conventions.

## Deterministic Environment

Record these values in `environment-report.json`:

```json
{
  "viewport": { "width": 1440, "height": 900 },
  "deviceScaleFactor": 1,
  "browser": "chromium",
  "fontSmoothing": "default",
  "node": "detected",
  "next": "detected"
}
```

## Quality Gate

Do not continue if the target is not a Next.js project unless the user explicitly asks to create one. If a project is created, use CLI setup and keep it separate from existing source.

