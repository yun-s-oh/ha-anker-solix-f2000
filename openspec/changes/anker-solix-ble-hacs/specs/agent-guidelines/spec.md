## ADDED Requirements

### Requirement: Structured Technical Documentation
The repository SHALL contain standardized markdown files detailing the codebase layout, module dependencies, and code guidelines for developer and agent reference.

#### Scenario: Agent reads developer guidelines
- **WHEN** an automated coding agent reads the developer instructions in the repository
- **THEN** it quickly identifies the location of the core parser, the HA integration wrapper, and standard verification procedures.

### Requirement: Protocol Specification Reference
The documentation SHALL include a detailed data decoding matrix mapping known byte offsets in the Anker Solix telemetry frame to specific sensors.

#### Scenario: Adding a new sensor entity
- **WHEN** a contributor or agent wants to add support for a new telemetry metric
- **THEN** they reference the protocol specification matrix to retrieve the correct byte offset, length, and scaling multiplier.
