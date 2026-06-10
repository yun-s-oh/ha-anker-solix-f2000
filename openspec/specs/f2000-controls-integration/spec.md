# f2000-controls-integration Specification

## Purpose
TBD - created by archiving change add-f2000-controls. Update Purpose after archive.
## Requirements
### Requirement: Switch Controls
The integration SHALL expose switch entities to control `AC Output`, `DC Output`, and `Power Saving Mode` on the Anker F2000. Because the F2000's BLE commands `0x86` (AC) and `0x87` (DC) behave as toggles that flip the current state regardless of payload value, the AC and DC switch entities SHALL implement state-guarded toggle logic: `turn_on` SHALL be a no-op when the device is already ON, and `turn_off` SHALL be a no-op when the device is already OFF. When the current state is unknown (`None`), the command SHALL be sent unconditionally. The Power Saving Mode switch (`0x8A`) respects the ON/OFF payload and SHALL NOT use toggle guard logic. However, the integration SHALL suppress the deferred telemetry refresh after sending a Power Save ON command to prevent BLE activity from causing the F2000 to auto-exit Power Save mode. The coordinator SHALL use state-inversion for optimistic updates on AC/DC commands and payload-based updates for Power Save.

#### Scenario: Turn AC Output ON when currently OFF
- **WHEN** the user calls `turn_on` on the AC Output switch entity and the current state is OFF
- **THEN** the integration sends the BLE toggle command (`0x86`) and the AC output toggles to ON.

#### Scenario: Turn AC Output ON when already ON
- **WHEN** the user calls `turn_on` on the AC Output switch entity and the current state is already ON
- **THEN** the integration SHALL NOT send any BLE command, preventing an unintended toggle to OFF.

#### Scenario: Turn DC Output OFF when already OFF
- **WHEN** the user calls `turn_off` on the DC Output switch entity and the current state is already OFF
- **THEN** the integration SHALL NOT send any BLE command, preventing an unintended toggle to ON.

#### Scenario: Turn Power Save ON
- **WHEN** the user calls `turn_on` on the Power Saving Mode switch entity
- **THEN** the integration sends the BLE command (`0x8A`) with payload `0x01` and SHALL NOT schedule a deferred telemetry refresh, allowing the device to remain in Power Save mode.

#### Scenario: Optimistic state update after AC/DC toggle command
- **WHEN** a toggle command is sent for AC or DC
- **THEN** the coordinator SHALL optimistically update the local state by inverting the current known state.

#### Scenario: Send command when state is unknown
- **WHEN** the user calls `turn_on` or `turn_off` on any switch entity and the current state is `None` (no telemetry received yet)
- **THEN** the integration SHALL send the BLE command unconditionally.

### Requirement: Select Controls
The integration SHALL expose select entities to set `LED Brightness` (Off, Low, Mid, High), `Screen Brightness`, and `Screen Timeout` (20s, 30s, 1min, 5mins, 30mins).

#### Scenario: Set LED Brightness to HIGH
- **WHEN** the user selects "High" from the LED Brightness entity dropdown
- **THEN** the integration sends the corresponding command frame to update the LED level.

### Requirement: AC Recharging Power Control
The integration SHALL expose a number entity to configure the `AC Recharging Power` limit from 200W to 2200W in increments of 100W.

#### Scenario: Adjust recharging power to 500W
- **WHEN** the user adjusts the number entity value to 500
- **THEN** the integration sends the command setting the recharging rate to 500W.

