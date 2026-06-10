## Context

To implement device controls (AC/DC toggle, recharging power, LED state, display state, and timeouts) on the Anker F2000 via Home Assistant, we need to transition the integration from a read-only telemetry sensor platform to an interactive control platform. Since the F2000's control command structures are not fully documented in open-source libraries, we must build a robust exploration test framework first to verify and discover the exact byte sequences required to control the physical hardware.

## Goals / Non-Goals

**Goals:**
- Create an interactive BLE command-line exploration script `tests/explore_controls.py` to send custom unencrypted payload hexes and listen for state ACKs or command ACKs.
- Establish the architecture for adding `switch`, `select`, and `number` entities under `custom_components/anker_solix_f2000`.
- Document how to retrieve sensors and control the device in `README.md`.

**Non-Goals:**
- Overwriting the telemetry queries which are already working.

## Decisions

### 1. Standalone Exploration Framework Architecture
We will create `tests/explore_controls.py` using `bleak`. It will dynamically load the MAC address from `.env` and offer an interactive console menu:
1. **Send Raw Packet:** Prompts the user for a hex payload, calculates the 1-byte checksum, structures the unencrypted header (`09 ff 00 00 01`), and writes it to the WRITE_UUID.
2. **Listen & Sniff:** Automatically logs all incoming notifications from NOTIFY_UUID, printing them as beautifully formatted raw hex grids and decoded telemetry or state ACK blocks.
3. **Common Preset Tests:** Pre-bake common unencrypted command patterns to test toggling actions (e.g. attempting to send C1000 equivalent payloads in unencrypted frames).

```
[ User Input / Preset ] ──► [ Checksum Calculator ] ──► [ Raw BLE write to 00007777 ]
                                                                   │
                                                                   ▼
[ Real-time Log / Decoded State ] ◄── [ BLE notification from 00008888 ]
```

### 2. Home Assistant Platform Design
We will structure the component with new platform handlers:
- **[switch.py](/custom_components/anker_solix_f2000/switch.py)**: Exposes `ac_outlet_on` and `dc_12v_on` as HASS switches.
- **[select.py](/custom_components/anker_solix_f2000/select.py)**: Exposes dropdown menus for setting `led_state` (Off, Low, Mid, High, SOS) and screen timeouts.
- **[number.py](/custom_components/anker_solix_f2000/number.py)**: Exposes a slider for `ac_recharging_power`.

Each command write will trigger an immediate active query to update the state coordinator, guaranteeing instant state updates on the UI.

## Risks / Trade-offs

- **[Risk]**: Encryption required.
  - *Status*: **Resolved/Nullified**. Physical scanning and GATT characteristic inspection proved the Anker F2000 does not expose any encrypted session characteristics. All controls are verified to execute successfully via unencrypted command writes, making the integration highly lightweight and resilient.


## Discovered Protocol Registers & Command Structures

We have reverse-engineered, successfully tested, and programmatically verified the unencrypted BLE command structures and telemetry layout on the Anker F2000 physical hardware.

### 1. Unencrypted Packet Protocol Format
All inbound/outbound packets follow the structure:
- **Header Prefix**: `08 EE 00 00 00` (for command writes) or `09 FF 00 00 01` (for notifications)
- **Packet Type**: `0x01` (Telemetry/State/Aux) or `0x02` (Command/Control)
- **Sub-Type / Command ID**: The parameter identifier (e.g. `0x86` for AC, `0x02` for AC Timer)
- **Length**: `uint16 LE` (representing total packet size in bytes)
- **Payload**: The value to set (1 or 2 bytes, depending on command type)
- **Checksum**: `uint8` calculated as sum of preceding bytes & `0xFF`

### 2. Verified Control Opcodes (Command ID / Parameter Sub-Type)

| Control Function | Command ID | Payload Format | Values / Limits |
| --- | --- | --- | --- |
| **AC Sockets Toggle** | `0x86` | 1-Byte `uint8` | `0x00` = OFF, `0x01` = ON |
| **DC Sockets Toggle** | `0x87` | 1-Byte `uint8` | `0x00` = OFF, `0x01` = ON |
| **Power Saving Mode** | `0x8A` | 1-Byte `uint8` | `0x00` = OFF, `0x01` = ON |
| **LED Light Utility** | `0x8B` | 1-Byte `uint8` | `0` = Off, `1` = Low, `2` = Mid, `3` = High, `4` = SOS |
| **Screen Brightness** | `0x88` | 1-Byte `uint8` | `0` = Low, `1` = Mid, `2` = High, `3` = Max |
| **Screen Timeout** | `0x82` | 2-Byte LE `uint16` | Time in seconds: `20`, `30`, `60`, `300`, `1800` |
| **AC Charging Limit** | `0x80` | 2-Byte LE `uint16` | Watts limit: `200` to `2200` |
| **AC Output Timer** | `0x02` | 2-Byte LE `uint16` | Shutdown timer (seconds): `0` (disabled) or `300` to `86100` |
| **DC Output Timer** | `0x03` | 2-Byte LE `uint16` | Shutdown timer (seconds): `0` (disabled) or `300` to `86100` |

### 3. Telemetry Register Map (SubType 0x49 & 0x01 Frames)

- **AC Sockets Power**: Bytes `21-22` (LE `uint16` Watts)
- **DC Car Sockets Power**: Socket 1 is at bytes `33-34`, Socket 2 is at bytes `35-36` (LE `uint16` Watts)
- **AC Output Timer Remaining**: Bytes `9-10` (LE `uint16` seconds remaining)
- **DC Output Timer Remaining**: Bytes `13-14` (LE `uint16` seconds remaining)
- **AC Recharging Power limit**: Bytes `101-102` of the 122-byte Aux State frame (`sub_type 0x01`, LE `uint16` Watts)
- **Screen Timeout setting**: Bytes `105-106` of the 122-byte Aux State frame (`sub_type 0x01`, LE `uint16` seconds)


