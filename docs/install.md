# Installation

Craft Harness installs a full harness directory, not only a Python entry point.
The CLI needs the bundled `agents/`, `skills/`, `commands/`, `templates/`, and
adapter files at runtime.

## curl

Install the latest `main` branch from the public repository with:

```bash
curl -fsSL https://raw.githubusercontent.com/woogi-kang/craft-harness/main/scripts/install.sh | bash
```

Install a specific ref:

```bash
curl -fsSL https://raw.githubusercontent.com/woogi-kang/craft-harness/main/scripts/install.sh \
  | CRAFT_HARNESS_REF=v0.1.0 bash
```

Use a custom prefix:

```bash
curl -fsSL https://raw.githubusercontent.com/woogi-kang/craft-harness/main/scripts/install.sh \
  | CRAFT_HARNESS_PREFIX="$HOME/.craft" bash
```

The default install root is `~/.local/share/craft-harness`, and the default
executable link is `~/.local/bin/craft`.

For orchestration commands, run `craft` inside the git repository you want the
workers to operate on. Bundled examples such as `examples/plan.json` are
resolved from the installed harness when they are not present in the current
project.

## Homebrew

```bash
brew install woogi-kang/tap/craft-harness
```

The Homebrew formula lives in the dedicated
[`woogi-kang/homebrew-tap`](https://github.com/woogi-kang/homebrew-tap)
repository and points to a tagged Craft Harness release.

## Source Checkout

For development:

```bash
git clone https://github.com/woogi-kang/craft-harness.git
cd craft-harness
python3 -m pip install -e .
craft doctor
```

For local installer testing from a checkout:

```bash
bash scripts/install.sh --local . --prefix /tmp/craft-harness-install
/tmp/craft-harness-install/bin/craft doctor
```

## Uninstall

For the default curl install:

```bash
rm -rf ~/.local/share/craft-harness
rm -f ~/.local/bin/craft
```

For Homebrew:

```bash
brew uninstall craft-harness
brew untap woogi-kang/tap
```
