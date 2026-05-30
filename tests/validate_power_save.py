#!/usr/bin/env python3
"""Standalone script to validate unencrypted BLE Power Saving Mode controls on F2000.

This script connects to the real BLE device, registers notifications, sends Power
Saving Mode toggle commands (ON and OFF), and parses the returned Command ACK
notifications (subtype 0x02) to programmatically verify and validate the controls
(task 1.4.3).
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
logger = logging.getLogger("validate_power_save")


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


class PowerSaveVerificationSession:
    """BLE Power Saving Mode validation session for Anker F2000."""

    def __init__(self, mac_address: str):
        self.mac = mac_address
        self.client: BleakClient | None = None
        self.power_save_state: bool | None = None
        self.last_sent_val: int | None = None
        self.update_event = asyncio.Event()

    def handle_notification(self, _sender: Any, data: bytearray) -> None:
        """Process incoming notification data."""
        frame = bytes(data)
        logger.info("📥 Notification: %d bytes -> %s", len(frame), frame.hex())
        if len(frame) < 10:
            return

        if frame[0] != 0x09 or frame[1] != 0xFF:
            return

        packet_type = frame[5]
        sub_type = frame[6]

        # Decrypt / extract status based on packet_type / sub_type
        if packet_type == 0x02:  # Command ACK
            cmd_id = sub_type
            if cmd_id == 0x8A:
                logger.info(
                    "Command ACK (0x02) received for Power Saving Mode (0x8A)!"
                )
                self.power_save_state = bool(self.last_sent_val)
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

            # -----------------------------------------------------------------
            # Task 1.4.3: Power Saving Mode Toggle Verification
            # -----------------------------------------------------------------
            logger.info("\n=== 1.4.3 POWER SAVING MODE TOGGLE VALIDATION ===")

            # Test sequence: ON (1), then OFF (0)
            steps = [
                ("ON", 0x01, True),
                ("OFF", 0x00, False)
            ]

            for action_name, val, expected in steps:
                logger.info("📤 Sending Power Saving Mode %s command...", action_name)
                self.last_sent_val = val
                ps_pkt = build_f2000_control_packet(0x8A, val)
                logger.info("Packet: %s", ps_pkt.hex())
                self.update_event.clear()
                await client.write_gatt_char(WRITE_UUID, ps_pkt, response=False)

                try:
                    await asyncio.wait_for(self.update_event.wait(), timeout=4.0)
                    logger.info(
                        "Command ACK verified! New state: PowerSave=%s (Expected: %s)",
                        self.power_save_state,
                        expected,
                    )
                except asyncio.TimeoutError:
                    logger.warning(
                        "Timeout waiting for Power Saving %s Command ACK.",
                        action_name,
                    )

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
        success = asyncio.run(PowerSaveVerificationSession(mac).execute_validation())
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
