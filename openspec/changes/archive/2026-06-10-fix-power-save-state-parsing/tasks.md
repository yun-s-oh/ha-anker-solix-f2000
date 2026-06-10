## 1. Modify Coordinator State Parsing

- [x] 1.1 In `coordinator.py`, remove the parsing of `power_save_on` from `parse_telemetry()`
- [x] 1.2 In `coordinator.py`, update `parse_aux_state()` to parse `power_save_on` from `data[117]`

## 2. Update Tests, Mocks, and Verification Scripts

- [x] 2.1 In `tests/validate_toggle_guard.py`, update `handle_notification()` to query `power_save_state` from byte index `117` in the `0x01` packet and stop checking `0x49`
- [x] 2.2 In `tests/mock_f2000.py`, remove `power_save_on` from `generate_telemetry()` and the `0x49` packet parser
- [x] 2.3 In `tests/mock_f2000.py`'s `parse_packet()`, add `power_save_on` parsing from `data[117]` for the `0x01` packet
- [x] 2.4 Update unit tests in `tests/test_mock_telemetry.py` to match the updated mock outputs and parsing logic
- [x] 2.5 Verify all unit tests compile and pass successfully

## 3. Verify on Physical Hardware

- [x] 3.1 Run `tests/validate_toggle_guard.py` on the physical F2000 to verify correct Power Save parsing during state query
