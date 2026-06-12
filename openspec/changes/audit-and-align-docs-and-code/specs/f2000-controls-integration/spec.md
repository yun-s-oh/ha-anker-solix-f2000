## MODIFIED Requirements

### Requirement: Select Controls
The integration SHALL expose select entities to set `LED Brightness` (OFF, LOW, MID, HIGH, SOS), `Screen Brightness`, and `Screen Timeout` (20s, 30s, 1m, 5m, 30m).

#### Scenario: Set LED Brightness to HIGH
- **WHEN** the user selects "HIGH" from the LED Brightness entity dropdown
- **THEN** the integration sends the corresponding command frame to update the LED level.
