## 1. Documentation Updates

- [x] 1.1 Update `tests/README.md` to explain using `uv sync` and `uv.lock` for environment syncing.
- [x] 1.2 Update `README.md` macOS setup instructions to reference `uv sync`.
- [x] 1.3 Update `agent-guidelines.md` quality check instructions to use `uv` and lockfile-based setup.
- [x] 1.4 Update `openspec/style-guide.md` quality check verification instructions to use `uv`.

## 2. Lockfile & Environment Implementation

- [x] 2.1 Create a minimal `pyproject.toml` file at the root.
- [x] 2.2 Generate the secure `uv.lock` file using `uv lock`.
- [x] 2.3 Provision the virtual environment `tests/venv` using `uv sync`.
- [x] 2.4 Verify that linting and unit tests pass in the synced environment.
