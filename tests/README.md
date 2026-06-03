# 🧪 Standalone BLE Verification & Testing Suite

This directory contains standalone Python utility scripts to explore, discover, sniff,
and programmatically validate unencrypted Bluetooth Low Energy (BLE) controls and
telemetry schemas for the Anker Solix F2000 (PowerHouse 767) portable power station.

These scripts run natively on the host system to interact directly with CoreBluetooth
(on macOS) or BlueZ (on Linux), enabling quick exploration and validation without
requiring a full Home Assistant installation.

---

## 🏗️ CLI Architecture & Communication Flow

The standalone CLI scripts (e.g., `explore_controls.py`, `test_passive_telemetry.py`)
communicate with the F2000 power station using the following logic:

```mermaid
graph TD
    A[Start Scanner] --> B{Resolved MAC Address?}
    B -- No --> C[Scan & Auto-Save MAC to .env]
    C --> D[Connect to F2000 BLE Client]
    B -- Yes --> D
    D --> E[Subscribe to Telemetry Char 00008888]
    E --> F{Receive Bytes?}
    F -- Yes --> G[Print Decoded JSON & Format UI]
    F -- No (Timeout 5s) --> H[Ping Command Char 00007777]
    H --> F
```

The F2000 power station broadcasts unencrypted telemetry bytes on the notification
characteristic `00008888` and receives keep-alive queries or control commands on
the write-without-response characteristic `00007777`. When running a test script,
the scanner resolves the target BLE MAC address (auto-discovering the nearby device
if none is configured) and automatically saves it to the root `.env` file for
subsequent executions.

---

## ⚙️ Initial Setup

### 1. Initialize Virtual Environment & Dependencies
All scripts run inside an isolated Python virtual environment:
```bash
# Create the virtual environment using Python 3.11
python3.11 -m venv tests/venv

# Activate the virtual environment
source tests/venv/bin/activate

# Install dependencies (bleak, flake8, pytest, etc.)
pip install -r tests/requirements.txt
```

### 2. Configure Local Hardware Parameters (`.env`)
Create a `.env` file at the root of the project:
```ini
# Private Local Hardware Parameters (Git-Ignored)
ANKER_MAC_ADDRESS=XX:XX:XX:XX:XX:XX  # Target BLE MAC Address / macOS UUID
ANKER_DEVICE_NAME=767_PowerHouse
```

---

## 🛠️ Testing & Validation Scripts

### 1. Interactive Explorer & Sniffer (`explore_controls.py`)
An interactive CLI console menu to send raw hex payloads or predefined presets (AC/DC toggles,
LED, Screen Brightness/Timeout, Recharging Power, and Output Shutdown Timers) and sniff
incoming notifications in a clean hex-grid format.
```bash
tests/venv/bin/python tests/explore_controls.py
```

### 2. Output Shutdown Timers Validator (`validate_timers.py`)
Programmatically verifies Task 1.4.8 (AC Output Timer) and Task 1.4.9 (DC Output Timer). It ensures
ports are active, sets timers to 10 minutes, verifies command ACKs, tracks count-down,
and resets timers back to 0.
```bash
tests/venv/bin/python tests/validate_timers.py
```

### 3. AC/DC Output Toggle Validator (`validate_ac_dc.py`)
Verifies unencrypted AC (0x86) and DC (0x87) toggle commands, tracking immediate State ACK
changes.
```bash
tests/venv/bin/python tests/validate_ac_dc.py
```

### 4. LED Brightness Level Validator (`validate_led.py`)
Verifies LED Light utility states (Off, Low, Mid, High, SOS) via command 0x8B.
```bash
tests/venv/bin/python tests/validate_led.py
```

### 5. Power Saving Mode Validator (`validate_power_save.py`)
Verifies Power Saving Mode toggle (0x8A) and monitors active State ACK transitions.
```bash
tests/venv/bin/python tests/validate_power_save.py
```

### 6. Screen Brightness Validator (`validate_screen_brightness.py`)
Verifies Screen Brightness adjustments (Low, Mid, High, Max) via command 0x88.
```bash
tests/venv/bin/python tests/validate_screen_brightness.py
```

### 7. Screen Timeout Validator (`validate_screen_timeout.py`)
Verifies Screen Timeout selections (20s, 30s, 1m, 5m, 30m) via command 0x82.
```bash
tests/venv/bin/python tests/validate_screen_timeout.py
```

### 8. AC Recharging Power Limit Validator (`validate_recharge_power.py`)
Verifies setting the AC Recharging limit (200W - 2200W) via command 0x80.
```bash
tests/venv/bin/python tests/validate_recharge_power.py
```

---

## 🔬 Diagnostic & Utility Tools

* **Passive Telemetry Streamer (`test_passive_telemetry.py`)**: Subscribes and parses real-time
  telemetry data. Run with `--scan` to auto-discover nearby F2000 devices, or add the `--raw` flag
  to dump the raw hex byte grid side-by-side with the decoded metrics.
* **GATT Service Dumper (`diagnose_gatt.py`)**: Discovers and logs physical BLE GATT services,
  descriptors, and properties.
* **Heartbeat Verification (`test_heartbeat.py`)**: Tests unencrypted query keep-alive ping.
* **Pytest Unit Tests (`test_mock_telemetry.py`)**: Offline verification of correct byte parsing,
  scaling, and coordinator coordination without a physical BLE connection. Asserts correct byte
  scaling, offset calculation, and dynamic coordinator rescheduling logic. Run via:
  ```bash
  tests/venv/bin/pytest tests/
  ```
