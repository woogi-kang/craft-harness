# Forbidden Fallbacks

The strict converter must never hide fidelity problems with substitutes.

## Forbidden

- Placeholder images.
- Generated gradients or blocks standing in for missing images.
- `lucide-react`, `heroicons`, `react-icons`, Font Awesome, or similar icon libraries.
- Manual SVG approximations for Figma icons.
- Default browser fonts replacing Figma fonts.
- Tailwind default colors replacing extracted colors.
- shadcn/ui default sizing replacing Figma sizing.
- Skipping a failed node and claiming completion.
- Human approval overriding failed diff gates.

## Required Response

When a fallback would normally be used, stop and report:

```yaml
status: BLOCKED
reason: missing_asset | missing_font | unsupported_effect | unavailable_tool
required_user_action: "..."
strict_completion: false
```

