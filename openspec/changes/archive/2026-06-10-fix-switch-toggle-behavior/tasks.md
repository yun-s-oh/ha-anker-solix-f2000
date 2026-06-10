## 1. Hardware Validation Test Script

- [x] 1.1 Create `tests/validate_toggle_guard.py` with BLE connection setup reusing pattern from `validate_ac_dc.py`
- [x] 1.2 Implement AC toggle test: query initial state, send same-state command, verify no state change; send opposite-state command, verify state changes; restore original state
- [x] 1.3 Implement DC toggle test: same pattern as AC test using command `0x87`
- [x] 1.4 Implement Power Save refresh test: send Power Save ON, wait 3s WITHOUT sending telemetry query, then query to check if it stayed ON; also test with immediate query to confirm revert behavior
- [x] 1.5 Run `tests/validate_toggle_guard.py` on physical F2000 hardware and verify all tests pass

## 2. Fix AC/DC Switch Toggle Guard Logic

- [x] 2.1 Add `_is_toggle_command` method to `AnkerSolixSwitch` in `switch.py` that returns `True` for `ac_outlet_on` and `twelve_volt_on` keys
- [x] 2.2 Add state-guard to `async_turn_on`: for toggle commands, skip BLE command if `self.is_on` is truthy (already ON); allow command when `self.is_on` is `None`
- [x] 2.3 Add state-guard to `async_turn_off`: for toggle commands, skip BLE command if `self.is_on is False` (already OFF); allow command when `self.is_on` is `None`
- [x] 2.4 Add debug logging for skipped commands

## 3. Fix Power Save Deferred Refresh Suppression

- [x] 3.1 Add `skip_refresh` keyword-only parameter (default `False`) to `async_send_control_command` in `coordinator.py`
- [x] 3.2 Conditionally skip scheduling `_async_deferred_refresh()` when `skip_refresh=True`
- [x] 3.3 In `switch.py`, pass `skip_refresh=True` when sending Power Save ON command (`key == "power_save_on"` and payload `0x01`)

## 4. Fix Optimistic State Updates in Coordinator

- [x] 4.1 Change optimistic update for `cmd_id == 0x86` (AC) from `bool(payload[0])` to `not self._state_data.get("ac_outlet_on", False)`
- [x] 4.2 Change optimistic update for `cmd_id == 0x87` (DC) from `bool(payload[0])` to `not self._state_data.get("twelve_volt_on", False)`
- [x] 4.3 Keep Power Save optimistic update as `bool(payload[0])` (payload-based, correct for explicit commands)

## 5. Documentation Updates

- [x] 5.1 Update `tests/README.md` with entry for the new `validate_toggle_guard.py` script
