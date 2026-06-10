## Context

The repository currently utilizes standard Python virtual environments (`python3 -m venv`) and
`pip` to set up and manage script dependencies. Transitioning to `uv` (a fast Rust-based Python
package installer and resolver) will optimize virtual environment creation speed, resolve package
version dependencies cleanly, and allow automatic bootstrapping of the correct Python version
(Python 3.11).

## Goals / Non-Goals

**Goals:**
- Update [openspec/style-guide.md](/openspec/style-guide.md), [README.md](/README.md), [tests/README.md](/tests/README.md), and [agent-guidelines.md](/agent-guidelines.md) to use `uv`.
- Transition local developer setup instructions from `pip install` to `uv pip install`.
- Update the quality check commands in agent guidelines and workflows to refer to running under the new `uv`-based virtual environment path.

**Non-Goals:**
- Rewriting or altering runtime Python code in custom components.
- Changing HACS deployment mechanisms.
- Changing CI runner configurations if they do not run local venv tests.

## Decisions

### Decision 1: Use `pyproject.toml` and `uv.lock` for dependency locking and syncing
- **Rationale**: To prevent supply chain attacks and guarantee identical environments across
  machines, all direct and transitive dependencies are locked in a secure, hash-verified
  `uv.lock` file. We define a minimal root `pyproject.toml` containing project dependencies
  and development tools, and use `uv sync` (with `UV_PROJECT_ENVIRONMENT=tests/venv`) to
  provision the environment cleanly.
- **Alternatives Considered**: Using standard `pip install -r requirements.txt` or `uv pip install
  -r requirements.txt` without a lockfile, but that does not guarantee deterministic,
  identical environments and does not protect against supply chain attacks (since transitive
  dependencies could change silently).

## Risks / Trade-offs

- **[Risk]**: Developers do not have `uv` installed.
  - *Mitigation*: Provide clear instructions in the README on how to install `uv` (e.g. `curl -LsSf https://astral.sh/uv/install.sh | sh` or `brew install uv`).
- **[Risk]**: `uv` venv path differs.
  - *Mitigation*: Keep the destination venv path strictly as `tests/venv/` so all existing helper scripts and CI steps targeting `./tests/venv/bin/...` continue to work without modification.
