## MODIFIED Requirements

### Requirement: Standardized Tests Directory Layout
The isolated functional verification CLI suite and mock telemetry unit tests SHALL be housed under
the standard `tests/` directory. Their environment setup SHALL use `uv` and a root `pyproject.toml`
to natively lock all direct and transitive dependencies into a secure, hash-verified `uv.lock` file,
guaranteeing identical and secure environments across machines.

#### Scenario: Running the verification scripts
- **WHEN** the user synchronizes the environment via `uv sync`
- **THEN** it provisions the virtual environment, locks dependencies, and runs tests cleanly.
