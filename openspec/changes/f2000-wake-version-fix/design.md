## Context

The Anker Solix F2000's BLE radio goes to sleep when idle (not charging, AC/DC ports off) to save
power. To maintain continuous telemetry in HASS without physically pressing the IoT button, the
integration must proactively keep the device awake. Additionally, the CI release workflow
creates Git tags on commits that contain the old `manifest.json` version, leading to version
misalignment under HACS.

## Goals / Non-Goals

**Goals:**
- Establish the active BLE keep-alive heartbeat polling via persistent local GATT connection,
  preventing the BLE radio and CPU from entering deep standby mode.
- Align the GitHub Actions release workflow so that the Git tag is pushed *after* the updated
  `manifest.json` is committed to the main branch.

**Non-Goals:**
- Toggling the high-drain AC outlets to keep the device awake.
- Preventing the device from going to sleep if keep-awake is explicitly disabled by the user.

## Decisions

### Decision 1: Use Active BLE Interrogation Heartbeat
- **Options Considered**:
  - Option A: Toggle physical ports/sensors ON to keep CPU active (port toggling tested as non-viable).
  - Option B: Maintain an active persistent GATT connection with periodic query heartbeats (mimicking an active app session).
- **Decision**: Option B.
- **Rationale**: Maintaining the BLE connection and sending a query every few seconds serves as an active heartbeat that keeps the F2000 awake natively, without needing to manipulate physical power ports or waste idle energy.

### Decision 2: Run CI Tag Bump in Dry-Run First
- **Options Considered**:
  - Option A: Create tag, then update and push manifest to main (current behavior).
  - Option B: Run tag action in dry-run mode, extract version, commit update, then tag.
- **Decision**: Option B.
- **Rationale**: Tagging the commit that already contains the updated `manifest.json` ensures that
  HACS successfully verifies version alignment under releases.

## Risks / Trade-offs

- **[Risk] Bluetooth timeout during restarts**: If Home Assistant restarts or BLE adapter goes offline, the persistent connection is severed. After 12 hours of absolute silence, the F2000 shuts down its BLE radio entirely.
  - *Mitigation*: Users who experience long downtimes can turn **Power Saving Mode OFF** on the F2000 (either physically or via HASS switch entity). This permanently overrides the auto-standby power rules, keeping the BLE radio broadcasting indefinitely.
