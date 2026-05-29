#!/usr/bin/env python3
"""Standalone CLI tool to scan and stream telemetry from an Anker Solix F2000 via BLE.

This script complies with the project's Python Code Style Guide (PEP 8, Type Hints, 100 char limit).
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from typing import Any, Optional

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
import SolixBLE.const
import SolixBLE.device
from SolixBLE import F2000, discover_devices


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


def save_env(mac: str, name: str) -> None:
    """Save the discovered MAC address and name to the .env file if not already set."""
    env_path = ".env"
    paths = [".env", "../.env", "test-scripts/.env"]
    for p in paths:
        if os.path.exists(p) or p == ".env":
            env_path = p
            break

    already_configured = False
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "ANKER_MAC_ADDRESS" in content:
                already_configured = True

    if not already_configured:
        logger.info("Saving discovered device to %s...", env_path)
        with open(
            env_path, "a" if os.path.exists(env_path) else "w", encoding="utf-8"
        ) as f:
            f.write("\n# Private Local Hardware Parameters (Git-Ignored)\n")
            f.write(f"ANKER_MAC_ADDRESS={mac}\n")
            f.write(f"ANKER_DEVICE_NAME={name}\n")
        logger.info(
            "Saved! ANKER_MAC_ADDRESS=%s, ANKER_DEVICE_NAME=%s", mac, name
        )
        os.environ["ANKER_MAC_ADDRESS"] = mac
        os.environ["ANKER_DEVICE_NAME"] = name
    else:
        logger.info(
            "ANKER_MAC_ADDRESS already configured in %s. Skipping auto-save.",
            env_path,
        )


# Hot-patch BleakClient to force response=False for write-without-response characteristic 00007777
original_write_gatt_char = BleakClient.write_gatt_char


async def custom_write_gatt_char(self, char_specifier, data, response=True):
    if str(char_specifier).lower() == "00007777-0000-1000-8000-00805f9b34fb":
        response = False
    return await original_write_gatt_char(self, char_specifier, data, response=response)


BleakClient.write_gatt_char = custom_write_gatt_char  # type: ignore[method-assign]

# Hot-patch SolixBLE UUID constants for compatibility with this F2000 model/firmware
SolixBLE.const.UUID_COMMAND = "00007777-0000-1000-8000-00805f9b34fb"
SolixBLE.const.UUID_TELEMETRY = "00008888-0000-1000-8000-00805f9b34fb"
SolixBLE.device.UUID_COMMAND = "00007777-0000-1000-8000-00805f9b34fb"
SolixBLE.device.UUID_TELEMETRY = "00008888-0000-1000-8000-00805f9b34fb"

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("solix_telemetry")


def print_telemetry(device: F2000) -> None:
    """Read and format all telemetry attributes from the F2000 device as a JSON block."""
    telemetry: dict[str, Any] = {
        "device_info": {
            "name": device.name,
            "address": device.address,
            "connected": device.connected,
            "available": device.available,
            "serial_number": device.serial_number,
            "software_version": device.software_version,
            "software_version_controller": device.software_version_controller,
        },
        "battery": {
            "percentage": device.battery_percentage,
            "health": device.battery_health,
            "temperature": device.temperature,
            "time_remaining_hours": device.hours_remaining,
            "time_remaining_days": device.days_remaining,
        },
        "power_input": {
            "ac_power_in": device.ac_power_in,
            "solar_power_in": device.solar_power_in,
            "ac_to_battery": device.ac_to_battery,
        },
        "power_output": {
            "ac_power_out": device.ac_power_out,
            "ac_sockets_on": device.ac_power_out_sockets,
            "dc_1_power_out": device.dc_1_power_out,
            "dc_2_power_out": device.dc_2_power_out,
            "usb_a1_power": device.usb_a1_power,
            "usb_a2_power": device.usb_a2_power,
            "usb_c1_power": device.usb_c1_power,
            "usb_c2_power": device.usb_c2_power,
            "usb_c3_power": device.usb_c3_power,
        },
    }

    # Ensure expansion battery telemetry is captured if present
    if device.num_expansion > 0:
        telemetry["expansion"] = {
            "num_expansion": device.num_expansion,
            "percentage": device.battery_percentage_expansion,
            "health": device.battery_health_expansion,
            "temperature": device.temperature_expansion,
            "software_version": device.software_version_expansion,
        }

    # Print formatted output to stdout
    print("\n--- Telemetry Update ---")
    print(json.dumps(telemetry, indent=2))
    print("------------------------\n")


async def scan_for_devices(timeout: int = 15) -> None:
    """Scan for nearby Anker Solix BLE devices and print discovery details."""
    logger.info("Starting SolixBLE filtered scan (timeout=%ds)...", timeout)
    try:
        devices = await discover_devices(timeout=timeout)
        if devices:
            logger.info("Discovered %d Solix device(s) via filtered scan:", len(devices))
            for dev in devices:
                print(f"[Anker Solix] MAC: {dev.address} | Name: {dev.name or 'Unknown'}")
        else:
            logger.info("No Solix devices discovered via filtered scan (UUID ff09 filter).")

        logger.info("Starting Raw Bleak Scan of ALL nearby BLE devices to troubleshoot...")
        raw_devices = await BleakScanner.discover(timeout=timeout)
        logger.info("Raw Scan discovered %d total BLE devices:", len(raw_devices))

        anker_candidates = []
        other_devices = []

        for dev in raw_devices:
            name = dev.name or "Unknown"
            # Flag any potential Anker devices
            if any(
                term in name.lower()
                for term in ["anker", "powerhouse", "solix", "767", "f2000"]
            ):
                anker_candidates.append(dev)
            else:
                other_devices.append(dev)

        if anker_candidates:
            print("\n*** POTENTIAL ANKER SOLIX CANDIDATES FOUND: ***")
            for dev in anker_candidates:
                print(f"-> MAC: {dev.address} | Name: {dev.name or 'Unknown'}")
            print("**********************************************\n")
        print("All Discovered BLE Devices (Raw list):")
        for dev in raw_devices:
            print(f"- MAC: {dev.address} | Name: {dev.name or 'Unknown'}")

        # Auto-save discovered candidate to .env on first run
        found_mac = None
        found_name = None
        if devices:
            found_mac = devices[0].address
            found_name = devices[0].name or "767_PowerHouse"
        elif anker_candidates:
            found_mac = anker_candidates[0].address
            found_name = anker_candidates[0].name or "767_PowerHouse"

        if found_mac and found_name:
            save_env(found_mac, found_name)

    except Exception as err:
        logger.error("Scan failed: %s", err, exc_info=True)


async def stream_telemetry(mac_address: str) -> None:
    """Connect to a specific Anker F2000 MAC address and stream parsed telemetry."""
    logger.info("Resolving BLE device for address: %s...", mac_address)

    # Resolve the BLE Device object
    ble_device: Optional[BLEDevice] = await BleakScanner.find_device_by_address(
        mac_address, timeout=10.0
    )
    if not ble_device:
        logger.error(
            "Could not find BLE device with address %s. Make sure it is in range.",
            mac_address,
        )
        return

    logger.info(
        "Device resolved: %s (%s). Initializing F2000 client...",
        ble_device.name,
        ble_device.address,
    )
    device = F2000(ble_device)

    # State update callback handler
    def on_state_changed() -> None:
        logger.info("State update received from Anker F2000")
        print_telemetry(device)

    # Register the callback
    device.add_callback(on_state_changed)

    try:
        logger.info("Connecting to Anker F2000 BLE radio (Exclusive link)...")
        logger.warning(
            "Ensure the official Anker app is force-closed to prevent connection lockout."
        )
        await device.connect()
        logger.info("Successfully connected! Streaming telemetry. Press Ctrl+C to disconnect.")

        # Keep the connection alive in an infinite loop
        while True:
            await asyncio.sleep(1.0)

    except asyncio.CancelledError:
        logger.info("Stream session interrupted. Initiating clean disconnect...")
    except Exception as err:
        logger.error("BLE connection error: %s", err, exc_info=True)
    finally:
        device.remove_callback(on_state_changed)
        if device.connected:
            logger.info("Disconnecting from BLE device...")
            await device.disconnect()
            logger.info("Cleanly disconnected from BLE radio.")


def main() -> None:
    """CLI Entrypoint parsing arguments and orchestrating execution."""
    load_env()

    parser = argparse.ArgumentParser(
        description="Stream local telemetry and verify BLE link with Anker Solix F2000."
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Scan and list all nearby discoverable Anker Solix BLE devices.",
    )
    parser.add_argument(
        "--mac",
        type=str,
        help="Connect and stream telemetry from the specified F2000 BLE MAC address.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=5,
        help="BLE scan timeout in seconds (default: 5).",
    )

    args = parser.parse_args()

    # Fallback to .env variable if --mac is not supplied
    target_mac = args.mac or os.getenv("ANKER_MAC_ADDRESS")

    try:
        if args.scan:
            asyncio.run(scan_for_devices(timeout=args.timeout))
        elif target_mac:
            asyncio.run(stream_telemetry(target_mac))
        else:
            logger.error(
                "No MAC address specified. Please provide a MAC address via --mac "
                "or define ANKER_MAC_ADDRESS in your .env file."
            )
            parser.print_help()
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Exiting cleanly via keyboard interrupt.")
        sys.exit(0)


if __name__ == "__main__":
    main()
