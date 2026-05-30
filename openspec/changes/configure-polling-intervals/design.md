## Context

Currently, the custom component uses a static polling frequency (`DEFAULT_POLL_INTERVAL = 30`) and a static maximum reconnection limit (`MAX_RETRY_INTERVAL = 60`). Users want the ability to request a higher polling rate (e.g., every 5 seconds) for real-time telemetry, or lower rates to save battery and network bandwidth. Furthermore, they need a configurable reconnection retry limit (between 30 and 300 seconds) to adapt the failover engine to their local RF environment.

To support this cleanly, we need to introduce a Home Assistant `OptionsFlow` that modifies the configuration entry’s options, and dynamically updates the data coordinator and reconnection loops at runtime. We also need to package custom offline branding assets and update our integration guide for seamless HACS deployment, following standard patterns from Tuya and NeoVolt battery plugins.

## Goals / Non-Goals

**Goals:**
- **Dynamic Polling Configuration**: Change the default poll interval to 5 seconds and allow users to select between 5 and 30 seconds.
- **Configurable Max Retry Limits**: Change the default max retry limit to 30 seconds and allow users to select between 30 and 300 seconds.
- **Seamless Options Flow Integration**: Implement a standard options flow handler in `config_flow.py` with validated input fields.
- **Runtime Rescheduling**: Support updating the coordinator's update frequency and reconnection back-off dynamically when options change, without requiring an integration restart.
- **Offline Branding Support**: Generate and bundle a set of premium branding assets (logo/icon files) directly inside the component directory.
- **HACS Setup Instructions**: Revise the README to explain custom HACS repository installations clearly, following the structure and visual flow of established integrations (like Tuya and NeoVolt).

**Non-Goals:**
- **Per-entity Polling Frequency**: Custom polling speeds for specific sensors are out of scope. All entities will update together via the coordinator.
- **Arbitrary Input Ranges**: Disallow intervals outside the safe boundaries (5s - 30s for poll, 30s - 300s for max retry) to prevent BLE stack crashes.

## Decisions

### Decision 1: Option Flow Updates vs. Integration Restart
- **Option Considered**: Fully reloading/restarting the configuration entry when options change.
- **Decision**: Update the active coordinator configuration dynamically in an options update listener callback without restarting.
- **Rationale**: Re-creating the configuration entry tears down and re-establishes the physical Bleak GATT connection. By subscribing to the options update event via `entry.add_update_listener`, we can dynamically alter the coordinator's `update_interval` and the reconnection exponential back-off thresholds instantly, preserving connection state.

### Decision 2: Schema Keys and Constants Location
- **Option Considered**: Declaring validation schemas inside `config_flow.py` only.
- **Decision**: Declare the option schema keys and updated fallback defaults in `const.py` to be shared between `config_flow.py`, `coordinator.py`, and `__init__.py`.
- **Rationale**: Placing keys such as `CONF_POLL_INTERVAL` and `CONF_MAX_RETRY_INTERVAL` in `const.py` avoids duplicate string declarations and ensures type consistency.

### Decision 3: Local Offline Branding Assets vs. Brands Repository PRs
- **Option Considered**: Submitting a pull request to the `home-assistant/brands` GitHub repository.
- **Decision**: Deliver brand images locally by packaging them in the integration's new `brand/` directory (`custom_components/anker_solix_f2000/brand/`).
- **Rationale**: Modern Home Assistant versions (2026.3+) support and prioritize local `brand/` assets. This avoids submitting upstream pull requests, works completely offline, and renders instant logos throughout the user's dashboard during HACS custom installations.

### Decision 4: Installation Guide Structure
- **Option Considered**: Simple textual HACS instructions.
- **Decision**: Design a detailed HACS custom repository installation section inside `README.md` following the highly professional, visual layout of `neovoltBattery_HomeAssistantPlugin`.
- **Rationale**: A visual layout featuring HACS custom repository configuration menus reduces setup friction, assists novice smart home users, and gives the project a high-end product feel.

## Risks / Trade-offs

- **[Risk] RF Congestion with 5-Second Polling**: A high poll rate could saturate the Bluetooth controller queue, particularly on platforms with multiple BLE integrations.
  - *Mitigation*: Limit the minimum selectable polling interval to 5 seconds. The central Home Assistant `bluetooth` package manages query rates, and the bleak queue will safely serialize requests.
- **[Risk] Stale Reconnection Loops**: An active back-off loop might not read the updated max retry duration if it's stored in a local variable.
  - *Mitigation*: Ensure `_async_reconnect_loop` and `_async_update_data` access the max retry interval dynamically from the coordinator's config entry option properties.
