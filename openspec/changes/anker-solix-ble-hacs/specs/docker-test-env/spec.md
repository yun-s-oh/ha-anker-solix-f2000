## ADDED Requirements

### Requirement: Docker Test Environment Build
The system SHALL provide a Dockerfile and docker-compose configurations to build and run a containerized testing suite.

#### Scenario: Building the testing container
- **WHEN** the user runs `docker compose build` in the root of the repository
- **THEN** the Docker image builds successfully with all Python dependencies installed (including bleak, pytest, and SolixBLE).

### Requirement: Telemetry Decoding Mock Test
The testing suite inside the Docker container SHALL support mock Bluetooth interfaces to verify telemetry parsing without physical hardware.

#### Scenario: Running unit tests inside the container
- **WHEN** the user executes the test suite inside the running container
- **THEN** the mock BLE client injects predefined hex byte packets and asserts that the parser decodes battery, power, and status correctly.
