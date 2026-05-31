## Why

Currently, the `ha-anker-solix-f2000` Home Assistant integration only supports monitoring sensors (telemetry) and does not allow users to control any settings on the F2000. Enabling controls (such as toggling AC/DC outputs, power saving modes, LED bar levels, recharging power, and screen configurations) will elevate the integration to a full-featured control platform, allowing users to automate their power station based on home events.

## What Changes

- Develop a standalone, interactive exploration test script under `tests/` to connect, send, and sniff BLE control command packets for the F2000.
- Implement the successfully verified control switches, selectors, and number configuration entities inside Home Assistant.
- Update `README.md` to document the control entity features and how developers can utilize the test scripts.

## Capabilities

### New Capabilities
- `f2000-controls-exploration`: Requirements and frameworks for testing, sniffing, and discovering unencrypted or encrypted F2000 BLE control commands.
- `f2000-controls-integration`: Exposing device control actions (switches, selectors, numbers) in Home Assistant.

### Modified Capabilities
<!-- None -->

## Impact

- Adds new Home Assistant switch entities (AC output, DC output, Power Saving Mode, LED SOS Mode).
- Adds new Home Assistant select entities (LED Brightness, Screen Brightness, Screen Timeout).
- Adds a new Home Assistant number entity (AC Recharging Power limit from 200W to 2200W).
- Expands the `tests/` directory with exploration scripts.
