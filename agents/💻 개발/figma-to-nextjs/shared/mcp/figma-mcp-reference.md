---
name: "Figma MCP Tool Reference"
description: "Figma MCP tools reference and API documentation"
---

# Figma MCP Tool Reference

> Consolidated reference for all Figma MCP tools used in the conversion pipeline

---

## Overview

The Figma-to-Next.js conversion pipeline uses six MCP tools to extract design data:

| Tool | Phase | Purpose | Tokens Est. |
|------|-------|---------|-------------|
| `get_metadata` | 0, 1 | Project structure | ~500 |
| `get_design_context` | 1, 4 | React + Tailwind code | ~2000 |
| `get_variable_defs` | 2 | Design tokens | ~1000 |
| `get_screenshot` | 5, 6 | Visual assets | ~100 |
| `get_code_connect_map` | 3 | Component mappings | ~500 |
| `add_code_connect_map` | 4 | Register components | ~100 |

---

## Tool Details

### 1. get_metadata

**Purpose**: Retrieve Figma file structure and node information

**When to Use**:
- Phase 0: Initial project scan
- Phase 1: Structure analysis

**Parameters**:
```typescript
interface GetMetadataParams {
  fileKey: string;      // Required: Figma file key (from URL)
  nodeId?: string;      // Optional: Specific node to analyze
  depth?: number;       // Optional: Tree depth (default: 2)
}
```

**Example Call**:
```typescript
get_metadata({
  fileKey: "ABC123xyz",
  depth: 3
})
```

**Response Structure**:
```typescript
interface MetadataResponse {
  name: string;
  lastModified: string;
  version: string;
  document: {
    id: string;
    name: string;
    type: "DOCUMENT";
    children: NodeInfo[];
  };
  components: Record<string, ComponentInfo>;
  styles: Record<string, StyleInfo>;
}
```

**Error Handling**:
- `FILE_NOT_FOUND`: Invalid file key
- `ACCESS_DENIED`: No permission to file
- `RATE_LIMIT`: Too many requests

---

### 2. get_design_context

**Purpose**: Extract React + Tailwind code from Figma nodes

**When to Use**:
- Phase 1: Understand design structure
- Phase 4: Generate component code

**Parameters**:
```typescript
interface GetDesignContextParams {
  fileKey: string;      // Required: Figma file key
  nodeId: string;       // Required: Node ID to extract
  format?: "react" | "html";  // Optional: Output format (default: react)
}
```

**Example Call**:
```typescript
get_design_context({
  fileKey: "ABC123xyz",
  nodeId: "123:456"
})
```

**Response Structure**:
```typescript
interface DesignContextResponse {
  code: string;           // Generated React/Tailwind code
  nodeInfo: {
    id: string;
    name: string;
    type: string;
    bounds: BoundingBox;
  };
  styles: ExtractedStyles;
  children?: DesignContextResponse[];
}
```

**Best Practices**:
- Call once per major section (Hero, Features, CTA)
- Avoid calling for individual elements
- Cache responses to minimize API calls

---

### 3. get_variable_defs

**Purpose**: Extract design tokens (colors, typography, spacing)

**When to Use**:
- Phase 2: Token extraction

**Parameters**:
```typescript
interface GetVariableDefsParams {
  fileKey: string;      // Required: Figma file key
  collectionId?: string; // Optional: Specific variable collection
}
```

**Example Call**:
```typescript
get_variable_defs({
  fileKey: "ABC123xyz"
})
```

**Response Structure**:
```typescript
interface VariableDefsResponse {
  collections: VariableCollection[];
  variables: {
    colors: ColorVariable[];
    typography: TypographyVariable[];
    spacing: SpacingVariable[];
    effects: EffectVariable[];
  };
  modes: Mode[];  // Light/Dark mode definitions
}

interface ColorVariable {
  name: string;
  value: string;        // HEX or RGBA
  resolvedValue: string;
  description?: string;
  scopes: string[];     // Where this variable can be used
}
```

**Mapping to Tailwind**:
```typescript
// Example token mapping
const tokenMapping = {
  "colors/primary/500": "primary",
  "colors/gray/100": "gray-100",
  "spacing/4": "1",     // 4px = 0.25rem = spacing-1
  "radius/md": "md",    // 6px = rounded-md
};
```

---

### 4. get_screenshot

**Purpose**: Capture visual screenshots of Figma nodes

**When to Use**:
- Phase 5: Asset extraction
- Phase 6: Pixel-perfect comparison

**Parameters**:
```typescript
interface GetScreenshotParams {
  nodeId: string;       // Required: Node to capture
  scale?: number;       // Optional: Scale factor (default: 1, max: 4)
  format?: "png" | "jpg" | "svg";  // Optional: Image format
}
```

**Example Call**:
```typescript
get_screenshot({
  nodeId: "123:460",
  scale: 2,
  format: "png"
})
```

**Response Structure**:
```typescript
interface ScreenshotResponse {
  imageData: string;    // Base64 encoded image
  format: string;
  dimensions: {
    width: number;
    height: number;
  };
  nodeId: string;
}
```

**Usage Patterns**:

```typescript
// For hero background image
const heroImage = await get_screenshot({
  nodeId: heroNodeId,
  scale: 2,  // 2x for retina
  format: "png"
});

// Save to public folder
await saveAsset(heroImage.imageData, "public/images/hero/hero-bg.png");

// For SVG icons (use svg format)
const icon = await get_screenshot({
  nodeId: iconNodeId,
  format: "svg"
});
```

---

### 5. get_code_connect_map

**Purpose**: Retrieve existing component-to-code mappings

**When to Use**:
- Phase 3: Component mapping

**Parameters**:
```typescript
interface GetCodeConnectMapParams {
  fileKey: string;      // Required: Figma file key
}
```

**Example Call**:
```typescript
get_code_connect_map({
  fileKey: "ABC123xyz"
})
```

**Response Structure**:
```typescript
interface CodeConnectMapResponse {
  mappings: ComponentMapping[];
}

interface ComponentMapping {
  figmaComponentId: string;
  figmaComponentName: string;
  codeComponentPath: string;   // e.g., "@/components/ui/button"
  codeComponentName: string;   // e.g., "Button"
  props: PropMapping[];
  variants: VariantMapping[];
}
```

---

### 6. add_code_connect_map

**Purpose**: Register new component mappings

**When to Use**:
- Phase 4: After generating components

**Parameters**:
```typescript
interface AddCodeConnectMapParams {
  fileKey: string;
  mapping: {
    figmaComponentId: string;
    codeComponentPath: string;
    codeComponentName: string;
    props?: PropMapping[];
  };
}
```

**Example Call**:
```typescript
add_code_connect_map({
  fileKey: "ABC123xyz",
  mapping: {
    figmaComponentId: "123:789",
    codeComponentPath: "@/components/ui/button",
    codeComponentName: "Button",
    props: [
      { figmaProp: "Label", codeProp: "children" },
      { figmaProp: "Variant", codeProp: "variant" }
    ]
  }
})
```

---

## Phase-to-Tool Matrix

| Phase | Primary Tool | Secondary Tools |
|-------|--------------|-----------------|
| 0 - Project Scan | `get_metadata` | - |
| 1 - Structure | `get_design_context` | `get_metadata` |
| 2 - Tokens | `get_variable_defs` | - |
| 3 - Mapping | `get_code_connect_map` | `get_metadata` |
| 4 - Generate | `get_design_context` | `add_code_connect_map` |
| 5 - Assets | `get_screenshot` | - |
| 6 - Verify | `get_screenshot` | - |
| 7 - Responsive | - | - |

---

## Token Budget Management

### Estimated Tokens per Phase

```
Phase 0: ~500 tokens   (1 get_metadata call)
Phase 1: ~3000 tokens  (1-2 get_design_context calls)
Phase 2: ~1000 tokens  (1 get_variable_defs call)
Phase 3: ~500 tokens   (1 get_code_connect_map call)
Phase 4: ~5000 tokens  (3-5 get_design_context calls)
Phase 5: ~500 tokens   (2-4 get_screenshot calls)
Phase 6: ~300 tokens   (2-3 get_screenshot calls)
Phase 7: ~0 tokens     (no MCP calls)
─────────────────────────────────────────────────
Total:   ~11,000 tokens (typical conversion)
```

### Optimization Strategies

1. **Batch Requests**: Group related nodes in single calls when possible
2. **Cache Responses**: Store `get_metadata` results for reuse
3. **Selective Extraction**: Only call `get_design_context` for top-level sections
4. **Screenshot Efficiency**: Use appropriate scale (1x for comparison, 2x for assets)

---

## Error Handling

### Common Errors

| Error Code | Cause | Recovery |
|------------|-------|----------|
| `INVALID_FILE_KEY` | Wrong file key format | Verify URL parsing |
| `NODE_NOT_FOUND` | Deleted or moved node | Refresh metadata |
| `ACCESS_DENIED` | No file permission | Request access |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Implement backoff |
| `TIMEOUT` | Large file/node | Reduce scope |

### Retry Strategy

```typescript
async function callWithRetry<T>(
  fn: () => Promise<T>,
  maxRetries = 3
): Promise<T> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (error.code === "RATE_LIMIT_EXCEEDED" && attempt < maxRetries) {
        await sleep(1000 * attempt); // Exponential backoff
        continue;
      }
      throw error;
    }
  }
  throw new Error("Max retries exceeded");
}
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│                  FIGMA MCP QUICK REFERENCE                  │
├─────────────────────────────────────────────────────────────┤
│ get_metadata(fileKey, [nodeId], [depth])                    │
│   → File structure, components, styles                      │
│                                                             │
│ get_design_context(fileKey, nodeId, [format])               │
│   → React + Tailwind code                                   │
│                                                             │
│ get_variable_defs(fileKey, [collectionId])                  │
│   → Colors, typography, spacing tokens                      │
│                                                             │
│ get_screenshot(nodeId, [scale], [format])                   │
│   → Base64 image (png/jpg/svg)                              │
│                                                             │
│ get_code_connect_map(fileKey)                               │
│   → Existing Figma-to-code mappings                         │
│                                                             │
│ add_code_connect_map(fileKey, mapping)                      │
│   → Register new component mapping                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-01 | Initial reference document |
