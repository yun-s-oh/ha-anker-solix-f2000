# f2000-controls-exploration Specification

## Purpose
This specification outlines the utility scripts and exploration tools developed to interface directly with the Anker Solix F2000 over BLE. It defines the requirements for standalone CLI scripts that allow developers to construct, checksum, and transmit unencrypted control commands, and capture inbound device notifications for protocol analysis.
## Requirements
### Requirement: Standalone BLE Command Sender
The test suite SHALL include a command-line exploration script `tests/explore_controls.py` that allows sending arbitrary hexadecimal BLE payloads to the F2000's control characteristic (`00007777-0000-1000-8000-00805f9b34fb`) and printing returned responses from notification descriptor (`00008888-0000-1000-8000-00805f9b34fb`).

#### Scenario: Send custom hex frame
- **WHEN** the script is run with a specific hex payload command
- **THEN** it connects, writes to the WRITE_UUID characteristic, and listens for a corresponding Command ACK or State ACK response.

### Requirement: Automatic Unencrypted Checksum Generation
The exploration script MUST automatically calculate the required unencrypted checksum byte (sum of preceding bytes & 0xFF) for any unencrypted command packet before writing it to the BLE characteristic.

#### Scenario: Payload checksum append
- **WHEN** the user specifies a raw unencrypted command sequence
- **THEN** the script automatically calculates the 1-byte checksum and appends it to form a valid unencrypted frame.

