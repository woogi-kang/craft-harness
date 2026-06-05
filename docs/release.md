# Release Process

This checklist is for Craft Harness maintainers. A release touches two
repositories:

- `woogi-kang/craft-harness`: source, tag, GitHub Release, curl installer target
- `woogi-kang/homebrew-tap`: Homebrew formula for `brew install woogi-kang/tap/craft-harness`

## 1. Prepare the Source Repo

Start from a clean `main` branch.

```bash
cd path/to/craft-harness
git status --short
git pull --ff-only origin main
```

Update version references:

- `pyproject.toml`
- `CHANGELOG.md`
- release notes draft
- any README or docs examples that mention the version

For patch releases, keep the public scope explicit. Do not add optional domain
packs unless their license, secret, and quality reviews are complete.

## 2. Run Pre-release Checks

```bash
craft doctor
craft validate
craft catalog --format json --output /tmp/craft-catalog.json
craft catalog --format md --output /tmp/craft-skill-catalog.md
craft orchestrate examples/plan.json --dry-run
python3 scripts/validate-plan.py examples/plan.json
python3 scripts/check-markdown-links.py .
python3 -m compileall -q src scripts
```

Check the public file boundary:

```bash
git ls-files | rg '(__pycache__|\.pyc$|egg-info|\.env|secret|backup|settings\.local|workspace|work-social|\.codex|\.orchestration)' || true
```

Run installer checks:

```bash
rm -rf /tmp/craft-harness-install /tmp/craft-harness-target
bash scripts/install.sh --local . --prefix /tmp/craft-harness-install
mkdir -p /tmp/craft-harness-target
cd /tmp/craft-harness-target
git init
/tmp/craft-harness-install/bin/craft orchestrate examples/plan.json --dry-run
```

## 3. Commit and Wait for CI

```bash
cd path/to/craft-harness
git add pyproject.toml CHANGELOG.md README.md README.ko.md docs
git commit -s -m "Prepare vX.Y.Z release"
git push origin main
gh run watch "$(gh run list --limit 1 --json databaseId --jq '.[0].databaseId')" --exit-status
```

Only tag after CI passes.

## 4. Tag and Create GitHub Release

```bash
VERSION=vX.Y.Z
git tag -a "$VERSION" -m "Craft Harness $VERSION"
git push origin "$VERSION"
gh release create "$VERSION" \
  --title "Craft Harness $VERSION" \
  --notes-file /tmp/craft-harness-release-notes.md
```

The release notes should include:

- highlights
- compatibility notes
- install commands
- validation status
- known limitations

## 5. Update Homebrew Tap

Calculate the release tarball checksum:

```bash
VERSION=vX.Y.Z
curl -fsSL "https://github.com/woogi-kang/craft-harness/archive/refs/tags/$VERSION.tar.gz" \
  -o "/tmp/craft-harness-$VERSION.tar.gz"
shasum -a 256 "/tmp/craft-harness-$VERSION.tar.gz"
```

Update `Formula/craft-harness.rb` in the `woogi-kang/homebrew-tap` checkout:

- `url`
- `sha256`

Then test the formula:

```bash
cd path/to/homebrew-tap
ruby -c Formula/craft-harness.rb
git diff -- Formula/craft-harness.rb
git add Formula/craft-harness.rb
git commit -s -m "Update craft-harness to vX.Y.Z"
git push

HOMEBREW_NO_AUTO_UPDATE=1 brew install woogi-kang/tap/craft-harness
/opt/homebrew/bin/craft doctor
HOMEBREW_NO_AUTO_UPDATE=1 brew test craft-harness
brew uninstall craft-harness
brew untap woogi-kang/tap
brew developer off || true
```

## 6. Verify Public Install Paths

Verify curl install from the public tag:

```bash
VERSION=vX.Y.Z
rm -rf /tmp/craft-curl-install
curl -fsSL https://raw.githubusercontent.com/woogi-kang/craft-harness/main/scripts/install.sh \
  | CRAFT_HARNESS_REF="$VERSION" CRAFT_HARNESS_PREFIX=/tmp/craft-curl-install bash
/tmp/craft-curl-install/bin/craft doctor
rm -rf /tmp/craft-curl-install
```

Verify Homebrew install:

```bash
brew install woogi-kang/tap/craft-harness
craft doctor
brew uninstall craft-harness
brew untap woogi-kang/tap
```

## 7. Post-release Notes

After release:

- confirm GitHub Release is not draft or prerelease unless intended
- confirm README install commands still match the tap
- create or update the next milestone
- open follow-up issues for known limitations
- post a short announcement with release link and install commands

For urgent release fixes, keep the scope narrow and cut a patch release instead
of rewriting the existing tag.
