#!/usr/bin/env python3
"""Telemetry byte sniffer to detect display setting changes on F2000.

Connects to the F2000, continuously queries telemetry, and highlights
any bytes that change in real-time. Use this to discover the screen
timeout byte offsets and values by toggling settings in the official app.
"""

import asyncio
import logging
import os
import sys
from typing import Any

from bleak import BleakClient, BleakScanner

# Constants
NOTIFY_UUID = "00008888-0000-1000-8000-00805f9b34fb"
WRITE_UUID = "00007777-0000-1000-8000-00805f9b34fb"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("sniff_display")


def load_env() -> None:
    """Load key-value pairs from .env files into environment variables."""
    paths = [".env", "../.env", "tests/.env"]
    for path in paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, val = line.split("=", 1)
                        os.environ[key.strip()] = val.strip()
            break


def hex_grid(data: bytes, cols: int = 16) -> str:
    """Format raw bytes as a beautifully aligned hex grid."""
    lines = []
    for offset in range(0, len(data), cols):
        chunk = data[offset:offset + cols]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        hex_part = hex_part.ljust(cols * 3 - 1)
        ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
        lines.append(f"  {offset:04x}  {hex_part}  |{ascii_part}|")
    return "\n".join(lines)


class DisplaySettingsSniffer:
    """Sniffs BLE notifications to capture changes in real-time."""

    def __init__(self, mac_address: str):
        self.mac = mac_address
        self.last_telemetry: bytes | None = None
        self.last_state_ack: bytes | None = None

    def handle_notification(self, _sender: Any, data: bytearray) -> None:
        """Process notifications and highlight differences."""
        frame = bytes(data)
        if len(frame) < 10:
            return

        if frame[0] != 0x09 or frame[1] != 0xFF:
            return

        packet_type = frame[5]
        sub_type = frame[6]

        if packet_type == 0x01:  # Telemetry / State
            if sub_type == 0x49:  # Telemetry (102 bytes)
                if self.last_telemetry is None:
                    self.last_telemetry = frame
                    print("\n📥 INITIAL TELEMETRY RECEIVED (102 bytes):")
                    print(hex_grid(frame))
                else:
                    self.compare_frames("Telemetry (0x49)", self.last_telemetry, frame)
                    self.last_telemetry = frame
            elif sub_type == 0x48:  # State ACK (14 bytes)
                if self.last_state_ack is None:
                    self.last_state_ack = frame
                    print("\n📥 INITIAL STATE ACK RECEIVED (14 bytes):")
                    print(hex_grid(frame))
                else:
                    self.compare_frames("State ACK (0x48)", self.last_state_ack, frame)
                    self.last_state_ack = frame
        elif packet_type == 0x02:  # Command ACK
            print(f"📥 Received Command ACK: subtype=0x{sub_type:02x} -> {frame.hex()}")

    def compare_frames(self, name: str, old: bytes, new: bytes) -> None:
        """Compare two byte sequences and print differing bytes."""
        if len(old) != len(new):
            print(f"⚠️ {name} length changed from {len(old)} to {len(new)}!")
            return

        diffs = []
        for i in range(len(old)):
            if old[i] != new[i]:
                diffs.append(i)

        # Ignore rapid changes like remaining run time (index 17) or output power bytes
        filtered_diffs = [
            i for i in diffs
            if i not in (17, 101)  # 17 = hours remaining, 101 = checksum
            and i not in range(19, 43)  # Input/output power values fluctuate
        ]

        if filtered_diffs:
            print(f"\n🔄 {name} CHANGE DETECTED:")
            for idx in filtered_diffs:
                print(
                    f"  Index {idx:2d} (0-indexed) / {idx+1:2d} (1-indexed): "
                    f"Old={old[idx]:02x} ({old[idx]:3d}) ──> New={new[idx]:02x} ({new[idx]:3d})"
                )

    async def run(self) -> None:
        """Main connection and sniffing loop."""
        logger.info("Resolving BLE device for: %s...", self.mac)
        device = await BleakScanner.find_device_by_address(self.mac, timeout=20.0)
        if not device:
            logger.error("Could not find F2000 device in range.")
            return

        logger.info("Connecting to %s...", device.name or "F2000")
        async with BleakClient(device) as client:
            logger.info("Connected successfully! Subscribing...")
            await client.start_notify(NOTIFY_UUID, self.handle_notification)
            logger.info("Subscribed! Listening for updates...")

            # Telemetry ping packet
            query_pkt = bytes([0x08, 0xEE, 0x00, 0x00, 0x00, 0x01, 0x01, 0x0A, 0x00, 0x02])

            print("\n💡 Tip: Change the 'Screen Timeout' settings in your Anker App now!")
            print("Press Ctrl+C to disconnect and exit.\n")

            while client.is_connected:
                # Query telemetry every 2 seconds to keep the BLE session active
                # and prompt state updates
                try:
                    await client.write_gatt_char(WRITE_UUID, query_pkt, response=False)
                except Exception as err:
                    logger.warning("Failed to write query: %s", err)
                    break
                await asyncio.sleep(2.0)


def main() -> None:
    """Script entry point."""
    load_env()
    mac = os.getenv("ANKER_MAC_ADDRESS")
    if not mac:
        logger.error("ANKER_MAC_ADDRESS is not set in environment or .env.")
        sys.exit(1)

    try:
        asyncio.run(DisplaySettingsSniffer(mac).run())
    except KeyboardInterrupt:
        print("\n✋ Stopping sniffer session. Exiting cleanly.")


if __name__ == "__main__":
    main()
