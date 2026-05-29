---
description: Validate, format, and commit changes following repository standards and conventional commits
---

Validate, format, and commit changes in the codebase to ensure repository health, clean history, and high-quality standards.

**Input**: Optionally specify a commit scope or message hint (e.g., `/opsx:commit feat(api): add polling`). If omitted, the agent will analyze the unstaged changes to automatically generate a compliant message.

---

## Steps

### 1. Identify Modified Files
Scan the working directory to identify modified, untracked, and deleted files:
```bash
git status
```

### 2. Pre-Commit Checklist (Validation & Style)
Before staging or committing any files, ensure that the proposed changes are fully validated.

#### A. Format & Style Checks
- Ensure the code complies with PEP 8 standards.
- Limit all modified or newly introduced lines to a maximum of 100 characters.
- Run linting checks using `flake8` on the appropriate custom component path (e.g., `custom_components/anker_solix` or generic component directory):
  ```bash
  venv/bin/flake8 custom_components/ --max-line-length=100
  ```
  *(Note: Adjust the target path if you are working within a specific subdirectory or if the venv path differs).*

#### B. Syntax Verification
- Compile modified files to verify no syntax errors exist:
  ```bash
  venv/bin/python -m py_compile custom_components/**/*.py
  ```

### 3. Review Diffs
Inspect the exact lines of code being changed to ensure no extraneous modifications, leftover debugging logs, or sensitive values are included:
```bash
git diff
```

### 4. Stage Intended Files
Stage files selectively. Do NOT commit temporary directories, virtual environments, cache files, or environment variables (`.env`).

#### 🔀 Atomic & Split Commits
If your changes contain logically distinct or independent modifications (e.g., editing documentation in `README.md` and adding a new python feature in `custom_components/`, or introducing a bug fix alongside a large refactor), **do not commit them all in a single giant commit**.
Instead, **split them into multiple atomic commits**:
1. Group files by logical change boundaries (e.g. `docs` files, `test` files, `feat` or `fix` files).
2. Stage only the files for the first distinct change:
   ```bash
   git add openspec/style-guide.md
   ```
3. Proceed to validation (Step 2) and commit (Step 5) only for the staged files.
4. Repeat staging, validation, and committing for the remaining files:
   ```bash
   git add test-scripts/test_passive_telemetry.py
   ```

```bash
# Stage specific files
git add path/to/file.py

# Stage all files in a specific directory
git add tests/
```

### 5. Write a Conventional Commit Message
Use the Conventional Commits specification to format your commit messages. The message should explain "why" the change was made rather than just "what". Each split commit must have its own descriptive conventional message.

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
