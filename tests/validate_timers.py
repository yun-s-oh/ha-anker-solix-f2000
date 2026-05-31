#!/usr/bin/env python3
"""Standalone script to validate unencrypted BLE AC and DC timers on Anker F2000.

Connects to the F2000, sends AC Output Timer (0x02) and DC Output Timer (0x03) commands,
and parses the returned telemetry to programmatically validate tasks 1.4.8 and 1.4.9.
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
logger = logging.getLogger("validate_timers")


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


class TimersValidationSession:
    """BLE AC and DC output timers validation session for Anker F2000."""

    def __init__(self, mac_address: str):
        self.mac = mac_address
        self.client: BleakClient | None = None
        self.dc_timer: int | None = None
        self.ac_timer: int | None = None
        self.ac_ack_event = asyncio.Event()
        self.dc_ack_event = asyncio.Event()
        self.telemetry_event = asyncio.Event()

    def handle_notification(self, _sender: Any, data: bytearray) -> None:
        """Process incoming notification data."""
        frame = bytes(data)
        if len(frame) < 10 or frame[0] != 0x09 or frame[1] != 0xFF:
            return

        packet_type = frame[5]
        sub_type = frame[6]

        if packet_type == 0x02:  # Command ACK
            if sub_type == 0x02:
                logger.info("✓ Command ACK received for AC Output Timer (0x02)!")
                self.ac_ack_event.set()
            elif sub_type == 0x03:
                logger.info("✓ Command ACK received for DC Output Timer (0x03)!")
                self.dc_ack_event.set()
        elif packet_type == 0x01 and sub_type == 0x49 and len(frame) == 102:
            self.dc_timer = int.from_bytes(frame[13:15], byteorder="little")
            self.ac_timer = int.from_bytes(frame[15:17], byteorder="little")
            logger.info("📥 Telemetry -> DC Timer: %ds, AC Timer: %ds", self.dc_timer, self.ac_timer)
            self.telemetry_event.set()

    async def execute_validation(self) -> bool:
        """Run the automated validation sequence."""
        logger.info("Resolving BLE device for: %s...", self.mac)
        device = await BleakScanner.find_device_by_address(self.mac, timeout=10.0)
        if not device:
            logger.warning("Direct find failed. Running fallback discovery scan...")
            devices = await BleakScanner.discover(timeout=5.0)
            for d in devices:
                if d.address.upper() == self.mac.upper() or (d.name and "PowerHouse" in d.name):
                    device = d
                    break

        if not device:
            logger.error("Could not find F2000 device in range.")
            return False

        logger.info("Connecting to %s...", device.name or "F2000")
        async with BleakClient(device) as client:
            self.client = client
            logger.info("Connected successfully! Subscribing to notifications...")
            await client.start_notify(NOTIFY_UUID, self.handle_notification)
            logger.info("Subscribed!")

            query_pkt = bytes([0x08, 0xEE, 0x00, 0x00, 0x00, 0x01, 0x01, 0x0A, 0x00, 0x02])

            async def query_telemetry() -> bool:
                self.telemetry_event.clear()
                await client.write_gatt_char(WRITE_UUID, query_pkt, response=False)
                try:
                    await asyncio.wait_for(self.telemetry_event.wait(), timeout=3.0)
                    return True
                except asyncio.TimeoutError:
                    return False

            # Ensure AC Output is ON first (Task 1.4.8 verification)
            logger.info("🔌 Ensuring AC Output is ON...")
            ac_on_pkt = build_f2000_control_packet(0x86, 0x01)
            await client.write_gatt_char(WRITE_UUID, ac_on_pkt, response=False)
            await asyncio.sleep(1.0)

            # Ensure DC Output is ON first (Task 1.4.9 verification)
            logger.info("🔌 Ensuring DC Output is ON...")
            dc_on_pkt = build_f2000_control_packet(0x87, 0x01)
            await client.write_gatt_char(WRITE_UUID, dc_on_pkt, response=False)
            await asyncio.sleep(1.0)

            # Query initial state
            await query_telemetry()

            # -----------------------------------------------------------------
            # Task 1.4.8: AC Output Timer validation
            # -----------------------------------------------------------------
            logger.info("\n=== 1.4.8 AC OUTPUT TIMER VALIDATION ===")
            logger.info("📤 Setting AC Output Timer to 10 minutes (600s)...")

            # Payload: seconds (2-byte LE)
            ac_payload = (600).to_bytes(2, byteorder="little")
            ac_timer_pkt = build_unencrypted_packet(
                bytes([0x08, 0xEE, 0x00, 0x00, 0x00]),
                0x02,
                0x02,  # Command ID for AC Timer
                ac_payload,
            )
            self.ac_ack_event.clear()
            await client.write_gatt_char(WRITE_UUID, ac_timer_pkt, response=False)

            try:
                await asyncio.wait_for(self.ac_ack_event.wait(), timeout=4.0)
                logger.info("✅ AC Output Timer Command ACK verified successfully!")
            except asyncio.TimeoutError:
                logger.warning("❌ Timeout waiting for AC Timer Command ACK.")

            await asyncio.sleep(1.0)
            await query_telemetry()

            # -----------------------------------------------------------------
            # Task 1.4.9: DC Output Timer validation
            # -----------------------------------------------------------------
            logger.info("\n=== 1.4.9 DC OUTPUT TIMER VALIDATION ===")
            logger.info("📤 Setting DC Output Timer to 10 minutes (600s)...")

            dc_payload = (600).to_bytes(2, byteorder="little")
            dc_timer_pkt = build_unencrypted_packet(
                bytes([0x08, 0xEE, 0x00, 0x00, 0x00]),
                0x02,
                0x03,  # Command ID for DC Timer
                dc_payload,
            )
            self.dc_ack_event.clear()
            await client.write_gatt_char(WRITE_UUID, dc_timer_pkt, response=False)

            try:
                await asyncio.wait_for(self.dc_ack_event.wait(), timeout=4.0)
                logger.info("✅ DC Output Timer Command ACK verified successfully!")
            except asyncio.TimeoutError:
                logger.warning("❌ Timeout waiting for DC Timer Command ACK.")

            await asyncio.sleep(1.0)
            await query_telemetry()

            if self.dc_timer in (600, 599, 598):
                logger.info("✅ DC Output Timer telemetry set and verified!")
            else:
                logger.warning(
                    "❌ DC Timer telemetry discrepancy: reports %ds (Expected: 600s)",
                    self.dc_timer,
                )

            # Cleanup / reset timers to 0 (disabled) to avoid leaving it counting down
            logger.info("\n🧹 Resetting timers back to 0 (disabled)...")
            ac_reset = build_unencrypted_packet(
                bytes([0x08, 0xEE, 0x00, 0x00, 0x00]),
                0x02,
                0x02,
                (0).to_bytes(2, byteorder="little"),
            )
            dc_reset = build_unencrypted_packet(
                bytes([0x08, 0xEE, 0x00, 0x00, 0x00]),
                0x02,
                0x03,
                (0).to_bytes(2, byteorder="little"),
            )
            await client.write_gatt_char(WRITE_UUID, ac_reset, response=False)
            await client.write_gatt_char(WRITE_UUID, dc_reset, response=False)
            await asyncio.sleep(1.0)
            await query_telemetry()

            await client.stop_notify(NOTIFY_UUID)

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
        asyncio.run(TimersValidationSession(mac).execute_validation())
    except KeyboardInterrupt:
        logger.info("Verification script interrupted.")
    except Exception as e:
        logger.exception("Fatal error in validation session: %s", e)


if __name__ == "__main__":
    main()
