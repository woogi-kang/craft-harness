# OSS Launch Checklist

- [x] `LICENSE` is Apache-2.0.
- [x] `CONTRIBUTING.md` includes DCO sign-off instructions.
- [x] `SECURITY.md` defines private vulnerability reporting.
- [x] `craft doctor` passes locally.
- [x] `craft validate` passes locally.
- [x] Catalog generation passes locally.
- [x] Markdown link check passes locally.
- [x] `git ls-files` contains no private workspace files locally.
- [x] No `workspace/`, `work-social/`, logs, local settings, memory, sessions, or checkpoints are tracked locally.
- [x] GitHub Actions pass on a clean checkout.
- [x] Dependabot configuration is present.
- [x] GitHub vulnerability alerts and automated security fixes are enabled.
- [ ] Branch protection is enabled for `main`.

Note: branch protection currently requires GitHub Pro while the repo remains
private, or it can be enabled after switching the repository to public.
