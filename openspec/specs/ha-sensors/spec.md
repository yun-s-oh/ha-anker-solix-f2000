# ha-sensors Specification

## Purpose
This specification defines the exposed Home Assistant sensor and binary sensor platforms, including configuration flow entry options and dynamic polling updates.
## Requirements
### Requirement: HA BLE Configuration Flow
The Home Assistant integration SHALL implement a `config_flow` allowing the user to select the discovered F2000 from a list of nearby BLE devices, or manually input the MAC address as a fallback.

#### Scenario: User adds integration via UI (Auto-Discovery)
- **WHEN** the user selects the Anker Solix F2000 integration in Settings -> Devices & Services
- **THEN** Home Assistant scans for nearby BLE advertisements matching names `"767"`, `"PowerHouse"`, `"F2000"`, or `"Anker"`, presents them in a user selection list, and successfully registers the selected device.

#### Scenario: User adds integration via UI (Manual Fallback)
- **WHEN** the user initiates the setup flow and opts for manual entry, or if auto-discovery finds no candidates
- **THEN** Home Assistant prompts the user to manually enter the Bluetooth MAC address, validates its format, and registers the device.

### Requirement: Unified Data Update Coordinator
The integration SHALL utilize a single `DataUpdateCoordinator` to manage active polling and passive
notification parsing, avoiding redundant GATT queries. The active polling interval SHALL be
configurable by the user via an options flow between 5 and 300 seconds, defaulting to 30 seconds.

#### Scenario: Concurrent sensor updates
- **WHEN** a telemetry notification is received by the coordinator
- **THEN** all associated sensor entities (battery level, AC output, DC output) update their
  state in Home Assistant simultaneously without issuing new Bluetooth requests.

#### Scenario: User changes default poll interval in options flow
- **WHEN** the user changes the default poll interval option to 60 seconds and clicks save
- **THEN** the DataUpdateCoordinator instantly updates its update interval to 60 seconds without
  restarting the integration.

### Requirement: Standardized Sensor and Binary Sensor Entities
The integration SHALL expose comprehensive telemetry as native Home Assistant sensor and binary sensor entities with appropriate device classes and units. Both the internal battery capacity and external battery expansion capacity metrics SHALL be exposed as first-class standard sensor entities without diagnostic categorization to ensure they are visible in primary Home Assistant dashboards. The duplicate binary sensor entities for AC Outlet State, 12V DC Master State, and Power Save Mode State SHALL NOT be exposed as they are fully represented by the corresponding switch entities.

#### Mapped Entities:
- **Sensors (SensorDeviceClass.BATTERY, POWER, TEMPERATURE, etc.)**:
  - Battery %
  - Internal Battery % (Promoted to first-class, standard sensor)
  - External Battery Expansion % (Promoted to first-class, standard sensor)
  - Internal Temperature (°C)
  - External Temperature (°C)
  - Battery Operating State (Idle, Charging, Discharging)
  - Battery Runtime Remaining (Duration)
  - AC Input Power (W)
  - Solar Input Power (W)
  - Total Input Power (W)
  - AC Outlet Power Output (W)
  - Total Output Power (W)
  - USB-C Port 1, Port 2, Port 3 Power (W)
  - USB-A Port 1, Port 2 Power (W)
  - 12V Car Port 1, Port 2 Power (W)
- **Binary Sensors (BinarySensorDeviceClass.POWER, etc.)**:
  - USB-C Port 1, Port 2, Port 3 Active States (ON/OFF)
  - USB-A Port 1, Port 2 Active States (ON/OFF)
  - 12V Car Port 1, Port 2 Active States (ON/OFF)

#### Scenario: Promoted battery sensors render in standard view
- **WHEN** the integration is successfully added and telemetry is received
- **THEN** both the "Internal Battery" and "External Battery Expansion" sensors SHALL be registered as standard entities without diagnostic categorization, making them visible in default Home Assistant dashboard cards.

### Requirement: Primary Battery Entity Badge
The primary battery sensor `total_pct` SHALL be registered with the name `"Battery"`. Home Assistant SHALL natively associate this entity as the main device battery status, displaying its value next to the integration card/logo in the UI.

#### Scenario: Registering the sensor
- **WHEN** the integration starts up and adds sensor entities
- **THEN** the entity `sensor.<device_name>_battery` is successfully created with name `"Battery"`, and the sub-pack battery sensors remain diagnostic.

### Requirement: Config Flow Options Setup
The configuration flow SHALL prompt the user for the MAC Address (for manual setups), Integration
Name, Active Telemetry Polling Rate (5s to 300s), and Maximum Reconnection Back-Off Limit
(30s to 600s). The flow SHALL enforce that the Maximum Reconnection Back-Off Limit is greater
than or equal to the Active Telemetry Polling Rate. These polling options SHALL be available in
both the manual setup flow and the automatic discovery flow steps, as well as the post-setup
options flow.

#### Scenario: Submitting manual configuration setup options with valid parameters
- **WHEN** the user inputs a manual setup with poll_interval=30 and max_retry_interval=60
- **THEN** the setup succeeds, the config entry is created, and parameters are stored in options.

#### Scenario: Submitting automatic discovery setup options with valid parameters
- **WHEN** the user completes discovery setup with poll_interval=30 and max_retry_interval=60
- **THEN** the setup succeeds, the config entry is created, and parameters are stored in options.

#### Scenario: Submitting setup options with invalid retry interval
- **WHEN** the user sets poll_interval=60 and max_retry_interval=30 in any setup step
- **THEN** validation fails, and the flow presents an error indicating the retry interval must be
  greater than or equal to the polling interval.

### Requirement: AC Sockets Timer Remaining Entity
The integration SHALL expose the remaining AC outlet shutdown duration in seconds as a standard Home
Assistant sensor entity named `"AC Sockets Timer Remaining"`.

#### Scenario: Continuous AC socket timer updates
- **WHEN** the F2000 is active and the AC sockets master shutdown timer is configured
- **THEN** the sensor `sensor.<device_name>_ac_sockets_timer_remaining` SHALL update with the
  remaining duration in seconds.

### Requirement: Smart Battery Fallback Logic
The primary battery sensor (`total_pct` / `"Battery"`) SHALL return the accurate internal battery cell percentage
(`internal_pct`) if no external battery expansion is physically connected.

#### Scenario: Single unit battery updates
- **WHEN** no external expansion battery is connected (`external_pct` is `None`)
- **THEN** the primary `"Battery"` entity returns the value of `"internal_pct"`.

#### Scenario: Expanded unit battery updates
- **WHEN** an external expansion battery is connected
- **THEN** the primary `"Battery"` entity returns the combined value of `"total_pct"`.

### Requirement: Car Port Master Icon
The `twelve_volt_on` switch entity ("12V Car Port Master") SHALL use the standard, working Material
Design Icon `"mdi:car-power-outlet"`.

#### Scenario: Retrieve entity icon
- **WHEN** the 12V Car Port Master switch is registered in Home Assistant
- **THEN** the entity uses `"mdi:car-power-outlet"` as its icon.

### Requirement: Safe Shutdown Timer Durations
The pre-generated dropdown options for the AC and DC Output Shutdown select entities SHALL be capped
at a maximum of 18 hours (64,800 seconds) to ensure that the duration fits safely inside a 2-byte
little-endian uint16 without causing integer overflow exceptions.

#### Scenario: Verify dropdown options limit
- **WHEN** the AC or DC shutdown select entity dropdown options are generated
- **THEN** the options list SHALL NOT contain any durations exceeding 18 hours, and the highest option is "18h".

