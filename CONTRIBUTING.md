# Contributing

Thanks for contributing to Craft Harness.

## Development Setup

```bash
python3 -m pip install -e .
craft doctor
craft validate
craft catalog --format json --output /tmp/craft-catalog.json
craft orchestrate examples/plan.json --dry-run
```

## Contribution Rules

- Keep the public repo free of personal projects, logs, secrets, local settings,
  and generated run state.
- Add or update tests when changing CLI behavior.
- Keep skill changes scoped and include frontmatter.
- Do not add optional domain packs to core without a roadmap issue.

## Releases

Maintainers should follow [Release Process](docs/release.md) before tagging a
new version or updating the Homebrew tap.

## DCO

Contributions are accepted under the Developer Certificate of Origin.

Sign off each commit:

```bash
git commit -s -m "your change"
```

By signing off, you certify that you have the right to submit the contribution
under the Apache-2.0 license.
