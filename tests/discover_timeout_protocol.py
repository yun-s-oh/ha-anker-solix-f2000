#!/usr/bin/env python3
"""Automated protocol discovery script for Anker F2000 Screen Timeout.

Connects to the F2000, tries candidate packet formats, and verifies
them against real-time telemetry changes at bytes 105-106.
"""

import asyncio
import os
import sys
from typing import Any

from bleak import BleakClient, BleakScanner

NOTIFY_UUID = "00008888-0000-1000-8000-00805f9b34fb"
WRITE_UUID = "00007777-0000-1000-8000-00805f9b34fb"


def calculate_checksum(data: bytes) -> int:
    return sum(data) & 0xFF


def build_unencrypted_packet(
    header_prefix: bytes, packet_type: int, cmd_id: int, payload: bytes
) -> bytes:
    packet = bytearray()
    packet.extend(header_prefix)
    packet.append(packet_type)
    packet.append(cmd_id)
    total_len = len(header_prefix) + 1 + 1 + 2 + len(payload) + 1
    packet.extend(total_len.to_bytes(2, byteorder="little"))
    packet.extend(payload)
    packet.append(calculate_checksum(bytes(packet)))
    return bytes(packet)


class TimeoutProtocolDiscoverer:
    """BLE automated protocol discovery session."""

    def __init__(self, mac: str):
        self.mac = mac
        self.current_timeout: int | None = None
        self.event = asyncio.Event()

    def handle_notification(self, _sender: Any, data: bytearray) -> None:
        frame = bytes(data)
        if len(frame) == 122 and frame[5] == 0x01 and frame[6] == 0x01:
            # Bytes 105-106 form a uint16 LE seconds value
            self.current_timeout = int.from_bytes(frame[105:107], byteorder="little")
            self.event.set()

    async def run_discovery(self) -> None:
        device = await BleakScanner.find_device_by_address(self.mac, timeout=20.0)
        if not device:
            print("❌ Could not find device in range.")
            return

        print(f"🔗 Connected successfully to {device.name or 'F2000'}!")
        async with BleakClient(device) as client:
            await client.start_notify(NOTIFY_UUID, self.handle_notification)

            # Define telemetry query ping
            query_pkt = bytes([0x08, 0xEE, 0x00, 0x00, 0x00, 0x01, 0x01, 0x0A, 0x00, 0x02])

            async def get_current_timeout_state() -> int:
                self.event.clear()
                await client.write_gatt_char(WRITE_UUID, query_pkt, response=False)
                try:
                    await asyncio.wait_for(self.event.wait(), timeout=5.0)
                    return self.current_timeout or 0
                except asyncio.TimeoutError:
                    return 0

            # Get initial state
            initial = await get_current_timeout_state()
            print(f"📊 Initial Screen Timeout state in telemetry: {initial}s")

            # Candidate structures for setting Screen Timeout to 30 seconds
            candidates = [
                ("1-Byte Index 0x01", bytes([0x01])),
                ("1-Byte Index 0x02", bytes([0x02])),
                ("1-Byte Seconds (30)", bytes([30])),
                ("2-Byte LE Seconds (30)", (30).to_bytes(2, byteorder="little")),
                ("2-Byte BE Seconds (30)", (30).to_bytes(2, byteorder="big")),
                (
                    "3-Byte 0x00 + LE Seconds (30)",
                    bytes([0x00]) + (30).to_bytes(2, byteorder="little"),
                ),
                (
                    "3-Byte 0x00 + BE Seconds (30)",
                    bytes([0x00]) + (30).to_bytes(2, byteorder="big"),
                ),
            ]

            success_format = None

            for name, payload in candidates:
                print(f"\n⚙️ Testing format: {name} (Payload hex: {payload.hex()})...")
                packet = build_unencrypted_packet(
                    bytes([0x08, 0xEE, 0x00, 0x00, 0x00]),
                    0x02,
                    0x82,
                    payload,
                )

                # Send command packet
                await client.write_gatt_char(WRITE_UUID, packet, response=False)
                await asyncio.sleep(1.0)

                # Query telemetry to see if timeout changed to 30s
                new_state = await get_current_timeout_state()
                print(f"   🔍 Telemetry state is now: {new_state}s")

                if new_state == 30:
                    print(f"🎉 SUCCESS! Match found using format: {name}!")
                    success_format = name
                    break

            if success_format:
                # Let's verify by setting to 1m (60 seconds)
                print("\n🧪 Double-verifying: Setting timeout to 1 minute (60s)...")
                if "Index" in success_format:
                    # If index-based: index 3 represents 1m
                    verify_payload = bytes([0x03])
                elif "1-Byte Seconds" in success_format:
                    verify_payload = bytes([60])
                elif "2-Byte LE" in success_format:
                    verify_payload = (60).to_bytes(2, byteorder="little")
                elif "2-Byte BE" in success_format:
                    verify_payload = (60).to_bytes(2, byteorder="big")
                elif "3-Byte 0x00 + LE" in success_format:
                    verify_payload = bytes([0x00]) + (60).to_bytes(2, byteorder="little")
                else:
                    verify_payload = bytes([0x00]) + (60).to_bytes(2, byteorder="big")

                verify_packet = build_unencrypted_packet(
                    bytes([0x08, 0xEE, 0x00, 0x00, 0x00]),
                    0x02,
                    0x82,
                    verify_payload,
                )
                await client.write_gatt_char(WRITE_UUID, verify_packet, response=False)
                await asyncio.sleep(1.0)

                final_state = await get_current_timeout_state()
                print(f"   🔍 Final telemetry state is: {final_state}s")
                if final_state == 60:
                    print("✅ Double-verification successful! Timeout protocol fully resolved.")
                else:
                    print("❌ Double-verification failed.")
            else:
                print(
                    "\n❌ None of the tested candidate formats successfully "
                    "updated the timeout state."
                )

            await client.stop_notify(NOTIFY_UUID)


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
    mac = load_env()
    if not mac:
        print("❌ ANKER_MAC_ADDRESS is not set in environment or .env.")
        sys.exit(1)

    try:
        asyncio.run(TimeoutProtocolDiscoverer(mac).run_discovery())
    except KeyboardInterrupt:
        print("\n✋ Discovery script interrupted.")


if __name__ == "__main__":
    main()
