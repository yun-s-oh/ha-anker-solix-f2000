## Why

This proposal addresses four distinct usability and refinement enhancements to the Anker Solix F2000 HACS BLE integration:
1. **README Redesign**: The landing page lacks professional integration guidelines, exposed entities list, and redirect badges, hindering community adoption.
2. **Directory Renaming**: The `test-scripts/` directory deviates from standard Python conventions (which prefer `tests/`).
3. **Battery UI Bug**: The integrations panel and device cards in the Home Assistant UI show no battery percentage (or 0% previously) next to the Anker logo.
4. **Manual Setup Polling Options**: Users cannot configure active polling rates and failover retry limits directly during the initial manual configuration flow step.

## What Changes

- Overhaul `README.md` to provide a premium landing page incorporating badges, redirection shortcuts, exposed entities tables, and architecture diagrams.
- Rename the `test-scripts/` directory to `tests/` and update all associated imports, scripts, and spec references.
- Rename the primary battery entity description from `"Total Battery"` to `"Battery"` in `sensor.py` to enable HASS to display the battery percentage next to the device/integration logo.
- Extend `config_flow.py` and `strings.json` to accept and save `CONF_POLL_INTERVAL` and `CONF_MAX_RETRY_INTERVAL` during initial setup.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `ha-sensors`: Update requirements to reflect the `"Battery"` main entity and custom initial setup flow options.
- `test-scripts`: Rename capability to `tests` to reflect standard directory layouts.

## Impact

- **Affected Components**: `sensor.py`, `config_flow.py`, `strings.json`, and all standalone verification scripts under the `test/` directory.
- **Affected Documentation**: `README.md`, `agent-guidelines.md`.
