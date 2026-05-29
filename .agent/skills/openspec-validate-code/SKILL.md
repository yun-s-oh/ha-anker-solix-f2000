---
name: openspec-validate-code
description: Validate codebase quality, formatting, syntax, and type compliance. Use when you want to run PEP 8 linting, mypy static analysis, syntax compiling, and Home Assistant schema validation.
license: MIT
compatibility: Requires python virtual environment with flake8, mypy, and py_compile.
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "1.3.1"
---

Validate codebase quality, formatting, syntax, and type compliance.

> [!IMPORTANT]
> **Execution Timing Guideline**: To maintain maximum efficiency, do NOT run these validations each time code changes following the OpenSpec guideline. Instead, it should ideally run after code changes are completely finished, or as a final gate prior to staging/committing changes (`/opsx-commit`).

**Input**: Optionally specify a target directory or file path. If omitted, you must dynamically locate and validate the custom component directory (e.g., `custom_components/anker_solix_f2000` or generic component folders).

---

## Steps

### 1. Identify Target Components
Find the active custom components and test directories in the workspace:
- Target component: `custom_components/` (e.g., `custom_components/anker_solix` or similar)
- Target tests: `tests/`

### 2. Pre-Check Verification
Verify that the python virtual environment is configured and necessary linting tools (`flake8`, `mypy`) are installed:
```bash
# Check if venv exists and activate it
source venv/bin/activate
```

### 3. Run Quality & Compliance Checks

#### A. Linting & Formatting Check (PEP 8)
Verify formatting compliance and limit all modified or newly introduced lines to a maximum of 100 characters:
```bash
venv/bin/flake8 custom_components/ --max-line-length=100
```

#### B. Type Checking (Mypy)
Verify static typing compliance across target components, ignoring missing imports for third-party libraries:
```bash
venv/bin/mypy custom_components/ --ignore-missing-imports
```

#### C. Syntax Verification
Verify compile-time syntax correctness for all Python scripts:
```bash
venv/bin/python3 -m py_compile custom_components/**/*.py
```

#### D. Home Assistant Integration Schema Validation
Verify custom component structure and configuration flows:
```bash
venv/bin/hass-config-check custom_components/
```
*(Note: If `hass-config-check` or `hassfest` CLI tool is unavailable locally, fall back to compiling and testing config flow schemas using `pytest`).*

---

## Output During Execution

Your response during execution should clearly log each step:

```
## Initiating Code Validation Suite

### Step 1: Formatting & Linting Check (flake8)
Running: flake8 custom_components/ --max-line-length=100
✓ PEP 8 formatting check passed! (No style issues found)

### Step 2: Static Type Checking (mypy)
Running: mypy custom_components/ --ignore-missing-imports
✓ Type verification passed! (Success: no issues found)

### Step 3: Compile Syntax Check
Running: python3 -m py_compile custom_components/**/*.py
✓ Syntax compilation passed! (All files compiled successfully)

### Step 4: Home Assistant Integration Check
Running: hass-config-check custom_components/
✓ Integration schema is valid!

✓ All validation checks passed successfully!
```

---

## Guardrails
- **Timing & Frequency**: Do NOT run these validation checks each time code changes to follow the OpenSpec guideline. It should ideally run only after code changes are complete, or as a final verification before committing.
- **Zero Errors Allowed**: Never skip or ignore linting or type-checking errors. If any step fails, fix the code or prompt the user with details before proceeding to commit or release.
- **Strict Line Limits**: Keep modified and newly introduced code capped at 100 characters per line.
- **No Swallowed Exceptions**: Ensure `try/except` blocks in component code do not swallow exceptions without proper logs (warn/error).
