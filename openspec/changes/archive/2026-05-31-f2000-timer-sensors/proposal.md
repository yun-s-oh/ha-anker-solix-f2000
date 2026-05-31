## Why

The current unencrypted BLE custom integration for the Anker Solix F2000 exposes the 12V Car
Port Remaining Timer as "12V Car Port 1 Timer Remaining", which is redundant since the F2000
only has a single logical 12V car port control. Additionally, there is no sensor entity
exposing the AC Sockets Shutdown Timer remaining duration, even though the unencrypted
telemetry frame already decodes it at bytes 9-10.

## What Changes

- Rename the `dc_12v_port1_timer` sensor from `"12V Car Port 1 Timer Remaining"` to
  `"12V Car Port Timer Remaining"`.
- Introduce a new numeric sensor `ac_outlet_timer` named `"AC Sockets Timer Remaining"` to
  track the remaining AC outlet shutdown duration in seconds.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `ha-sensors`: Add the `"AC Sockets Timer Remaining"` duration entity and refine the
  `"12V Car Port 1 Timer Remaining"` duration entity name.

## Impact

- **Affected Files**:
  - `custom_components/anker_solix_f2000/sensor.py`
