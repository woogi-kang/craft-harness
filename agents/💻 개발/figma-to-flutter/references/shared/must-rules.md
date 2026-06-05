# MUST RULES (Shared)

> **Version**: 3.2.0 | **Type**: Shared Reference
> These rules apply to ALL strategies (Pro, Ralph Hybrid, Ralph Pure)

---

## CRITICAL MUST RULES (NON-NEGOTIABLE)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CRITICAL MUST RULES                                   │
│                These rules CANNOT be violated under ANY circumstances    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  MUST #1: FIGMA ASSET DOWNLOAD                                          │
│  ════════════════════════════════════════════════════════════════════   │
│  • ALL images MUST be downloaded from Figma using MCP tools             │
│  • ALL icons MUST be downloaded from Figma (NO icon libraries)          │
│  • NEVER use placeholder images or generate SVG manually                │
│  • NEVER use flutter_icons, font_awesome, cupertino_icons, Icons.*      │
│  • Download command: mcp__figma__get_screenshot for each asset          │
│  • Save to: assets/images/ and assets/icons/                            │
│  • If Figma export fails, STOP and report - do NOT substitute           │
│                                                                          │
│  MUST #2: MINIMUM ACCURACY THRESHOLD                                    │
│  ════════════════════════════════════════════════════════════════════   │
│  • Pro Strategy: 95% minimum                                            │
│  • Ralph Hybrid: 98% minimum (99% target)                               │
│  • Ralph Pure: 98% minimum (self-assessed)                              │
│  • Loop CANNOT exit until threshold is met                              │
│  • MUST verify with actual screenshot comparison                        │
│                                                                          │
│  MUST #3: BUILD & ANALYZE SUCCESS                                       │
│  ════════════════════════════════════════════════════════════════════   │
│  • MUST run `flutter analyze` with ZERO errors                          │
│  • MUST run `flutter build web` before declaring completion             │
│  • Build MUST succeed with ZERO errors                                  │
│  • All imports MUST be valid and resolvable                             │
│  • Dart analysis errors = cannot complete                               │
│  • Lint errors MUST be resolved                                         │
│                                                                          │
│  VIOLATION = IMMEDIATE FAILURE                                          │
│  ─────────────────────────────────────────────────────────────────────  │
│  Breaking ANY of these rules means the conversion is FAILED,            │
│  regardless of visual appearance or score calculations.                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Asset Download Workflow

```bash
# 1. Get design context for asset inventory
mcp__figma__get_design_context(nodeId: "xxx")

# 2. Download each image/icon
mcp__figma__get_screenshot(nodeId: "icon-xxx", format: "png", scale: 3)

# 3. Save to appropriate directory
assets/
├── images/
│   ├── hero-image.png
│   └── background.png
└── icons/
    ├── icon-home.png
    ├── icon-settings.png
    └── icon-profile.png
```

---

## Build Verification Checklist

```bash
# Pre-completion verification
flutter analyze         # MUST be zero errors
flutter build web       # MUST succeed
flutter test            # MUST pass (if tests exist)
```
