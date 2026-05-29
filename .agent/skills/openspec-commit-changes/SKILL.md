---
name: openspec-commit-changes
description: Validate, format, and commit changes following repository standards and conventional commits. Use when you want to validate style/syntax, review diffs, stage files, and make a structured conventional commit.
license: MIT
compatibility: Requires git and python environment with flake8.
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "1.3.1"
---

Validate, format, and commit changes in the codebase to ensure repository health, clean history, and high-quality standards.

**Input**: Optionally specify a commit scope or message hint (e.g., `feat(api): add polling`). If omitted, you must analyze unstaged changes to automatically suggest and formulate a conventional commit message.

---

## Steps

### 1. Identify Modified Files
Check the git status to see which files are modified, untracked, or staged:
```bash
git status
```

### 2. Pre-Commit Checklist (Validation & Style)
Before staging or committing any files, ensure that the proposed changes are fully validated.

#### A. Format & Style Checks
- Ensure the code complies with PEP 8 standards.
- Limit all modified or newly introduced lines to a maximum of 100 characters.
- Dynamically locate python package/component folders in `custom_components/` (e.g. `custom_components/anker_solix` or similar). If none exists yet, run linting on any modified python files.
- Run linting checks using `flake8`:
  ```bash
  venv/bin/flake8 custom_components/ --max-line-length=100
  ```
  *(Note: If `venv` is not present, check for system-wide `flake8` or look for the active python environment).*

#### B. Syntax Verification
- Compile modified files to verify no syntax errors exist:
  ```bash
  venv/bin/python -m py_compile custom_components/**/*.py
  ```

### 3. Review Diffs
Inspect the exact lines of code being changed to ensure no extraneous modifications, leftover debugging logs, or sensitive values (like api keys, secrets, or personal tokens) are included:
```bash
git diff
```

### 4. Stage Intended Files
Stage files selectively. Do NOT commit temporary directories, virtual environments, cache files, or environment variables (`.env`).
```bash
# Stage specific files
git add path/to/file.py

# Stage all files in a specific directory
git add tests/
```

### 5. Write a Conventional Commit Message
Use the Conventional Commits specification to format your commit messages. The message should explain "why" the change was made rather than just "what".

#### Message Structure:
```text
<type>(<scope>): <short summary>

[optional body explaining rationale and decisions]
```

#### Allowed Types:
- `feat`: A new feature (e.g., adding a sensor, custom service, or API support)
- `fix`: A bug fix
- `docs`: Documentation-only changes (e.g., updating `README.md` or adding comments)
- `style`: Formatting, missing semi-colons, etc.; no production code change
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools/libraries

#### Example Commit:
```bash
git commit -m "feat(api): add standalone test script"
```

### 6. Confirm Clean Working Tree
Run `git status` one last time to make sure all intended files were successfully committed and that no unwanted files are left untracked:
```bash
git status
```

---

## Output During Execution

Your response during execution should clearly log each step:

```
## Initiating Commit Process

### Step 1: Pre-Commit Checks
✓ PEP 8 compliance verified (flake8 check passed)
✓ Syntax compilation verified (py_compile passed)

### Step 2: Staging Changes
Staged files:
- custom_components/anker_solix/sensor.py
- custom_components/anker_solix/api.py

### Step 3: Committing Changes
Commit Type: feat
Scope: sensor
Summary: add telemetry polling for F2000 battery

Running: git commit -m "feat(sensor): add telemetry polling for F2000 battery"
[main 1a2b3c4] feat(sensor): add telemetry polling for F2000 battery
 2 files changed, 45 insertions(+)

✓ Commit complete!
```

---

## Guardrails
- **No Unintended Files**: Never commit `.env` files, virtual environments (`venv/`), temporary artifacts, or personal API keys.
- **Strict Character Limits**: Ensure no modified line exceeds 100 characters.
- **Run Checks First**: Always execute linting and compilation *before* committing. If there are syntax or linting errors, fix them or prompt the user before continuing.
- **Conventional Commits Only**: Always use the defined conventional types (`feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`). Do not invent new types.
