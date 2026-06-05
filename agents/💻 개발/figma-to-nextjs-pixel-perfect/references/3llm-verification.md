# 3LLM Verification Panel

The 3LLM panel is advisory. It improves diagnosis and patch quality, but deterministic gates remain the only pass/fail authority.

## Roles

### Main/Claude Design Reviewer

Focus:

- Figma layer semantics.
- Source spec completeness.
- Auto Layout interpretation.
- Asset and font scope.

Output:

```json
{
  "role": "design",
  "can_block": true,
  "findings": [],
  "fix_recommendations": []
}
```

### Gemini Visual Reviewer

Focus:

- Screenshot-level differences.
- Missing/extra elements.
- Color, spacing, and visual hierarchy mismatches.

Use only after deterministic visual diff fails or when mismatch source is unclear.

### Codex Code Reviewer

Focus:

- TSX/CSS cause analysis.
- Computed style mismatch.
- CSS specificity.
- Tailwind arbitrary value correctness.
- Build, hydration, and render route issues.

Codex should inspect code and propose minimal patches, especially when computed styles differ from `design-spec.json`.

## Escalation Policy

```yaml
run_deterministic_gates:
  when: every_iteration

run_codex:
  when:
    - computed_style_diff_failed
    - build_failed
    - same_diff_repeats_twice

run_gemini:
  when:
    - visual_diff_failed_after_two_fixes
    - pixel_diff_regions_are_unclear

run_full_3llm_panel:
  when:
    - repeated_regression
    - blocker_unclear
    - productionize_refactor_changes_visual_output
```

## Authority

```yaml
llm_panel:
  can_block_completion: true
  can_explain_differences: true
  can_propose_fixes: true
  can_override_diff_failure: false
  can_declare_pass_without_gates: false
```

