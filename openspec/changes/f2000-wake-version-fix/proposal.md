## Why

The Anker Solix F2000 enters a low-power deep standby state when it is not charging and both AC
and DC outlet ports are turned OFF. In this standby state, the physical BLE radio is powered
down, preventing the Home Assistant integration from connecting or querying telemetry sensors.
Additionally, the GitHub Actions release workflow pushes the new Git tag before updating the
`manifest.json` version, leading to version misalignment inside the HACS integration directory.

## What Changes

- **Automatic DC Keep-Awake Mechanism**: Investigate and implement an automatic "DC Keep-Awake"
  switch in HASS. Toggling the DC 12V output (car socket) ON keeps the unit's CPU and BLE radio
  active indefinitely. Unlike the AC inverter (which has a 15W–20W idle drain), the DC 12V rail
  draws virtually 0W when idle, making it a highly efficient keep-awake channel.
- **GitHub Release Workflow Restructuring**: Refactor `.github/workflows/release.yaml` to run
  the tag-bump action in a dry-run mode first, extract the calculated next version, commit
  and push the updated `manifest.json` to the `main` branch, and then create the Git tag and
  release on that latest commit.

## Capabilities

### New Capabilities

- `f2000-keep-awake`: Keeps the F2000 CPU and BLE radio active using an efficient
  DC keep-awake toggle.
- `automated-version-alignment`: Restructures the CI release workflow to ensure tag
  and manifest version synchronization.

### Modified Capabilities

None.

## Impact

- **Affected Files**:
  - `custom_components/anker_solix_f2000/coordinator.py`
  - `.github/workflows/release.yaml`
  - `custom_components/anker_solix_f2000/manifest.json`
