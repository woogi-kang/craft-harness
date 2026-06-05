# Must Rules

These rules apply to every `figma-to-nextjs-pixel-perfect` run.

## Completion

- Deterministic gates decide completion.
- LLM review can block completion but cannot pass failed gates.
- Never declare `PASS_STRICT` if any required gate is missing.

## Assets

- Every image, icon, logo, illustration, and rasterized unsupported layer must come from Figma.
- Placeholder images, generated substitutes, similar replacements, icon libraries, and manual SVG redraws are forbidden.
- Missing asset means `BLOCKED`, not degraded completion.

## Fonts

- Every required font family, weight, and style must be available.
- Missing font means `BLOCKED`.
- Browser fallback fonts cannot be used for strict completion.

## CSS Fidelity

- Use exact Figma values first.
- Tailwind presets are allowed only when exact.
- Arbitrary values and CSS custom properties are preferred for non-tokenized Figma values.
- shadcn/ui visual defaults must not override Figma values.

## Responsive Claims

- Pixel-perfect responsive output requires matching Figma frames for each claimed breakpoint.
- If only a desktop frame exists, claim only desktop fidelity.

