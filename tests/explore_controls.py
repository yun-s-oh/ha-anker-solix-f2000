#!/usr/bin/env python3
"""Standalone BLE exploration and control discovery script for Anker F2000.

This script complies with the Python Code Style Guide (PEP 8, Type Hints, 100 char limit).
"""

import asyncio
import os
import sys
from typing import Any

from bleak import BleakClient, BleakScanner

# Constants
NOTIFY_UUID = "00008888-0000-1000-8000-00805f9b34fb"
WRITE_UUID = "00007777-0000-1000-8000-00805f9b34fb"


def load_env() -> None:
    """Dynamically load key-value pairs from .env files into environment variables."""
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
    """Calculate the unencrypted protocol checksum (sum of all preceding bytes & 0xFF)."""
    return sum(data) & 0xFF


def hex_grid(data: bytes, cols: int = 16) -> str:
    """Format raw bytes as a beautifully aligned hex grid with an ASCII sidebar."""
    lines = []
    for offset in range(0, len(data), cols):
        chunk = data[offset:offset + cols]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        hex_part = hex_part.ljust(cols * 3 - 1)
        ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
        lines.append(f"  {offset:04x}  {hex_part}  |{ascii_part}|")
    return "\n".join(lines)


def build_unencrypted_packet(
    header_prefix: bytes, packet_type: int, cmd_id: int, payload: bytes
) -> bytes:
    """Build a complete unencrypted protocol frame with dynamic length and checksum."""
    packet = bytearray()
    packet.extend(header_prefix)  # Default: 08 EE 00 00 00
    packet.append(packet_type)    # Default: 01 (or 02)
    packet.append(cmd_id)         # Command Subtype
    # Calculate length: header (5) + type (1) + cmd_id (1) + len_bytes (2) + payload + checksum (1)
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


def parse_packet(data: bytes) -> str:
    """Introspect and parse key known packets to help with control exploration."""
    if len(data) < 10:
        return "Short Packet"

    chk = data[-1]
    expected_chk = calculate_checksum(data[:-1])
    chk_status = "OK" if chk == expected_chk else f"INVALID (expected {expected_chk:02x})"

    packet_type_byte = data[5]
    sub_type = data[6]

    res = f"Type: 0x{packet_type_byte:02x}, SubType: 0x{sub_type:02x}, Checksum: {chk_status}\n"
    if packet_type_byte == 0x01:
        if sub_type == 0x48:
            res += (
                f"  [State ACK]\n"
                f"  AC Sockets: {'ON' if data[9] else 'OFF'}\n"
                f"  12V DC:     {'ON' if data[10] else 'OFF'}\n"
                f"  Power Save: {'ON' if data[11] else 'OFF'}\n"
                f"  LED State:  {data[12]}"
            )
        elif sub_type == 0x49:
            res += "  [Telemetry ACK]"
    elif packet_type_byte == 0x02:
        res += "  [Command ACK]"
    return res


class ExplorationConsole:
    """Interactive BLE command-line exploration console for Anker F2000."""

    def __init__(self, mac_address: str):
        self.mac_address = mac_address
        self.client: BleakClient | None = None
        self.sniffer_active = False

    def notification_handler(self, _sender: Any, data: bytearray) -> None:
        """Handle and print incoming notifications."""
        frame = bytes(data)
        print("\n" + "=" * 60)
        print(f"📥 RECEIVED NOTIFICATION ({len(frame)} bytes)")
        print("=" * 60)
        print(hex_grid(frame))
        try:
            parsed = parse_packet(frame)
            print("-" * 60)
            print(parsed)
        except Exception as e:
            print(f"  Error parsing packet: {e}")
        print("=" * 60)
        print("\nExplore F2000 > ", end="", flush=True)

    async def connect(self) -> bool:
        """Connect to the Anker F2000."""
        print(f"Resolving BLE device for: {self.mac_address}...")
        device = await BleakScanner.find_device_by_address(self.mac_address, timeout=10.0)
        if not device:
            print(f"Error: Could not find device {self.mac_address} in range.")
            return False

        print(f"Connecting to {device.name or 'Unknown'} ({device.address})...")
        self.client = BleakClient(device)
        await self.client.connect()
        print("Connected successfully!")
        print(f"Subscribing to notifications on {NOTIFY_UUID}...")
        await self.client.start_notify(NOTIFY_UUID, self.notification_handler)
        print("Subscribed!")
        return True

    async def send_payload(self, packet: bytes) -> None:
        """Send a packet to the WRITE_UUID characteristic."""
        if not self.client or not self.client.is_connected:
            print("Error: Client is not connected.")
            return
        print(f"\n📤 Writing packet to {WRITE_UUID} ({len(packet)} bytes):")
        print(hex_grid(packet))
        await self.client.write_gatt_char(WRITE_UUID, packet, response=False)
        print("Sent successfully!")

    async def send_custom_hex(self) -> None:
        """Prompt user for hex input and construct + send packet."""
        print("\n--- Send Custom Hex Packet ---")
        header_hex = input("Header prefix (hex, default: 08ee000000): ").strip()
        if not header_hex:
            header_prefix = bytes([0x08, 0xEE, 0x00, 0x00, 0x00])
        else:
            header_prefix = bytes.fromhex(header_hex)

        ptype_str = input("Packet Type (hex, default: 01): ").strip()
        packet_type = int(ptype_str, 16) if ptype_str else 0x01

        cmd_str = input("Command SubType (hex, default: 02): ").strip()
        cmd_id = int(cmd_str, 16) if cmd_str else 0x02

        payload_hex = input("Payload data (hex, e.g. a10121a2020101): ").strip()
        payload = bytes.fromhex(payload_hex) if payload_hex else b""

        packet = build_unencrypted_packet(header_prefix, packet_type, cmd_id, payload)
        await self.send_payload(packet)

    async def run_preset_menu(self) -> None:
        """List and run preset test packets."""
        while True:
            print("\n--- Preset Command Selection ---")
            print("1. Query Telemetry (Standard Ping)")
            print("2. AC Output ON (Preset)")
            print("3. AC Output OFF (Preset)")
            print("4. DC Output ON (Preset)")
            print("5. DC Output OFF (Preset)")
            print("6. LED Light SOS (Preset)")
            print("7. LED Light OFF (Preset)")
            print("8. Back to Main Menu")
            choice = input("Select preset: ").strip()

            if choice == "1":
                # Standard query ping
                packet = bytes([0x08, 0xEE, 0x00, 0x00, 0x00, 0x01, 0x01, 0x0A, 0x00, 0x02])
                await self.send_payload(packet)
            elif choice == "2":
                # AC ON preset (Cmd: 86, Value: 01)
                packet = build_f2000_control_packet(0x86, 0x01)
                await self.send_payload(packet)
            elif choice == "3":
                # AC OFF preset (Cmd: 86, Value: 00)
                packet = build_f2000_control_packet(0x86, 0x00)
                await self.send_payload(packet)
            elif choice == "4":
                # DC ON preset (Cmd: 87, Value: 01)
                packet = build_f2000_control_packet(0x87, 0x01)
                await self.send_payload(packet)
            elif choice == "5":
                # DC OFF preset (Cmd: 87, Value: 00)
                packet = build_f2000_control_packet(0x87, 0x00)
                await self.send_payload(packet)
            elif choice == "6":
                # LED SOS preset (Cmd: 8B, Value: 04)
                packet = build_f2000_control_packet(0x8B, 0x04)
                await self.send_payload(packet)
            elif choice == "7":
                # LED OFF preset (Cmd: 8B, Value: 00)
                packet = build_f2000_control_packet(0x8B, 0x00)
                await self.send_payload(packet)
            elif choice == "8":
                break

    async def test_encrypted_solixble(self) -> None:
        """Connect and test encrypted control commands using the SolixBLE library."""
        # Disconnect the existing unencrypted client to release the BLE resource
        if self.client and self.client.is_connected:
            print("Releasing unencrypted BLE connection to prepare for encrypted SolixBLE...")
            await self.client.stop_notify(NOTIFY_UUID)
            await self.client.disconnect()
            print("Unencrypted client disconnected successfully.")

        from SolixBLE.devices.f2000 import F2000

        print(f"\nResolving BLE device for encrypted session: {self.mac_address}...")
        ble_device = await BleakScanner.find_device_by_address(self.mac_address, timeout=10.0)
        if not ble_device:
            print(f"Error: Could not resolve device {self.mac_address}.")
            await self.connect()
            return

        solix_device = F2000(ble_device)
        print("Connecting and negotiating encrypted session (ECDH Handshake)...")
        try:
            connected = await solix_device.connect()
            if not connected:
                print("Error: Encrypted negotiation failed.")
                await self.connect()
                return

            print(f"Negotiation successful! Session Negotiated: {solix_device.negotiated}")

            while True:
                print("\n--- Encrypted SolixBLE Control Sub-Menu ---")
                print("1. Turn AC ON (Encrypted)")
                print("2. Turn AC OFF (Encrypted)")
                print("3. Turn DC ON (Encrypted)")
                print("4. Turn DC OFF (Encrypted)")
                print("5. Back to Main Menu")
                choice = input("Select Encrypted action: ").strip()

                if choice == "1":
                    print("Sending encrypted AC ON command...")
                    await solix_device._send_command(
                        bytes.fromhex("404a"), bytes.fromhex("a10121a2020101")
                    )
                    print("Sent successfully!")
                elif choice == "2":
                    print("Sending encrypted AC OFF command...")
                    await solix_device._send_command(
                        bytes.fromhex("404a"), bytes.fromhex("a10121a2020100")
                    )
                    print("Sent successfully!")
                elif choice == "3":
                    print("Sending encrypted DC ON command...")
                    await solix_device._send_command(
                        bytes.fromhex("404b"), bytes.fromhex("a10121a2020101")
                    )
                    print("Sent successfully!")
                elif choice == "4":
                    print("Sending encrypted DC OFF command...")
                    await solix_device._send_command(
                        bytes.fromhex("404b"), bytes.fromhex("a10121a2020100")
                    )
                    print("Sent successfully!")
                elif choice == "5":
                    break
        except Exception as e:
            print(f"Error during encrypted session: {e}")
        finally:
            print("Cleaning up encrypted connection...")
            try:
                await solix_device.disconnect()
            except Exception:
                pass
            print("Restoring unencrypted BLE connection...")
            await self.connect()

    async def start(self) -> None:
        """Start the interactive loop."""
        connected = await self.connect()
        if not connected:
            return

        try:
            while True:
                print("\n" + "=" * 40)
                print(" ANKER F2000 EXPLORATION CONSOLE")
                print("=" * 40)
                print("1. Send Custom Hex Packet")
                print("2. Send Preset Commands")
                print("3. Query Telemetry Now")
                print("4. Live Notifications Sniffer (10s block)")
                print("5. Test Encrypted SolixBLE Connection & Controls")
                print("6. Disconnect & Exit")
                print("=" * 40)
                choice = input("Explore F2000 > ").strip()

                if choice == "1":
                    await self.send_custom_hex()
                elif choice == "2":
                    await self.run_preset_menu()
                elif choice == "3":
                    packet = bytes([0x08, 0xEE, 0x00, 0x00, 0x00, 0x01, 0x01, 0x0A, 0x00, 0x02])
                    await self.send_payload(packet)
                elif choice == "4":
                    print("\nSniffer active for 10 seconds. Listening for notifications...")
                    await asyncio.sleep(10.0)
                    print("\nSniffer paused.")
                elif choice == "5":
                    await self.test_encrypted_solixble()
                elif choice == "6":
                    break
        finally:
            if self.client and self.client.is_connected:
                print("Disconnecting...")
                await self.client.stop_notify(NOTIFY_UUID)
                await self.client.disconnect()
                print("Disconnected.")


def main() -> None:
    """Script entry point."""
    load_env()
    mac_address = os.getenv("ANKER_MAC_ADDRESS")
    if not mac_address:
        print("Error: ANKER_MAC_ADDRESS is not defined in your environment/ .env file.")
        sys.exit(1)

    try:
        asyncio.run(ExplorationConsole(mac_address).start())
    except KeyboardInterrupt:
        print("\nExiting cleanly.")
    except Exception as e:
        print(f"\nFatal Error: {e}")


if __name__ == "__main__":
    main()
