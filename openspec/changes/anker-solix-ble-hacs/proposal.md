## Why

The Anker Solix F2000 (PowerHouse 767) portable power station is a premium energy storage system. However, integrating it with Home Assistant natively lacks local, cloud-free support. Although Wi-Fi cloud integrations exist, they introduce latency, require internet dependency, and are subject to API limit rate changes. 

Bluetooth is the optimal local communication channel, but the F2000 has aggressive power-saving sleep timeouts and proprietary telemetry formats. By developing a native direct BLE Home Assistant (HACS) integration, users will get real-time, local, reliable energy statistics (such as battery percentage, input power, and output power) in their smart home dashboards without relying on external cloud APIs or complex DIY bridges.

## What Changes

- **NEW** Standalone Python command-line verification scripts (`test-scripts`) to safely test BLE connectivity, poll telemetry, and send keep-alive commands.
- **NEW** Detailed repository protocol specifications (`ble-protocol`) documenting GATT services, characteristics, byte offsets, and decoding schemas.
- **NEW** Home Assistant Custom Component (HACS) integration using direct BLE APIs, incorporating HA best practices (e.g., config flow for automatic discovery, `DataUpdateCoordinator`, and native sensor entities).
- **NEW** Failover and connection recovery engine (`failover-recovery`) that periodically prompts heartbeats to prevent F2000 Bluetooth radio sleep and cleanly re-establishes broken links.
- **NEW** Dockerized test environment (`docker-test-env`) featuring Bluetooth mock tools or instructions to safely dry-run test scripts and verify telemetry decoding.
- **NEW** Developer and agent-oriented markdown guidelines (`agent-guidelines`) detailing how subsequent agent models and contributors can develop, test, and expand the repository.

## Capabilities

### New Capabilities

- `ble-protocol`: Deep-dive documentation mapping F2000 BLE services, notification characteristics, and custom hex telemetry byte structures.
- `test-scripts`: Independent CLI Python test scripts leveraging `bleak` and `SolixBLE` to scan, connect, and stream decoded battery telemetry.
- `ha-sensors`: Native HA integration exposing battery level, input/output AC/DC power, and temperatures utilizing HA's central Bluetooth and sensor entity frameworks.
- `failover-recovery`: Robust connection recovery module that handles timeouts, active heartbeats, and re-connection logic to bypass the 12-hour BLE sleep timer.
- `docker-test-env`: Docker container definition and configurations to facilitate standardized testing and execution of verification scripts.
- `agent-guidelines`: Comprehensive technical documentation explaining the repository architecture, protocol decoding tables, and code patterns for automated agents.

### Modified Capabilities

*(None. This is an initial repository scaffolding and greenfield implementation).*

## Impact

- **External Dependencies**: Adds `bleak`, `pydantic` (optional, for validated schemas), and `homeassistant` (for development/testing).
- **System Footprint**: Requires a host running Home Assistant with direct Bluetooth adapter access (e.g., Raspberry Pi, Home Assistant Green/Yellow, or dedicated Linux server).
- **Firmware Warnings**: Interfacing over Bluetooth is non-invasive and read-only by default, but excessive connections can cause temporary lockouts due to Anker's exclusive BLE pairing limit.
