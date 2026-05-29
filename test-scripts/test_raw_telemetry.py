#!/usr/bin/env python3
"""Standalone CLI script to stream and decode unencrypted BLE telemetry from the Anker F2000.

This script parses plain byte notification frames from characteristic 00008888,
and dumps the entire raw byte grid to facilitate discovering other telemetry registers.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any

from bleak import BleakClient, BleakScanner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("anker_raw_telemetry")


def load_env() -> None:
    """Dynamically find and load key-value pairs from .env or ../.env into os.environ."""
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


def get_int16(frame: bytes, offset: int) -> int:
    """Parse 2 bytes at the specified offset as a little-endian integer."""
    try:
        return int.from_bytes(frame[offset:offset + 2], byteorder="little")
    except IndexError:
        return 0


def format_time(minutes: int) -> str:
    """Convert minutes remaining into a human-readable duration string."""
    if minutes == 0 or minutes > 60000:
        return "Calculating..."
    days = minutes // 1440
    hours = (minutes % 1440) // 60
    mins = minutes % 60

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if mins > 0 or not parts:
        parts.append(f"{mins}m")

    return " ".join(parts)


def print_raw_byte_grid(frame: bytes) -> None:
    """Print the entire raw byte array as a beautifully structured grid with offset indices."""
    print("\n======================= RAW BYTE GRID =======================")
    print("Offset |  00  01  02  03  04  05  06  07  08  09 | HEX REPRESENTATION")
    print("-------+----------------------------------------+-------------------")

    for row_start in range(0, len(frame), 10):
        row_slice = frame[row_start:row_start + 10]
        # Format hex representations of the 10 bytes in this row
        hex_bytes = [f"{b:02x}" for b in row_slice]
        # Pad with empty spaces if the last row is shorter than 10 bytes
        while len(hex_bytes) < 10:
            hex_bytes.append("  ")

        hex_row_str = "  ".join(hex_bytes)
        ascii_representation = "".join(
            chr(b) if 32 <= b <= 126 else "." for b in row_slice
        )

        print(f" {row_start:4d}  |  {hex_row_str}  | {ascii_representation}")
    print("=============================================================\n")


def parse_frame(frame: bytes) -> dict[str, Any]:
    """Parse telemetry registers from raw unencrypted BLE byte frames."""
    try:
        # Basic boundary validation based on the F2000 telemetry payload length
        if len(frame) < 70:
            logger.warning("Frame length too short to parse: %d bytes", len(frame))
            return {}

        ac_output = get_int16(frame, 21)
        solar_input = get_int16(frame, 37)
        total_input = get_int16(frame, 39)
        total_output = get_int16(frame, 41)
        minutes_remaining = get_int16(frame, 76) if len(frame) > 77 else 0

        # Derived metrics
        ac_input = max(0, total_input - solar_input)

        data = {
            "device_status": {
                "frame_length_bytes": len(frame),
            },
            "battery": {
                "battery_level_pct": frame[70] if len(frame) > 70 else 0,
                "battery_temp_c": frame[66] if len(frame) > 66 else 0,
                "minutes_remaining": minutes_remaining,
                "time_remaining_str": format_time(minutes_remaining),
            },
            "power_in": {
                "solar_input_w": solar_input,
                "total_input_w": total_input,
                "grid_ac_input_w": ac_input,
            },
            "power_out": {
                "ac_output_w": ac_output,
                "total_output_w": total_output,
            },
        }

        # Check for expansion battery metrics
        if len(frame) > 71:
            data["expansion_battery"] = {
                "expansion_battery_level_pct": frame[71],
                "expansion_temp_c": frame[67] if len(frame) > 67 else 0,
            }

        # Scan for other non-zero registers (potential undocumented metrics)
        potential_registers = {}
        for offset in range(0, len(frame) - 1, 2):
            val = get_int16(frame, offset)
            # Filter out known offsets and zero values
            if val > 0 and offset not in [21, 37, 39, 41, 66, 67, 70, 71, 76]:
                potential_registers[f"int16_offset_{offset}"] = val

        if potential_registers:
            data["potential_undocumented_metrics"] = potential_registers

        return data
    except Exception as err:
        logger.error("Error parsing frame: %s", err, exc_info=True)
        return {}


async def main() -> None:
    load_env()
    mac_address = os.getenv("ANKER_MAC_ADDRESS")
    if not mac_address:
        logger.error("No ANKER_MAC_ADDRESS configured in your .env file.")
        sys.exit(1)

    logger.info("Resolving BLE device for address: %s...", mac_address)
    ble_device = await BleakScanner.find_device_by_address(mac_address, timeout=15.0)
    if not ble_device:
        logger.error("Could not find F2000 in range. Make sure it is in advertising mode.")
        return

    logger.info("Connecting to %s...", ble_device.name or "767_PowerHouse")

    async with BleakClient(ble_device) as client:
        logger.info("Connected! Connection state: %s", client.is_connected)

        # Try to read all readable characteristics to trigger macOS pairing/bonding if needed
        logger.info("Attempting to read all readable characteristics to trigger pairing/bonding...")
        for service in client.services:
            for char in service.characteristics:
                if "read" in char.properties:
                    try:
                        value = await client.read_gatt_char(char.uuid)
                        logger.info(
                            "Read Char %s: %s (hex: %s)",
                            char.uuid,
                            value,
                            value.hex(),
                        )
                    except Exception as read_err:
                        logger.warning(
                            "Could not read Char %s: %s", char.uuid, read_err
                        )

        # Locate notification and command characteristics
        notify_char_uuid = None
        write_char_uuid = None
        for service in client.services:
            for char in service.characteristics:
                if "8888" in char.uuid.lower():
                    notify_char_uuid = char.uuid
                elif "7777" in char.uuid.lower():
                    write_char_uuid = char.uuid

        if not notify_char_uuid:
            logger.error("Characteristic 00008888 (notify) not found in GATT database!")
            return

        logger.info("Subscribed to characteristic: %s", notify_char_uuid)

        notification_received = asyncio.Event()

        async def notification_handler(_sender: Any, data: bytearray) -> None:
            logger.info("Notification received! Received %d bytes.", len(data))
            notification_received.set()
            frame_bytes = bytes(data)

            # Print beautiful raw byte matrix
            print_raw_byte_grid(frame_bytes)

            # Parse unencrypted registers
            parsed_data = parse_frame(frame_bytes)
            if parsed_data:
                print("=================== DECODED VALUES ===================")
                print(json.dumps(parsed_data, indent=2))
                print("======================================================\n")

        await client.start_notify(notify_char_uuid, notification_handler)
        logger.info("Streaming telemetry stream... Press Ctrl+C to stop.")

        # If we have a write characteristic and haven't received anything, try sending pings
        ping_attempts = 0
        while client.is_connected:
            try:
                await asyncio.wait_for(notification_received.wait(), timeout=5.0)
                # Reset event for next notification
                notification_received.clear()
            except asyncio.TimeoutError:
                if write_char_uuid:
                    ping_attempts += 1
                    logger.info(
                        "No notifications received for 5s. Sending ping #%d...",
                        ping_attempts,
                    )
                    try:
                        # Try writing different query payloads to trigger telemetry
                        if ping_attempts == 1:
                            # 1. Standard negotiation initiation command from SolixBLE
                            payload = bytes.fromhex(
                                "ff0936000300010001a10442ad8c69a2246232646"
                                "3306231372d623735642d346162662d62613665"
                                "2d656337633939376332336537b9"
                            )
                            logger.info("Writing negotiation init hex to 00007777...")
                            await client.write_gatt_char(
                                write_char_uuid, payload, response=False
                            )
                        elif ping_attempts == 2:
                            # 2. Simple single byte 0x01
                            logger.info("Writing [0x01] to 00007777...")
                            await client.write_gatt_char(
                                write_char_uuid, bytes([0x01]), response=False
                            )
                        elif ping_attempts == 3:
                            # 3. Simple single byte 0x00
                            logger.info("Writing [0x00] to 00007777...")
                            await client.write_gatt_char(
                                write_char_uuid, bytes([0x00]), response=False
                            )
                        else:
                            logger.info("Waiting for telemetry notifications...")
                    except Exception as write_err:
                        logger.error(
                            "Failed to write ping command: %s", write_err
                        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stream interrupted. Exiting cleanly.")
        sys.exit(0)
    except Exception as e:
        logger.error("Fatal exception: %s", e, exc_info=True)
