# failover-recovery Specification

## Purpose
This specification defines the Bluetooth failover, reconnection, startup retry, and keep-alive heartbeat requirements for maintaining reliable long-term F2000 connections.
## Requirements
### Requirement: Active BLE Heartbeat Keep-Alive
The system SHALL issue a telemetry query command to the F2000 at the configured polling interval (defaulting to 30 seconds, configurable between 5 and 300 seconds) to update sensor data and prevent the Bluetooth radio from shutting down after the 12-hour inactivity limit.

#### Scenario: 12-hour continuous monitoring test
- **WHEN** the integration is active for over 12 hours without any user interactions
- **THEN** the periodic polling query keeps the F2000's Bluetooth radio awake and the connection stays active.

### Requirement: Graceful Reconnection and Back-off
The system SHALL implement an exponential back-off reconnection loop if the Bluetooth connection is lost or blocked by another device (e.g., the official Anker smartphone app). The maximum reconnection delay SHALL be configurable by the user via an options flow between 30 and 600 seconds, defaulting to 60 seconds.

#### Scenario: Connection dropped or device app-locked
- **WHEN** the BLE connection is lost or blocked
- **THEN** the BLE client schedules retries starting at 5 seconds, scaling exponentially up to the user-configured maximum delay (defaulting to 60 seconds) to avoid overloading the Bluetooth stack, defaulting sensor states gracefully, and automatically restoring connection when the device is reachable again.

### Requirement: Resilient Startup Retries
The integration SHALL raise `ConfigEntryNotReady` if the physical F2000 BLE device is not yet resolved from the central Bluetooth subsystem cache during startup, enabling Home Assistant to automatically reschedule clean setup attempts in the background.

#### Scenario: Bluetooth adapter not ready at boot
- **WHEN** Home Assistant restarts and attempts to set up the Anker Solix F2000 integration before the Bluetooth scanner has populated its cache
- **THEN** the integration raises `ConfigEntryNotReady` and Home Assistant displays a "Retrying setup" status, automatically running background retries until the BLE device is discovered.

