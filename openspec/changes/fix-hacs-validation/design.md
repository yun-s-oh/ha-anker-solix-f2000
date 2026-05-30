## Context

The repository failed three vital HACS validation checks because of missing HACS metadata file (`hacs.json`), missing integration `issue_tracker` in `manifest.json`, and missing topics on the GitHub repository settings.

## Goals / Non-Goals

**Goals:**
- Create a compliant `hacs.json` file.
- Update `manifest.json` with the required `"issue_tracker"` key.
- Outline steps to set the correct repository topics in GitHub settings.

**Non-Goals:**
- Altering core BLE protocol integration logics or HASS entity mappings.

## Decisions

### 1. Structure of `hacs.json`
We will create a root `hacs.json` file specifying the custom HACS integration information:
```json
{
  "name": "Anker Solix F2000",
  "render_readme": true
}
```
*Rationale:* `render_readme` ensures HACS renders our detailed landing page quickstart inside the HACS dashboard UI.

### 2. Integration Manifest Update
Add the required `issue_tracker` metadata key to the `manifest.json` file:
```json
  "issue_tracker": "https://github.com/yun-s-oh/ha-anker-solix-f2000/issues"
```
*Rationale:* This maps HACS and Home Assistant user errors directly to the correct repository tracking page.

### 3. GitHub Repository Topics Update
Instruct the repository owner to configure the following GitHub topics in their Repository settings (under "About"):
* `home-assistant`, `integration`, `hacs`, `hacs-integration`

## Risks / Trade-offs

- **[Risk]**: HACS Validation CI continues to fail on Topics check.
  - *Mitigation*: The user must update the topics in the GitHub repository's web interface, as this setting cannot be configured via local git commits.
