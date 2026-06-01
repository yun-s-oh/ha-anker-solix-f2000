## Why

The AC Sockets and 12V Car Port shutdown timers currently reset back to their nearest 5-minute boundaries whenever Home Assistant UI elements, voice assistants (e.g. Google Assistant, Apple HomeKit), or state-restoration routines synchronize state. This occurs because the rounded option string is written back to the integration, triggering redundant Bluetooth control commands that reset the countdown. Additionally, the repository landing `README.md` and `agent-guidelines.md` contain outdated directory structures and an unprofessional warning quote that needs to be refactored and moved to the dedicated `tests/README.md`.

## What Changes

* **Short-Circuit Timer Updates**: Add a check in `custom_components/anker_solix_f2000/select.py`'s `async_select_option` to immediately return if the requested option matches the current option, halting the feedback loop that resets active countdown timers.
* **Warning Rephrasing**: Remove the snarky "Yes — Anker decided to save milliwatts..." sentence in `README.md` and professionally rephrase the warning block to explain that the F2000 Bluetooth radio shuts off after 12 hours of inactivity or when the battery is fully drained, requiring manual button press reactivation.
* **Test Documentation Consolidation**: Move the detailed testing setup and script run instructions from `README.md` to `tests/README.md`, replacing it with a concise link to reduce redundancy.
* **Document Refinements**: 
  * Enrich `tests/README.md` with missing `--raw` flag and `pytest` assertion details.
  * Update `agent-guidelines.md` with an accurate directory tree layout mapping all current programmatic validation scripts under `tests/`.

## Capabilities

### New Capabilities
*None*

### Modified Capabilities
- `ha-sensors`: Refine the select entity update scenarios for the AC and DC shutdown timers to avoid redundant control writes when the state value is unchanged.

## Impact

* **Integration Core**: Modifies the `select` platform (`custom_components/anker_solix_f2000/select.py`) to prevent redundant BLE write commands.
* **Documentation**: Refactors and cleans up the root `README.md`, `tests/README.md`, and `agent-guidelines.md` files.
