# 🤖 Anker Solix F2000 BLE HACS — Developer & Agent Guidelines

Welcome to the Anker Solix F2000 (PowerHouse 767) Home Assistant BLE Custom Integration repository. This document serves as a standardized alignment reference for both human contributors and AI coding agents.

---

## 🏗️ Repository Directory Structure

```text
├── .agent/                    # Specialized agent workflow definitions and skills
├── openspec/                  # OpenSpec change directories, design docs, and specs
│   ├── changes/               # Active development changes
│   │   └── anker-solix-ble-hacs/
│   │       ├── proposal.md    # Product goals, impact, and capabilities
│   │       ├── design.md      # Architecture, coordinator strategy, and risks
│   │       ├── tasks.md       # Implementation task checklists
│   │       └── specs/         # Sub-component requirements and specifications
│   ├── config.yaml            # OpenSpec validation configuration
│   └── style-guide.md         # Custom style standards (PEP 8, line limits, guidelines)
├── tests/                     # Isolated functional verification suite
│   ├── diagnose_gatt.py       # GATT database structure prober & service dumper
│   ├── test_passive_telemetry.py # Standalone continuous polling & scanning script
│   ├── requirements.txt       # Isolated script dependencies
│   └── venv/                  # Python 3.11 virtual environment (Git-ignored)
├── README.md                  # Project landing page & quickstart instructions
├── .env                       # Local private device credentials (Git-ignored)
└── .gitignore                 # Safe pattern definitions
```

---

## 🔌 BLE Protocol Summary

The Anker Solix F2000 communicates locally over unencrypted Bluetooth Low Energy (BLE).

### GATT Profile UUIDs
*   **Service**: `014bf5da-0000-1000-8000-00805f9b34fb`
*   **Command (Write)**: `00007777-0000-1000-8000-00805f9b34fb` (Write-Without-Response)
*   **Telemetry (Notify)**: `00008888-0000-1000-8000-00805f9b34fb` (Notification Subscription)

### Header & Checksum
All packets exchanged on `7777`/`8888` follow standard formats. Outbound control commands use a command header (`08 EE 00 00 00 02`) while inbound telemetry packets use an advertising header (`09 FF 00 00 01`).
The final byte of every packet contains a checksum computed as:
$$\text{Checksum} = \sum(\text{all preceding bytes}) \ \& \ 0\text{xFF}$$

For detailed packet layouts, see [ble-protocol/spec.md](file:///Users/yunseokoh/Projects/ha-anker-solix-f2000/openspec/changes/anker-solix-ble-hacs/specs/ble-protocol/spec.md).

---

## 🔒 Hardware Privacy & Git Safeguards

Leaking private hardware credentials in public git history is strictly prohibited. All developers and agents must comply with these guidelines:

1.  **No Hardcoded MACs or Serials**: Never hardcode real MAC addresses (e.g. macOS CoreBluetooth UUIDs `E05A51D0-...`) or serial numbers in source code. Load them dynamically:
    ```python
    mac_address = os.getenv("ANKER_MAC_ADDRESS")
    ```
2.  **Environment Isolation**: Use a local `.env` file at the root to store parameters. Ensure the `.env` remains Git-ignored.
3.  **JSON Log Filtering**: Do not commit active run logs (like `last_telemetry.json` or `investigation_results.json`). Check that `.gitignore` contains `*results.json` and `*telemetry.json`.
4.  **Redacted Documentation**: Always use placeholders (e.g. `XX:XX:XX:XX:XX:XX` or `AZV25N0FXXXXXXXX`) in example snippets.

---

## 📜 Development & Code Style Guidelines

All code contributions must follow these strict validation standards:

*   **Python Version**: Code must be compatible with Python 3.9+.
*   **Strict Line Limits**: Limit all source code and script lines to a **maximum of 100 characters**.
*   **PEP 8 Standards**: Code must be properly formatted and documented.
*   **Type Hinting**: Provide explicit type hints for all parameters, variables, and return types.
*   **Quality Checks**: Before staging files, always run syntax validation and linting using `flake8` under the isolated virtual environment:
    ```bash
    ./tests/venv/bin/flake8 tests/test_passive_telemetry.py --max-line-length=100
    ./tests/venv/bin/python -m py_compile tests/test_passive_telemetry.py
    ```
*   **DataUpdateCoordinator**: When transitioning scripts to the core Home Assistant integration, always channel BLE reads and updates through a central `DataUpdateCoordinator` to manage polling cycles and prevent connection overload.
