## ADDED Requirements

### Requirement: AC Sockets Timer Remaining Entity
The integration SHALL expose the remaining AC outlet shutdown duration in seconds as a standard Home
Assistant sensor entity named `"AC Sockets Timer Remaining"`.

#### Scenario: Continuous AC socket timer updates
- **WHEN** the F2000 is active and the AC sockets master shutdown timer is configured
- **THEN** the sensor `sensor.<device_name>_ac_sockets_timer_remaining` SHALL update with the
  remaining duration in seconds.

## RENAMED Requirements

### Requirement: 12V Car Port Timer Remaining Entity
FROM: "12V Car Port 1 Timer Remaining"
TO: "12V Car Port Timer Remaining"
