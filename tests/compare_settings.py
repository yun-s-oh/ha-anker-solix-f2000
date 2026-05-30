#!/usr/bin/env python3
"""Script to save and compare F2000 telemetry frames to find display setting bytes.

Usage:
  1. Set screen timeout to 30m in the app.
  2. Run: python compare_settings.py save
  3. Close app, set screen timeout to 20s (or 30s) in the app.
  4. Run: python compare_settings.py compare
"""

import asyncio
import os
import sys
from typing import Any

from bleak import BleakClient, BleakScanner

NOTIFY_UUID = "00008888-0000-1000-8000-00805f9b34fb"
WRITE_UUID = "00007777-0000-1000-8000-00805f9b34fb"
BIN_FILE = "telemetry_saved.bin"


def calculate_checksum(data: bytes) -> int:
    return sum(data) & 0xFF


class TelemetryCollector:
    """Connects to the F2000, fetches a single 122-byte frame, and exits."""

    def __init__(self, mac: str):
        self.mac = mac
        self.frame: bytes | None = None
        self.event = asyncio.Event()

    def handle_notification(self, _sender: Any, data: bytearray) -> None:
        frame = bytes(data)
        if len(frame) == 122 and frame[5] == 0x01 and frame[6] == 0x01:
            self.frame = frame
            self.event.set()

    async def collect(self) -> bytes | None:
        device = await BleakScanner.find_device_by_address(self.mac, timeout=20.0)
        if not device:
            print("❌ Could not find device in range.")
            return None

        async with BleakClient(device) as client:
            await client.start_notify(NOTIFY_UUID, self.handle_notification)

            # Query 0x01 packet
            query_pkt = bytes([0x08, 0xEE, 0x00, 0x00, 0x00, 0x01, 0x01, 0x0A, 0x00, 0x02])
            await client.write_gatt_char(WRITE_UUID, query_pkt, response=False)

            try:
                await asyncio.wait_for(self.event.wait(), timeout=8.0)
            except asyncio.TimeoutError:
                print("⚠️ Timeout waiting for 122-byte telemetry frame.")

            await client.stop_notify(NOTIFY_UUID)

        return self.frame


def load_env() -> str:
    paths = [".env", "../.env", "tests/.env"]
    for path in paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line:
                        k, v = line.split("=", 1)
                        if k.strip() == "ANKER_MAC_ADDRESS":
                            return v.strip()
    return ""


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in ("save", "compare"):
        print("Usage:")
        print("  python compare_settings.py save")
        print("  python compare_settings.py compare")
        sys.exit(1)

    mac = load_env()
    if not mac:
        print("❌ ANKER_MAC_ADDRESS not found in .env.")
        sys.exit(1)

    action = sys.argv[1]

    if action == "save":
        print(f"🔗 Connecting to {mac} to save current telemetry...")
        loop = asyncio.new_event_loop()
        frame = loop.run_until_complete(TelemetryCollector(mac).collect())
        if frame:
            with open(BIN_FILE, "wb") as f:
                f.write(frame)
            print(f"✅ Saved 122 bytes of telemetry to {BIN_FILE}.")
            print(
                "Now open the app, change your Screen Timeout to 20s (or other), "
                "close the app, and run:"
            )
            print("  python compare_settings.py compare")
        else:
            print("❌ Failed to collect telemetry.")

    elif action == "compare":
        if not os.path.exists(BIN_FILE):
            print(f"❌ Saved file {BIN_FILE} not found. Run 'save' first.")
            sys.exit(1)

        with open(BIN_FILE, "rb") as f:
            old_frame = f.read()

        print(f"🔗 Connecting to {mac} to get new telemetry for comparison...")
        loop = asyncio.new_event_loop()
        new_frame = loop.run_until_complete(TelemetryCollector(mac).collect())
        if not new_frame:
            print("❌ Failed to collect new telemetry.")
            sys.exit(1)

        print("\n=== TELEMETRY COMPARISON RESULTS ===")
        diffs = []
        for i in range(len(old_frame)):
            if old_frame[i] != new_frame[i]:
                diffs.append(i)

        # Filter out power fluctuations (bytes 19-42), remaining hours (index 17),
        # and checksum (index 121)
        filtered_diffs = [
            i for i in diffs
            if i not in (17, 121)
            and i not in range(19, 43)
        ]

        if not filtered_diffs:
            print("No static setting changes detected.")
        else:
            for idx in filtered_diffs:
                old_val = old_frame[idx]
                new_val = new_frame[idx]
                print(f"Index {idx} (1-based: {idx+1}):")
                print(f"  Old (Saved):  0x{old_val:02x} ({old_val})")
                print(f"  New (Current): 0x{new_val:02x} ({new_val})")


if __name__ == "__main__":
    main()
