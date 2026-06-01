## Context

Currently, the integration utilizes a periodic active poll of the `0x49` Telemetry packet to retrieve device statistics. Although the `0x49` Telemetry packet contains `ac_outlet_on` at byte index `63`, the fields `"twelve_volt_on"` and `"power_save_on"` are omitted from `parse_telemetry()`. Instead, they are only updated when the F2000 emits the `0x48` State ACK packet, which occurs passively when the official Anker app is running or immediately after a manual switch toggle command. Because the State ACK is not actively queried on startup, the state of the 12V Car Port Master and Power Saving Mode switches are undetermined (displaying as `Unknown`) upon Home Assistant restart.

Additionally, three read-only binary sensors (`ac_outlet_on`, `twelve_volt_on`, `power_save_on`) exist in `binary_sensor.py`, duplicating the exact states already managed by the respective switch entities in `switch.py`.

## Goals / Non-Goals

**Goals:**
- Update `parse_telemetry()` to parse `"twelve_volt_on"` and `"power_save_on"` from the `0x49` Telemetry packet.
- Ensure that the "12V Car Port Master" and "Power Saving Mode" switches populate their states immediately on integration startup/reconnect.
- Delete the redundant binary sensor entities for AC Sockets Master, 12V Car Port Master, and Power Saving Mode.
- Update `tests/mock_f2000.py` and `tests/test_mock_telemetry.py` so that all offline telemetry validation tests continue to pass.

**Non-Goals:**
- Modifying the unencrypted command packet builders or how switch toggles are executed.
- Modifying screen timeout, screen brightness, LED levels, or recharging power entity logic.

## Decisions

### Decision 1: Map `twelve_volt_on` to `dc_12v_port1_on` (`data[80]`) in Telemetry
- **Rationale**: The physical F2000 portable power station has a single master control command (`0x87`) to toggle the DC 12V outlets, turning both DC ports 1 and 2 ON or OFF together. In the unencrypted telemetry frame, `12V-1 On` is located at byte index `80`. Therefore, checking `bool(data[80])` in telemetry perfectly reflects the master 12V Car Port switch status.
- **Alternatives Considered**: Using `dc_12v_port2_on` (`data[81]`) or checking if either is ON. Both ports operate under the same master switch, but `data[80]` is the primary port indicator and is fully sufficient.

### Decision 2: Map `power_save_on` to `data[82]` in Telemetry
- **Rationale**: In the F2000 BLE protocol, byte index `82` of the `0x49` Telemetry packet is the dedicated status register for Power Saving Mode (`0x00` = Off, `0x01` = On). Extracting `bool(data[82])` ensures the switch status matches the device's actual configuration.
- **Alternatives Considered**: Relying on periodic background commands to query state. This is not supported by the unencrypted BLE protocol and would waste radio bandwidth.

### Decision 3: Delete Duplicate State Binary Sensors
- **Rationale**: Having both a `switch.anker_solix_f2000_...` and a `binary_sensor.anker_solix_f2000_...` for the exact same master toggles is redundant, increases integration clutter, and causes confusion for users building automations. Switch entities in Home Assistant natively maintain and display their current status, making these secondary binary sensors completely unnecessary.
- **Alternatives Considered**: Keeping them but marking them as diagnostic. This still leaves redundant entities in HASS registry. Deleting them is cleaner.

## Risks / Trade-offs

- **[Risk]** Mock unit tests in `tests/test_mock_telemetry.py` could fail due to missing fields in mock telemetry packets.
  - *Mitigation*: Update `tests/mock_f2000.py` and the unit test suite to populate and assert the new telemetry dictionary keys.
- **[Risk]** Users might have existing automations referencing the old binary sensor entities.
  - *Mitigation*: The release notes will clearly state that these binary sensors have been removed because the switch entities now support real-time state feedback. Automations should be updated to target the switch entities.
