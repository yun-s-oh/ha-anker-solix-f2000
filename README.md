# 🔋 Anker Solix F2000 Home Assistant BLE Integration

A premium, cloud-free custom HACS integration for the **Anker Solix F2000 (PowerHouse 767)** portable power station, operating completely locally via Bluetooth Low Energy (BLE).

This repository contains local testing CLI verification scripts, diagnostic GATT utilities, and technical specification guidelines to verify telemetry streams before integration scaffolding.

> [!NOTE]
> This integration leverages local BLE advertising, bypassing latency, internet dependencies, and cloud API limits, enabling a fully cloud-free smart home dashboard.

---

## 🏗️ Architecture & Communication Flow

The F2000 power station broadcasts unencrypted telemetry bytes on a custom notification characteristic and receives keep-alive pings on a write-without-response characteristic.

```mermaid
graph TD
    A[Start Scanner] --> B{Resolved MAC Address?}
    B -- No --> C[Scan & Auto-Save MAC to .env]
    C --> D[Connect to F2000 BLE Client]
    B -- Yes --> D
    D --> E[Subscribe to Telemetry Char 00008888]
    E --> F{Receive Bytes?}
    F -- Yes --> G[Print Raw Byte Grid & Decoded JSON]
    F -- No (Timeout 5s) --> H[Ping Command Char 00007777]
    H --> F
```

---

## 🛠️ Getting Started & Virtual Environment Setup

To run the verification scripts and test local telemetry safely, configure an isolated Python 3.11 virtual environment under `test-scripts/`.

### 1. Initialize Virtual Environment
Navigate to your workspace and create the virtual environment:
```bash
# Create venv using Python 3.11
python3.11 -m venv test-scripts/venv

# Activate the virtual environment
source test-scripts/venv/bin/activate
```

### 2. Install Required Dependencies
Install the required packages (`bleak` for BLE connectivity and `SolixBLE` for structured parsing):
```bash
pip install -r test-scripts/requirements.txt
```

---

## ⚙️ Configuration (`.env`)

To protect your local hardware parameters from being leaked in public repositories, they are safely loaded from a Git-ignored `.env` file at the root.

Create a `.env` file at the root:
```ini
# Private Local Hardware Parameters (Git-Ignored)
ANKER_MAC_ADDRESS=XX:XX:XX:XX:XX:XX  # Your Anker BLE MAC Address
ANKER_DEVICE_NAME=767_PowerHouse
```

---

## 🔍 Running Verification Scripts

### A. BLE Device Scanning & Auto-Configuration
To scan for nearby Anker devices and automatically configure your local `.env` file, place your F2000 in active Bluetooth pairing mode (press the physical IoT/Bluetooth button on the front of the unit once so that the Bluetooth symbol begins blinking) and run:
```bash
test-scripts/venv/bin/python test-scripts/test_passive_telemetry.py --scan
```
> [!TIP]
> Once a candidate is discovered, the script will register its BLE MAC address and name inside your `.env` file and exit cleanly. Subsequent commands (diagnostics, telemetry, and heartbeats) read from this file and run parameter-free!


### B. GATT Database Diagnostics
Inspect the service GATT structure to confirm the device characteristics (reads MAC from the configured `.env` file):
```bash
test-scripts/venv/bin/python test-scripts/diagnose_gatt.py
```

### C. Streaming Decoded Passive Telemetry
Subscribe to telemetry notifications, parse the unencrypted 102-byte packets continuously, and print a formatted real-time dashboard:
```bash
test-scripts/venv/bin/python test-scripts/test_passive_telemetry.py
```

### D. Verifying Heartbeats & Connection Persistence
Test active 5-minute heartbeats to verify connection persistence and BLE radio sleep prevention:
```bash
test-scripts/venv/bin/python test-scripts/test_heartbeat.py
```

### E. Running Automated Unit Tests
To execute the comprehensive mock telemetry validation unit tests using `pytest` inside the local virtual environment:
```bash
test-scripts/venv/bin/pytest
```
> [!NOTE]
> This command runs `test-scripts/test_mock_telemetry.py` to assert correct byte extraction, register scaling, and checksum validation against the mock F2000 hardware state machine without requiring a physical BLE connection.

---

## 🐳 Deploying Home Assistant with Docker

This repository includes a pre-configured `docker-compose.yml` to package and run a local Home Assistant stable instance for dynamic custom component integration testing.

### 1. Spin Up Local Home Assistant
To spin up a local Home Assistant stable instance with our custom component dynamically mapped:
```bash
# Spin up Home Assistant in the background
docker compose up -d homeassistant
```
*   **Web Portal**: Access your local Home Assistant UI at [http://localhost:8123](http://localhost:8123).
*   **Active Scaffolding**: Any modifications made to `custom_components/anker_solix_f2000/` are instantly shared with the container and can be dynamically reloaded from the Home Assistant UI without rebuilding.

### 🛜 Host Bluetooth & OS Compatibility Guidelines
To ensure Home Assistant can discover and connect to your physical Anker F2000 unit over BLE inside Docker, note the following system requirements:

*   **Linux Hosts**: 
    *   The container uses **Host Networking** (`network_mode: host`) to directly bind to physical Bluetooth controllers.
    *   It mounts the **System D-Bus Socket** (`/var/run/dbus:/var/run/dbus:ro`) to communicate with the host's `bluez` Bluetooth system daemon. Ensure `dbus` is active on your host.
*   **macOS Hosts**: 
    *   > [!WARNING]
    *   > Docker on macOS runs inside a Linux virtual machine hypervisor. Because macOS does not support passing CoreBluetooth hardware controllers through to hypervisor guests, **Home Assistant running in Docker on macOS cannot access physical Bluetooth adapters**.
    *   👉 **Action**: To test real BLE operations (scanning, streaming, heartbeats) or to run `pytest` unit tests on macOS, execute the local Python CLI verification scripts or `pytest` directly on your host machine inside the local virtual environment (`test-scripts/venv/`).

---

## ⚠️ Troubleshooting & macOS Bluetooth Caching

Operating Bluetooth integrations on macOS can sometimes encounter system-level locking. Follow these guidelines to resolve connection drops:

*   **Exclusive Connection Lockout**: Anker devices only support **one active BLE client**. Ensure the **official Anker mobile app is completely force-closed** to prevent link lockouts.
*   **System Pairing/Bonding**: macOS will silently drop notification packet streams if secure pairing is not finalized.
    *   👉 **Action**: Press the physical **IoT button** on the front of the F2000 once to put it in active advertising mode.
*   **Resetting Caches**: If macOS aggressively caches old GATT profiles:
    *   Turn Bluetooth off and on in System Settings.
    *   "Forget" the peripheral in macOS Bluetooth Settings.
    *   Restart the system Bluetooth daemon: `sudo pkill bluetoothd`
