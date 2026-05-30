## Why

The Home Assistant Community Store (HACS) validation CI pipeline failed during testing because the repository lacks essential HACS configuration metadata. To allow the integration to be published and validated successfully on HACS, we need to add the required `hacs.json` configuration, include the necessary GitHub repository topics, and add the missing `issue_tracker` key to the integration's `manifest.json`.

## What Changes

- Create a new `hacs.json` file in the root directory.
- Update `custom_components/anker_solix_f2000/manifest.json` to include the `"issue_tracker"` key pointing to the GitHub repository's issue tracker.
- Document and ensure the GitHub repository has the required HACS topics (such as `home-assistant`, `integration`, `hacs`, `hacs-integration`).

## Capabilities

### New Capabilities
- `hacs-validation`: Outlines the requirements for HACS-compliant repository configurations, metadata attributes, and manifest structures.

### Modified Capabilities
<!-- None -->

## Impact

- Resolves all 3 HACS CI validation errors, enabling successful publishing and automatic updates within HACS.
- Updates metadata across `manifest.json` and a new `hacs.json` file, with zero impact on the core BLE integration code.
