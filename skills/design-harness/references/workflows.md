# Workflows

Use this file to choose the right operating mode.

## Shape

Use before code when direction or scope is unclear.

Output:

- Design read.
- Register and dial values.
- Surface map: sections/screens/components.
- Visual stance and anti-goals.
- Key assets needed.
- Open questions limited to blockers.
- Validation method.

Do not create a long generic design brief when a compact plan is enough.

## Craft

Use when building a page/screen/component.

Steps:

1. Inspect existing stack, tokens, components, and package dependencies.
2. Decide register and dials.
3. Identify the one visual idea or product usability goal.
4. Implement with existing primitives where they fit.
5. Add necessary states and responsive behavior.
6. Run mechanical preflight.
7. Run browser/screenshot QA when possible.

## Audit

Use for review without immediately rewriting.

Lead with:

| Before | After | Why |
|---|---|---|

Prioritize:

1. Broken usability or accessibility.
2. Layout/responsive failures.
3. Missing states.
4. AI slop signatures.
5. Visual polish.

## Polish

Use after a surface exists and mostly works.

Order of operations:

1. Fix readability and contrast.
2. Fix spacing rhythm and hierarchy.
3. Remove generic filler elements.
4. Add or correct interaction states.
5. Improve assets and copy.
6. Tune motion only where it communicates.

## Redesign

Use for existing projects.

1. Detect mode: preserve, evolve, or overhaul.
2. Inventory current font, palette, radius, shadows, spacing, icon set, section patterns.
3. List top 5 slop signatures and top 5 trust/usability issues.
4. Fix in low-risk order: typography, color tokens, interaction states, spacing, layout, assets, motion.
5. Preserve URL structure, form field names, legal copy, analytics hooks, and product behavior unless requested.

## Harden

Use before ship.

- Text overflow and longest words.
- Empty/loading/error/disabled/focus states.
- Keyboard and screen-reader access.
- Reduced motion.
- Mobile nav and touch targets.
- Image dimensions and CLS.
- i18n and Korean line breaking where relevant.
