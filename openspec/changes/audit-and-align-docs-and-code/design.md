## Context

During the integration audit, several discrepancies were found where the code's behavior, configuration defaults, names, and icons diverged from the specifications and external documentation (the main `README.md` and `tests/README.md`). Reconciling these ensures a clear, unified, and correct state for the repository.

## Goals / Non-Goals

**Goals:**
*   Reconcile the 12V Car Port Master switch icon specification in `ha-sensors/spec.md` to use `"mdi:car-electric"`, as the previously specified `"mdi:car-power-outlet"` is non-existent in the Material Design Icons library.
*   Align the naming of the duration timers, shutdown select dropdowns, and charging sliders in `README.md` with the Python class definitions in `custom_components/anker_solix_f2000/`.
*   Document all standalone discovery and utility scripts in `tests/README.md` to assist developers.
*   Incorporate the detailed telemetry register bytes (such as AC and DC shutdown timers) into the active `ble-protocol/spec.md` for completeness.

**Non-Goals:**
*   Refactoring the telemetry data parsing or coordinator connection logic.
*   Adding new entities or modifying existing entity keys which could break user configurations.

## Decisions

### 1. Reconcile Switch Icon Specification
*   **Decision**: Update the specification in `ha-sensors/spec.md` to use `"mdi:car-electric"` instead of `"mdi:car-power-outlet"`.
*   **Rationale**: Since `"mdi:car-power-outlet"` does not exist, keeping the working and valid `"mdi:car-electric"` in the code and aligning the spec is the most robust path.

### 2. Treat Code Definitions as Source of Truth for Entity Names
*   **Decision**: Align `README.md` names (e.g. changing `"12V Car Port Timer"` to `"12V Car Port Timer Remaining"`) to match Python code definitions.
*   **Rationale**: Modifying entity names in Python code changes the default friendly names in Home Assistant, which can confuse users or alter display badges. Updating the documentation to match the stable code prevents breaking changes.

## Risks / Trade-offs

*   **Risk**: *None* (since the icon code remains unchanged, there is no risk of breaking custom user dashboards).
