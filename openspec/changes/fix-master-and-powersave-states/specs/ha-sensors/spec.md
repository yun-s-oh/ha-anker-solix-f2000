## MODIFIED Requirements

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
