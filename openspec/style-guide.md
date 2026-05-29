# Python Code Style Guide

This project follows the PEP 8 style guide for Python code and requires all code to be properly formatted, commented, and type-hinted to ensure repository health, readability, and compatibility.

---

## Python Standards

### 1. Version Compatibility
- All code must be **Python 3.9+ compatible**.
- Avoid deprecated syntax or features removed in newer Python versions.

### 2. Formatting & Indentation
- Use **4 spaces** for indentation. **Do not use tabs**.
- Limit all lines of code to a **maximum of 100 characters**.
- Ensure a single trailing blank line at the end of every file.

### 3. Imports Grouping
Group imports logically and separate groups with a single blank line. Order imports alphabetically within each group:
1. **Standard Library Imports** (e.g., `import os`, `import sys`)
2. **Third-Party Imports** (e.g., `import bleak`, `import pydantic`)
3. **Home Assistant Modules** (e.g., `from homeassistant.core import HomeAssistant`)
4. **Local Component Imports** (e.g., `from .const import DOMAIN`)

### 4. Comments & Documentation
- **Explain "Why", Not "What"**: Code comments must focus on the rationale and logic rather than stating the obvious.
- **Docstrings**: Use triple double quotes (`"""`) for all modules, classes, and public/complex functions and methods.
- Follow the PEP 257 docstring style:
  ```python
  def poll_telemetry(device_id: str) -> dict:
      """Poll telemetry data from the Anker Solix F2000.

      Args:
          device_id: The BLE MAC address of the target device.

      Returns:
          A dictionary of decoded telemetry metrics.
      """
  ```

### 5. Type Hints
- **Required**: Provide explicit type hints for all new functions, methods, parameters, and return types.
- Use built-in types or typing/collections modules where appropriate (e.g., `dict[str, Any]`, `list[int]`).

### 6. Error Handling & Logging
- Wrap external IO, BLE connectivity, and parsing operations in `try/except` blocks.
- **Never swallow errors** silently unless explicitly intended (and documented).
- Use Home Assistant's logger with appropriate severity levels:
  - `DEBUG`: Verbose diagnostics (e.g., raw BLE byte arrays).
  - `INFO`: Significant state changes (e.g., successful connection).
  - `WARNING`: Recoverable errors (e.g., temporary disconnection, retry attempts).
  - `ERROR`: Unrecoverable faults (e.g., failed to establish BLE link, invalid telemetry format).

### 7. Named Constants (No Magic Numbers)
- Avoid hardcoded values ("magic numbers") in business logic.
- Always define reusable config keys, GATT service UUIDs, timeouts, and thresholds as uppercase named constants in `const.py`.

---

## Naming Conventions

### 1. Classes
- Use **CamelCase** (e.g., `AnkerSolixCoordinator`, `SolixBLEDevice`).

### 2. Constants
- Use **UPPER_CASE** with underscores (e.g., `DEFAULT_SCAN_INTERVAL`, `CONF_MAC_ADDRESS`).

### 3. Variables & Functions
- Use **snake_case** (e.g., `get_battery_status`, `is_connected`, `telemetry_data`).

---

## Home Assistant Custom Component Guidelines

Since this is a custom HACS integration, adhere to the following best practices:
- **Asynchronous Flow**: Leverage `async/await` for non-blocking I/O operations (e.g., BLE calls, network communication).
- **DataUpdateCoordinator**: Always route sensor polls and updates through a central `DataUpdateCoordinator` to prevent multiple entities from hammering the Bluetooth radio simultaneously.
- **Config Flow**: Implement `ConfigFlow` to enable automatic discovery or simple user setup via the HA Frontend.

---

## 🔒 Hardware Privacy & Git Safeguards

To prevent leaking sensitive, device-specific information (such as Bluetooth MAC addresses, peripheral UUIDs, or device serial numbers) in the public repository, developers must strictly adhere to the following rules:

1. **No Hardcoded Device Identifiers**: Never hardcode real MAC addresses, Bluetooth UUIDs, or serial numbers in any source code, test scripts, or examples. Always load them dynamically via the environment (e.g., using `os.getenv("ANKER_MAC_ADDRESS")`).
2. **Environment Variables only**: All private configuration and device parameters must be stored in the Git-ignored `.env` file at the root.
3. **No Device Logs in Commits**: Never commit actual device telemetry dumps or test output JSON logs (like `last_telemetry.json` or `investigation_results.json`). Verify that these are correctly ignored by `.gitignore` (`*results.json`, `*telemetry.json`).
4. **Redact Documentation Examples**: In READMEs, guidelines, or design plans, always use redacted placeholder strings (e.g., `XX:XX:XX:XX:XX:XX` or `AZV25N0FXXXXXXXX`) when demonstrating outputs or configuration setups.
