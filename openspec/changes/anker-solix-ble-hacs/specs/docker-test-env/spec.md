# Docker Test & Integration Environment Specification

This specification documents the containerized environments used to:
1. Run automated unit and mock telemetry tests in an isolated Python **virtual environment (`venv`)** container.
2. Dynamically execute and verify the custom HACS component inside a native stable **Home Assistant** instance.

## ADDED Requirements

### Requirement: Standardized Isolated Testing Environment
The repository SHALL provide a Dockerized environment to build and run the automated pytest verification suite inside an isolated Python virtual environment.

#### Scenario: Developer executes unit tests in Docker
- **WHEN** the developer runs `docker compose run --rm test-suite`
- **THEN** the pytest runner executes all tests and reports the results cleanly.

### Requirement: Containerized Home Assistant Environment with Host BLE Access
The repository SHALL configure a stable containerized Home Assistant service equipped to natively access the host's Bluetooth adapter.

#### Scenario: Running Home Assistant with native BLE hardware access
- **WHEN** the docker compose service is initialized on a Linux host with `docker compose up -d homeassistant`
- **THEN** the container utilizes host networking and DBus communication to discover and manage BLE devices.

---

## 🏗️ Docker Services Configuration (`docker-compose.yml`)

The repository provides a dual-service `docker-compose.yml` to support both command-line test validation and frontend runtime integration:

```yaml
version: "3.8"

services:
  # Service 1: Unit & Mock telemetry test runner inside an isolated python venv container
  test-suite:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: f2000-test-suite
    volumes:
      - ./test-scripts:/app/test-scripts
    environment:
      - ANKER_MAC_ADDRESS=XX:XX:XX:XX:XX:XX
      - ANKER_DEVICE_NAME=767_PowerHouse
    command: pytest -v

  # Service 2: Local Home Assistant stable environment for dynamic custom component integration testing
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

## 🔒 Virtual Environment (`venv`) Setup in Dockerfile

To comply with isolated development guidelines, the `Dockerfile` sets up a dedicated, isolated virtual environment under `/opt/venv` and adds its binary directory to the system `PATH`:

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environmental variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    bluez \
    && rm -rf /var/lib/apt/lists/*

# Set up virtual environment inside the container
RUN python -m venv /opt/venv

# Copy requirements file first to leverage Docker cache
COPY test-scripts/requirements.txt /app/

# Install python dependencies inside the virtual environment
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir pytest pytest-asyncio

# Copy the rest of the application files
COPY test-scripts/ /app/test-scripts/

# Copy guidelines or metadata if needed
COPY agent-guidelines.md /app/

# Set working directory to test-scripts
WORKDIR /app/test-scripts

# Default command runs the test suite
CMD ["pytest", "-v"]
```

---

## 🧪 Operational Scenarios & Instructions

### 1. Running the Automated Test Suite (Virtual Environment)

To build and run the unit test runner inside the isolated `venv` container:

```bash
# Build the test suite image
docker compose build test-suite

# Run the automated pytest verification
docker compose run --rm test-suite
```

#### Inside the Container Execution Flow:
- The base Debian environment is initialized.
- A virtual environment is created dynamically at `/opt/venv` using `python -m venv`.
- Dependencies (`bleak`, `pytest`, `pytest-asyncio`) are installed inside the venv.
- `pytest` executes `test-scripts/` inside the virtual environment.

---

### 2. Running the Live Home Assistant Environment

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
> - To test mock telemetry and parser logic: Use the isolated `test-suite` container or run the unit tests locally: `test-scripts/venv/bin/pytest`.
> - To test real-time BLE communication and scanner functions: Run the CLI scripts (`test_passive_telemetry.py` or `test_heartbeat.py`) directly on your macOS host using the local virtual environment (`test-scripts/venv/`), as the local python interpreter has direct native access to CoreBluetooth.

