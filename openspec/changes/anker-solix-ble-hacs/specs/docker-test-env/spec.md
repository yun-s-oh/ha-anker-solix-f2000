# Docker Test & Integration Environment Specification

This specification documents the containerized environments used to:
1. Run automated unit and mock telemetry tests in an isolated Python **virtual environment (`venv`)** container.
2. Dynamically execute and verify the custom HACS component inside a native stable **Home Assistant** instance.

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
    environment:
      - TZ=Australia/Sydney
    ports:
      - "8123:8123"
    restart: unless-stopped
    network_mode: bridge
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
Home Assistant will be available at [http://localhost:8123](http://localhost:8123). You can dynamically modify code inside `custom_components/anker_solix_f2000/` and reload it directly from the Home Assistant developer dashboard.
