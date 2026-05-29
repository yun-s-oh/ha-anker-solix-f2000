## ADDED Requirements

### Requirement: HA BLE Configuration Flow
The Home Assistant integration SHALL implement a `config_flow` allowing the user to select the discovered F2000 from a list of nearby BLE devices.

#### Scenario: User adds integration via UI
- **WHEN** the user selects the Anker Solix F2000 integration in Settings -> Devices & Services
- **THEN** Home Assistant lists nearby discovered Anker BLE devices and successfully registers the selected device.

### Requirement: Unified Data Update Coordinator
The integration SHALL utilize a single `DataUpdateCoordinator` to manage active polling and passive notification parsing, avoiding redundant GATT queries.

#### Scenario: Concurrent sensor updates
- **WHEN** a telemetry notification is received by the coordinator
- **THEN** all associated sensor entities (battery level, AC output, DC output) update their state in Home Assistant simultaneously without issuing new Bluetooth requests.

### Requirement: Standardized Sensor Entities
The integration SHALL expose telemetry as native Home Assistant sensor entities with appropriate device classes (e.g., `SensorDeviceClass.BATTERY`, `SensorDeviceClass.POWER`, `SensorDeviceClass.TEMPERATURE`).

#### Scenario: Sensor entities are rendered in HA
- **WHEN** the integration starts up successfully
- **THEN** Home Assistant registers entities like `sensor.anker_f2000_battery` with percentage units and `sensor.anker_f2000_ac_output_power` with Watt units.
