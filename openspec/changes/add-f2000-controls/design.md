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
- **[switch.py](file:///Users/yunseokoh/Projects/ha-anker-solix-f2000/custom_components/anker_solix_f2000/switch.py)**: Exposes `ac_outlet_on` and `dc_12v_on` as HASS switches.
- **[select.py](file:///Users/yunseokoh/Projects/ha-anker-solix-f2000/custom_components/anker_solix_f2000/select.py)**: Exposes dropdown menus for setting `led_state` (Off, Low, Mid, High, SOS) and screen timeouts.
- **[number.py](file:///Users/yunseokoh/Projects/ha-anker-solix-f2000/custom_components/anker_solix_f2000/number.py)**: Exposes a slider for `ac_recharging_power`.

Each command write will trigger an immediate active query to update the state coordinator, guaranteeing instant state updates on the UI.

## Risks / Trade-offs

- **[Risk]**: Encryption required.
  - *Status*: **Resolved/Nullified**. Physical scanning and GATT characteristic inspection proved the Anker F2000 does not expose any encrypted session characteristics. All controls are verified to execute successfully via unencrypted command writes, making the integration highly lightweight and resilient.


