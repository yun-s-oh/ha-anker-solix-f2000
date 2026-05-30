## ADDED Requirements

### Requirement: Standardized Tests Directory Layout
The isolated functional verification CLI suite and mock telemetry unit tests SHALL be housed under the standard `tests/` directory.

#### Scenario: Running the verification scripts
- **WHEN** the user executes the test script or pytest suite
- **THEN** it resolves paths and imports relative to the standard `tests/` directory cleanly.
