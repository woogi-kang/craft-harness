# Anti-Slop Reference

Use this for implementation, review, redesign, and final QA.

## Reflex Rejection

Run both checks:

1. If the category predicts the design, reject it.
   - AI -> purple/blue glow.
   - Fintech -> navy/gold.
   - Healthcare -> white/teal.
   - Developer tool -> dark terminal.
   - Luxury/artisan -> cream/brass/espresso.

2. If the anti-reference predicts the design, reject it too.
   - "Not purple AI" -> black neon terminal.
   - "Not SaaS cream" -> editorial serif.
   - "Not fintech navy" -> monochrome cyberpunk.

Pick the scene, audience, and brand truth. Do not pick from training-data reflex.

## Hard Bans By Default

- Gradient text for emphasis.
- Purple/blue AI gradient as the main identity.
- Glassmorphism as default surface language.
- Centered hero + pill badge + two CTAs + three equal feature cards.
- Identical card grids repeated across sections.
- Nested cards.
- Side-stripe card accents (`border-left` or `border-right` thicker than 1px).
- Hero metric template: large number + label + support stats as the main story.
- Fake screenshots made from div rectangles.
- Placeholder-only form labels.
- Decorative scroll cues.
- Decorative status dots on nav/list/badge items.
- Version labels in hero unless launch status is actually the message.
- Generic names: John Doe, Jane Doe, Acme, Nexus, SmartFlow.
- Generic copy: elevate, seamless, unleash, revolutionize, next-gen, game-changer.

## Layout Checks

- Hero fits the initial viewport; CTA visible without scrolling.
- Hero stack has at most one small cue, headline, subtext, CTA row.
- Logo walls and trust strips live below the hero, not inside it.
- Desktop nav is one line and under 80px tall.
- Do not repeat the same section layout family more than once per page.
- Bento grids have exactly the number of cells needed. No empty decorative cells.
- Multi-column layouts include explicit mobile collapse behavior.
- Use `min-h-[100dvh]`, not `h-screen`, for viewport-height sections.
- Text must not overflow containers on mobile or tablet.

## Color Checks

- Choose a color strategy first: restrained, committed, full palette, or drenched.
- Product UI defaults to one accent.
- Brand surfaces can commit to color when identity earns it.
- Tint neutrals toward the brand or scene; do not mix warm and cool gray families.
- Verify contrast for body text, buttons, helper text, placeholders, disabled states, and text over images.
- Keep one page-level theme. Do not randomly alternate light and dark sections.

## Typography Checks

- Body prose: 65-75ch max.
- Display headings: plan words, line length, and image size together.
- Avoid defaulting to Inter, Fraunces, Instrument Serif, Playfair, Space Grotesk, or IBM Plex Mono for brand work without a reason.
- Product UI may use system fonts when that improves native feel.
- Avoid all-caps body copy.
- Preserve italic descenders with line-height or padding.
- Use tabular numbers for prices, metrics, tables, and timers.

## Assets

- Brand/marketing surfaces need visual proof: real or generated images, actual screenshots, component previews, maps, charts, or canvas/WebGL scenes.
- Do not use abstract blobs, hand-rolled SVG illustrations, or fake browser windows as a substitute for a required product/place/person image.
- Verify external image URLs render.
- Give meaningful alt text for content images.
- Invented brands in logo walls need simple marks, not plain text rows.

## Interaction States

Check every user-facing flow:

- Loading: shape-matching skeleton or clear progress.
- Empty: explains the state and next action.
- Error: local, specific, recoverable.
- Disabled: visibly disabled but readable.
- Focus: keyboard-visible and high contrast.
- Mobile: touch targets 44px minimum, no hover-only affordance.
- Forms: label above input, helper text optional, error below input.
- Reduced motion: available for meaningful motion.

## Copy Self-Audit

Read every visible string before delivery. Rewrite anything that is:

- Grammatically broken.
- Cute but unclear.
- Fake-profound.
- Category-generic.
- Filled with unsupported numbers.
- Different in tone from the rest of the page.
