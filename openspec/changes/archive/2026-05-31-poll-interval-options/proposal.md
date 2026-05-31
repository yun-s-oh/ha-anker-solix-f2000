## Why

- The current default active telemetry polling rate of 5 seconds is too aggressive for some
  environments, potentially causing battery drain or congested Bluetooth traffic when multiple
  devices are nearby.
- Users need the flexibility to scale the active polling rate up to 300 seconds (5 minutes) and
  customize the maximum reconnection back-off ceiling up to 600 seconds (10 minutes).
- To prevent configuration errors, the reconnection delay (`max_retry_interval`) must always be
  greater than or equal to the active polling rate (`poll_interval`).
- Enabling setup of these polling parameters directly during automatic discovery (instead of only
  in manual setup or options) improves onboarding.

## What Changes

- Change the default telemetry polling rate (`poll_interval`) from 5 seconds to 30 seconds.
- Extend options and initial setup schemas to support `poll_interval` ranges from 5 to 300 seconds.
- Extend options and setup schemas to support `max_retry_interval` ranges from 30 to 600 seconds.
- Add validation logic ensuring `max_retry_interval` is greater than or equal to `poll_interval`.
- Update the auto-discovery step in `config_flow.py` to let users configure polling and retry
  intervals immediately upon discovery.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `ha-sensors`: Refine setup schemas, validation rules, and default telemetry polling rates.

## Impact

- **Affected Files**:
  - `custom_components/anker_solix_f2000/const.py` (Default constant updates)
  - `custom_components/anker_solix_f2000/config_flow.py` (Flow schemas and validation logic)
