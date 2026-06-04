## MODIFIED Requirements

### Requirement: Structured Technical Documentation
The repository SHALL contain standardized markdown files detailing the codebase layout, module
dependencies, and code guidelines for developer and agent reference. These guidelines SHALL
describe development quality check workflows (linting, syntax compilation) using the `uv`
toolchain, and SHALL be kept up-to-date and free from broken directory path references to ensure
accurate AI agent context aligning with the current codebase layout.

#### Scenario: Agent reads developer guidelines
- **WHEN** an automated coding agent reads the developer instructions in the repository
- **THEN** it quickly identifies the location of the core parser, the HA integration wrapper, and
  standard verification procedures (e.g. running linters via `uv`) without encountering obsolete
  or broken folder paths.
