# Completion Gates

Completion requires all gates below.

```yaml
required_gates:
  asset_lock_passed: true
  font_lock_passed: true
  build_passed: true
  visual_diff_passed: true
  computed_style_diff_passed: true
  forbidden_fallback_scan_passed: true
  responsive_scope_clear: true
```

## Gate Definitions

### Asset Lock

`asset-manifest.json` exists and every referenced asset is downloaded from Figma.

### Font Lock

`font-manifest.json` exists and every required font is available in the rendered browser environment.

### Build

`npm run build` succeeds. If lint/typecheck scripts exist, run them too.

### Visual Diff

Screenshot diff is below the configured threshold for every requested frame.

### Computed Style Diff

DOM bounds and computed styles match `design-spec.json` within tolerance.

### Forbidden Fallback Scan

Code and assets contain none of:

- `lucide-react`
- `@heroicons`
- `react-icons`
- placeholder image URLs
- generated substitute SVG
- TODO comments that hide a visual mismatch

### Responsive Scope

Final report states exactly which frames are strict and which, if any, are approximation-only.

