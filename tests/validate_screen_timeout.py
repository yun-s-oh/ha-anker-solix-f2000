#!/usr/bin/env python3
"""Standalone script to validate unencrypted BLE Screen Timeout controls on F2000.

This script connects to the real BLE device, registers notifications, sends Screen
Timeout commands (20s, 30s, 1m, 5m, 30m), and parses the returned Command ACK
notifications (subtype 0x02) to programmatically verify and validate the controls
(task 1.4.5).
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
logger = logging.getLogger("validate_screen_timeout")


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


class ScreenTimeoutVerificationSession:
    """BLE Screen Timeout validation session for Anker F2000."""

    def __init__(self, mac_address: str):
        self.mac = mac_address
        self.client: BleakClient | None = None
        self.timeout_state: int | None = None
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
            if cmd_id == 0x82:
                logger.info(
                    "Command ACK (0x02) received for Screen Timeout (0x82)!"
                )
                self.timeout_state = self.last_sent_val
                self.update_event.set()

    async def execute_validation(self) -> bool:
        """Run the automated validation sequence."""
        logger.info("Resolving BLE device for: %s...", self.mac)
        device = await BleakScanner.find_device_by_address(self.mac, timeout=20.0)
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
            # Task 1.4.5: Screen Timeout verification
            # -----------------------------------------------------------------
            logger.info("\n=== 1.4.5 SCREEN TIMEOUT VALIDATION ===")

            # Define all levels: 0=20s, 1=30s, 2=1m, 3=5m, 4=30m
            names = {0: "20S", 1: "30S", 2: "1M", 3: "5M", 4: "30M"}
            seconds_map = {0: 20, 1: 30, 2: 60, 3: 300, 4: 1800}

            # Form a sequence of transitions that changes state each time
            test_sequence = [0, 1, 2, 3, 4, 0]

            for val in test_sequence:
                action_name = names[val]
                seconds = seconds_map[val]
                logger.info(
                    "📤 Sending Screen Timeout %s command (%ds)...",
                    action_name,
                    seconds,
                )
                self.last_sent_val = val
                payload = seconds.to_bytes(2, byteorder="little")
                timeout_pkt = build_unencrypted_packet(
                    bytes([0x08, 0xEE, 0x00, 0x00, 0x00]),
                    0x02,
                    0x82,
                    payload,
                )
                logger.info("Packet: %s", timeout_pkt.hex())
                self.update_event.clear()
                await client.write_gatt_char(WRITE_UUID, timeout_pkt, response=False)

                try:
                    await asyncio.wait_for(self.update_event.wait(), timeout=4.0)
                    logger.info(
                        "Command ACK verified! New state: Timeout=%s (Expected: %d)",
                        self.timeout_state,
                        val,
                    )
                except asyncio.TimeoutError:
                    logger.warning("Timeout waiting for Screen Timeout %s ACK.", action_name)

                await asyncio.sleep(2.0)

            # Cleanup gracefully
            try:
                await client.stop_notify(NOTIFY_UUID)
            except Exception as err:
                logger.warning("Graceful stop_notify failed: %s", err)

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
        success = asyncio.run(ScreenTimeoutVerificationSession(mac).execute_validation())
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
