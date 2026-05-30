# Anker Solix F2000 (PowerHouse 767) BLE Protocol Specification

This specification documents the local Bluetooth Low Energy (BLE) communication protocol for the Anker Solix F2000 portable power station. The device uses an unencrypted, byte-oriented protocol for telemetry and commands.

## ADDED Requirements

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

## 🏗️ GATT Services & Characteristics

The F2000 uses a custom GATT service profile for communication:

| Component | UUID | Properties | Description |
|---|---|---|---|
| **Service** | `014bf5da-0000-1000-8000-00805f9b34fb` | - | Primary F2000 BLE service |
| **Command (Write)** | `00007777-0000-1000-8000-00805f9b34fb` | Write Without Response | For writing control command queries |
| **Telemetry (Notify)** | `00008888-0000-1000-8000-00805f9b34fb` | Notify | Emits raw telemetry and state frames |

> [!WARNING]
> The F2000 is **not compatible** with the newer encrypted "SolixBLE" protocol (UUID service `8c850001-...` with `8c850003` characteristics). Attempting to pair or perform ECDH key-exchange on the newer service will result in GATT connection failures or `BleakCharacteristicNotFoundError`.

---

## 📥 Inbound Packets (Notifications on `8888`)

All notification frames broadcast by the device on the `8888` characteristic begin with a standard header:

```text
Byte 0-4:  09 FF 00 00 01  (Standard Header)
Byte 5:    PacketType      (0x01 = Telemetry/State, 0x02 = Command Ack)
Byte 6:    SubType         (0x01/0x48/0x49 = Specific Data Sub-Type)
Byte 7-8:  PacketLength    (uint16 LE)
Byte 9+:   Payload data bytes
```

### 1. State Ack Packet (`SubType = 0x48`, Length = 14 bytes)
Emitted passively every ~3 seconds or immediately after a control state change.

| Byte Index | Field Name | Type / Format | Description |
|---|---|---|---|
| 0–4 | Header | `bytes[5]` | `09 FF 00 00 01` |
| 5 | PacketType | `uint8` | `0x01` (Telemetry/State) |
| 6 | SubType | `uint8` | `0x48` (State Ack) |
| 7–8 | Length | `uint16 LE` | `0x000E` (14 bytes total) |
| 9 | AC Sockets On | `bool / uint8` | `0x00` = Off, `0x01` = On |
| 10 | 12V DC Out On | `bool / uint8` | `0x00` = Off, `0x01` = On |
| 11 | Power Save On | `bool / uint8` | `0x00` = Off, `0x01` = On |
| 12 | LED Light State | `uint8` | `0` = Off, `1` = Low, `2` = Mid, `3` = High, `4` = SOS |
| 13 | Checksum | `uint8` | Sum of all preceding bytes & `0xFF` |

---

### 2. Main Telemetry Packet (`SubType = 0x49`, Length = 102 bytes)
Emitted in response to a telemetry query command. Contains full sensor statistics.

| Byte Index | Field Name | Type / Format | Scaling / Units | Description |
|---|---|---|---|---|
| 0–4 | Header | `bytes[5]` | - | `09 FF 00 00 01` |
| 5 | PacketType | `uint8` | - | `0x01` (Telemetry/State) |
| 6 | SubType | `uint8` | - | `0x49` (Telemetry) |
| 7–8 | Length | `uint16 LE` | - | `0x0066` (102 bytes total) |
| 13–14 | 12V Timer | `uint16 LE` | seconds | Remaining 12V output timer |
| 17 | Time Rem Hours | `uint8` | ÷10 (hours) | Time remaining hours partial |
| 18 | Time Rem Days | `uint8` | days | Time remaining days |
| 19–20 | AC Input Watts | `uint16 LE` | W | AC charging power input |
| 21–22 | AC Output Watts| `uint16 LE` | W | AC socket output power |
| 23–24 | USB-C1 Watts | `uint16 LE` | W | USB-C Port 1 power |
| 25–26 | USB-C2 Watts | `uint16 LE` | W | USB-C Port 2 power |
| 27–28 | USB-C3 Watts | `uint16 LE` | W | USB-C Port 3 power |
| 29–30 | USB-A1 Watts | `uint16 LE` | W | USB-A Port 1 power |
| 31–32 | USB-A2 Watts | `uint16 LE` | W | USB-A Port 2 power |
| 33–34 | 12V DC1 Watts | `uint16 LE` | W | Car Socket 1 power |
| 35–36 | 12V DC2 Watts | `uint16 LE` | W | Car Socket 2 power |
| 37–38 | Solar In Watts | `uint16 LE` | W | Solar charging input power |
| 39–40 | Total In Watts | `uint16 LE` | W | Aggregated total input power |
| 41–42 | Total Out Watts| `uint16 LE` | W | Aggregated total output power |
| 63 | AC Sockets On | `bool / uint8` | - | `0x00` = Off, `0x01` = On |
| 66 | Int Battery Temp| `uint8` | °C | Main Internal battery temperature |
| 67 | Ext Battery Temp| `uint8` | °C | Expansion Battery temperature |
| 68 | Battery State | `uint8` | - | `0` = Idle, `1` = Discharging, `2` = Charging |
| 70 | Int Battery % | `uint8` | % | Internal battery State of Charge |
| 71 | Ext Battery % | `uint8` | % | Expansion battery State of Charge |
| 72 | Total Battery % | `uint8` | % | Combined battery State of Charge |
| 75 | USB-C1 On | `bool / uint8` | - | USB-C Port 1 status |
| 76 | USB-C2 On | `bool / uint8` | - | USB-C Port 2 status |
| 77 | USB-C3 On | `bool / uint8` | - | USB-C Port 3 status |
| 78 | USB-A1 On | `bool / uint8` | - | USB-A Port 1 status |
| 79 | USB-A2 On | `bool / uint8` | - | USB-A Port 2 status |
| 80 | 12V DC1 On | `bool / uint8` | - | Car Socket 1 status |
| 81 | 12V DC2 On | `bool / uint8` | - | Car Socket 2 status |
| 85–100| Device Serial | `char[16]` | ASCII string | Serial Number (e.g. `AZV25N0F...`) |
| 101 | Checksum | `uint8` | - | Sum of preceding bytes & `0xFF` |

---

### 3. Auxiliary State Packet (`SubType = 0x01`, Length = 122 bytes)
Emitted passively alongside telemetry. Contains serial metadata, display timers, and hardware limits.

| Byte Index | Field Name | Type / Format | Description |
|---|---|---|---|
| 0–4 | Header | `bytes[5]` | `09 FF 00 00 01` |
| 5 | PacketType | `uint8` | `0x01` (Telemetry/State) |
| 6 | SubType | `uint8` | `0x01` (Aux State) |
| 7–8 | Length | `uint16 LE` | `0x007A` (122 bytes total) |
| 82–97 | Device Serial | `char[16]` | ASCII string duplication for verification |
| 121 | Checksum | `uint8` | Sum of preceding bytes & `0xFF` |

---

## 📤 Outbound Packets (Commands on `7777`)

Control commands written to the write-without-response `7777` characteristic follow a strict command structure:

```text
Header:     08 EE 00 00 00 02  (Standard Command Header; or 01 for queries)
Byte 6:     CommandType/ID     (Toggles or Parameter keys)
Byte 7:     Parameter Length   (uint8)
Byte 8+:    Parameter Bytes    (Command variables)
Last Byte:  Checksum           (Sum of all preceding bytes & 0xFF)
```

### 1. Telemetry Query Command
Used to request a fresh 102-byte `0x49` Telemetry frame. This keeps the BLE radio awake and overrides sleep timers.
*   **Payload (10 bytes)**: `08 EE 00 00 00 01 01 0A 00 02`
*   *Note*: Byte 5 is `01` (Query Format). Byte 6 is `01` (Query ID). Checksum at Byte 9 is `02`.

### 2. Control Command IDs
All control commands use the standard `02` header (`08 EE 00 00 00 02`):

| Command Name | Command ID | Parameter Length | Parameter Values |
|---|---|---|---|
| **Toggle AC Sockets** | `0x86` | 1 | `0x00` = Off, `0x01` = On |
| **Toggle 12V DC Out** | `0x87` | 1 | `0x00` = Off, `0x01` = On |
| **Set LED Light** | `0x8B` | 1 | `0x00` = Off, `0x01` = Low, `0x02` = Mid, `0x03` = High, `0x04` = SOS |
| **Toggle Power Save** | `0x8A` | 1 | `0x00` = Off, `0x01` = On |
| **Screen Timeout** | `0x82` | 1 | Time in seconds |
| **Screen Brightness**| `0x88` | 1 | `0x00` = Low to `0x03` = Max |
