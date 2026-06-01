## Why

Currently, when the Home Assistant integration restarts, the status of the "12V Car Port Master" and "Power Saving Mode" switches cannot be determined and displays as unknown. This occurs because these switch states are not parsed from the periodic `0x49` Main Telemetry frame, requiring a manual toggle (which triggers a `0x48` State ACK) to update their states. Tying status updates to manual controls creates an inconsistent user experience and prevents reliable automation after restarts.

## What Changes

- **12V Car Port Master State**: Map `twelve_volt_on` directly to `data[80]` (`12V DC1 On`) in the periodic `0x49` Telemetry packet parser so that its status is correctly updated on integration startup and periodic polls.
- **Power Saving Mode State**: Map `power_save_on` directly to `data[82]` (`Power Save On`) in the periodic `0x49` Telemetry packet parser.
- **Sensor Removal**: Remove the redundant and duplicate `AC Outlet Master State`, `12V Car Port Master State`, and `Power Save Mode State` binary sensors from `binary_sensor.py` as their status is already natively presented by the corresponding switch entities.
- **Testing**: Update unit tests and mocks to reflect telemetry packet changes.

## Capabilities

### New Capabilities

<!-- None needed -->

### Modified Capabilities

- `ha-sensors`: Remove redundant binary sensors (`ac_outlet_on`, `twelve_volt_on`, `power_save_on`) as they are fully represented by the corresponding switch entities.
- `ble-protocol`: Document `power_save_on` (Power Saving Mode) byte mapping at index `82` of the `0x49` Main Telemetry BLE packet.

## Impact

- **Affected Files**:
  - `custom_components/anker_solix_f2000/coordinator.py`
  - `custom_components/anker_solix_f2000/binary_sensor.py`
  - `tests/mock_f2000.py`
  - `tests/test_mock_telemetry.py`
- **Dependencies**: No external dependency changes.
