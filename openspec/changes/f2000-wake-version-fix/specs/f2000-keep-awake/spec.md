## ADDED Requirements

### Requirement: DC Output Keep-Awake Configuration
The integration SHALL expose a configuration option in the Home Assistant Options Flow to
enable an automatic DC keep-awake mode.

#### Scenario: Enable DC Keep-Awake
- **WHEN** the "DC Keep-Awake" option is enabled in the integration options
- **THEN** the integration automatically ensures that the DC 12V output port (car socket) is
  set to ON whenever the AC output is toggled OFF and the unit is not charging.

### Requirement: Efficient Standby Telemetry Polling
The integration SHALL query telemetry data using the keep-awake state, preventing the unit's
CPU and Bluetooth radio from entering deep standby mode without requiring physical IoT button
interaction.

#### Scenario: Continuous telemetry delivery during idle state
- **WHEN** the F2000 has both AC OFF and is not charging, and the DC keep-awake is active
- **THEN** the BLE client maintains a persistent connection and queries telemetry successfully
  without experiencing connection timeouts.
