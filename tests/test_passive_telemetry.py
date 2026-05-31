#!/usr/bin/env python3
"""Passive BLE telemetry listener for the Anker F2000 / 767 PowerHouse.

Based on the anker_ble (cclaunch/anker_ble) protocol documentation:

Packet Format (09 ff header):
  Byte 0-4:  Header  09 ff 00 00 01
  Byte 5:    PacketType  (0x01 = Telemetry/StateAck, 0x02 = CommandAck)
  Byte 6:    SubType     (0x48 = StateAck, 0x49 = Telemetry)
  Byte 7-8:  PacketLength (uint16 LE)
  Byte 9+:   Payload data

StateAck (0x48, 14 bytes):
  Byte 9:    AC Outlet On
  Byte 10:   12V DC On
  Byte 11:   Power Save On
  Byte 12:   LED State (0=Off, 1=Low, 2=Mid, 3=High, 4=SOS)

Telemetry (0x49, 102 bytes):
  Byte 13-14: 12V Timer Remaining (uint16 LE seconds)
  Byte 17:    Hours remaining (/10)
  Byte 18:    Days remaining
  Byte 19-20: AC Input Watts (uint16 LE)
  Byte 21-22: AC Outlet Watts (uint16 LE)
  Byte 23-24: USB-C1 Watts
  Byte 25-26: USB-C2 Watts
  Byte 27-28: USB-C3 Watts
  Byte 29-30: USB-A1 Watts
  Byte 31-32: USB-A2 Watts
  Byte 33-34: 12V-1 Watts
  Byte 35-36: 12V-2 Watts
  Byte 37-38: Solar Input Watts
  Byte 39-40: Total Input Watts
  Byte 41-42: Total Output Watts
  Byte 63:    AC Outlet On
  Byte 66:    Internal Battery Temp (°C)
  Byte 67:    External Battery Temp (°C)
  Byte 68:    Battery State (0=Idle, 1=Discharging, 2=Charging)
  Byte 70:    Internal Battery %
  Byte 71:    External Battery %
  Byte 72:    Total Battery %
  Byte 75:    USB-C1 On
  Byte 76:    USB-C2 On
  Byte 77:    USB-C3 On
  Byte 78:    USB-A1 On
  Byte 79:    USB-A2 On
  Byte 80:    12V-1 On
  Byte 81:    12V-2 On
  Byte 85-100: Device Serial (UTF-8)

Usage:
    python test_passive_telemetry.py              # Use MAC from .env
    python test_passive_telemetry.py --scan       # Scan for device first
    python test_passive_telemetry.py --raw        # Also show raw byte grid
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import timedelta
from enum import IntEnum
from typing import Any

from bleak import BleakClient, BleakScanner

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NOTIFY_UUID = "00008888-0000-1000-8000-00805f9b34fb"
WRITE_UUID = "00007777-0000-1000-8000-00805f9b34fb"

# Identifier UUID used for scanning
IDENTIFIER_UUID = "0000ff09-0000-1000-8000-00805f9b34fb"


class BatteryState(IntEnum):
    IDLE = 0
    DISCHARGING = 1
    CHARGING = 2


class LedState(IntEnum):
    OFF = 0
    LOW = 1
    MID = 2
    HIGH = 3
    SOS = 4


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_env() -> None:
    """Load .env from standard locations."""
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


def save_env(mac_address: str, device_name: str) -> None:
    """Persist discovered device to .env."""
    env_path = "../.env" if os.path.exists("../.env") else ".env"
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = "# Private Local Hardware Parameters (Git-Ignored)\n"

    lines = content.splitlines()
    updated = {"ANKER_MAC_ADDRESS": False, "ANKER_DEVICE_NAME": False}
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("ANKER_MAC_ADDRESS="):
            new_lines.append(f"ANKER_MAC_ADDRESS={mac_address}")
            updated["ANKER_MAC_ADDRESS"] = True
        elif stripped.startswith("ANKER_DEVICE_NAME="):
            new_lines.append(f"ANKER_DEVICE_NAME={device_name}")
            updated["ANKER_DEVICE_NAME"] = True
        else:
            new_lines.append(line)

    if not updated["ANKER_MAC_ADDRESS"]:
        new_lines.append(f"ANKER_MAC_ADDRESS={mac_address}")
    if not updated["ANKER_DEVICE_NAME"]:
        new_lines.append(f"ANKER_DEVICE_NAME={device_name}")

    with open(env_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines) + "\n")
    print(f"✅ Saved {mac_address} ({device_name}) to {env_path}")


def extract16(data: bytes, index: int) -> int:
    """Extract a 16-bit LE integer from data at the given index."""
    return int.from_bytes(data[index:index + 2], byteorder="little")


def hex_grid(data: bytes, cols: int = 16) -> str:
    """Format raw bytes as a hex grid with ASCII sidebar."""
    lines = []
    for offset in range(0, len(data), cols):
        chunk = data[offset:offset + cols]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        hex_part = hex_part.ljust(cols * 3 - 1)
        ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
        lines.append(f"  {offset:04x}  {hex_part}  |{ascii_part}|")
    return "\n".join(lines)


def format_duration(td: timedelta) -> str:
    """Format a timedelta as a human-readable duration."""
    total_seconds = int(td.total_seconds())
    if total_seconds <= 0:
        return "N/A"
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes or not parts:
        parts.append(f"{minutes}m")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Packet Parsing
# ---------------------------------------------------------------------------


def parse_state_ack(data: bytes) -> dict:
    """Parse a 14-byte State Ack (0x48) packet."""
    try:
        led = LedState(data[12]) if data[12] <= 4 else data[12]
    except ValueError:
        led = data[12]

    return {
        "type": "state_ack",
        "ac_outlet_on": bool(data[9]),
        "twelve_volt_on": bool(data[10]),
        "power_save_on": bool(data[11]),
        "led_state": str(led),
        "led_raw": data[12],
    }


def parse_telemetry(data: bytes) -> dict:
    """Parse a 102-byte Telemetry (0x49) packet using the anker_ble byte map."""
    try:
        battery_state = BatteryState(data[68])
        battery_state_str = battery_state.name
    except ValueError:
        battery_state_str = f"UNKNOWN({data[68]})"

    # Duration: hours_raw is stored as hours * 10 (byte 17), days in byte 18
    hours_raw = data[17] / 10.0
    days_raw = data[18]
    battery_remaining = timedelta(days=days_raw, hours=hours_raw)

    # 12V Timer remaining (seconds)
    timer_12v_seconds = extract16(data, 13)

    # Serial number
    try:
        serial = data[85:101].decode("utf-8").rstrip("\x00")
    except (UnicodeDecodeError, IndexError):
        serial = "N/A"

    return {
        "type": "telemetry",
        # Battery
        "battery": {
            "internal_pct": data[70],
            "external_pct": data[71],
            "total_pct": data[72],
            "state": battery_state_str,
            "remaining": format_duration(battery_remaining),
            "internal_temp_c": data[66],
            "external_temp_c": data[67],
        },
        # Power Input
        "power_input": {
            "ac_input_w": extract16(data, 19),
            "solar_input_w": extract16(data, 37),
            "total_input_w": extract16(data, 39),
        },
        # Power Output
        "power_output": {
            "ac_outlet_w": extract16(data, 21),
            "ac_outlet_on": bool(data[63]),
            "total_output_w": extract16(data, 41),
        },
        # USB Ports
        "usb": {
            "c1": {"on": bool(data[75]), "watts": extract16(data, 23)},
            "c2": {"on": bool(data[76]), "watts": extract16(data, 25)},
            "c3": {"on": bool(data[77]), "watts": extract16(data, 27)},
            "a1": {"on": bool(data[78]), "watts": extract16(data, 29)},
            "a2": {"on": bool(data[79]), "watts": extract16(data, 31)},
        },
        # 12V DC Ports
        "dc_12v": {
            "port_1": {
                "on": bool(data[80]),
                "watts": extract16(data, 33),
                "timer_s": timer_12v_seconds,
            },
            "port_2": {
                "on": bool(data[81]),
                "watts": extract16(data, 35),
            },
        },
        # Device Info
        "device": {
            "serial": serial,
            "frame_length": len(data),
        },
    }


def parse_packet(data: bytes) -> dict | None:
    """Parse any incoming BLE notification packet from the F2000."""
    if len(data) < 10:
        return {"type": "short", "length": len(data), "hex": data.hex()}

    # Validate header: 09 ff 00 00 01
    if data[0] != 0x09 or data[1] != 0xFF:
        return {"type": "unknown_header", "hex": data.hex()}

    packet_type_byte = data[5]  # 0x01 = Telemetry/StateAck, 0x02 = CommandAck
    sub_type = data[6]  # 0x48 = StateAck, 0x49 = Telemetry

    if packet_type_byte == 0x01:
        if sub_type == 0x48:
            return parse_state_ack(data)
        elif sub_type == 0x49:
            if len(data) >= 102:
                return parse_telemetry(data)
            else:
                return {
                    "type": "telemetry_truncated",
                    "expected": 102,
                    "got": len(data),
                    "hex": data.hex(),
                }
    elif packet_type_byte == 0x02:
        return {
            "type": "command_ack",
            "command_id": f"0x{sub_type:02x}",
            "length": len(data),
        }

    return {
        "type": "unknown",
        "packet_type": f"0x{packet_type_byte:02x}",
        "sub_type": f"0x{sub_type:02x}",
        "hex": data.hex(),
    }


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------


def display_telemetry(parsed: dict) -> None:
    """Pretty-print parsed telemetry to the console."""
    sep = "═" * 62
    print(f"\n{sep}")
    print(f"  📊 ANKER F2000 TELEMETRY — {time.strftime('%H:%M:%S')}")
    print(sep)

    b = parsed["battery"]
    print("\n  🔋 Battery")
    print(f"     Internal:     {b['internal_pct']}%")
    print(f"     External:     {b['external_pct']}%")
    print(f"     Total:        {b['total_pct']}%")
    print(f"     State:        {b['state']}")
    print(f"     Remaining:    {b['remaining']}")
    print(f"     Int Temp:     {b['internal_temp_c']}°C")
    print(f"     Ext Temp:     {b['external_temp_c']}°C")

    pi = parsed["power_input"]
    print("\n  ⚡ Power Input")
    print(f"     AC In:        {pi['ac_input_w']} W")
    print(f"     Solar In:     {pi['solar_input_w']} W")
    print(f"     Total In:     {pi['total_input_w']} W")

    po = parsed["power_output"]
    print("\n  🔌 Power Output")
    print(f"     AC Outlet:    {po['ac_outlet_w']} W {'(ON)' if po['ac_outlet_on'] else '(OFF)'}")
    print(f"     Total Out:    {po['total_output_w']} W")

    usb = parsed["usb"]
    print("\n  🔌 USB Ports")
    for name, port in usb.items():
        status = "ON " if port["on"] else "OFF"
        print(f"     USB-{name.upper():3s}:     {port['watts']:>4d} W [{status}]")

    dc = parsed["dc_12v"]
    print("\n  🔌 12V DC Ports")
    for name, port in dc.items():
        status = "ON " if port["on"] else "OFF"
        extra = f" (timer: {port.get('timer_s', 0)}s)" if port.get("timer_s", 0) > 0 else ""
        print(f"     {name}:      {port['watts']:>4d} W [{status}]{extra}")

    dev = parsed["device"]
    print("\n  ℹ️  Device")
    print(f"     Serial:       {dev['serial']}")
    print(f"     Frame:        {dev['frame_length']} bytes")
    print(f"\n{sep}\n")


def display_state_ack(parsed: dict) -> None:
    """Pretty-print a State Ack."""
    print(
        f"  📋 State: AC={'ON' if parsed['ac_outlet_on'] else 'OFF'} "
        f"| 12V={'ON' if parsed['twelve_volt_on'] else 'OFF'} "
        f"| PowerSave={'ON' if parsed['power_save_on'] else 'OFF'} "
        f"| LED={parsed['led_state']}  [{time.strftime('%H:%M:%S')}]"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("f2000_passive")


async def main() -> None:
    show_raw = "--raw" in sys.argv
    scan = "--scan" in sys.argv

    load_env()

    if scan:
        logger.info("🔍 Scanning for Anker devices (10s)...")
        devices = await BleakScanner.discover(timeout=10)
        found = []
        for dev in devices:
            if dev.name:
                terms = ["767", "powerhouse", "f2000", "anker", "a1780", "solix"]
                if any(term in dev.name.lower() for term in terms):
                    found.append(dev)
                logger.info("  Found: %s (%s)", dev.name, dev.address)

        if not found:
            logger.error("No Anker devices found.")
            return

        dev = found[0]
        save_env(dev.address, dev.name or "767_PowerHouse")
        logger.info("✅ Scan complete and saved to .env. Run without --scan to stream telemetry.")
        return

    mac_address = os.getenv("ANKER_MAC_ADDRESS")
    if not mac_address:
        logger.error("No ANKER_MAC_ADDRESS. Run with --scan or set in .env")
        sys.exit(1)

    logger.info("Resolving %s...", mac_address)
    ble_device = await BleakScanner.find_device_by_address(mac_address, timeout=15.0)
    if not ble_device:
        logger.error("Device not found.")
        return

    logger.info("Found: %s (%s)", ble_device.name, ble_device.address)

    telemetry_count = 0
    state_ack_count = 0
    last_telemetry: dict | None = None

    def notification_handler(_sender: Any, data: bytearray) -> None:
        nonlocal telemetry_count, state_ack_count, last_telemetry

        frame = bytes(data)

        if show_raw:
            print(f"\n  ── Raw ({len(frame)} bytes) ──")
            print(hex_grid(frame))

        parsed = parse_packet(frame)
        if parsed is None:
            logger.warning("Unparseable packet: %s", frame.hex())
            return

        ptype = parsed.get("type", "unknown")

        if ptype == "telemetry":
            telemetry_count += 1
            last_telemetry = parsed
            display_telemetry(parsed)
        elif ptype == "state_ack":
            state_ack_count += 1
            display_state_ack(parsed)
        elif ptype == "command_ack":
            logger.info("Command Ack: %s", parsed)
        else:
            logger.info("Other packet: %s", json.dumps(parsed, indent=2))

    async with BleakClient(ble_device) as client:
        logger.info("Connected! Subscribing to notifications...")

        await client.start_notify(NOTIFY_UUID, notification_handler)
        logger.info("✅ Subscribed to notifications on %s", NOTIFY_UUID)

        # The telemetry query command the Anker app sends to request data.
        # Header: 08 EE 00 00 00 01, CmdID: 01, Length: 0A 00, Checksum: 02
        # The device only sends full telemetry (0x49, 102 bytes) in RESPONSE
        # to this command — it does NOT push telemetry on its own.
        telemetry_query = bytes([0x08, 0xEE, 0x00, 0x00, 0x00, 0x01, 0x01, 0x0A, 0x00, 0x02])

        # Send initial query immediately
        logger.info("📤 Sending initial telemetry query...")
        try:
            await client.write_gatt_char(WRITE_UUID, telemetry_query, response=False)
            logger.info("   ✅ Query sent: %s", telemetry_query.hex())
        except Exception as e:
            logger.warning("   ⚠️ Query failed: %s", e)

        poll_interval = 5  # seconds between polls
        logger.info(
            "⏳ Polling every %ds for telemetry. Press Ctrl+C to stop.", poll_interval
        )

        # Continuous polling loop
        elapsed = 0
        try:
            while client.is_connected:
                await asyncio.sleep(1)
                elapsed += 1
                if elapsed % poll_interval == 0:
                    try:
                        await client.write_gatt_char(
                            WRITE_UUID, telemetry_query, response=False
                        )
                        if telemetry_count == 0:
                            logger.info(
                                "📤 Poll #%d sent (%ds elapsed, waiting for first telemetry...)",
                                elapsed // poll_interval,
                                elapsed,
                            )
                    except Exception as e:
                        logger.warning("Poll write failed: %s", e)
                        break
        except asyncio.CancelledError:
            pass

    logger.info(
        "Session ended. Received %d telemetry frame(s) and %d state ack(s).",
        telemetry_count,
        state_ack_count,
    )

    if last_telemetry:
        log_path = "last_telemetry.json"
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(last_telemetry, f, indent=2)
        logger.info("Last telemetry saved to %s", log_path)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✋ Interrupted. Exiting cleanly.")
        sys.exit(0)
    except Exception as e:
        logger.error("Fatal: %s", e, exc_info=True)
