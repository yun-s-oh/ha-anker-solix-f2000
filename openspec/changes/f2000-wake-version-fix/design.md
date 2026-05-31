## Context

The Anker Solix F2000's BLE radio goes to sleep when idle (not charging, AC/DC ports off) to save
power. To maintain continuous telemetry in HASS without physically pressing the IoT button, the
integration must proactively keep the device awake. Additionally, the CI release workflow
creates Git tags on commits that contain the old `manifest.json` version, leading to version
misalignment under HACS.

## Goals / Non-Goals

**Goals:**
- Implement a "DC Keep-Awake" configuration switch that automatically toggles the DC 12V port
  ON when AC is OFF and the unit is not charging, keeping the BLE radio active at virtually 0W
  drain.
- Align the GitHub Actions release workflow so that the Git tag is pushed *after* the updated
  `manifest.json` is committed to the main branch.

**Non-Goals:**
- Toggling the high-drain AC outlets to keep the device awake.
- Preventing the device from going to sleep if keep-awake is explicitly disabled by the user.

## Decisions

### Decision 1: Use DC 12V Keep-Awake Workaround
- **Options Considered**:
  - Option A: Toggle AC Output ON to keep the unit awake (high idle power draw: 15W–20W).
  - Option B: Toggle DC 12V Output ON (virtually 0W idle power draw).
- **Decision**: Option B.
- **Rationale**: Toggling the DC 12V outlet keeps the F2000's internal CPU and BLE radio active
  indefinitely while consuming almost no energy when no load is attached.

### Decision 2: Run CI Tag Bump in Dry-Run First
- **Options Considered**:
  - Option A: Create tag, then update and push manifest to main (current behavior).
  - Option B: Run tag action in dry-run mode, extract version, commit update, then tag.
- **Decision**: Option B.
- **Rationale**: Tagging the commit that already contains the updated `manifest.json` ensures that
  HACS successfully verifies version alignment under releases.

## Risks / Trade-offs

- **[Risk] User toggles DC off manually**: If the user manually toggles the DC port off, the
  device will eventually enter standby.
  - *Mitigation*: If "DC Keep-Awake" is enabled in HASS, the coordinator will automatically
    re-dispatch a DC ON command when the AC port is toggled off and the device is idle.
