## Why

The Anker F2000's BLE switch controls have two distinct bugs:

1. **AC/DC Toggle Bug**: Commands `0x86` (AC) and `0x87` (DC) behave as **toggles** — they flip the current state regardless of the payload value. The current `switch.py` assumes explicit ON/OFF semantics, causing `turn_off` to toggle ON when already OFF, and vice versa.

2. **Power Save Auto-Revert Bug**: Command `0x8A` (Power Save) does respect the ON/OFF payload, but Power Save frequently reverts to OFF within ~1 second of being turned ON. The likely cause is the integration's deferred telemetry refresh (`_async_deferred_refresh`) and periodic polling sending active BLE queries that cause the F2000 to auto-exit Power Save mode.

The optimistic state update in `coordinator.py` is also incorrect for AC/DC (sets state based on payload rather than inverting current state for toggle commands).

## What Changes

- **State-guarded toggle logic for AC/DC in `switch.py`**: Add pre-send state checks so `turn_on` is a no-op when already ON, and `turn_off` is a no-op when already OFF. This prevents unintended toggles.
- **Fix optimistic state updates for AC/DC in `coordinator.py`**: Change from payload-based to state-inversion to reflect toggle behavior.
- **Skip deferred refresh for Power Save commands in `coordinator.py`**: After sending a Power Save ON command, suppress the 0.5s deferred telemetry query to prevent the BLE activity from causing the device to auto-exit Power Save mode.
- **Update protocol documentation**: Correct specs to document AC/DC as toggles and Power Save's sensitivity to BLE polling activity.
- **Add a BLE validation test script**: Create a targeted test script to verify toggle guard behavior and diagnose Power Save revert timing on physical hardware.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `f2000-controls-integration`: AC/DC switch controls must implement state-guarded toggle logic. Power Save command must suppress the deferred telemetry refresh to prevent auto-revert.
- `ble-protocol`: Protocol documentation must be corrected to reflect that `0x86` (AC) and `0x87` (DC) are toggles. Power Save (`0x8A`) respects payload but is sensitive to subsequent BLE activity.

## Impact

- **`custom_components/anker_solix_f2000/switch.py`**: State guard logic in `async_turn_on` / `async_turn_off` for AC/DC switches.
- **`custom_components/anker_solix_f2000/coordinator.py`**: Optimistic state update changes for AC/DC; conditional deferred refresh suppression for Power Save commands.
- **`tests/`**: New validation test script for toggle and Power Save behavior.
- **`openspec/specs/ble-protocol/spec.md`**: Protocol documentation corrections.
- **`openspec/specs/f2000-controls-integration/spec.md`**: Requirements update.
