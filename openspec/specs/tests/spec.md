# tests Specification

## Purpose
Specification for the isolated tests and verification suite in the tests folder.
## Requirements
### Requirement: CLI Telemetry Logger
The standalone Python test script SHALL connect to the designated F2000 MAC address and print a formatted console report of decoded telemetry.

#### Scenario: Running the telemetry CLI script
- **WHEN** the user executes the test script with a valid MAC address
- **THEN** the script establishes a connection, prints parsed values (battery %, AC/DC input/output watts, temperatures), and exits cleanly.

### Requirement: CLI Keep-Alive Test
The standalone test script SHALL support a keep-alive mode that sends periodic query packets to verify connection persistence.

#### Scenario: Running the keep-alive script over extended time
- **WHEN** the script is run in keep-alive mode for 30 minutes
- **THEN** it sends a query packet every 5 minutes, keeps the BLE radio active, and reports zero connection drops.

### Requirement: Standardized Tests Directory Layout
The isolated functional verification CLI suite and mock telemetry unit tests SHALL be housed under
the standard `tests/` directory. Their environment setup SHALL use `uv` and a root `pyproject.toml`
to natively lock all direct and transitive dependencies into a secure, hash-verified `uv.lock` file,
guaranteeing identical and secure environments across machines.

#### Scenario: Running the verification scripts
- **WHEN** the user synchronizes the environment via `uv sync`
- **THEN** it provisions the virtual environment, locks dependencies, and runs tests cleanly.

