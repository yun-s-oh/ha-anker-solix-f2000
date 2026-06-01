## 1. Protocol Parsing Updates

- [x] 1.1 Update `parse_telemetry` in `coordinator.py` to decode `twelve_volt_on` from `data[80]`
- [x] 1.2 Update `parse_telemetry` in `coordinator.py` to decode `power_save_on` from `data[82]`

## 2. Sensor Registry Refinement

- [x] 2.1 Remove duplicate binary sensors from `BINARY_SENSOR_DESCRIPTIONS` in `binary_sensor.py`

## 3. Test Suite Integration

- [x] 3.1 Update `generate_telemetry` in `tests/mock_f2000.py` to include mock payload bytes for `power_save` and `twelve_volt`
- [x] 3.2 Update `parse_packet` in `tests/mock_f2000.py` to parse `power_save_on` and `twelve_volt_on` from mock telemetry frames
- [x] 3.3 Update unit tests in `tests/test_mock_telemetry.py` to assert correct telemetry-based parsing of master switch states
- [x] 3.4 Execute test suite via `pytest` to verify all mock tests pass cleanly
