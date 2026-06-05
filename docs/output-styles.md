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

## Current Use

Claude adapter guidance defaults to `output-styles/concise-engineer.md`.
For other runtimes, copy the body of the desired style into the target project's
runtime guidance file:

```bash
sed -n '1,160p' output-styles/qa-report.md
```

Then paste the relevant response contract into `AGENTS.md`, `GEMINI.md`, or the
runtime-specific instruction file.

## Planned Native Config

Future versions may support a project-level `harness.yml` field and
`craft output-styles install`:

```yaml
output_style: concise-engineer
```
