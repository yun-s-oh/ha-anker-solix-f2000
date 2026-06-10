# f2000-controls-integration Specification

## Purpose
This specification defines the Home Assistant integration entities (switches, selects, numbers) exposed to control operational parameters of the Anker Solix F2000 over BLE. It covers the logic for changing AC Output, DC Output, Power Saving Mode, LED light intensity, screen brightness/timeout settings, and AC charging current limit thresholds.
## Requirements
### Requirement: Switch Controls
The integration SHALL expose switch entities to control `AC Output`, `DC Output`, and `Power Saving Mode` on the Anker F2000. The integration SHALL update the state of the Power Saving Mode switch entity based on the `power_save_on` state received via the 14-byte `0x48` State ACK packet (byte register `11`) and the 122-byte `0x01` Auxiliary State packet (byte register `117`), and SHALL NOT query or update the Power Saving Mode state from the 102-byte `0x49` Telemetry packet.

#### Scenario: Turn AC Output ON
- **WHEN** the user toggles the AC Output switch entity to ON in Home Assistant
- **THEN** the integration formats and sends the corresponding unencrypted BLE frame to the F2000.

#### Scenario: Update Power Saving Mode switch state
- **WHEN** HASS receives a 122-byte Auxiliary State packet with Power Save set to ON at byte register 117
- **THEN** HASS updates the Power Saving Mode switch entity state to ON.

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

