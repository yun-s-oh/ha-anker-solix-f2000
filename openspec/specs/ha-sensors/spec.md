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
The integration SHALL utilize a single `DataUpdateCoordinator` to manage active polling and passive notification parsing, avoiding redundant GATT queries. The active polling interval SHALL be configurable by the user via an options flow between 5 and 30 seconds, defaulting to 5 seconds.

#### Scenario: Concurrent sensor updates
- **WHEN** a telemetry notification is received by the coordinator
- **THEN** all associated sensor entities (battery level, AC output, DC output) update their state in Home Assistant simultaneously without issuing new Bluetooth requests.

#### Scenario: User changes default poll interval in options flow
- **WHEN** the user changes the default poll interval option to 10 seconds and clicks save
- **THEN** the DataUpdateCoordinator instantly updates its update interval to 10 seconds without restarting the integration.

### Requirement: Standardized Sensor and Binary Sensor Entities
The integration SHALL expose comprehensive telemetry as native Home Assistant sensor and binary sensor entities with appropriate device classes and units. Both the internal battery capacity and external battery expansion capacity metrics SHALL be exposed as first-class standard sensor entities without diagnostic categorization to ensure they are visible in primary Home Assistant dashboards.

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
- **Binary Sensors (BinarySensorDeviceClass.CONNECTIVITY, POWER, etc.)**:
  - AC Outlet State (ON/OFF)
  - 12V DC State (ON/OFF)
  - Power Save Mode (ON/OFF)
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
The manual configuration flow step SHALL prompt the user for the MAC Address, Integration Name, Active Telemetry Polling Rate, and Maximum Reconnection Back-Off Limit. 

#### Scenario: Submitting manual configuration setup options
- **WHEN** the user inputs a valid MAC Address, Name, Polling Interval, and Max Retry limit in the setup step
- **THEN** the config entry is created, and the parameters are stored in `entry.options` instantly.

