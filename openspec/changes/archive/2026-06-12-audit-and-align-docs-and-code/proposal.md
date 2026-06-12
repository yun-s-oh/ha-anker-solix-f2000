## Why

Over the course of implementing and refining the Anker Solix F2000 Home Assistant integration, several discrepancies have emerged between the actual Python implementation, the active specifications, the main repository `README.md`, and the testing suite documentation. This audit and alignment change will reconcile all mismatched naming conventions, UI icons, default parameters, protocol registers, and testing docs to ensure the codebase and documentation are 100% correct, synchronized, and compliant with coding guidelines.

## What Changes

*   **Specification Icon Update**: Reconcile the `ha-sensors` specification to use the valid `mdi:car-electric` icon for the 12V Car Port Master switch (since the previously specified `mdi:car-power-outlet` does not exist in the Material Design Icons library).
*   **Documentation Alignment**: Standardize all entity names, select options, and default ranges across `README.md`, specifications, and Python source code.
*   **Protocol Spec Supplement**: Document missing telemetry byte registers (like AC and DC shutdown timers) in the main `ble-protocol` specification.
*   **Testing Suite Documentation**: Update `tests/README.md` to document all utility and discovery scripts developed during integration exploration.
*   **Code Linting Compliance**: Ensure all custom components and test scripts are fully clean of formatting/lint issues.

## Capabilities

### New Capabilities
*None*

### Modified Capabilities
- `ha-sensors`: Align entity names and correct the switch icon specification to `mdi:car-electric`.
- `f2000-controls-integration`: Standardize screen timeout and LED brightness option values.
- `failover-recovery`: Correct default polling rate and max reconnection delay ranges.
- `ble-protocol`: Supplement protocol specification with missing byte registers (AC and DC timers).
- `tests`: Document all diagnostic, utility, and discovery scripts in `tests/README.md`.

## Impact

*   **Custom Components**: *None* (no icon or code modifications are required for the switch icon since the code already implements `mdi:car-electric`).
*   **General Documentation**: [README.md](file:///Users/yunseokoh/Projects/ha-anker-solix-f2000/README.md) and [tests/README.md](file:///Users/yunseokoh/Projects/ha-anker-solix-f2000/tests/README.md) will be updated.
*   **Specifications**: Active spec files under [openspec/specs/](file:///Users/yunseokoh/Projects/ha-anker-solix-f2000/openspec/specs) will be modified to reconcile naming, default parameters, and protocol register details.
