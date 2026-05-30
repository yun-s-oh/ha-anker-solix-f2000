## Why

Currently, the Anker Solix F2000 Home Assistant integration polls for BLE telemetry at a hardcoded 30-second interval, and uses a hardcoded 60-second maximum reconnection retry back-off limit. While 30 seconds keeps the connection alive, many users desire higher resolution real-time telemetry (such as 5 seconds) to track power generation and consumption dynamics during home appliance activity. Conversely, hardcoding these intervals prevents advanced users from optimizing Bluetooth radio bandwidth, avoiding congestion, and adjusting reconnection schedules to fit their specific home network density.

Furthermore, during Home Assistant system startups, the Bluetooth adapter might not be fully initialized or the F2000 might not have broadcasted its BLE advertisement yet. Currently, if the BLE device is not discovered on startup, the integration setup fails permanently. Raising a dynamic retry exception is required to let HASS automatically recover in the background.

In addition, the repository currently lacks clear HACS custom repository installation instructions in the README and does not package premium, high-quality local branding assets (icons/logos). This limits the visual presentation of the integration inside the Home Assistant and HACS dashboards.

## What Changes

- **Modify default poll interval** from 30 seconds to 5 seconds to provide higher frequency telemetry.
- **Modify maximum retry back-off** from 60 seconds to 30 seconds by default for faster reconnection.
- **Add Integration Options Flow**: Implement Home Assistant Options Flow (`options_flow`), allowing users to click "Configure" on the integration in the UI and dynamically change these intervals:
  - **Default Poll Interval**: Selectable between 5 seconds and 30 seconds.
  - **Max Polling / Reconnection Back-Off**: Selectable between 30 seconds and 300 seconds.
- **Dynamic Coordinator Adaptation**: Update the `BluetoothDataUpdateCoordinator` to dynamically read these intervals from the configuration entry options, automatically rescheduling update timers when modified.
- **Resilient Startup Retry Logic**: In `__init__.py`, raise HASS `ConfigEntryNotReady` if the F2000 BLE device is not discovered at boot, enabling Home Assistant to safely schedule automatic background retries instead of failing permanently.
- **HACS Custom Repository Installation Guide**: Revise and expand `README.md` to detail clean HACS installation procedures, referencing pattern structures from official and community integrations (such as Tuya and NeoVolt).
- **Local Brand Assets Integration**: Implement local brand image delivery by placing high-quality custom Anker Solix icons and logos inside a new `brand/` directory inside the custom component, enabling native offline brand rendering inside Home Assistant.

## Capabilities

### New Capabilities

*(None)*

### Modified Capabilities

- `ha-sensors`: Polling update interval requirements are changing from a static 30-second period to a user-configurable frequency (ranging from 5 to 30 seconds).
- `failover-recovery`: Reconnection exponential back-off schedules are changing from hardcoded limits to user-configurable maximum thresholds (ranging from 30 to 300 seconds).

## Impact

- **Affected Files**:
  - `custom_components/anker_solix_f2000/const.py`: Update default polling/retry intervals and define config options schema keys.
  - `custom_components/anker_solix_f2000/config_flow.py`: Register and implement the options flow handler.
  - `custom_components/anker_solix_f2000/coordinator.py`: Dynamically load update intervals and reconnection schedules from config entry options, and listen for config entry options updates.
  - `README.md`: Expand with a dedicated HACS integration setup section.
  - `custom_components/anker_solix_f2000/brand/`: New directory containing brand assets (`icon.png`, `logo.png`, `dark_icon.png`, `dark_logo.png`).
- **Dependencies**: No new external package dependencies are introduced.
- **User Interface**: Adds a new configuration options modal in the Home Assistant integrations dashboard, and registers offline branding icons across device/entity pages.
