## MODIFIED Requirements

### Requirement: Unified Data Update Coordinator
The integration SHALL utilize a single `DataUpdateCoordinator` to manage active polling and passive notification parsing, avoiding redundant GATT queries. The active polling interval SHALL be configurable by the user via an options flow between 5 and 30 seconds, defaulting to 5 seconds.

#### Scenario: Concurrent sensor updates
- **WHEN** a telemetry notification is received by the coordinator
- **THEN** all associated sensor entities (battery level, AC output, DC output) update their state in Home Assistant simultaneously without issuing new Bluetooth requests.

#### Scenario: User changes default poll interval in options flow
- **WHEN** the user changes the default poll interval option to 10 seconds and clicks save
- **THEN** the DataUpdateCoordinator instantly updates its update interval to 10 seconds without restarting the integration.
