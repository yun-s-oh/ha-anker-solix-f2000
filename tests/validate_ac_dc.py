#!/usr/bin/env python3
"""Standalone script to validate unencrypted BLE AC and DC controls on the Anker F2000.

This script connects to the real BLE device, registers notifications, sends AC and DC
toggle commands, and parses the returned state/telemetry notifications to programmatically
verify and validate the controls (tasks 1.4.1 and 1.4.2).
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
logger = logging.getLogger("validate_ac_dc")


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


def calculate_checksum(data: bytes) -> int:
    """Calculate the unencrypted protocol checksum."""
    return sum(data) & 0xFF


def build_unencrypted_packet(
    header_prefix: bytes, packet_type: int, cmd_id: int, payload: bytes
) -> bytes:
    """Build a complete unencrypted protocol frame with dynamic length and checksum."""
    packet = bytearray()
    packet.extend(header_prefix)
    packet.append(packet_type)
    packet.append(cmd_id)
    # Total length = prefix (5) + type (1) + cmd_id (1) + len_bytes (2) + payload + checksum (1)
    total_len = len(header_prefix) + 1 + 1 + 2 + len(payload) + 1
    packet.extend(total_len.to_bytes(2, byteorder="little"))
    packet.extend(payload)
    packet.append(calculate_checksum(bytes(packet)))
    return bytes(packet)


def build_f2000_control_packet(cmd_id: int, value: int) -> bytes:
    """Build a complete unencrypted command packet for Anker F2000 controls."""
    return build_unencrypted_packet(
        bytes([0x08, 0xEE, 0x00, 0x00, 0x00]),
        0x02,
        cmd_id,
        bytes([value]),
    )


def hex_grid(data: bytes) -> str:
    """Format raw bytes as a beautifully aligned hex grid."""
    cols = 16
    lines = []
    for offset in range(0, len(data), cols):
        chunk = data[offset:offset + cols]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        hex_part = hex_part.ljust(cols * 3 - 1)
        ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
        lines.append(f"  {offset:04x}  {hex_part}  |{ascii_part}|")
    return "\n".join(lines)


class VerificationSession:
    """BLE control validation session for Anker F2000."""

    def __init__(self, mac_address: str):
        self.mac = mac_address
        self.client: BleakClient | None = None
        self.ac_state: bool | None = None
        self.dc_state: bool | None = None
        self.last_parsed_packet_type: int | None = None
        self.last_parsed_sub_type: int | None = None
        self.update_event = asyncio.Event()

    def handle_notification(self, _sender: Any, data: bytearray) -> None:
        """Process incoming notification data."""
        frame = bytes(data)
        if len(frame) < 10:
            return

        if frame[0] != 0x09 or frame[1] != 0xFF:
            return

        packet_type = frame[5]
        sub_type = frame[6]

        self.last_parsed_packet_type = packet_type
        self.last_parsed_sub_type = sub_type

        # Decrypt / extract status based on sub_type
        if packet_type == 0x01:
            if sub_type == 0x48:  # StateAck
                self.ac_state = bool(frame[9])
                self.dc_state = bool(frame[10])
                logger.info(
                    "StateAck (0x48) received: AC=%s, DC=%s",
                    self.ac_state,
                    self.dc_state,
                )
                self.update_event.set()
            elif sub_type == 0x49 and len(frame) >= 102:  # Telemetry
                self.ac_state = bool(frame[63])
                self.dc_state = bool(frame[80])
                logger.info(
                    "Telemetry (0x49) received: AC=%s, DC=%s",
                    self.ac_state,
                    self.dc_state,
                )
                self.update_event.set()
            elif sub_type == 0x02:  # Subtype 2 Notification (State-like)
                # Let's log it and capture the state of data[9] and data[10]
                self.ac_state = bool(frame[9])
                self.dc_state = bool(frame[10])
                logger.info(
                    "Notification (0x02) received: data[9]=%02x, data[10]=%02x",
                    frame[9],
                    frame[10],
                )
                self.update_event.set()

    async def execute_validation(self) -> bool:
        """Run the automated validation sequence."""
        logger.info("Resolving BLE device for: %s...", self.mac)
        device = await BleakScanner.find_device_by_address(self.mac, timeout=10.0)
        if not device:
            logger.error("Could not find F2000 device in range.")
            return False

        logger.info("Connecting to %s...", device.name or "F2000")
        async with BleakClient(device) as client:
            self.client = client
            logger.info("Connected successfully! Subscribing to notifications...")
            await client.start_notify(NOTIFY_UUID, self.handle_notification)
            logger.info("Subscribed!")

            # 1. Query initial state
            query_pkt = bytes([0x08, 0xEE, 0x00, 0x00, 0x00, 0x01, 0x01, 0x0A, 0x00, 0x02])
            logger.info("📤 Querying initial device state...")
            self.update_event.clear()
            await client.write_gatt_char(WRITE_UUID, query_pkt, response=False)

            # Wait a moment for notifications
            await asyncio.sleep(2.0)
            logger.info(
                "Initial values captured: AC=%s, DC=%s",
                self.ac_state,
                self.dc_state,
            )

            # -----------------------------------------------------------------
            # Task 1.4.1: AC Output Toggle Verification
            # -----------------------------------------------------------------
            logger.info("\n=== 1.4.1 AC OUTPUT TOGGLE VALIDATION ===")

            if self.ac_state:
                ac_steps = [
                    ("OFF", 0x01, False),
                    ("ON", 0x00, True)
                ]
            else:
                ac_steps = [
                    ("ON", 0x00, True),
                    ("OFF", 0x01, False)
                ]

            for action_name, val, expected in ac_steps:
                logger.info("📤 Sending AC Output %s command...", action_name)
                ac_pkt = build_f2000_control_packet(0x86, val)
                logger.info("Packet: %s", ac_pkt.hex())
                self.update_event.clear()
                await client.write_gatt_char(WRITE_UUID, ac_pkt, response=False)

                try:
                    await asyncio.wait_for(self.update_event.wait(), timeout=4.0)
                    logger.info(
                        "Received update! Checked state: AC=%s (Expected: %s)",
                        self.ac_state,
                        expected,
                    )
                except asyncio.TimeoutError:
                    logger.warning("Timeout waiting for AC %s state notification.", action_name)

                await asyncio.sleep(2.0)

            # -----------------------------------------------------------------
            # Task 1.4.2: DC Output Toggle Verification
            # -----------------------------------------------------------------
            logger.info("\n=== 1.4.2 DC OUTPUT TOGGLE VALIDATION ===")

            if self.dc_state:
                dc_steps = [
                    ("OFF", 0x01, False),
                    ("ON", 0x00, True)
                ]
            else:
                dc_steps = [
                    ("ON", 0x00, True),
                    ("OFF", 0x01, False)
                ]

            for action_name, val, expected in dc_steps:
                logger.info("📤 Sending DC Output %s command...", action_name)
                dc_pkt = build_f2000_control_packet(0x87, val)
                logger.info("Packet: %s", dc_pkt.hex())
                self.update_event.clear()
                await client.write_gatt_char(WRITE_UUID, dc_pkt, response=False)

                try:
                    await asyncio.wait_for(self.update_event.wait(), timeout=4.0)
                    logger.info(
                        "Received update! Checked state: DC=%s (Expected: %s)",
                        self.dc_state,
                        expected,
                    )
                except asyncio.TimeoutError:
                    logger.warning("Timeout waiting for DC %s state notification.", action_name)

                await asyncio.sleep(2.0)

            await client.stop_notify(NOTIFY_UUID)

        logger.info("\n=== VALIDATION SESSION COMPLETED ===")
        return True


def main() -> None:
    """Script entry point."""
    load_env()
    mac = os.getenv("ANKER_MAC_ADDRESS")
    if not mac:
        logger.error("ANKER_MAC_ADDRESS is not set in your environment / .env file.")
        sys.exit(1)

    try:
        success = asyncio.run(VerificationSession(mac).execute_validation())
        if success:
            logger.info("Script completed successfully.")
        else:
            logger.error("Script encountered issues.")
    except KeyboardInterrupt:
        logger.info("Verification script interrupted.")
    except Exception as e:
        logger.exception("Fatal error in validation session: %s", e)


if __name__ == "__main__":
    main()
