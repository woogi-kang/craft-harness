# Scoring Weights (Shared)

> **Version**: 3.2.0 | **Type**: Shared Reference
> Scoring system used by all strategies

---

## Category Weights

```yaml
scoring_weights:
  layout:      25%  # Widget hierarchy, Flex properties, positioning
  spacing:     25%  # Padding, margin, gaps (EdgeInsets, SizedBox)
  typography:  20%  # FontFamily, fontSize, fontWeight, letterSpacing
  colors:      15%  # Fill colors, text colors, gradients
  effects:     15%  # Shadows (BoxShadow), borders, opacity
```

---

## Category Thresholds

```yaml
category_thresholds:
  layout:      95%  # Must achieve - widget structure is critical
  spacing:     95%  # Must achieve - visual alignment depends on it
  typography:  95%  # Must achieve - text is highly visible
  colors:      95%  # Must achieve - brand identity
  effects:     90%  # Slightly lower due to rendering differences
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
- Widget hierarchy matches Figma layer structure
- Flex properties (mainAxisAlignment, crossAxisAlignment)
- Positioning (Stack children, Positioned)
- Container sizing (width, height, constraints)

### Spacing (25%)
- Padding values (EdgeInsets)
- Margin/Gap (SizedBox, Spacer)
- Row/Column spacing (mainAxisSpacing, crossAxisSpacing)

### Typography (20%)
- Font family (exact match or fallback)
- Font size (exact px to logical pixels)
- Font weight (w400, w500, w600, w700)
- Letter spacing and line height

### Colors (15%)
- Fill colors (Container color, Text color)
- Gradient colors (LinearGradient, RadialGradient)
- Opacity values

### Effects (15%)
- Box shadows (offset, blur, spread, color)
- Border radius (BorderRadius.circular)
- Border styles (Border, BorderSide)
- Opacity and blend modes
