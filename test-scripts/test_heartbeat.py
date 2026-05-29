#!/usr/bin/env python3
"""Standalone CLI script to test F2000 BLE connection persistence and active heartbeats.

This script complies with the Python Code Style Guide (PEP 8, Type Hints, 100 char limit).
"""

import argparse
import asyncio
import logging
import os
import sys
from typing import Any

from bleak import BleakClient, BleakScanner

# Constants
NOTIFY_UUID = "00008888-0000-1000-8000-00805f9b34fb"
WRITE_UUID = "00007777-0000-1000-8000-00805f9b34fb"

# Structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("f2000_heartbeat")


def load_env() -> None:
    """Dynamically load key-value pairs from .env files into environment variables."""
    paths = [".env", "../.env", "test-scripts/.env"]
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


async def main() -> None:
    """Entry point orchestrating the BLE connection and periodic pings."""
    load_env()

    parser = argparse.ArgumentParser(
        description="Verify BLE connection persistence and heartbeat timeouts on Anker F2000."
    )
    parser.add_argument(
        "--mac",
        type=str,
        help="Target MAC address or UUID to connect to.",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Interval between heartbeats in seconds (default: 300 / 5 minutes).",
    )
    args = parser.parse_args()

    mac_address = args.mac or os.getenv("ANKER_MAC_ADDRESS")
    if not mac_address:
        logger.error("No MAC address specified. Use --mac or define ANKER_MAC_ADDRESS in .env.")
        sys.exit(1)

    logger.info("Resolving BLE device: %s...", mac_address)
    ble_device = await BleakScanner.find_device_by_address(mac_address, timeout=15.0)
    if not ble_device:
        logger.error("Device %s not found in range.", mac_address)
        sys.exit(1)

    logger.info("Device resolved: %s (%s)", ble_device.name or "Unknown", ble_device.address)

    # Standard unencrypted telemetry query packet (10 bytes)
    # Header: 08 EE 00 00 00 01, Cmd: 01, Length: 0A 00, Checksum: 02
    heartbeat_ping = bytes([0x08, 0xEE, 0x00, 0x00, 0x00, 0x01, 0x01, 0x0A, 0x00, 0x02])

    ping_count = 0
    response_count = 0

    def notification_handler(_sender: Any, data: bytearray) -> None:
        nonlocal response_count
        frame = bytes(data)
        response_count += 1
        logger.info(
            "📥 Received notification response #%d (%d bytes): %s",
            response_count,
            len(frame),
            frame[:12].hex() + ("..." if len(frame) > 12 else ""),
        )

    logger.info("Connecting to Anker F2000...")
    async with BleakClient(ble_device) as client:
        logger.info("Connected successfully!")
        logger.info("Subscribing to notifications on %s...", NOTIFY_UUID)
        await client.start_notify(NOTIFY_UUID, notification_handler)
        logger.info("✓ Subscribed!")

        # Initial keep-alive ping
        ping_count += 1
        logger.info("📤 Sending initial heartbeat ping #%d...", ping_count)
        await client.write_gatt_char(WRITE_UUID, heartbeat_ping, response=False)
        logger.info("   ✓ Heartbeat sent: %s", heartbeat_ping.hex())

        logger.info(
            "⏳ Connection active. Sending heartbeat pings every %ds. Press Ctrl+C to exit.",
            args.interval,
        )

        try:
            while client.is_connected:
                await asyncio.sleep(1)
                args.interval -= 1
                if args.interval <= 0:
                    ping_count += 1
                    logger.info("📤 Sending periodic heartbeat ping #%d...", ping_count)
                    try:
                        await client.write_gatt_char(WRITE_UUID, heartbeat_ping, response=False)
                        logger.info("   ✓ Heartbeat sent successfully!")
                    except Exception as err:
                        logger.error("   ❌ Heartbeat failed: %s", err)
                    # Reset interval
                    args.interval = args.interval or 300
        except asyncio.CancelledError:
            pass

    logger.info("Session ended. Heartbeats sent: %d, Responses: %d", ping_count, response_count)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n✋ Keyboard Interrupt. Exiting cleanly.")
        sys.exit(0)
    except Exception as e:
        logger.error("Fatal exception: %s", e, exc_info=True)
        sys.exit(1)
