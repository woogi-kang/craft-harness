---
name: "Phase 5: Exact Render"
phase_id: 5
description: "Generate TSX/CSS from design-spec.json with exact values first"
---

# Phase 5: Exact Render

## Purpose

Render the Figma frame as faithfully as possible before refactoring for maintainability.

## CSS Policy

Prefer exact arbitrary values:

```tsx
<section className="w-[1440px] min-h-[900px] bg-[#FFFFFF]">
  <h1 className="text-[47px] leading-[55px] tracking-[-0.2px] font-[700]">
    Title
  </h1>
</section>
```

Use Tailwind presets only when the preset exactly matches the Figma value.

## Layout Policy

- Preserve Figma order and hierarchy unless semantic HTML can be added without visual change.
- Use `box-border` when dimensions include strokes/padding.
- Use absolute positioning only when it better matches the Figma layer model.
- Use flex/grid only when it faithfully maps Auto Layout constraints.
- Avoid shadcn visual defaults unless fully overridden.

## Required Artifact

```text
generated-files.json
render-route.txt
```

## Quality Gate

Generated code must build and render a preview route for every target frame.

