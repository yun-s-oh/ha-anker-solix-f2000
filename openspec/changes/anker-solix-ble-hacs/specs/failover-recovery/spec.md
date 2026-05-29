## ADDED Requirements

### Requirement: Active BLE Heartbeat Keep-Alive
The system SHALL issue a lightweight heartbeat command to the F2000 every 5 minutes to prevent the Bluetooth radio from shutting down after the 12-hour inactivity limit.

#### Scenario: 12-hour continuous monitoring test
- **WHEN** the integration is active for over 12 hours without any user interactions
- **THEN** the periodic 5-minute heartbeat keeps the F2000's Bluetooth radio awake and the connection stays connected.

### Requirement: Graceful Reconnection and Back-off
The system SHALL implement an exponential back-off reconnection loop if the Bluetooth connection is lost or blocked by another device.

#### Scenario: Connection dropped due to device out-of-range
- **WHEN** the F2000 goes out of range and disconnects
- **THEN** the BLE client schedules retries starting at 5 seconds, doubling up to a maximum of 5 minutes, logging warnings without crashing Home Assistant.
