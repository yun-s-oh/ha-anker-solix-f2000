#!/usr/bin/env python3
"""Exhaustive protocol discovery script for Anker F2000 AC Recharging Power Limit.

Scans command IDs 0x80 to 0x90 and tests four payload formats to find the
correct unencrypted write command.
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


class ExhaustiveDiscoverer:
    """BLE exhaustive recharging limit protocol discovery session."""

    def __init__(self, mac: str):
        self.mac = mac
        self.current_limit: int | None = None
        self.event = asyncio.Event()

    def handle_notification(self, _sender: Any, data: bytearray) -> None:
        frame = bytes(data)
        if len(frame) == 122 and frame[5] == 0x01 and frame[6] == 0x01:
            self.current_limit = int.from_bytes(frame[101:103], byteorder="little")
            self.event.set()

    async def run_discovery(self) -> None:
        device = await BleakScanner.find_device_by_address(self.mac, timeout=20.0)
        if not device:
            print("❌ Could not find device in range.")
            return

        print(f"🔗 Connected successfully to {device.name or 'F2000'}!")
        async with BleakClient(device) as client:
            await client.start_notify(NOTIFY_UUID, self.handle_notification)

            query_pkt = bytes([0x08, 0xEE, 0x00, 0x00, 0x00, 0x01, 0x01, 0x0A, 0x00, 0x02])

            async def get_current_limit_state() -> int:
                self.event.clear()
                await client.write_gatt_char(WRITE_UUID, query_pkt, response=False)
                try:
                    await asyncio.wait_for(self.event.wait(), timeout=4.0)
                    return self.current_limit or 0
                except asyncio.TimeoutError:
                    return 0

            # Get initial state
            initial = await get_current_limit_state()
            print(f"📊 Initial AC Recharging Power Limit in telemetry: {initial}W")

            # Command range 0x80 to 0x90
            commands = list(range(0x80, 0x91))

            target_watts = 300

            success_cmd = None
            success_name = None

            for cmd in commands:
                # Exclude already-verified standard toggles to prevent accidental changes
                # 0x86=AC, 0x87=DC, 0x8a=PowerSave, 0x8b=LED
                if cmd in (0x86, 0x87, 0x8a, 0x8b):
                    continue

                # Formats to test:
                formats = [
                    ("1-Byte Scale 100 (0x03)", bytes([target_watts // 100])),
                    ("1-Byte Scale 10 (0x1e)", bytes([target_watts // 10])),
                    ("2-Byte LE Watts (2c01)", target_watts.to_bytes(2, byteorder="little")),
                    (
                        "3-Byte 0x00+LE (002c01)",
                        bytes([0x00]) + target_watts.to_bytes(2, byteorder="little"),
                    ),
                ]

                for name, payload in formats:
                    print(
                        f"⚙️ Testing Cmd 0x{cmd:02x} | Format: {name:25s} | "
                        f"Payload: {payload.hex()}"
                    )
                    packet = build_unencrypted_packet(
                        bytes([0x08, 0xEE, 0x00, 0x00, 0x00]),
                        0x02,
                        cmd,
                        payload,
                    )

                    try:
                        await client.write_gatt_char(WRITE_UUID, packet, response=False)
                    except Exception as err:
                        print(f"   ⚠️ Write failed: {err}")
                        continue

                    await asyncio.sleep(0.8)
                    new_state = await get_current_limit_state()

                    if new_state == 300:
                        print("\n🎉 SUCCESS! Match found!")
                        print(f"   Command ID:  0x{cmd:02x}")
                        print(f"   Format:      {name}")
                        print(f"   Payload Hex: {payload.hex()}")
                        success_cmd = cmd
                        success_name = name
                        break

                if success_cmd is not None:
                    break

            if success_cmd is not None:
                # Double-verify by setting to 400W
                print("\n🧪 Double-verifying: Setting limit to 400W...")
                verify_watts = 400
                if "Scale 100" in success_name:
                    verify_payload = bytes([verify_watts // 100])
                elif "Scale 10" in success_name:
                    verify_payload = bytes([verify_watts // 10])
                elif "2-Byte LE" in success_name:
                    verify_payload = verify_watts.to_bytes(2, byteorder="little")
                else:
                    verify_payload = bytes([0x00]) + verify_watts.to_bytes(2, byteorder="little")

                verify_packet = build_unencrypted_packet(
                    bytes([0x08, 0xEE, 0x00, 0x00, 0x00]),
                    0x02,
                    success_cmd,
                    verify_payload,
                )
                await client.write_gatt_char(WRITE_UUID, verify_packet, response=False)
                await asyncio.sleep(1.0)

                final_state = await get_current_limit_state()
                print(f"   🔍 Final telemetry state is: {final_state}W")
                if final_state == 400:
                    print("✅ Double-verification successful! Recharging limit fully resolved.")
                else:
                    print("❌ Double-verification failed.")
            else:
                print("\n❌ Exhaustive scan completed. No matching format found.")

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
        asyncio.run(ExhaustiveDiscoverer(mac).run_discovery())
    except KeyboardInterrupt:
        print("\n✋ Discovery script interrupted.")


if __name__ == "__main__":
    main()
