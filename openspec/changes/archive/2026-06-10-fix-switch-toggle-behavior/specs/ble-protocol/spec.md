## MODIFIED Requirements

### Requirement: Unencrypted BLE Communication Protocol
The system SHALL use unencrypted BLE characteristic read/write operations on custom UUIDs `7777` (write) and `8888` (notify) for commanding and receiving telemetry from the Anker F2000. Control command IDs `0x86` (AC toggle) and `0x87` (DC toggle) SHALL be documented as **toggle commands** — the device flips the current state regardless of the payload byte value. Control command ID `0x8A` (Power Save) SHALL be documented as an **explicit command** that respects the ON/OFF payload value, but is sensitive to subsequent BLE activity — active telemetry queries sent shortly after a Power Save ON command can cause the device to auto-exit Power Save mode.

#### Scenario: Subscribing and writing to the BLE device
- **WHEN** the BLE client connects to the F2000
- **THEN** it successfully subscribes to characteristic `00008888-0000-1000-8000-00805f9b34fb` and writes command packets to `00007777-0000-1000-8000-00805f9b34fb` without any ECDH encryption handshake.

#### Scenario: AC/DC toggle command behavior
- **WHEN** a control command with ID `0x86` or `0x87` is written to the BLE characteristic
- **THEN** the F2000 toggles the corresponding output (AC or DC) to the opposite of its current state, regardless of the payload byte value sent.

#### Scenario: Power Save command sensitivity to BLE activity
- **WHEN** a Power Save ON command (`0x8A` with payload `0x01`) is sent, followed by a telemetry query within approximately 1 second
- **THEN** the F2000 may auto-exit Power Save mode due to the BLE write activity from the telemetry query.
