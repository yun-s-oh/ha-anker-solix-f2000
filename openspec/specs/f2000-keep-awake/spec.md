# f2000-keep-awake Specification

## Purpose
This specification defines the integration's keep-awake heartbeat mechanism. It details the requirements for maintaining a persistent GATT connection and dispatching periodic query pings over BLE to prevent the Anker Solix F2000 from entering low-power standby mode when ports are idle.
## Requirements
### Requirement: Active BLE Interrogation Heartbeat
The integration SHALL maintain a persistent active GATT connection and dispatch periodic
telemetry query pings to prevent the F2000's CPU from entering low-power deep standby.

#### Scenario: Continuous local BLE polling
- **WHEN** the F2000 is running on idle (AC/DC ports OFF, not charging)
- **THEN** the BLE client maintains a persistent connection and actively queries the device
  every few seconds to obtain real-time telemetry and prevent the radio from sleeping.

