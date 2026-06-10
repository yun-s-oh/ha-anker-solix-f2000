## Why

Transitioning the Python virtual environment setup and dependency management from `pip` and
`venv` to `uv` improves developer setup reliability, speeds up local environment build times,
and simplifies Python version bootstrapping. Additionally, to prevent supply chain attacks and
guarantee identical environments across machines, `uv` will be used to natively lock all direct
and transitive dependencies into a secure, hash-verified `uv.lock` file.

## What Changes

- Create a minimal root `pyproject.toml` to declare dependencies and development tools.
- Generate a secure, hash-verified `uv.lock` file locking all direct and transitive dependencies.
- Modify [openspec/style-guide.md](/openspec/style-guide.md)
  to reference `uv` instead of `pip`/`venv` for quality checks.
- Update [README.md](/README.md)
  development setup notes to recommend `uv` and lockfile-based syncing.
- Update [tests/README.md](/tests/README.md)
  to explain environment syncing using `uv.lock` instead of manual pip installation.
- Refactor the automated development/agent setup guidelines and spec files to standardize
  on `uv` lockfile commands.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `tests`: Update testing suite instructions and setup workflow to use `uv` and `uv.lock`.
- `agent-guidelines`: Update developer guidelines and quality check command instructions to use `uv`.

## Impact

- Impacted files: `pyproject.toml` [NEW], `uv.lock` [NEW], `openspec/style-guide.md`, `README.md`, `tests/README.md`, `agent-guidelines.md`, and spec files under `openspec/specs/`.
- No runtime impact on the Home Assistant custom component itself.
