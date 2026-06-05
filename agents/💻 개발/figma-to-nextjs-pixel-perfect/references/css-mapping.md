# CSS Mapping for Exact Fidelity

## General Policy

Use the smallest CSS that matches Figma exactly.

```tsx
// Exact value preferred
className="w-[371px] h-[58px] rounded-[13px]"

// Preset allowed only when exact
className="w-96" // only if Figma width is exactly 384px
```

## Typography

Map exact values:

```tsx
className="font-[600] text-[17px] leading-[22px] tracking-[-0.2px]"
```

Do not use `text-lg`, `leading-normal`, or `tracking-tight` unless they exactly match the Figma values.

## Layout

Figma Auto Layout mapping:

| Figma | CSS |
|-------|-----|
| Horizontal | `flex flex-row` |
| Vertical | `flex flex-col` |
| Gap | `gap-[Npx]` |
| Padding | `pt-[Npx] pr-[Npx] pb-[Npx] pl-[Npx]` |
| Fill | `flex-1` or exact width depending on parent constraints |
| Hug | `w-fit` / `h-fit` only when browser result matches |
| Fixed | `w-[Npx] h-[Npx]` |

## Effects

Use exact CSS for:

- Multiple shadows.
- Filters.
- Backdrop filters.
- Gradient stops.
- Opacity.
- Blend modes when supported.

If unsupported, rasterize the exact Figma layer or block completion.

## shadcn/ui

shadcn may provide behavior. It must not provide visual truth.

```tsx
<Button
  className="h-[48px] rounded-[12px] bg-[#111111] px-[24px] text-[16px] leading-[24px]"
>
  Label
</Button>
```

