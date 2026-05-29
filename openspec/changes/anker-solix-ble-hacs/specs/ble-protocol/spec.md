## ADDED Requirements

### Requirement: BLE Device Discovery
The system SHALL scan and identify the Anker Solix F2000 by its local name prefix (e.g., `PowerHouse 767` or `F2000`) and capture its MAC address or UUID.

#### Scenario: Successful device discovery
- **WHEN** the BLE scanner starts
- **THEN** the scanner detects an advertisement matching the Anker Solix F2000 local name and returns its MAC address and RSSI.

### Requirement: Telemetry Characteristic Subscription
The system SHALL register notifications on the custom GATT notification characteristic to continuously stream hex packets.

#### Scenario: Successful subscription to telemetry notifications
- **WHEN** the BLE client connects to the F2000 and registers for notifications on the telemetry characteristic
- **THEN** the client receives continuous raw byte packets containing the device's battery and power telemetry.
