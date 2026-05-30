## ADDED Requirements

### Requirement: Primary Battery Entity Badge
The primary battery sensor `total_pct` SHALL be registered with the name `"Battery"`. Home Assistant SHALL natively associate this entity as the main device battery status, displaying its value next to the integration card/logo in the UI.

#### Scenario: Registering the sensor
- **WHEN** the integration starts up and adds sensor entities
- **THEN** the entity `sensor.<device_name>_battery` is successfully created with name `"Battery"`, and the sub-pack battery sensors remain diagnostic.

### Requirement: Config Flow Options Setup
The manual configuration flow step SHALL prompt the user for the MAC Address, Integration Name, Active Telemetry Polling Rate, and Maximum Reconnection Back-Off Limit. 

#### Scenario: Submitting manual configuration setup options
- **WHEN** the user inputs a valid MAC Address, Name, Polling Interval, and Max Retry limit in the setup step
- **THEN** the config entry is created, and the parameters are stored in `entry.options` instantly.
