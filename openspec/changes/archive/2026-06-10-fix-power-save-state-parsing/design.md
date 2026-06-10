## Context

The Anker Solix F2000 Bluetooth integration suffers from intermittent state discrepancies where the Power Saving Mode switch is shown as OFF in Home Assistant even when it is physically enabled on the hardware. 

This occurs because:
1. `parse_telemetry()` in `coordinator.py` extracts `"power_save_on"` from byte register `82` of the `0x49` packet.
2. In both the 102-byte Telemetry (`0x49`) and the 122-byte Auxiliary State (`0x01`) packets, byte `82` is actually padding (`0x00`), not the Power Save state.
3. Every time HASS queries telemetry or receives an auxiliary state packet, `parse_telemetry` parses `bool(data[82])` as `False`, overwriting the correct state received via `StateAck (0x48)` packets.
4. Physical BLE diagnostic sniffing confirmed that the real Power Save state register is located at index `117` in the 122-byte `0x01` Auxiliary State packet, and is absent in the 102-byte `0x49` Telemetry packet.

## Goals / Non-Goals

**Goals:**
- Correct the state register mapping for the Power Saving Mode switch so it accurately reflects the physical state.
- Prevent periodic telemetry polls and passive auxiliary state notifications from overwriting the correct Power Save state with `False`.
- Update the mock F2000 BLE packet generator and parser unit tests to match the corrected byte registers.

**Non-Goals:**
- Changing control commands (switch toggle actions).
- Modifying other sensors or settings.

## Decisions

### 1. Remove Power Save Parsing from Telemetry `0x49`
- **Approach**: Remove `"power_save_on"` from the `parse_telemetry` function return dictionary.
- **Rationale**: The 102-byte Telemetry packet does not contain the Power Save state at register `82` or any other byte. Eliminating it prevents the constant overwrite to `False`.

### 2. Add Power Save Parsing to Auxiliary State `0x01`
- **Approach**: Parse `"power_save_on": bool(data[117])` in `parse_aux_state` (which parses the 122-byte `0x01` Auxiliary State packet).
- **Rationale**: Sniffer traces confirmed index `117` toggles between `0x00` and `0x01` when Power Save is physically switched. Because `parse_aux_state` is updated in HASS alongside `parse_telemetry` when `0x01` is received, this ensures correct real-time feedback.

### 3. Update Unit Tests, Mocks, and Verification Scripts
- **Approach**:
  - In `tests/mock_f2000.py`'s `generate_telemetry`, remove `power_save_on` from the generated `0x49` payload.
  - In `tests/mock_f2000.py`'s `parse_packet` for `0x49`, remove `"power_save_on"`.
  - Update tests in `tests/test_mock_telemetry.py` to assert correct mock state mappings.
  - Update the `tests/validate_toggle_guard.py` script to parse `power_save_state` from byte index `117` in the `0x01` Aux State packet and stop querying index `82` in `0x49` Telemetry.

## Risks / Trade-offs

- **[Risk]** The Power Save state is no longer updated during the `0x49` Telemetry packet parsing.
  - *Mitigation*: The state is still updated by `StateAck (0x48)` (emitted passively on change) and `AuxState (0x01)` (emitted during query). This provides complete coverage on startup, reconnection, and command execution.
