# Docker Integration Environment Specification

This specification documents the containerized environment used to dynamically execute, run, and verify the custom HACS component inside a native stable **Home Assistant** instance.

## ADDED Requirements

### Requirement: Containerized Home Assistant Environment with Host BLE Access
The repository SHALL configure a stable containerized Home Assistant service equipped to natively access the host's Bluetooth adapter.

#### Scenario: Running Home Assistant with native BLE hardware access
- **WHEN** the docker compose service is initialized on a Linux host with `docker compose up -d homeassistant`
- **THEN** the container utilizes host networking and DBus communication to discover and manage BLE devices.

---

## 🏗️ Docker Services Configuration (`docker-compose.yml`)

The repository provides a `docker-compose.yml` to support local frontend runtime integration and custom component debugging:

```yaml
version: "3.8"

services:
  # Local Home Assistant stable environment for dynamic custom component integration testing
  homeassistant:
    container_name: homeassistant
    image: "ghcr.io/home-assistant/home-assistant:stable"
    volumes:
      - ./config:/config
      - ./custom_components:/config/custom_components
      - /var/run/dbus:/var/run/dbus:ro
    environment:
      - TZ=Australia/Sydney
    restart: unless-stopped
    network_mode: host
```

---

## 🧪 Operational Scenarios & Instructions

### Running the Live Home Assistant Environment

To mount and debug the custom components dynamically in the Home Assistant stable build:

```bash
# Start the Home Assistant environment in the background
docker compose up -d homeassistant
```
Home Assistant will be available at [http://localhost:8123](http://localhost:8123).

#### 🛜 Linux Bluetooth Integration in Docker:
To allow the Home Assistant container to discover and communicate with the host's physical BLE hardware, the container configuration requires two critical settings:
1.  **`network_mode: host`**: This bypasses Docker's virtual network bridge and exposes the container directly to the host's network interfaces, allowing the Home Assistant Bluetooth component to manage advertisements natively.
2.  **`/var/run/dbus:/var/run/dbus:ro` Volume Mount**: On Linux hosts, the `bluez` Bluetooth system daemon communicates over DBus. Mounting this socket enables the containerized Home Assistant to command and receive notifications from the host's BLE adapter.

> [!WARNING]
> **macOS Docker Bluetooth Limitations:**
> Docker on macOS runs inside a lightweight Linux virtualization machine (hypervisor). Because macOS does not natively support passing the host’s Bluetooth CoreBluetooth PCIe/USB controller through to the hypervisor, the Home Assistant container on macOS **cannot** access the host's Bluetooth adapter.
>
> **Recommended macOS Developer Workflow:**
> - To run unit tests and verify parser logic: Execute the tests locally within the host venv: `test-scripts/venv/bin/pytest`.
> - To test real-time BLE communication and scanner functions: Run the CLI scripts (`test_passive_telemetry.py` or `test_heartbeat.py`) directly on your macOS host using the local virtual environment (`test-scripts/venv/`), as the local python interpreter has direct native access to CoreBluetooth.
