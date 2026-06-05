---
name: "Figma to Next.js Pixel-Perfect Usage Guide"
description: "Strict Figma to Next.js conversion workflow with deterministic visual verification"
---

# Figma to Next.js Pixel-Perfect Usage Guide

Use this agent when exact visual fidelity matters more than speed.

## Quick Start

```bash
@figma-to-nextjs-pixel-perfect [FIGMA_URL]
@figma-to-nextjs-pixel-perfect [FIGMA_URL] --frame "Desktop"
@figma-to-nextjs-pixel-perfect [FIGMA_URL] --frames "Desktop,Tablet,Mobile"
```

## Expected Input

- Figma URL with file key and node id.
- Target Next.js project path.
- Scope: frame, page, component, or multi-frame responsive set.
- Confirmation that strict failure is acceptable when assets/fonts are missing.

## Strict vs Normal Converter

| Concern | `figma-to-nextjs` | `figma-to-nextjs-pixel-perfect` |
|---------|-------------------|----------------------------------|
| Goal | Production-ready similarity | Measurable visual fidelity |
| Completion | Score threshold | Deterministic gates |
| CSS values | Tailwind presets preferred | Figma exact values preferred |
| Assets | Figma assets required, older docs have fallback conflicts | Figma assets required, no fallback |
| Fonts | Best effort | Missing font blocks completion |
| 3LLM review | Optional | Advisory panel for failed diffs |
| Refactor | During generation | After strict pass only |

## Recommended Flow

1. Run strict conversion on one desktop frame.
2. Resolve font and asset blockers.
3. Pass screenshot and computed-style diff.
4. Add tablet/mobile Figma frames if responsive strictness is required.
5. Run productionize mode after strict pass.

## Important Caveats

- Perfect pixel equality can be affected by browser, OS, device scale factor, and font rendering.
- The agent therefore uses a tiny diff budget and fails on structural mismatches.
- If Figma lacks a responsive frame, the agent can only claim exactness for the provided frame.
- If Figma uses unsupported blend modes or proprietary effects, the agent must report a blocker or rasterize that exact layer from Figma.

## Output Status

```yaml
PASS_STRICT:
  meaning: All strict gates passed for requested frames.

PASS_SCOPED:
  meaning: Strict gates passed for a smaller explicit scope.

BLOCKED:
  meaning: Missing font/asset/tool or unsupported effect prevents faithful conversion.

FAIL:
  meaning: Verification failed and no safe fix remains.
```

