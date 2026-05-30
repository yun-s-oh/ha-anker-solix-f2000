#!/usr/bin/env python3
"""Diagnostic script to print all GATT services and characteristics from the Anker F2000."""

import asyncio
import os
import sys
from bleak import BleakClient, BleakScanner


def load_env() -> None:
    """Dynamically find and load key-value pairs from .env or ../.env into os.environ."""
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


async def main():
    load_env()
    mac_address = os.getenv("ANKER_MAC_ADDRESS")
    if not mac_address:
        print(
            "Error: No MAC address specified. "
            "Please define ANKER_MAC_ADDRESS in your .env file."
        )
        sys.exit(1)

    print(f"Resolving BLE device for address: {mac_address}...")
    ble_device = await BleakScanner.find_device_by_address(mac_address, timeout=10.0)
    if not ble_device:
        print(f"Could not find device {mac_address} in range.")
        return

    print(f"Device resolved: {ble_device.name or 'Unknown'} ({ble_device.address})")
    print("Connecting to peripheral...")

    async with BleakClient(ble_device) as client:
        print(f"Connected! Connection state: {client.is_connected}")
        print("\n--- Discovered GATT Services & Characteristics ---")
        for service in client.services:
            print(f"\n[Service] {service.uuid} - {service.description}")
            for char in service.characteristics:
                props = ", ".join(char.properties)
                print(
                    f"  |- [Char] {char.uuid} | "
                    f"Properties: {props} | "
                    f"Description: {char.description}"
                )
        print("\n-------------------------------------------------")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
