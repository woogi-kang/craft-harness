---
description: "Smart commit - Analyze changes and create logical commits"
argument-hint: "[message]"
type: utility
allowed-tools: AskUserQuestion, Bash, Read, Glob, Grep
model: opus
---

## Pre-execution Context

!git status --porcelain
!git branch --show-current
!git diff --stat
!git diff --cached --stat
!git log -10 --oneline

---

# /commit - Smart Commit Command

## Core Principle

Analyze all changes (staged + unstaged) and create logical, well-organized commits.

## Command Flow

```
START: Check Current Branch
  ↓
IF protected branch (master/main/develop):
  → Ask: Create new branch?
  ↓
Analyze ALL changes (staged + unstaged)
  ↓
Group changes logically
  ↓
Check existing commit style OR use gitflow
  ↓
Create commits (may be multiple)
```

## Step 1: Branch Protection Check

Protected branches: `master`, `main`, `develop`, `development`

IF on protected branch:
- Use AskUserQuestion:
  - Question: "보호된 브랜치입니다. 새 브랜치를 생성할까요?"
  - Options:
    1. "새 브랜치 생성" - Ask for branch name, then checkout
    2. "현재 브랜치에 커밋" - Continue on protected branch

## Step 2: Analyze All Changes

Collect ALL changes regardless of staging status:

```bash
# Staged changes
git diff --cached --name-status

# Unstaged changes
git diff --name-status

# Untracked files
git ls-files --others --exclude-standard
```

## Step 3: Group Changes Logically

Analyze and group by:
- **Feature**: Related functionality changes
- **Fix**: Bug fixes
- **Refactor**: Code restructuring
- **Style**: Formatting, whitespace
- **Docs**: Documentation
- **Test**: Test files
- **Chore**: Config, dependencies

Example grouping:
```
Group 1 (feat): src/auth.ts, src/login.tsx
Group 2 (test): tests/auth.test.ts
Group 3 (docs): README.md
```

## Step 4: Determine Commit Message Style

Check existing commits first:
```bash
git log -10 --oneline
```

Detect pattern:
- Conventional Commits: `feat:`, `fix:`, `chore:`
- Gitmoji: `:sparkles:`, `:bug:`
- Simple: Just description
- Ticket prefix: `[JIRA-123]`, `#123`

IF no clear pattern detected → Use Conventional Commits (gitflow)

## Step 5: Create Commits

For each logical group:
1. Stage relevant files: `git add <files>`
2. Commit with appropriate message
3. Repeat for next group

Commit message format (HEREDOC):
```bash
git commit -m "$(cat <<'EOF'
<type>(<scope>): <description>

<body if needed>

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

## Output Format

```markdown
## Commit Complete

**Branch**: feat/add-auth

### Commits Created (3)

1. **abc1234** `feat(auth): add login functionality`
   - src/auth.ts
   - src/login.tsx

2. **def5678** `test(auth): add login tests`
   - tests/auth.test.ts

3. **ghi9012** `docs: update README`
   - README.md

### Summary
- 3 commits created
- 5 files changed
- 120 insertions(+), 15 deletions(-)
```

---

## EXECUTION DIRECTIVE

1. Get current branch: `git branch --show-current`

2. IF branch is protected (master/main/develop/development):
   - Use AskUserQuestion:
     - Question: "보호된 브랜치입니다. 새 브랜치를 생성할까요?"
     - Header: "Branch"
     - Options:
       - Label: "새 브랜치 생성", Description: "새 브랜치를 생성한 후 커밋합니다"
       - Label: "현재 브랜치에 커밋", Description: "보호된 브랜치에 직접 커밋합니다"
   - IF "새 브랜치 생성":
     - Ask branch name via AskUserQuestion
     - Execute: `git checkout -b <branch-name>`

3. Collect all changes:
   ```bash
   git diff --cached --name-status  # staged
   git diff --name-status           # unstaged
   git ls-files --others --exclude-standard  # untracked
   ```

4. Analyze and group changes logically by:
   - Related functionality
   - Type (feat/fix/refactor/test/docs/chore)
   - Affected module/component

5. Check commit message style from recent history:
   ```bash
   git log -10 --oneline
   ```
   - Detect existing pattern (conventional/gitmoji/simple/ticket)
   - If unclear, default to Conventional Commits

6. For each logical group:
   - Stage files: `git add <files>`
   - Create commit with detected style
   - Use HEREDOC format with Co-Authored-By

7. After all commits, show summary:
   - List of commits with hash and message
   - Files in each commit
   - Total stats

---

Version: 2.0.0
Last Updated: 2026-01-14
Core: Smart multi-commit with logical grouping
