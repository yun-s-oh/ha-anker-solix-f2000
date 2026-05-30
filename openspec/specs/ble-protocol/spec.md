# ble-protocol Specification

## Purpose
This specification defines the unencrypted Bluetooth Low Energy (BLE) communication characteristics, frame headers, packet structures, and decoding schemas used to interface with the Anker Solix F2000.
## Requirements
### Requirement: Unencrypted BLE Communication Protocol
The system SHALL use unencrypted BLE characteristic read/write operations on custom UUIDs `7777` (write) and `8888` (notify) for commanding and receiving telemetry from the Anker F2000.

#### Scenario: Subscribing and writing to the BLE device
- **WHEN** the BLE client connects to the F2000
- **THEN** it successfully subscribes to characteristic `00008888-0000-1000-8000-00805f9b34fb` and writes command packets to `00007777-0000-1000-8000-00805f9b34fb` without any ECDH encryption handshake.

### Requirement: Structured Packet Telemetry Parsing
The system SHALL parse 102-byte telemetry packets (`0x49` subtype) and 14-byte state packets (`0x48` subtype) by validating the `09 ff 00 00 01` header and decoding individual byte registers.

#### Scenario: Validating and decoding a telemetry frame
- **WHEN** a notification frame starting with `09 ff 00 00 01` and subtype `0x49` is received
- **THEN** the parser successfully extracts battery, temperature, solar input power, AC outlet power, and serial numbers.

---

