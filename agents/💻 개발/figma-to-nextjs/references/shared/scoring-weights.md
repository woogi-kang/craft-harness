# Scoring Weights (Shared)

> **Version**: 3.2.0 | **Type**: Shared Reference
> Scoring system used by all strategies

---

## Category Weights

```yaml
scoring_weights:
  layout:      25%  # Flex/Grid structure, positioning
  spacing:     25%  # Padding, margin, gap
  typography:  20%  # Font family, size, weight, line-height
  colors:      15%  # Text colors, backgrounds, gradients
  effects:     15%  # Shadows, borders, opacity
```

---

## Category Thresholds

```yaml
category_thresholds:
  layout:      95%  # Must achieve - structure is critical
  spacing:     95%  # Must achieve - visual alignment
  typography:  95%  # Must achieve - text is visible
  colors:      95%  # Must achieve - brand identity
  effects:     90%  # Slightly lower due to rendering
```

---

## Scoring Formula

```
Total Score = Σ (category_score × category_weight)

Example:
- Layout: 98% × 0.25 = 24.5
- Spacing: 96% × 0.25 = 24.0
- Typography: 97% × 0.20 = 19.4
- Colors: 99% × 0.15 = 14.85
- Effects: 92% × 0.15 = 13.8

Total = 96.55%
```

---

## Category Details

### Layout (25%)
- Flex/Grid structure matches Figma
- justify-content, align-items
- Positioning (relative, absolute)
- Container sizing (width, height)

### Spacing (25%)
- Padding values (p-*, px-*, py-*)
- Margin values (m-*, mx-*, my-*)
- Gap (gap-*)
- Space between elements

### Typography (20%)
- Font family (font-sans, font-serif)
- Font size (text-sm, text-lg)
- Font weight (font-medium, font-bold)
- Line height, letter spacing

### Colors (15%)
- Text colors (text-gray-900)
- Background colors (bg-white)
- Gradients (bg-gradient-to-r)
- Opacity values

### Effects (15%)
- Box shadows (shadow-md, shadow-lg)
- Border radius (rounded-lg)
- Borders (border, border-gray-200)
- Opacity and blend modes
