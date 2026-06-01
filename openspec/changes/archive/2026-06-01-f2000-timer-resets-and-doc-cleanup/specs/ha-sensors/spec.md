## ADDED Requirements

### Requirement: Redundant Timer Update Suppression
To prevent active countdown timers from being reset by automated dashboard synchronizations, voice assistants, or state-restoration routines, the integration's select entities for `ac_outlet_timer` and `dc_12v_port1_timer` SHALL suppress any outgoing Bluetooth control commands if the newly requested option already matches the entity's current rounded option state.

#### Scenario: Ignore identical option selection
- **WHEN** the `select.ac_sockets_shutdown_timer` or `select.dc_12v_port1_timer` receives a command to set its option to a value
- **AND** the current rounded state of the entity is already equal to that value
- **THEN** the integration SHALL NOT transmit a BLE control command packet to the F2000.

#### Scenario: Process different option selection
- **WHEN** the `select.ac_sockets_shutdown_timer` or `select.dc_12v_port1_timer` receives a command to set its option to a value
- **AND** the current rounded state of the entity is different from that value
- **THEN** the integration SHALL format and transmit the corresponding BLE control command packet to the F2000.
