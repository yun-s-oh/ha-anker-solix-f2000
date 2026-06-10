# ble-protocol Specification

## Purpose
This specification defines the unencrypted Bluetooth Low Energy (BLE) communication characteristics, frame headers, packet structures, and decoding schemas used to interface with the Anker Solix F2000.
## Requirements
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

### Requirement: Structured Packet Telemetry Parsing
The system SHALL parse 102-byte telemetry packets (`0x49` subtype), 14-byte state packets (`0x48` subtype), and 122-byte auxiliary state packets (`0x01` subtype) by validating the `09 ff 00 00 01` header and decoding individual byte registers. In the `0x49` telemetry packet, the system SHALL decode `twelve_volt_on` from byte register `80` (but shall NOT decode `power_save_on` from byte register `82`). In the 122-byte `0x01` auxiliary state packet, the system SHALL decode `power_save_on` from byte register `117`.

#### Scenario: Validating and decoding a telemetry frame
- **WHEN** a notification frame starting with `09 ff 00 00 01` and subtype `0x49` is received
- **THEN** the parser successfully extracts battery, temperature, solar input power, AC outlet power, twelve_volt_on master state, and serial numbers, but does not extract power_save_on state.

#### Scenario: Validating and decoding an auxiliary state frame
- **WHEN** a notification frame starting with `09 ff 00 00 01`, subtype `0x01`, and length 122 is received
- **THEN** the parser successfully extracts ac_recharging_power, screen_timeout, and power_save_on state (from byte register 117).

