## Context

The goal is to integrate the Anker Solix F2000 (PowerHouse 767) portable power station into Home Assistant as a local HACS integration via Bluetooth. 
To build a premium, robust integration, we need to solve:
- Custom data stream formats over BLE notifications.
- Reliable connection management to address Anker's 12-hour Bluetooth radio timeout.
- Coexistence with other integrations on Home Assistant's shared host Bluetooth adapter.

Instead of writing a raw `bleak` parser from scratch, this design favors building on top of the community-driven `SolixBLE` library as the core client engine, and wraps it in a modern Home Assistant `DataUpdateCoordinator`.

## Goals / Non-Goals

**Goals:**
- **Local Control**: Zero cloud dependencies; all communication remains entirely local over BLE.
- **HA Best Practices**: Support modern Home Assistant BLE features (config flow for discovery, shared coordinator to prevent connection spam, and appropriate device classes for sensor entities).
- **Testability**: Provide standalone CLI scripts and a Dockerized environment for functional testing without needing physical hardware.
- **Robustness**: Implement active heartbeats and reconnection back-offs to keep the BLE link alive and gracefully recover when the device enters deep sleep.
- **Documentation**: Write clean documentation for future developers and AI agents to understand the repository structure.

**Non-Goals:**
- **Wi-Fi Integration**: This integration does *not* support Wi-Fi or cloud-based Modbus TCP communication. Those are out of scope.
- **Control Commands (Initially)**: The initial focus is strictly telemetry and sensor reporting. Active control features (like toggling AC/DC plugs or changing lights) are out of scope for Phase 1.
- **Non-F2000 Support**: While `SolixBLE` supports other power stations, our custom wrapping, test scripts, and guidelines are specifically focused on and optimized for the Anker Solix F2000.

## Decisions

### Decision 1: Direct HA BLE Integration vs. Standalone MQTT Bridge
- **Option Considered**: A Python MQTT daemon (Option A) running outside HA.
- **Decision**: Direct HA BLE Integration (Option B - Native HACS).
- **Rationale**: Direct integration delivers a vastly superior user experience (plug-and-play). By leveraging HA's central Bluetooth architecture (`homeassistant.components.bluetooth`), we avoid adapter conflicts and ensure seamless pairing.

### Decision 2: Protocol Integration Strategy (Custom Bleak vs. SolixBLE Library)
- **Option Considered**: Utilizing the newer ECDH-encrypted `SolixBLE` library by `flip-dots`.
- **Decision**: Develop a direct custom BLE client using `bleak` on unencrypted characteristics `7777` (write) and `8888` (notify).
- **Rationale**: Dynamic hardware diagnostics proved that the F2000 uses the older, unencrypted BLE service profile. Newer `SolixBLE` libraries targeting the encrypted `8c8500xx` profile fail on F2000 with characteristic discovery and key-exchange exceptions. Writing a direct unencrypted parser ensures zero-dependency reliability and maximum device compatibility.

### Decision 3: Keep-Alive Heartbeat Strategy
- **Option Considered**: A persistent, high-frequency active polling loop (every 1 second).
- **Decision**: Standard 30-second active query polling during active operation.
- **Rationale**: While a periodic 5-minute active ping is sufficient for keeping the BLE radio awake, a 30-second active poll interval provides real-time sensor updates to Home Assistant while naturally satisfying the keep-alive requirement without flooding the BLE host stack.

## Risks / Trade-offs

- **[Risk] Exclusive Connection Lockout**: Anker devices only support a single concurrent BLE connection. If the user leaves their official smartphone app open, the integration will fail to poll.
  - *Mitigation*: The integration SHALL detect connection failures, log a descriptive warning to the user, and schedule exponential back-off retries (`5s`, `15s`, `1m`, `5m`, up to a max of `15m`) rather than crashing.
- **[Risk] Host Bluetooth Adapter Overload**: Home Assistant host running multiple BLE integrations may drop packets.
  - *Mitigation*: Use HA's native `BluetoothDataUpdateCoordinator` which integrates with the host's central BLE queuing mechanism rather than spawning independent unmanaged threads.
- **[Risk] Hardware Isolation during Testing**: Developing and verifying BLE connections requires physical hardware.
  - *Mitigation*: Develop a Dockerized mock environment (`docker-test-env`) that mocks the BLE client parser interface so developers and automated agents can verify the integration code statically and dynamically without a physical device.

---

## 🏗️ Core Custom Component Scaffolding Architecture

The custom component will reside inside the repository under `custom_components/anker_solix_f2000/`. The codebase layout and file roles are designed as follows:

| File Name | Role | Responsibilities |
|---|---|---|
| **`manifest.json`** | HACS Metadata | Defines integration domain (`anker_solix_f2000`), version, and dependencies (`bleak`, `bleak-retry-connector`). |
| **`const.py`** | Domain Constants | Exposes shared parameters, UUIDs (`7777`/`8888`), query frames, and retry intervals. |
| **`__init__.py`** | Setup Entry Point | Initializes the config entry, sets up platforms, handles the shared BLE coordinator lifecycle, and unloads cleanups. |
| **`config_flow.py`** | User Configuration Flow | Manages auto-discovery scanning (filtering BLE names `767`, `PowerHouse`, `F2000`, `Anker`) and provides a manual MAC address fallback UI. |
| **`coordinator.py`** | BLE Data Coordinator | Manages the single persistent `BleakClient` connection, handles notification subscriptions on `8888`, issues `7777` queries every 30s, and handles exponential retry back-offs. |
| **`sensor.py`** | Numeric Sensor Platform | Registers individual sensor entities (Battery %, Wattages, Temperatures) matching official Home Assistant DeviceClasses. |
| **`binary_sensor.py`**| State Binary Sensors | Registers active binary status toggles (AC Outlet active, Power Save active, Port active flags). |
