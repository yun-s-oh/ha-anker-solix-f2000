## ADDED Requirements

### Requirement: Switch Controls
The integration SHALL expose switch entities to control `AC Output`, `DC Output`, and `Power Saving Mode` on the Anker F2000.

#### Scenario: Turn AC Output ON
- **WHEN** the user toggles the AC Output switch entity to ON in Home Assistant
- **THEN** the integration formats and sends the corresponding unencrypted BLE frame to the F2000.

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
