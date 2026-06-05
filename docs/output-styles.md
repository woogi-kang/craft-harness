# Output Styles

Output styles make agent responses easier to scan and easier to automate.

## Design Principles

- Human-readable Markdown first.
- Machine-readable artifacts in sidecar files.
- Short final answers, detailed logs in run artifacts.
- Clear PASS/FAIL language for verification.

## Included Styles

- `concise-engineer`: coding and repo work.
- `research-brief`: research and comparisons.
- `qa-report`: verification and bug reporting.
- `executive-summary`: roadmap and planning.

Future versions may support a project-level `harness.yml` field:

```yaml
output_style: concise-engineer
```
