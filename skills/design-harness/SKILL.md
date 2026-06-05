---
name: design-harness
description: "차세대 프론트엔드 디자인 하네스. UI/UX 디자인, 랜딩/대시보드/앱/포트폴리오/브랜드 페이지, 리디자인, UX 리뷰, visual QA, anti-slop, 스타일/컬러/타이포그래피/레이아웃/모션 의사결정, 접근성/반응형/상태 하드닝에 사용한다. 과거 ui-ux-pro-max, design-craft, ui-design-agent-skills를 대체하는 1차 디자인 진입점이다."
license: MIT
metadata:
  category: "🎨 디자인"
  version: "0.1.0"
  tags: "frontend-design, ui-ux, anti-slop, visual-qa, redesign, design-system"
---

# Design Harness

Use this as the primary UI/UX design entrypoint. It replaces the old split between `ui-ux-pro-max` planning, `design-craft` anti-slop checks, and the granular `🎨 디자인/ui-design-agent-skills/*` template skills.

The job is not to generate a style from a database. The job is to read the product, pick the right register, make explicit design decisions, implement or review the interface, then verify that it does not look like default AI output.

## Core Flow

1. **Load project context**
   - Read `PRODUCT.md` and `DESIGN.md` when present.
   - Inspect at least one representative UI file: tokens/theme CSS, a page, or a component.
   - Check `package.json` before recommending or importing libraries.
   - For redesigns, preserve existing behavior, IA, and brand identity unless the user asks for overhaul.

2. **Write a design read**

   ```text
   Reading this as: <surface> for <audience>, in <scene>, using <brand|product> register, with <visual stance>, avoiding <main slop risk>.
   ```

   Ask one short question only when two plausible reads would materially change the design. Otherwise state assumptions and proceed.

3. **Set three dials**

   | Dial | 1-3 | 4-7 | 8-10 |
   |---|---|---|---|
   | `DISTINCTION` | familiar | specific | highly authored |
   | `MOTION` | feedback only | subtle choreography | advanced scroll/physics |
   | `DENSITY` | sparse | normal | compact/operational |

   Product UI usually sits at `3-5 / 2-4 / 6-9`. Brand surfaces usually sit at `6-9 / 4-8 / 2-5`. Regulated or public-sector surfaces bias lower distinction and motion.

4. **Pick a mode**

   | Mode | Use when | Required reference |
   |---|---|---|
   | `shape` | UX/UI plan before code | `references/workflows.md` |
   | `craft` | implement a new UI surface end-to-end | `references/registers.md`, `references/anti-slop.md` |
   | `audit` | review UX, a11y, responsive, visual quality | `references/workflows.md`, `references/anti-slop.md` |
   | `polish` | improve an existing surface before ship | `references/anti-slop.md`, `references/motion-interaction.md` |
   | `redesign` | modernize existing UI | `references/workflows.md` |
   | `typeset` | typography hierarchy/font work | `references/registers.md` |
   | `colorize` | palette/theme work | `references/registers.md`, `references/anti-slop.md` |
   | `animate` | purposeful motion/interactions | `references/motion-interaction.md` |
   | `harden` | states, edge cases, i18n, text overflow | `references/anti-slop.md`, `references/korean-ui.md` when Korean applies |

5. **Use the right downstream skill**
   - Component implementation: `ui-styling`.
   - Token architecture: `design-system`.
   - Logos, banners, CIP, social images: `design`, `logo-creator`, `banner-design`.
   - Historical database lookup is archived; do not route new design work to it.

## Register Split

Read `references/registers.md` when the task touches a full screen, page, app shell, landing page, dashboard, or redesign.

- **Product register**: design serves repeated task completion. Favor predictable controls, complete states, restrained color, density, speed, and clarity.
- **Brand register**: design is part of the product. Favor a clear point of view, real assets, committed art direction, layout variation, and strong first impression.

Do not use brand-page tactics on dashboards. Do not use dashboard restraint on portfolio or campaign pages.

## Anti-Slop Defaults

Read `references/anti-slop.md` for implementation or review. The short version:

- Reject category reflexes: AI product does not imply purple glow; finance does not imply navy/gold; luxury does not imply cream/brass.
- Avoid repeated centered heroes, pill badges, equal card grids, gradient text, decorative glass, fake screenshots, generic logo walls, and cliche copy.
- Use actual images, screenshots, generated raster assets, real component previews, charts, maps, or canvas/WebGL scenes when the surface needs visual proof.
- Every interactive flow needs loading, empty, error, disabled, focus, mobile, and reduced-motion behavior when relevant.

## Mechanical Preflight

When UI code exists locally, run the detector on changed UI files or the focused source directory:

```bash
node skills/design-harness/scripts/detect-design-slop.mjs src app components pages
```

Use the findings as prompts for inspection, not as a substitute for judgment. After implementation, verify in a browser when the project has a runnable frontend.

## Legacy Policy

- `ui-ux-pro-max` and `design-craft` are legacy entrypoints outside the public active skill tree.
- `🎨 디자인/ui-design-agent-skills/*` is a legacy template split outside the public active skill tree. Do not use those old template snippets as primary guidance.

## Review Output

For reviews, lead with a table:

| Before | After | Why |
|---|---|---|
| Current pattern or issue | Proposed change | Design reason and risk |

Then list only the highest-impact fixes. Avoid long taste-preference inventories.
