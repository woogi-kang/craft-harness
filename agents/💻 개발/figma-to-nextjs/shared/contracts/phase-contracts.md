---
name: "Phase Contract System"
description: "Phase dependencies, inputs, outputs, and rollback strategies"
---

# Phase Contract System

> Explicit dependencies, inputs, outputs, and rollback strategies for each conversion phase

---

## Overview

Phase Contracts ensure predictable, resumable, and fault-tolerant Figma-to-Next.js conversions. Each phase declares:

1. **Dependencies**: What must be completed before this phase
2. **Inputs**: Required data/artifacts from previous phases
3. **Outputs**: What this phase produces
4. **Validation**: How to verify successful completion
5. **Rollback**: Recovery strategy on failure

---

## Contract Schema

```yaml
---
phase_id: number              # 0-7
phase_name: string            # Human-readable name
description: string           # Brief description

dependencies:
  - phase_id: number          # Required phase
    artifacts: string[]       # Required artifacts from that phase
    validation: string        # Validation function/check

inputs:
  required: string[]          # Must have
  optional: string[]          # Nice to have

outputs:
  artifacts: string[]         # Files/data produced
  state_updates: string[]     # State changes

validation:
  success_criteria: string[]  # What makes this phase "complete"
  quality_gates: string[]     # Optional quality checks

rollback:
  on_failure: string          # Action on failure
  cleanup: string[]           # Files/state to clean up
  can_resume: boolean         # Whether checkpoint resume is supported

mcp_calls:
  estimated: number           # Expected MCP API calls
  tools: string[]             # Which MCP tools are used
---
```

---

## Phase Dependency Graph

```
┌───────────────────────────────────────────────────────────────┐
│                    Phase Dependency Flow                       │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│   Phase 0 ──┬──▶ Phase 1 ──▶ Phase 2 ──▶ Phase 3             │
│  (Project)  │   (Design)    (Token)     (Mapping)             │
│             │                                                 │
│             │                   ┌──────────────────────┐      │
│             │                   ▼                      │      │
│             └──▶ Phase 4 ──▶ Phase 5 ──▶ Phase 6 ──▶ Phase 7 │
│                 (Code)      (Asset)    (Verify)    (Responsive)│
│                                                               │
│   Legend:                                                     │
│   ──▶ Sequential dependency                                   │
│   - - ▶ Optional/parallel dependency                          │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## Contracts by Phase

### Phase 0: Project Scan

```yaml
phase_id: 0
phase_name: "Project Scan"
description: "Analyze Next.js project structure and identify reusable components"

dependencies: []  # No dependencies - entry point

inputs:
  required:
    - project_path
  optional:
    - existing_config

outputs:
  artifacts:
    - project_analysis.json
    - reusable_components.json
  state_updates:
    - project.framework
    - project.ui_library
    - project.styling

validation:
  success_criteria:
    - package.json exists and contains Next.js
    - Project type identified (App Router / Pages Router)
    - Styling system identified
  quality_gates:
    - TypeScript strict mode recommended

rollback:
  on_failure: abort_conversion
  cleanup: []
  can_resume: false

mcp_calls:
  estimated: 0
  tools: []  # Uses local file system only
```

### Phase 1: Design Scan

```yaml
phase_id: 1
phase_name: "Design Scan"
description: "Scan Figma design structure and create layer map"

dependencies:
  - phase_id: 0
    artifacts: [project_analysis.json]
    validation: project_is_nextjs

inputs:
  required:
    - figma_url
    - project_analysis
  optional:
    - specific_node_ids

outputs:
  artifacts:
    - design_scan.json
    - node_map.json
    - conversion_plan.json
  state_updates:
    - figma.file_key
    - figma.node_ids

validation:
  success_criteria:
    - Figma file accessible
    - Layer structure documented
    - Conversion targets identified
  quality_gates:
    - MCP call budget not exceeded

rollback:
  on_failure: log_error_and_retry
  cleanup:
    - design_scan.json
  can_resume: true

mcp_calls:
  estimated: 2
  tools:
    - get_metadata
    - get_screenshot  # Optional for preview
```

### Phase 2: Token Extract

```yaml
phase_id: 2
phase_name: "Token Extract"
description: "Extract design tokens and generate Tailwind/CSS configuration"

dependencies:
  - phase_id: 1
    artifacts: [design_scan.json]
    validation: design_scan_exists

inputs:
  required:
    - figma_file_key
    - node_ids
  optional:
    - existing_tailwind_config
    - existing_css_variables

outputs:
  artifacts:
    - tokens.json
    - tailwind.config.patch.ts
    - css_variables.css
  state_updates:
    - artifacts.phase_2.tokens
    - artifacts.phase_2.tailwind_config

validation:
  success_criteria:
    - Colors extracted
    - Spacing values mapped
    - Typography defined
  quality_gates:
    - Token naming follows convention
    - CSS variables use RGB format for opacity support

rollback:
  on_failure: use_default_tokens
  cleanup:
    - tokens.json
  can_resume: true

mcp_calls:
  estimated: 1
  tools:
    - get_variable_defs
```

### Phase 3: Component Mapping

```yaml
phase_id: 3
phase_name: "Component Mapping"
description: "Map Figma components to existing codebase components"

dependencies:
  - phase_id: 0
    artifacts: [reusable_components.json]
    validation: components_list_exists
  - phase_id: 1
    artifacts: [node_map.json]
    validation: node_map_exists

inputs:
  required:
    - node_map
    - reusable_components
    - figma_file_key
  optional:
    - existing_code_connect_map

outputs:
  artifacts:
    - component_mapping.json
    - dependency_graph.json
    - creation_plan.json
  state_updates:
    - artifacts.phase_3.component_mapping

validation:
  success_criteria:
    - All Figma components categorized (mapped/mappable/create)
    - Dependency graph complete
    - Creation order determined
  quality_gates:
    - shadcn/ui components prioritized for reuse
    - No circular dependencies

rollback:
  on_failure: log_and_continue_with_defaults
  cleanup:
    - component_mapping.json
  can_resume: true

mcp_calls:
  estimated: 2
  tools:
    - get_code_connect_map
    - add_code_connect_map
```

### Phase 4: Code Generate

```yaml
phase_id: 4
phase_name: "Code Generate"
description: "Generate React/TSX components from Figma design context"

dependencies:
  - phase_id: 2
    artifacts: [tokens.json, tailwind.config.patch.ts]
    validation: tokens_extracted
  - phase_id: 3
    artifacts: [component_mapping.json, creation_plan.json]
    validation: mapping_complete

inputs:
  required:
    - tokens
    - component_mapping
    - creation_plan
    - figma_file_key
  optional:
    - style_preferences
    - custom_templates

outputs:
  artifacts:
    - components/*.tsx
    - types/generated.ts
    - index.ts  # Barrel export
  state_updates:
    - artifacts.phase_4.components
    - checkpoint (per component)

validation:
  success_criteria:
    - All planned components generated
    - TypeScript compiles without errors
    - Imports resolve correctly
  quality_gates:
    - 'use client' only where needed
    - Accessibility attributes present
    - No hardcoded values (use tokens)

rollback:
  on_failure: checkpoint_and_pause
  cleanup:
    - Partially generated components
  can_resume: true

mcp_calls:
  estimated: 3-5
  tools:
    - get_design_context
```

### Phase 5: Asset Process

```yaml
phase_id: 5
phase_name: "Asset Process"
description: "Extract, optimize, and integrate images and icons"

dependencies:
  - phase_id: 4
    artifacts: [components/*.tsx]
    validation: components_generated

inputs:
  required:
    - asset_list (from Phase 1)
    - component_asset_refs
  optional:
    - optimization_settings

outputs:
  artifacts:
    - public/images/*
    - public/icons/*
    - asset_manifest.json
  state_updates:
    - artifacts.phase_5.assets

validation:
  success_criteria:
    - All referenced assets downloaded
    - Images in correct formats
    - Asset paths match component imports
  quality_gates:
    - Images optimized (WebP/AVIF)
    - SVGs cleaned and minified
    - next/image used for raster images

rollback:
  on_failure: use_placeholder_assets
  cleanup:
    - Downloaded assets
  can_resume: true

mcp_calls:
  estimated: 2-4
  tools:
    - get_screenshot
```

### Phase 6: Pixel-Perfect Verification

```yaml
phase_id: 6
phase_name: "Pixel-Perfect Verification"
description: "Compare rendered output with Figma design"

dependencies:
  - phase_id: 4
    artifacts: [components/*.tsx]
    validation: components_generated
  - phase_id: 5
    artifacts: [asset_manifest.json]
    validation: assets_processed

inputs:
  required:
    - generated_components
    - figma_screenshots
  optional:
    - diff_threshold

outputs:
  artifacts:
    - verification_report.json
    - diff_images/*
    - fix_recommendations.md
  state_updates:
    - artifacts.phase_6.verification_report

validation:
  success_criteria:
    - All components rendered
    - Diff calculated for each component
    - Report generated
  quality_gates:
    - Visual diff under threshold (default 5%)
    - Critical elements match exactly

rollback:
  on_failure: generate_partial_report
  cleanup:
    - diff_images/*
  can_resume: true

mcp_calls:
  estimated: 2-3
  tools:
    - get_screenshot
```

### Phase 7: Responsive Validation

```yaml
phase_id: 7
phase_name: "Responsive Validation"
description: "Verify responsive behavior across breakpoints"

dependencies:
  - phase_id: 6
    artifacts: [verification_report.json]
    validation: verification_complete

inputs:
  required:
    - components
    - breakpoints (default: [375, 768, 1024, 1440])
  optional:
    - figma_responsive_variants

outputs:
  artifacts:
    - responsive_report.json
    - final_report.md
    - breakpoint_screenshots/*
  state_updates:
    - artifacts.phase_7.responsive_report
    - pipeline.phase_status[7] = completed

validation:
  success_criteria:
    - All breakpoints tested
    - No layout breaks
    - Final report generated
  quality_gates:
    - Touch targets >= 44px on mobile
    - Text readable at all sizes
    - No horizontal scroll

rollback:
  on_failure: generate_partial_report
  cleanup:
    - breakpoint_screenshots/*
  can_resume: true

mcp_calls:
  estimated: 0
  tools: []  # Uses Playwright/browser testing
```

---

## Contract Validation Functions

```typescript
// lib/phase-contracts.ts

export interface PhaseContract {
  phase_id: number;
  dependencies: PhaseDependency[];
  inputs: { required: string[]; optional: string[] };
  outputs: { artifacts: string[]; state_updates: string[] };
  validation: { success_criteria: string[]; quality_gates: string[] };
  rollback: { on_failure: string; cleanup: string[]; can_resume: boolean };
}

export function validatePhaseEntry(
  contract: PhaseContract,
  state: ConversionState
): { valid: boolean; missing: string[] } {
  const missing: string[] = [];

  // Check dependencies
  for (const dep of contract.dependencies) {
    const depStatus = state.pipeline.phase_status[dep.phase_id];
    if (depStatus !== 'completed') {
      missing.push(`Phase ${dep.phase_id} not completed`);
    }

    for (const artifact of dep.artifacts) {
      if (!artifactExists(state, dep.phase_id, artifact)) {
        missing.push(`Missing artifact: ${artifact} from Phase ${dep.phase_id}`);
      }
    }
  }

  return {
    valid: missing.length === 0,
    missing,
  };
}

export function validatePhaseExit(
  contract: PhaseContract,
  state: ConversionState,
  results: PhaseResult
): { valid: boolean; failures: string[] } {
  const failures: string[] = [];

  // Check success criteria
  for (const criterion of contract.validation.success_criteria) {
    if (!evaluateCriterion(criterion, results)) {
      failures.push(`Failed criterion: ${criterion}`);
    }
  }

  // Check artifacts
  for (const artifact of contract.outputs.artifacts) {
    if (!results.artifacts.includes(artifact)) {
      failures.push(`Missing output artifact: ${artifact}`);
    }
  }

  return {
    valid: failures.length === 0,
    failures,
  };
}
```

---

## Usage

### Before Phase Execution

```typescript
const contract = loadPhaseContract(phaseId);
const entryValidation = validatePhaseEntry(contract, state);

if (!entryValidation.valid) {
  throw new PhaseDependencyError(
    `Cannot start Phase ${phaseId}`,
    entryValidation.missing
  );
}
```

### After Phase Execution

```typescript
const exitValidation = validatePhaseExit(contract, state, results);

if (!exitValidation.valid) {
  if (contract.rollback.can_resume) {
    saveCheckpoint(state, phaseId, 'validation_failed', results);
    throw new ResumablePhaseError(exitValidation.failures);
  } else {
    executeRollback(contract.rollback);
    throw new FatalPhaseError(exitValidation.failures);
  }
}
```

---

## Best Practices

### DO

- Define explicit input/output contracts for each phase
- Use checkpoint-friendly rollback strategies
- Validate dependencies before starting
- Update state immediately after artifact creation

### DON'T

- Skip dependency validation
- Leave partial artifacts on failure
- Ignore quality gates in production
- Assume previous phase success without validation
