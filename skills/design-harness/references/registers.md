# Registers

Use this file to decide what "good" means for the surface.

## Product Register

Use for dashboards, admin tools, SaaS app shells, settings, forms, tables, command palettes, editors, and operational workflows.

Product UI succeeds when the interface becomes reliable muscle memory.

- Prefer standard controls and predictable placement.
- Color is restrained: primary actions, selection, semantic status, and focus.
- Typography optimizes scanning. System fonts and neutral sans families are acceptable.
- Density can be high when it helps comparison or repeated work.
- Motion is short and causal: press feedback, state continuity, overlay entry, loading transitions.
- Every component needs default, hover, active, focus, disabled, loading, empty, and error states when relevant.
- Cards are tools, not decoration. Use tables, lists, segmented controls, tabs, split panes, and inline editing when they fit better.

Product UI failures:

- Overdesigned poster layouts for daily workflows.
- Display fonts in controls or tables.
- Decorative motion on high-frequency actions.
- Non-standard forms, unclear focus, hidden affordances, hover-only interactions.
- Missing empty/loading/error states.

## Brand Register

Use for landing pages, portfolios, campaign pages, event pages, editorial microsites, product marketing, and first-impression surfaces.

Brand UI succeeds when the visitor can remember the page after closing it.

- Commit to a visual stance: restrained, committed, full palette, or drenched.
- Use real assets: product shots, photography, generated images, screenshots, data visuals, maps, or live component previews.
- Vary section layouts. Repeating the same header + card grid rhythm is a tell.
- Typography can carry personality, but the choice must match the brand, audience, and physical scene.
- Copy should be specific. Avoid grand adjectives and empty claims.
- One strong idea per fold beats many decorative fillers.

Brand UI failures:

- Centered hero + pill badge + two CTAs + three equal cards.
- Small uppercase eyebrow on every section.
- Decorative status dots, version labels, fake location/weather strips, scroll cues.
- Fake product screenshots made from rectangles.
- Stock-sounding testimonials and generic company names.

## Design System Register

Use when the user asks for tokens, CSS variables, component specs, theming, or reusable primitives.

- Define primitive, semantic, and component tokens.
- Use OKLCH or existing project token conventions.
- Keep one radius, shadow, spacing, and type scale system unless a documented exception exists.
- Hand implementation to `design-system` and `ui-styling` after design decisions are clear.

## Asset Register

Use for logos, banners, social images, app store screenshots, CIP, slide visuals, and brand-kit boards.

- Do not route asset-only work through web UI rules.
- Use `logo-creator`, `banner-design`, `app-store-screenshots`, `design`, or `slides` as the primary owner.
- Use this harness only for art direction, anti-slop review, or cross-surface consistency.
