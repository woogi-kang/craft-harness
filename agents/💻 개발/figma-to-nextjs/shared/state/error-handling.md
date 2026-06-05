---
name: "Error Handling Framework"
description: "Error classification and recovery strategies"
---

# Error Handling Framework

> Comprehensive error classification, recovery strategies, and graceful degradation for Figma-to-Next.js conversion

---

## Error Taxonomy

### Category 1: Recoverable Errors (Auto-Recovery Possible)

| Error Code | Name | Cause | Auto-Recovery | User Action |
|------------|------|-------|---------------|-------------|
| `ERR_RATE_LIMIT` | Rate Limit Exceeded | MCP quota reached | Wait & retry | Upgrade plan or wait |
| `ERR_NETWORK_TIMEOUT` | Network Timeout | Connection issue | Retry 3x with backoff | Check network |
| `ERR_MCP_UNAVAILABLE` | MCP Service Down | Service outage | Retry after delay | Wait for service |
| `ERR_FIGMA_THROTTLE` | Figma API Throttle | Too many requests | Exponential backoff | Reduce request rate |

### Category 2: Partial Failure Errors (Continue with Degradation)

| Error Code | Name | Cause | Partial Result | Recovery |
|------------|------|-------|----------------|----------|
| `ERR_COMPONENT_PARSE` | Component Parse Error | Invalid Figma node | Skip component | Manual fix |
| `ERR_TOKEN_INCOMPLETE` | Token Extraction Incomplete | Missing variables | Use defaults | Define missing tokens |
| `ERR_ASSET_DOWNLOAD` | Asset Download Failed | Image unavailable | Use placeholder | Retry or replace |
| `ERR_MAPPING_AMBIGUOUS` | Mapping Ambiguous | Multiple matches | Use best guess | Manual verification |

### Category 3: Fatal Errors (Cannot Continue)

| Error Code | Name | Cause | Action Required |
|------------|------|-------|-----------------|
| `ERR_INVALID_URL` | Invalid Figma URL | Malformed URL | Re-enter URL |
| `ERR_ACCESS_DENIED` | Figma Access Denied | No permission | Update sharing settings |
| `ERR_PROJECT_INVALID` | Project Not Supported | Wrong project type | Use different agent |
| `ERR_CONFIG_MISSING` | Configuration Missing | Required config absent | Run setup first |

---

## Error Response Structure

```typescript
interface ConversionError {
  code: string;
  category: 'recoverable' | 'partial' | 'fatal';
  message: string;
  phase: number;
  step: string;

  // Context
  context: {
    nodeId?: string;
    componentName?: string;
    filePath?: string;
  };

  // Recovery info
  recovery: {
    canRetry: boolean;
    retryAfter?: number; // milliseconds
    fallbackAvailable: boolean;
    fallbackDescription?: string;
    userActionRequired?: string;
  };

  // Debugging
  debug: {
    timestamp: string;
    sessionId: string;
    stackTrace?: string;
  };
}
```

---

## Phase-Level Error Handling

### Phase 0: Project Scan

```typescript
const phase0Errors = {
  'ERR_PROJECT_INVALID': {
    condition: 'No package.json or not Next.js project',
    action: 'fatal',
    message: 'This project is not a valid Next.js project. Please ensure package.json exists and includes Next.js as a dependency.',
  },
  'ERR_CONFIG_MISSING': {
    condition: 'No tailwind.config found',
    action: 'partial',
    fallback: 'Will create default Tailwind configuration',
  },
};
```

### Phase 1: Design Scan

```typescript
const phase1Errors = {
  'ERR_ACCESS_DENIED': {
    condition: 'Figma file not accessible',
    action: 'fatal',
    message: 'Cannot access Figma file. Please ensure the file is shared with "Anyone with the link can view".',
  },
  'ERR_NODE_NOT_FOUND': {
    condition: 'Specified node ID does not exist',
    action: 'partial',
    fallback: 'Will scan entire file instead of specific node',
  },
};
```

### Phase 2: Token Extract

```typescript
const phase2Errors = {
  'ERR_TOKEN_INCOMPLETE': {
    condition: 'Some token types not found',
    action: 'partial',
    fallback: 'Will use Tailwind defaults for missing tokens',
    report: ['missing_tokens'],
  },
  'ERR_VARIABLE_PARSE': {
    condition: 'Cannot parse Figma variable',
    action: 'partial',
    fallback: 'Will skip variable and log warning',
  },
};
```

### Phase 3: Component Mapping

```typescript
const phase3Errors = {
  'ERR_MAPPING_AMBIGUOUS': {
    condition: 'Multiple possible component matches',
    action: 'partial',
    fallback: 'Will use highest confidence match',
    report: ['ambiguous_mappings'],
  },
  'ERR_NO_MAPPING': {
    condition: 'No existing component matches',
    action: 'partial',
    fallback: 'Will create new custom component',
  },
};
```

### Phase 4: Code Generate

```typescript
const phase4Errors = {
  'ERR_COMPONENT_PARSE': {
    condition: 'Cannot generate component from Figma node',
    action: 'partial',
    fallback: 'Will skip component and continue',
    checkpoint: true,
  },
  'ERR_TYPE_INFERENCE': {
    condition: 'Cannot infer TypeScript types',
    action: 'partial',
    fallback: 'Will use generic types with TODO comment',
  },
  'ERR_RATE_LIMIT': {
    condition: 'MCP rate limit reached',
    action: 'recoverable',
    checkpoint: true,
    resumable: true,
  },
};
```

### Phase 5: Asset Process

```typescript
const phase5Errors = {
  'ERR_ASSET_DOWNLOAD': {
    condition: 'Cannot download asset from Figma',
    action: 'partial',
    fallback: 'Will use placeholder image',
    report: ['failed_assets'],
  },
  'ERR_ASSET_OPTIMIZE': {
    condition: 'Cannot optimize image',
    action: 'partial',
    fallback: 'Will use original image',
  },
};
```

### Phase 6: Pixel-Perfect

```typescript
const phase6Errors = {
  'ERR_SCREENSHOT_FAILED': {
    condition: 'Cannot capture screenshot',
    action: 'partial',
    fallback: 'Will skip visual verification',
    report: ['skipped_verifications'],
  },
  'ERR_DIFF_THRESHOLD': {
    condition: 'Visual difference exceeds threshold',
    action: 'partial',
    fallback: 'Will report differences but continue',
    report: ['visual_differences'],
  },
};
```

### Phase 7: Responsive

```typescript
const phase7Errors = {
  'ERR_BREAKPOINT_FAILED': {
    condition: 'Cannot verify at breakpoint',
    action: 'partial',
    fallback: 'Will skip breakpoint and continue',
    report: ['skipped_breakpoints'],
  },
};
```

---

## Recovery Strategies

### Retry with Exponential Backoff

```typescript
async function retryWithBackoff<T>(
  operation: () => Promise<T>,
  options: {
    maxRetries: number;
    initialDelayMs: number;
    maxDelayMs: number;
    retryableErrors: string[];
  }
): Promise<T> {
  let lastError: ConversionError;
  let delay = options.initialDelayMs;

  for (let attempt = 0; attempt < options.maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error as ConversionError;

      // Check if error is retryable
      if (!options.retryableErrors.includes(lastError.code)) {
        throw error;
      }

      // Log retry attempt
      console.log(`Retry ${attempt + 1}/${options.maxRetries} after ${delay}ms`);

      // Wait before retry
      await sleep(delay);

      // Exponential backoff with jitter
      delay = Math.min(delay * 2 + Math.random() * 100, options.maxDelayMs);
    }
  }

  throw lastError;
}

// Usage
const result = await retryWithBackoff(
  () => mcpCall('get_design_context', { nodeId }),
  {
    maxRetries: 3,
    initialDelayMs: 1000,
    maxDelayMs: 10000,
    retryableErrors: ['ERR_NETWORK_TIMEOUT', 'ERR_MCP_UNAVAILABLE'],
  }
);
```

### Graceful Degradation

```typescript
async function executeWithFallback<T>(
  primary: () => Promise<T>,
  fallback: () => Promise<T>,
  errorCodes: string[]
): Promise<{ result: T; usedFallback: boolean }> {
  try {
    const result = await primary();
    return { result, usedFallback: false };
  } catch (error) {
    const convError = error as ConversionError;

    if (errorCodes.includes(convError.code)) {
      console.warn(`Using fallback due to: ${convError.message}`);
      const result = await fallback();
      return { result, usedFallback: true };
    }

    throw error;
  }
}

// Usage
const { result: tokens, usedFallback } = await executeWithFallback(
  () => extractTokensFromFigma(nodeId),
  () => getDefaultTailwindTokens(),
  ['ERR_TOKEN_INCOMPLETE', 'ERR_RATE_LIMIT']
);
```

### Checkpoint and Resume

```typescript
async function executeWithCheckpoint<T>(
  state: ConversionState,
  phase: number,
  steps: Array<{ name: string; execute: () => Promise<Partial<T>> }>
): Promise<T> {
  let result = {} as T;
  let startStep = 0;

  // Resume from checkpoint if available
  if (state.checkpoint.phase === phase && state.checkpoint.data) {
    result = state.checkpoint.data as T;
    startStep = steps.findIndex(s => s.name === state.checkpoint.step) + 1;
    console.log(`Resuming from step: ${state.checkpoint.step}`);
  }

  for (let i = startStep; i < steps.length; i++) {
    const step = steps[i];

    try {
      const stepResult = await step.execute();
      result = { ...result, ...stepResult };

      // Save checkpoint after each step
      saveCheckpoint(state, phase, step.name, result);

    } catch (error) {
      const convError = error as ConversionError;

      if (convError.recovery?.canRetry) {
        // Save checkpoint for retry
        saveCheckpoint(state, phase, step.name, result);
      }

      throw error;
    }
  }

  return result;
}
```

---

## Error Reporting

### Error Summary Template

```markdown
## Conversion Error Report

### Error Details
- **Code**: ERR_COMPONENT_PARSE
- **Phase**: 4 (Code Generate)
- **Component**: HeroSection
- **Time**: 2026-01-22T10:45:30Z

### Context
- Figma Node: 123:456
- Attempted Operation: Generate TSX from Figma context

### Root Cause
The Figma node contains an unsupported blend mode "LUMINOSITY" which cannot be mapped to CSS.

### Recovery Action
- **Automatic**: Skipped blend mode property
- **Manual Required**: Review generated component and add blend mode manually if needed

### Impact
- Component generated with incomplete styling
- Visual difference may occur

### Related Files
- Generated: `src/components/sections/hero-section.tsx`
- Verification: Will be checked in Phase 6
```

### Aggregated Error Report

```markdown
## Conversion Summary

### Overall Status: Completed with Warnings

### Error Summary

| Category | Count | Auto-Recovered | Manual Required |
|----------|-------|----------------|-----------------|
| Recoverable | 2 | 2 | 0 |
| Partial | 5 | 4 | 1 |
| Fatal | 0 | - | - |

### Recoverable Errors (Auto-Handled)
1. Rate limit reached at Phase 4 - Waited 60s and resumed
2. Network timeout at Phase 5 - Retried 2x successfully

### Partial Failures (Fallback Used)
1. Token extraction incomplete - Used Tailwind defaults for `shadow`
2. Component mapping ambiguous (3 cases) - Used highest confidence match
3. Asset download failed (1 image) - Used placeholder

### Manual Review Required
1. **HeroSection blend mode** - Review `src/components/sections/hero-section.tsx:45`

### Recommendations
- [ ] Review ambiguous component mappings in verification report
- [ ] Replace placeholder image at `public/images/placeholder-hero.png`
- [ ] Verify blend mode rendering in browser
```

---

## User Notification Patterns

### Non-Blocking Warning

```
⚠️ Warning: Token "shadow/heavy" not found in Figma variables
   Using Tailwind default: shadow-2xl
   Continuing conversion...
```

### Checkpoint Notification

```
💾 Checkpoint saved at Phase 4, Step 3 (6/10 components)
   Session ID: abc-123
   Resume command: "Continue Figma conversion abc-123"
```

### Fatal Error Notification

```
❌ Error: Cannot access Figma file

The Figma file is not accessible. This could be because:
1. The file is not shared publicly
2. The link has expired
3. You don't have permission to view this file

To fix:
1. Open the Figma file
2. Click "Share" button
3. Set "Anyone with the link" to "can view"
4. Try the conversion again with the new link
```

### Recovery Success Notification

```
✅ Recovered from rate limit
   Waited: 60 seconds
   Resuming from: Phase 4, Component 7/10
   Remaining MCP calls: 5
```

---

## Configuration

### Error Handling Settings

```yaml
# .moai/config/figma-conversion.yaml
error_handling:
  # Retry settings
  retry:
    max_attempts: 3
    initial_delay_ms: 1000
    max_delay_ms: 30000
    retryable_errors:
      - ERR_NETWORK_TIMEOUT
      - ERR_MCP_UNAVAILABLE
      - ERR_FIGMA_THROTTLE

  # Fallback settings
  fallback:
    use_defaults_for_missing_tokens: true
    skip_failed_components: true
    use_placeholder_for_failed_assets: true

  # Checkpoint settings
  checkpoint:
    enabled: true
    save_after_each_component: true
    save_on_error: true

  # Notification settings
  notifications:
    show_warnings: true
    show_recovery_actions: true
    verbose_errors: false
```
