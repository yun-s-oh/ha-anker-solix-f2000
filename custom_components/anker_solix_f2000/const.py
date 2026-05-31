"""Constants for the Anker Solix F2000 BLE Integration.

This module houses all constant definitions including domain keys, unencrypted Bluetooth low energy
UUIDs, standard query frames, and timing/reconnection intervals used across integration platforms.
"""

from typing import Final

DOMAIN: Final[str] = "anker_solix_f2000"

# Bluetooth Low Energy Service & Characteristic UUIDs (Unencrypted Profile)
NOTIFY_UUID: Final[str] = "00008888-0000-1000-8000-00805f9b34fb"
WRITE_UUID: Final[str] = "00007777-0000-1000-8000-00805f9b34fb"

# Packet Header Identifier
HEADER_PREFIX: Final[bytes] = bytes([0x09, 0xFF])

# Unencrypted 10-byte telemetry query frame sent to WRITE_UUID to request updates on NOTIFY_UUID
TELEMETRY_QUERY: Final[bytes] = bytes(
    [0x08, 0xEE, 0x00, 0x00, 0x00, 0x01, 0x01, 0x0A, 0x00, 0x02]
)

# Polling and retry configurations
DEFAULT_POLL_INTERVAL: Final[int] = 30  # Active query poll frequency (seconds)
MIN_POLL_INTERVAL: Final[int] = 5       # Minimum allowed poll frequency (seconds)
MAX_POLL_INTERVAL: Final[int] = 300     # Maximum allowed poll frequency (seconds)

MIN_RETRY_INTERVAL: Final[int] = 5      # Initial reconnect back-off delay (seconds)
MAX_RETRY_INTERVAL: Final[int] = 60     # Default reconnect back-off limit (60 seconds)
MIN_MAX_RETRY_INTERVAL: Final[int] = 30  # Minimum selectable max retry limit (seconds)
MAX_MAX_RETRY_INTERVAL: Final[int] = 600  # Maximum selectable max retry limit (seconds)

# Options Flow Configuration Keys
CONF_POLL_INTERVAL: Final[str] = "poll_interval"
CONF_MAX_RETRY_INTERVAL: Final[str] = "max_retry_interval"
