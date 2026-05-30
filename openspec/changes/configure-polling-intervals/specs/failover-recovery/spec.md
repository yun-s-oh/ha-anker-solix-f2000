## MODIFIED Requirements

### Requirement: Active BLE Heartbeat Keep-Alive
The system SHALL issue a telemetry query command to the F2000 at the configured polling interval (defaulting to 5 seconds, configurable between 5 and 30 seconds) to update sensor data and prevent the Bluetooth radio from shutting down after the 12-hour inactivity limit.

#### Scenario: 12-hour continuous monitoring test
- **WHEN** the integration is active for over 12 hours without any user interactions
- **THEN** the periodic polling query keeps the F2000's Bluetooth radio awake and the connection stays active.

### Requirement: Graceful Reconnection and Back-off
The system SHALL implement an exponential back-off reconnection loop if the Bluetooth connection is lost or blocked by another device (e.g., the official Anker smartphone app). The maximum reconnection delay SHALL be configurable by the user via an options flow between 30 and 300 seconds, defaulting to 30 seconds.

#### Scenario: Connection dropped or device app-locked
- **WHEN** the F2000 goes out of range, or if the user opens the official smartphone app (which claims the exclusive single-connection BLE slot)
- **THEN** the BLE client schedules retries starting at 5 seconds, scaling exponentially up to the user-configured maximum delay (defaulting to 30 seconds) to avoid overloading the Bluetooth stack, defaulting sensor states gracefully, and automatically restoring connection when the device is reachable again.
