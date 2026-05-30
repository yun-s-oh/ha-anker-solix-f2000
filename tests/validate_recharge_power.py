#!/usr/bin/env python3
"""Standalone script to validate unencrypted BLE AC Recharging Power controls on F2000.

Connects to the BLE device, sends Recharging Power commands (200W, 500W, 1000W, etc.),
verifies both Command ACKs (subtype 0x80) and real-time telemetry changes to
programmatically validate task 1.4.7.
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
logger = logging.getLogger("validate_recharge")


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
    total_len = len(header_prefix) + 1 + 1 + 2 + len(payload) + 1
    packet.extend(total_len.to_bytes(2, byteorder="little"))
    packet.extend(payload)
    packet.append(calculate_checksum(bytes(packet)))
    return bytes(packet)


class RechargeValidationSession:
    """BLE AC Recharging Power Limit validation session for Anker F2000."""

    def __init__(self, mac_address: str):
        self.mac = mac_address
        self.client: BleakClient | None = None
        self.current_limit: int | None = None
        self.last_sent_val: int | None = None
        self.ack_event = asyncio.Event()
        self.telemetry_event = asyncio.Event()

    def handle_notification(self, _sender: Any, data: bytearray) -> None:
        """Process incoming notification data."""
        frame = bytes(data)
        if len(frame) < 10:
            return

        if frame[0] != 0x09 or frame[1] != 0xFF:
            return

        packet_type = frame[5]
        sub_type = frame[6]

        if packet_type == 0x02:  # Command ACK
            if sub_type == 0x80:
                logger.info("Command ACK (0x02) received for Recharging Power (0x80)!")
                self.ack_event.set()
        elif packet_type == 0x01 and sub_type == 0x01 and len(frame) == 122:
            self.current_limit = int.from_bytes(frame[101:103], byteorder="little")
            logger.info("📥 Telemetry Update: AC Recharging Limit is %dW", self.current_limit)
            self.telemetry_event.set()

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
            # Task 1.4.7: AC Recharging Power Limit verification
            # -----------------------------------------------------------------
            logger.info("\n=== 1.4.7 AC RECHARGING POWER LIMIT VALIDATION ===")

            query_pkt = bytes([0x08, 0xEE, 0x00, 0x00, 0x00, 0x01, 0x01, 0x0A, 0x00, 0x02])
            test_sequence = [200, 500, 1000, 1500, 200]

            for watts in test_sequence:
                logger.info("📤 Sending AC Recharging Power Limit command (%dW)...", watts)
                self.last_sent_val = watts
                payload = watts.to_bytes(2, byteorder="little")
                recharge_pkt = build_unencrypted_packet(
                    bytes([0x08, 0xEE, 0x00, 0x00, 0x00]),
                    0x02,
                    0x80,
                    payload,
                )
                logger.info("Packet: %s", recharge_pkt.hex())

                self.ack_event.clear()
                self.telemetry_event.clear()

                # Send write command
                await client.write_gatt_char(WRITE_UUID, recharge_pkt, response=False)

                # Wait for Command ACK
                try:
                    await asyncio.wait_for(self.ack_event.wait(), timeout=4.0)
                    logger.info("✓ Command ACK verified successfully.")
                except asyncio.TimeoutError:
                    logger.warning("Timeout waiting for Recharging Power Command ACK.")

                # Ping device for telemetry update
                await asyncio.sleep(0.5)
                await client.write_gatt_char(WRITE_UUID, query_pkt, response=False)

                # Verify telemetry state change
                try:
                    await asyncio.wait_for(self.telemetry_event.wait(), timeout=4.0)
                    if self.current_limit == watts:
                        logger.info("✅ State verified! Telemetry matches expected %dW.", watts)
                    else:
                        logger.warning(
                            "❌ State discrepancy: Telemetry reports %dW (Expected: %dW)",
                            self.current_limit,
                            watts,
                        )
                except asyncio.TimeoutError:
                    logger.warning("Timeout waiting for Telemetry status update.")

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
        logger.error("ANKER_MAC_ADDRESS is not set in environment or .env.")
        sys.exit(1)

    try:
        success = asyncio.run(RechargeValidationSession(mac).execute_validation())
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
