## Why

- The primary battery sensor (`total_pct`) represents the combined total battery. However, when
  no external expansion battery is connected, the F2000 firmware unreliably broadcasts it as a
  static `100%`, causing the Home Assistant main battery badge next to the logo to be stuck.
- The `"12V Car Port Master"` switch currently maps to `"mdi:car-connector"`, which does not exist
  in standard MDI packages and fails to render an icon in Home Assistant.
- The pre-generated shutdown timer select options go up to 23 hours and 55 minutes (86,100 seconds),
  which exceeds the 2-byte uint16 limit (65,535 seconds) and causes an `OverflowError: int too big
  to convert` when written over BLE.
- The CI release pipeline does not detect `major` or `breaking` keywords to trigger major version
  bumps (forcing everything to be minor or patch).
- The `agent-guidelines.md` file contains outdated reference paths to archived changes, and
  `README.md` should be updated with our timer refinements.

## What Changes

- Implement a smart dynamic fallback in the primary `"Battery"` sensor entity: if no external
  battery is connected, fall back and return the accurate `internal_pct` telemetry value.
- Update `"12V Car Port Master"` switch to use the standard MDI icon `"mdi:car-power-outlet"`.
- Cap the pre-generated select dropdown options for both AC and DC shutdown timers to 18 hours
  (64,800 seconds) to fit within the 2-byte uint16 BLE packet constraint and resolve the overflow crash.
- Refactor the `Determine bump type` step in `.github/workflows/release.yaml` to detect
  `major`/`breaking` commit keywords.
- Update `agent-guidelines.md` and `README.md` to reflect current directories and entities.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `ha-sensors`: Implement smart fallback for `total_pct`, correct the 12V Car Port Master icon, and
  cap select timers at 18 hours to prevent integer overflow.
- `release`: Add `major`/`breaking` keyword detection to the CI release versioning step.
- `agent-guidelines`: Correct outdated references to archived change files in developer/agent guidelines.

## Impact

- **Affected Files**:
  - `custom_components/anker_solix_f2000/sensor.py`
  - `custom_components/anker_solix_f2000/switch.py`
  - `.github/workflows/release.yaml`
  - `README.md`
  - `agent-guidelines.md`
