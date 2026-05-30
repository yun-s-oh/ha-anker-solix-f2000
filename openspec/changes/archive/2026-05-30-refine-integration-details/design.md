## Context

This change refines the Anker Solix F2000 HACS BLE integration. We address folder mapping standards, integration documentation completeness, a battery UI display bug, and manual entry flow usability.

## Goals / Non-Goals

**Goals:**
- Present a visual, detailed quickstart document in `README.md`.
- Move test scripts to the PEP 8 compliant `test/` directory.
- Allow Home Assistant to natively bind and display the battery state next to the integration card/logo.
- Allow manual entry setup steps to configure polling seconds and reconnection retry limit options.

**Non-Goals:**
- Refactoring the entire unencrypted BLE protocol parser itself.
- Modifying binary sensor or switch platform structures.

## Decisions

### 1. Renaming `total_pct` description to `"Battery"`
- **Why**: Home Assistant's UI looks for a primary battery sensor belonging to the device that is not diagnostic and named `"Battery"`. Setting this name registers the entity as the standard `sensor.<device_name>_battery`.
- **Alternatives Considered**: Modifying the frontend code using custom Lovelace cards, but renaming the entity is the standard, cleanest, and 100% native Home Assistant approach.

### 2. Manual Config Flow Setup Schema Options
- **Why**: Placing `CONF_POLL_INTERVAL` and `CONF_MAX_RETRY_INTERVAL` directly inside the initial configuration step ensures that the telemetry polling coordinator runs with customized parameters immediately on creation.
- **Alternatives Considered**: Leaving them only configurable in options, which forces users to perform a secondary setup step.

### 3. Folder renaming
- **Why**: Conforming with standard Python guidelines by moving `test-scripts/` to `test/`.

## Risks / Trade-offs

- **Risk**: Renaming `Total Battery` to `Battery` could break custom dashboards for existing users.
- **Mitigation**: This is a new HACS integration currently under active development. Standardizing the primary battery state before release prevents downstream breaking changes.
