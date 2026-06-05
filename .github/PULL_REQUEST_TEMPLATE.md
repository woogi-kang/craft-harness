## Summary

- 

## Verification

- [ ] `craft doctor`
- [ ] `craft validate`
- [ ] `craft catalog --format json --output /tmp/craft-catalog.json`
- [ ] `craft orchestrate examples/plan.json --dry-run`
- [ ] `python scripts/check-markdown-links.py .`

## Public Repo Safety

- [ ] No local settings, logs, memory, sessions, checkpoints, workspaces, or secrets.
- [ ] Skill frontmatter is present when adding or editing skills.
- [ ] Optional domain packs were not added to core without an issue.
