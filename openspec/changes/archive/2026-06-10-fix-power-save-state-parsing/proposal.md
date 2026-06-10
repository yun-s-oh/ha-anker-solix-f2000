## Why

Currently, the Anker Solix F2000 Bluetooth integration intermittently reports the Power Saving Mode switch state as OFF even when it is physically ON on the machine. This is caused by an offset mismatch and packet overwriting bug in the coordinator, where the integration incorrectly parses the `power_save_on` state from byte register `82` of the 102-byte Telemetry (`0x49`) and 122-byte Auxiliary State (`0x01`) packets. These registers are always `0x00` (padding) in those packets, which constantly overwrites the correct state (received via the `0x48` State ACK packet) with `False`.

## What Changes

- Update the BLE protocol specification to document that the Power Saving Mode state is located at byte register `117` in the 122-byte `0x01` Auxiliary State packet, and is not present in the 102-byte `0x49` Telemetry packet.
- Modify the coordinator parser to stop parsing `power_save_on` from the `0x49` Telemetry packet.
- Modify the coordinator parser to extract `power_save_on` from byte register `117` in the `0x01` Auxiliary State packet.
- Maintain existing state parsing from the `0x48` State ACK packet (byte register `11`).

## Capabilities

### New Capabilities

<!-- None -->

### Modified Capabilities

- `ble-protocol`: Correctly document the byte register for Power Saving Mode state in the `0x01` packet and clarify its absence in the `0x49` packet.
- `f2000-controls-integration`: Update the switch state retrieval logic to parse Power Saving Mode from byte `117` of the `0x01` packet.

## Impact

- `custom_components/anker_solix_f2000/coordinator.py`: Modify parsing registers in `parse_telemetry` and `parse_aux_state` / `_notification_handler`.
- `tests/mock_f2000.py` & `tests/test_mock_telemetry.py`: Update unit tests and mocks to reflect the new byte register layout.
- `tests/validate_toggle_guard.py`: Update the physical hardware validation script to query Power Save status from byte register 117 of the 0x01 packet.
