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

### Decision 2: Library Selection (`SolixBLE` vs. custom bleak parser)
- **Option Considered**: Writing a proprietary parser on raw `bleak` bytes.
- **Decision**: Utilize the community library `SolixBLE` by `flip-dots`.
- **Rationale**: `SolixBLE` has already reverse-engineered and decoded the byte structures for Anker power stations (including F2000). Building on top of `SolixBLE` avoids reinventing the wheel and provides instant community-supported decoding of power, battery, and temperature states.

### Decision 3: Keep-Alive Heartbeat Strategy
- **Option Considered**: A persistent, high-frequency active polling loop (every 1 second).
- **Decision**: Combined passive listening with a 5-minute active heartbeat ping.
- **Rationale**: High-frequency active connection polling drains both the host and the power station's BLE module, and risks host resource exhaustion. Passive notification listening, backed by a periodic 5-minute active keep-alive query, successfully keeps the F2000 BLE radio awake without flooding the airwaves.

## Risks / Trade-offs

- **[Risk] Exclusive Connection Lockout**: Anker devices only support a single concurrent BLE connection. If the user leaves their official smartphone app open, the integration will fail to poll.
  - *Mitigation*: The integration SHALL detect connection failures, log a descriptive warning to the user, and schedule exponential back-off retries rather than crashing.
- **[Risk] Host Bluetooth Adapter Overload**: Home Assistant host running multiple BLE integrations may drop packets.
  - *Mitigation*: Use HA's native `BluetoothDataUpdateCoordinator` which integrates with the host's central BLE queuing mechanism rather than spawning independent unmanaged threads.
- **[Risk] Hardware Isolation during Testing**: Developing and verifying BLE connections requires physical hardware.
  - *Mitigation*: Develop a Dockerized mock environment (`docker-test-env`) that mocks the `SolixBLE` client interface so developers and automated agents can verify the integration code statically and dynamically without a physical device.
