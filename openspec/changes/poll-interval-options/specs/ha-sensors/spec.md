## MODIFIED Requirements

### Requirement: Unified Data Update Coordinator
The integration SHALL utilize a single `DataUpdateCoordinator` to manage active polling and passive
notification parsing, avoiding redundant GATT queries. The active polling interval SHALL be
configurable by the user via an options flow between 5 and 300 seconds, defaulting to 30 seconds.

#### Scenario: Concurrent sensor updates
- **WHEN** a telemetry notification is received by the coordinator
- **THEN** all associated sensor entities (battery level, AC output, DC output) update their
  state in Home Assistant simultaneously without issuing new Bluetooth requests.

#### Scenario: User changes default poll interval in options flow
- **WHEN** the user changes the default poll interval option to 60 seconds and clicks save
- **THEN** the DataUpdateCoordinator instantly updates its update interval to 60 seconds without
  restarting the integration.

### Requirement: Config Flow Options Setup
The configuration flow SHALL prompt the user for the MAC Address (for manual setups), Integration
Name, Active Telemetry Polling Rate (5s to 300s), and Maximum Reconnection Back-Off Limit
(30s to 600s). The flow SHALL enforce that the Maximum Reconnection Back-Off Limit is greater
than or equal to the Active Telemetry Polling Rate. These polling options SHALL be available in
both the manual setup flow and the automatic discovery flow steps, as well as the post-setup
options flow.

#### Scenario: Submitting manual configuration setup options with valid parameters
- **WHEN** the user inputs a manual setup with poll_interval=30 and max_retry_interval=60
- **THEN** the setup succeeds, the config entry is created, and parameters are stored in options.

#### Scenario: Submitting automatic discovery setup options with valid parameters
- **WHEN** the user completes discovery setup with poll_interval=30 and max_retry_interval=60
- **THEN** the setup succeeds, the config entry is created, and parameters are stored in options.

#### Scenario: Submitting setup options with invalid retry interval
- **WHEN** the user sets poll_interval=60 and max_retry_interval=30 in any setup step
- **THEN** validation fails, and the flow presents an error indicating the retry interval must be
  greater than or equal to the polling interval.
