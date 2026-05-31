# agent-guidelines Specification

## Purpose
This specification establishes standard technical guidelines, codebase layout structures, and coding paradigms for automated developer agents and contributors working in this repository.
## Requirements
### Requirement: Structured Technical Documentation
The repository SHALL contain standardized markdown files detailing the codebase layout, module dependencies,
and code guidelines for developer and agent reference. These guidelines SHALL be kept up-to-date and free
from broken directory path references to ensure accurate AI agent context aligning with the current codebase layout.

#### Scenario: Agent reads developer guidelines
- **WHEN** an automated coding agent reads the developer instructions in the repository
- **THEN** it quickly identifies the location of the core parser, the HA integration wrapper, and standard
  verification procedures without encountering obsolete or broken folder paths.

### Requirement: Protocol Specification Reference
The documentation SHALL include a detailed data decoding matrix mapping known byte offsets in the Anker Solix telemetry frame to specific sensors.

#### Scenario: Adding a new sensor entity
- **WHEN** a contributor or agent wants to add support for a new telemetry metric
- **THEN** they reference the protocol specification matrix to retrieve the correct byte offset, length, and scaling multiplier.

