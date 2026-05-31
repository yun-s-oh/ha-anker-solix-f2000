---
description: Fetch, rebase, validate, and safely push committed changes to GitHub
---

Fetch, rebase, validate, and safely push committed changes to GitHub to maintain a clean history.

> [!IMPORTANT]
> **Safety First**: Always prioritize `--force-with-lease` over standard force-pushing to prevent
> overwriting other people's commits. If standard force-with-lease fails due to stale references,
> follow the instructions in Step 4 to bind and push cleanly.

**Input**: None. The agent/developer will automatically detect the active branch and target.

---

## Steps

### 1. Verify Clean Working Tree
Before pushing, ensure all changes are committed and that you are on the correct branch:
```bash
git status
```

### 2. Fetch and Rebase from Upstream
To keep a linear, clean commit history and avoid conflicts, pull the latest changes from the
remote upstream branch and rebase your commits:
```bash
git fetch origin
git rebase origin/main
```
*(Note: If you encounter merge conflicts, resolve them, use `git add` on the resolved files, and
run `git rebase --continue` to finish).*

### 3. Pre-Push Validation Suite
Before pushing to the remote repository, run validation checks to ensure no regressions:
```bash
# Run styling checks
venv/bin/flake8 custom_components/ --max-line-length=100

# Run syntax compilation
venv/bin/python3 -m py_compile custom_components/**/*.py

# Run unit tests
venv/bin/pytest
```

### 4. Push Safely to GitHub
Push your commits to origin. Since rebasing modifies the commit history, a force push is required.

#### A. Standard Safe Push
Use `--force-with-lease` to safely force push. This ensures you do not overwrite remote commits
that you haven't fetched yet:
```bash
git push origin <branch-name> --force-with-lease
```

#### B. Resolving "Stale Info" or Missing Upstream Bindings
If the remote branch was deleted, recreated, or is missing a local tracking configuration, the
standard `--force-with-lease` will reject with `stale info` or standard errors. In such scenarios,
run:
```bash
git push -u origin <branch-name> --force
```

### 5. Submit/Update Pull Request
Go to the repository on GitHub, create a Pull Request, and fill in the PR details. The agent or
developer should print out a brief, professional PR message containing a summary of the changes
and the verification results to easily copy-paste into GitHub.

#### PR Message Structure:
```text
Title: <Conventional PR Title, e.g. docs(workflow): create safe push workflow>

## Description
- <Brief bullet point detailing the first major change>
- <Brief bullet point detailing the second major change>

## Verification Results
- [x] flake8 style checks passed
- [x] py_compile syntax checks passed
- [x] pytest unit tests passed
```

---

## Output During Execution

```
## Initiating GitHub Push Suite

### Step 1: Checking working tree status
✓ Branch is feature/f2000-wake-version-fix
✓ Working tree is clean

### Step 2: Syncing with upstream
Running: git fetch origin && git rebase origin/main
✓ Successfully rebased onto origin/main

### Step 3: Running Pre-Push Validation
✓ flake8 style validation passed
✓ py_compile syntax checks passed
✓ pytest unit tests passed (all tests green)

### Step 4: Pushing to remote repository
Running: git push origin feature/f2000-wake-version-fix --force-with-lease
✓ Successfully pushed to origin/feature/f2000-wake-version-fix!

### Step 5: Suggested Pull Request Message
Title: docs(workflow): create safe push workflow

## Description
- Created .agent/workflows/opsx-push.md for safe git push instructions
- Outlined rebase and flake8/pytest validation steps

## Verification Results
- [x] flake8 style checks passed
- [x] py_compile syntax checks passed
- [x] pytest unit tests passed

✓ Push complete!
```

---

## Guardrails
- **Verify before Pushing**: Always run validation tests before performing a push to origin.
- **Do Not Wipe Commits**: Never use a blind `git push -f` or `git push --force` unless
  `--force-with-lease` has failed specifically due to a tracking/recreation issue as outlined
  in Step 4.B.
- **Line Limits**: Ensure no newly introduced or modified code lines exceed 100 characters.
