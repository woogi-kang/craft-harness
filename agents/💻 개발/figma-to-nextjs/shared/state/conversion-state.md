---
name: "Conversion State Management"
description: "Session persistence and checkpointing for Figma conversion"
---

# Conversion State Management

> Session persistence, checkpointing, and resume capability for Figma-to-Next.js conversion

---

## Overview

This module provides state persistence to handle:
- Rate limit interruptions
- Session timeouts
- Partial failures
- Resume capability

---

## State Schema

```typescript
interface ConversionState {
  // Session metadata
  session_id: string;
  created_at: string;
  updated_at: string;

  // Input context
  figma: {
    url: string;
    file_key: string;
    node_ids: string[];
  };

  // Project context
  project: {
    path: string;
    framework: 'nextjs' | 'vue' | 'svelte';
    ui_library: 'shadcn' | 'radix' | 'headless' | 'custom';
  };

  // Progress tracking
  pipeline: {
    current_phase: number;
    phase_status: Record<number, PhaseStatus>;
  };

  // Phase artifacts (file references)
  artifacts: PhaseArtifacts;

  // MCP rate limit tracking
  mcp: {
    calls_made: number;
    calls_remaining: number;
    reset_at: string;
  };

  // Checkpoint for resume
  checkpoint: {
    phase: number;
    step: string;
    data: unknown;
    resumable: boolean;
  };
}

type PhaseStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped';

interface PhaseArtifacts {
  phase_0?: { project_analysis: string };
  phase_1?: { design_scan: string; node_map: string };
  phase_2?: { tokens: string; tailwind_config: string; css_variables: string };
  phase_3?: { component_mapping: string; dependency_graph: string };
  phase_4?: { components: string[]; types: string };
  phase_5?: { assets: string[]; optimized_images: string[] };
  phase_6?: { verification_report: string; diff_images: string[] };
  phase_7?: { responsive_report: string; final_report: string };
}
```

---

## Storage Location

```
.moai/figma-conversion/
├── sessions/
│   └── {session_id}/
│       ├── state.json              # Main state file
│       ├── artifacts/
│       │   ├── phase-0/
│       │   ├── phase-1/
│       │   └── ...
│       └── cache/
│           ├── mcp-responses/      # Cached MCP responses
│           └── screenshots/
└── active-session.txt              # Points to current session
```

---

## State Operations

### Initialize Session

```typescript
function initializeSession(figmaUrl: string, projectPath: string): ConversionState {
  const session: ConversionState = {
    session_id: crypto.randomUUID(),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),

    figma: {
      url: figmaUrl,
      file_key: extractFileKey(figmaUrl),
      node_ids: extractNodeIds(figmaUrl),
    },

    project: {
      path: projectPath,
      framework: 'nextjs',
      ui_library: 'shadcn',
    },

    pipeline: {
      current_phase: 0,
      phase_status: {
        0: 'pending',
        1: 'pending',
        2: 'pending',
        3: 'pending',
        4: 'pending',
        5: 'pending',
        6: 'pending',
        7: 'pending',
      },
    },

    artifacts: {},

    mcp: {
      calls_made: 0,
      calls_remaining: -1, // Unknown until first call
      reset_at: '',
    },

    checkpoint: {
      phase: 0,
      step: 'init',
      data: null,
      resumable: true,
    },
  };

  return session;
}
```

### Save Checkpoint

```typescript
function saveCheckpoint(
  state: ConversionState,
  phase: number,
  step: string,
  data: unknown
): void {
  state.checkpoint = {
    phase,
    step,
    data,
    resumable: true,
  };
  state.updated_at = new Date().toISOString();

  // Persist to file
  const statePath = `.moai/figma-conversion/sessions/${state.session_id}/state.json`;
  writeFile(statePath, JSON.stringify(state, null, 2));
}
```

### Resume Session

```typescript
function resumeSession(sessionId: string): ConversionState | null {
  const statePath = `.moai/figma-conversion/sessions/${sessionId}/state.json`;

  if (!fileExists(statePath)) {
    return null;
  }

  const state = JSON.parse(readFile(statePath)) as ConversionState;

  // Validate checkpoint is resumable
  if (!state.checkpoint.resumable) {
    console.warn('Checkpoint is not resumable, starting from last completed phase');
    state.checkpoint.phase = findLastCompletedPhase(state);
  }

  return state;
}
```

### Update Phase Status

```typescript
function updatePhaseStatus(
  state: ConversionState,
  phase: number,
  status: PhaseStatus,
  artifacts?: Partial<PhaseArtifacts>
): void {
  state.pipeline.phase_status[phase] = status;
  state.pipeline.current_phase = phase;

  if (artifacts) {
    state.artifacts = { ...state.artifacts, ...artifacts };
  }

  if (status === 'completed') {
    saveCheckpoint(state, phase + 1, 'init', null);
  } else if (status === 'failed') {
    state.checkpoint.resumable = true;
  }

  state.updated_at = new Date().toISOString();
}
```

---

## Rate Limit Handling

### Track MCP Calls

```typescript
function trackMcpCall(state: ConversionState, response: McpResponse): void {
  state.mcp.calls_made++;

  // Extract rate limit info from response headers if available
  if (response.rateLimit) {
    state.mcp.calls_remaining = response.rateLimit.remaining;
    state.mcp.reset_at = response.rateLimit.resetAt;
  }

  // Auto-checkpoint when rate limit is low
  if (state.mcp.calls_remaining <= 2) {
    console.warn('Rate limit nearly exhausted, saving checkpoint');
    saveCheckpoint(
      state,
      state.pipeline.current_phase,
      'rate_limit_pause',
      { reason: 'rate_limit_approaching' }
    );
  }
}
```

### Rate Limit Recovery

```markdown
## Rate Limit Recovery Flow

1. Rate limit detected
2. Current progress saved to checkpoint
3. User notified with:
   - Completed phases
   - Remaining work
   - Estimated reset time
4. Session marked as resumable
5. On resume:
   - Load checkpoint
   - Verify rate limit reset
   - Continue from saved state
```

---

## Session Recovery Commands

### List Sessions

```bash
# Show all conversion sessions
ls -la .moai/figma-conversion/sessions/

# Show active session
cat .moai/figma-conversion/active-session.txt
```

### Resume Session

```markdown
## Resume Command

"Resume the Figma conversion session {session_id}"

or

"Continue the last Figma conversion"
```

### Cleanup Old Sessions

```typescript
function cleanupOldSessions(maxAgeDays: number = 7): void {
  const sessionsPath = '.moai/figma-conversion/sessions/';
  const sessions = listDirectories(sessionsPath);

  for (const session of sessions) {
    const state = loadState(session);
    const age = daysSince(state.updated_at);

    if (age > maxAgeDays && state.pipeline.current_phase === 7) {
      // Only cleanup completed sessions older than maxAge
      removeDirectory(`${sessionsPath}/${session}`);
    }
  }
}
```

---

## Integration with Pipeline

### Phase Execution Wrapper

```typescript
async function executePhaseWithState(
  state: ConversionState,
  phase: number,
  executor: PhaseExecutor
): Promise<PhaseResult> {
  // Update status to running
  updatePhaseStatus(state, phase, 'running');

  try {
    // Check for existing checkpoint data
    const resumeData = state.checkpoint.phase === phase
      ? state.checkpoint.data
      : null;

    // Execute phase
    const result = await executor.execute(state, resumeData);

    // Save artifacts
    updatePhaseStatus(state, phase, 'completed', {
      [`phase_${phase}`]: result.artifacts,
    });

    return result;

  } catch (error) {
    // Handle errors with checkpoint
    if (isRateLimitError(error)) {
      saveCheckpoint(state, phase, 'rate_limit', {
        lastProgress: executor.getProgress(),
        error: error.message,
      });
      throw new ResumableError('Rate limit reached', state.session_id);
    }

    updatePhaseStatus(state, phase, 'failed');
    throw error;
  }
}
```

---

## User Interface

### Progress Display

```markdown
## Conversion Progress

Session: abc-123-def
Started: 2026-01-22 10:30:00

| Phase | Status | Artifacts |
|-------|--------|-----------|
| 0. Project Scan | ✅ Completed | project_analysis.json |
| 1. Design Scan | ✅ Completed | design_scan.json, node_map.json |
| 2. Token Extract | ✅ Completed | tokens.json, variables.css |
| 3. Component Map | ✅ Completed | mapping.json |
| 4. Code Generate | 🔄 Running (60%) | 6/10 components |
| 5. Asset Process | ⏳ Pending | - |
| 6. Pixel-Perfect | ⏳ Pending | - |
| 7. Responsive | ⏳ Pending | - |

MCP Calls: 4/6 remaining
Est. Reset: 2026-01-23 00:00:00
```

### Resume Prompt

```markdown
## Session Recovery Available

Found incomplete session from 2026-01-22 10:30:00

- Figma: Landing Page Design
- Progress: Phase 4 (60% complete)
- Last checkpoint: 6 components generated

Options:
1. Resume from checkpoint
2. Start fresh (discard progress)
3. View session details
```

---

## Best Practices

### DO

- Save checkpoint after each component in Phase 4
- Cache MCP responses to avoid duplicate calls
- Track rate limit proactively
- Preserve partial results on failure

### DON'T

- Overwrite state without backup
- Delete sessions with uncommitted work
- Ignore checkpoint data on resume
- Skip validation after resume
