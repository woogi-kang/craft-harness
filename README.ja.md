<p align="center">
  <img src="docs/assets/craft-harness-banner.png" alt="Craft Harness banner">
</p>

<h1 align="center">Craft Harness</h1>

<p align="center">
  複数の AI コーディングエージェントを使うチームのための、移植可能な
  エージェントパック、ランタイムアダプター、オーケストレーション契約です。
</p>

<p align="center">
  <a href="README.md">English</a> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.zh.md">中文</a>
</p>

<p align="center">
  <a href="https://github.com/woogi-kang/craft-harness/actions/workflows/ci.yml"><img src="https://github.com/woogi-kang/craft-harness/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/woogi-kang/craft-harness/releases"><img src="https://img.shields.io/github/v/release/woogi-kang/craft-harness?sort=semver" alt="Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/woogi-kang/craft-harness" alt="License"></a>
  <a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python 3.11+"></a>
  <a href="https://github.com/woogi-kang/homebrew-tap"><img src="https://img.shields.io/badge/homebrew-woogi--kang%2Ftap-orange" alt="Homebrew tap"></a>
</p>

<p align="center">
  <a href="docs/install.md">Installation</a> ·
  <a href="docs/architecture.md">Architecture</a> ·
  <a href="docs/skill-catalog.md">Skill Catalog</a> ·
  <a href="docs/spec-contract.md">Plan Contract</a>
</p>

> This Japanese README is a localized quick guide. The English
> [README.md](README.md) remains the canonical reference for the full project
> documentation.

## Craft Harness とは

Craft Harness は単体のコーディングエージェントではありません。Claude、Codex、
Gemini、OpenCode、OpenHands-style workflows の周辺で使うハーネスレイヤーです。

- 再利用可能な `agents/`、`skills/`、`commands/`
- ランタイム別の guidance adapter
- git worktree と tmux による worker DAG
- success criteria、eval type、handoff artifact
- 公開リポジトリ向けの validation と secret scan

## 向いているユーザー

- 複数の AI コーディングツールを同じコードベースで使うチーム
- プロンプトを毎回作り直さず、役割とスキルを pack として再利用したい開発者
- QA、レビュー、acceptance criteria を agent workflow に組み込みたいチーム
- git worktree で並列作業を管理したいユーザー

## ランタイムサポート

| Runtime | Command | Installed files | Support |
| --- | --- | --- | --- |
| Claude | `craft install --target claude --dest ~/.claude` | `agents/`, `skills/`, `commands/` | asset install |
| Codex | `craft install --target codex --dest PROJECT` | `AGENTS.md` | guidance adapter |
| Gemini | `craft install --target gemini --dest PROJECT` | `GEMINI.md` | guidance adapter |
| OpenCode | `craft install --target opencode --dest PROJECT` | `AGENTS.md` | guidance adapter |
| OpenHands | `craft install --target openhands --dest PROJECT` | `AGENTS.md`, `.agents/skills/` | skill registry export |

Install commands do not overwrite existing files by default. Use `--dry-run` to
preview changes and `--force` only when replacement is intentional.

## インストール

### curl

```bash
curl -fsSL https://raw.githubusercontent.com/woogi-kang/craft-harness/main/scripts/install.sh | bash
craft doctor
```

### Homebrew

```bash
brew install woogi-kang/tap/craft-harness
craft doctor
```

### Source checkout

```bash
git clone https://github.com/woogi-kang/craft-harness.git
cd craft-harness
python3 -m pip install -e .
craft validate
craft orchestrate examples/plan.json --dry-run
```

## Quick Start

```bash
craft doctor
craft validate
craft catalog --format md
```

Install one runtime adapter into a project:

```bash
craft install --target codex --dest /path/to/project
craft install --target openhands --dest /path/to/project --dry-run
```

Preview a worker DAG from inside a git repository:

```bash
craft orchestrate examples/plan.json --dry-run
```

## Plan Example

```json
{
  "session": "checkout-hardening",
  "base_ref": "HEAD",
  "workers": [
    {
      "name": "Implementation",
      "task": "Implement checkout validation for missing shipping address.",
      "success_criteria": [
        "The API rejects missing shipping addresses with a 422 response",
        "The UI shows a clear field-level error"
      ],
      "eval_type": "fullstack"
    },
    {
      "name": "QA",
      "task": "Review the implementation against every success criterion.",
      "depends_on": ["Implementation"],
      "success_criteria": [
        "Every criterion has a PASS or FAIL decision",
        "Any failure includes a concrete rework instruction"
      ],
      "eval_type": "review"
    }
  ]
}
```

See [Spec and Contract Notes](docs/spec-contract.md) for the complete plan
contract.

## Documentation

- [Installation](docs/install.md)
- [Architecture](docs/architecture.md)
- [Skill Catalog](docs/skill-catalog.md)
- [Output Styles](docs/output-styles.md)
- [Roadmap](ROADMAP.md)

