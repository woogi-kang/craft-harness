# Diff Policy

Pixel-perfect on the web needs a tiny tolerance because browser rendering can differ from Figma due to anti-aliasing and subpixel rounding.

## Default Tolerances

```yaml
visual_diff:
  allowed_pixel_diff_percent: 0.1
  fail_on_missing_or_extra_element: true
  fail_on_layout_shift_over_px: 1
  ignore_antialiasing_if_tool_supports_it: true

computed_style:
  bounds_tolerance_px: 0.5
  typography_tolerance_px: 0.5
  color_channel_tolerance: 1
  opacity_tolerance: 0.01
```

## Viewport Rules

- Viewport width and height must match the Figma frame.
- `deviceScaleFactor` must be fixed and recorded.
- Full-page screenshots are forbidden for component/frame diff unless the Figma reference is also full-page.
- Crop regions must be identical.

## Failure Categories

```yaml
critical:
  - missing visible element
  - extra visible element
  - wrong asset
  - missing font
  - layout shift > 1px

high:
  - text metric mismatch
  - color mismatch
  - border radius mismatch
  - shadow/filter mismatch

medium:
  - anti-aliasing-only difference
  - subpixel rounding under tolerance
```

Critical issues always fail strict completion.

