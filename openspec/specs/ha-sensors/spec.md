# ha-sensors Specification

## Purpose
TBD - created by archiving change anker-solix-ble-hacs. Update Purpose after archive.
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
The integration SHALL expose comprehensive telemetry as native Home Assistant sensor and binary sensor entities with appropriate device classes and units.

#### Mapped Entities:
- **Sensors (SensorDeviceClass.BATTERY, POWER, TEMPERATURE, etc.)**:
  - Total Battery %
  - Internal Battery %
  - External Battery %
  - Internal Temperature (°C)
  - External Temperature (°C)
  - Battery State (Idle, Charging, Discharging)
  - Time Remaining (Duration)
  - AC Input Watts (W)
  - Solar Input Watts (W)
  - Total Input Watts (W)
  - AC Outlet Watts (W)
  - Total Output Watts (W)
  - USB-C1, USB-C2, USB-C3 Watts (W)
  - USB-A1, USB-A2 Watts (W)
  - 12V DC Port 1, Port 2 Watts (W)
- **Binary Sensors (BinarySensorDeviceClass.CONNECTIVITY, POWER, etc.)**:
  - AC Outlet State (ON/OFF)
  - 12V DC State (ON/OFF)
  - Power Save Mode (ON/OFF)
  - USB-C1, C2, C3 Active States (ON/OFF)
  - USB-A1, A2 Active States (ON/OFF)
  - 12V DC Port 1, Port 2 Active States (ON/OFF)

