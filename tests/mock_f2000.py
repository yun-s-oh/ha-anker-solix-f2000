#!/usr/bin/env python3
"""Mock F2000 BLE protocol packet generator and parser for automated unit testing.

This module complies with the Python Code Style Guide (PEP 8, Type Hints, 100 char limit).
"""


def calculate_checksum(data: bytes) -> int:
    """Calculate the unencrypted protocol checksum (sum of all preceding bytes & 0xFF)."""
    return sum(data) & 0xFF


def generate_state_ack(
    ac_sockets_on: bool = False,
    dc_on: bool = False,
    power_save: bool = False,
    led_state: int = 0,
) -> bytes:
    """Generate a 14-byte State Ack (0x48) mock packet with correct checksum."""
    # Header: 09 ff 00 00 01, Type: 01, SubType: 48, Length: 0e 00 (LE)
    packet = bytearray([0x09, 0xFF, 0x00, 0x00, 0x01, 0x01, 0x48, 0x0E, 0x00])

    # Payload
    packet.append(1 if ac_sockets_on else 0)  # Byte 9: AC socket
    packet.append(1 if dc_on else 0)          # Byte 10: 12V DC
    packet.append(1 if power_save else 0)      # Byte 11: Power Save
    packet.append(led_state)                  # Byte 12: LED strip state

    # Checksum (Byte 13)
    packet.append(calculate_checksum(bytes(packet)))

    return bytes(packet)


def generate_telemetry(
    battery_pct: int = 100,
    ac_in_w: int = 0,
    ac_out_w: int = 0,
    temp_c: int = 25,
    serial: str = "AZV25N0F30400256",
    twelve_volt_on: bool = False,
    power_save_on: bool = False,
) -> bytes:
    """Generate a 102-byte Main Telemetry (0x49) mock packet with correct checksum."""
    # Header: 09 ff 00 00 01, Type: 01, SubType: 49, Length: 66 00 (102 bytes total)
    packet = bytearray([0x09, 0xFF, 0x00, 0x00, 0x01, 0x01, 0x49, 0x66, 0x00])

    # Padding / Empty bytes up to Byte 19
    packet.extend([0x00] * 10)  # Bytes 9 to 18

    # Byte 19-20: AC Input Watts (uint16 LE)
    packet.extend(ac_in_w.to_bytes(2, byteorder="little"))

    # Byte 21-22: AC Output Watts (uint16 LE)
    packet.extend(ac_out_w.to_bytes(2, byteorder="little"))

    # Padding up to Byte 63
    packet.extend([0x00] * 40)  # Bytes 23 to 62

    # Byte 63: AC Sockets On
    packet.append(1 if ac_out_w > 0 else 0)

    # Padding up to Byte 66
    packet.extend([0x00] * 2)   # Bytes 64, 65

    # Byte 66: Internal Battery Temp
    packet.append(temp_c)

    # Byte 67: External Battery Temp (0)
    packet.append(0)

    # Byte 68: Battery State (0 = Idle, 1 = Discharging, 2 = Charging)
    if ac_in_w > 0:
        packet.append(2)  # Charging
    elif ac_out_w > 0:
        packet.append(1)  # Discharging
    else:
        packet.append(0)  # Idle

    # Byte 69: Padding
    packet.append(0)

    # Byte 70: Internal Battery %
    packet.append(battery_pct)

    # Byte 71: External Battery % (0)
    packet.append(0)

    # Byte 72: Total Battery %
    packet.append(battery_pct)

    # Bytes 73 to 84 (containing USB states, 12V DC states, Power Save, etc.)
    padding_and_states = bytearray([0x00] * 12)
    padding_and_states[7] = 1 if twelve_volt_on else 0  # Byte 80
    padding_and_states[9] = 1 if power_save_on else 0   # Byte 82
    packet.extend(padding_and_states)

    # Byte 85-100: Serial Number (ASCII 16 bytes)
    serial_bytes = serial.encode("utf-8").ljust(16, b"\x00")[:16]
    packet.extend(serial_bytes)

    # Checksum (Byte 101)
    packet.append(calculate_checksum(bytes(packet)))

    return bytes(packet)


def parse_packet(data: bytes) -> dict | None:
    """Parse any incoming BLE notification packet from the F2000."""
    if len(data) < 10:
        return None

    # Validate header: 09 ff 00 00 01
    if data[0] != 0x09 or data[1] != 0xFF:
        return None

    # Verify checksum
    chk = data[-1]
    expected_chk = calculate_checksum(data[:-1])
    if chk != expected_chk:
        return {"type": "checksum_error", "got": chk, "expected": expected_chk}

    packet_type_byte = data[5]  # 0x01 = Telemetry/StateAck, 0x02 = CommandAck
    sub_type = data[6]          # 0x48 = StateAck, 0x49 = Telemetry

    if packet_type_byte == 0x01:
        if sub_type == 0x48:
            return {
                "type": "state_ack",
                "ac_outlet_on": bool(data[9]),
                "twelve_volt_on": bool(data[10]),
                "power_save_on": bool(data[11]),
                "led_state": data[12],
            }
        elif sub_type == 0x49:
            # 102-byte Telemetry frame
            ac_in = int.from_bytes(data[19:21], byteorder="little")
            ac_out = int.from_bytes(data[21:23], byteorder="little")
            serial_str = data[85:101].decode("utf-8").rstrip("\x00")
            return {
                "type": "telemetry",
                "battery": {
                    "internal_pct": data[70],
                    "total_pct": data[72],
                    "temp_c": data[66],
                },
                "power_input": {
                    "ac_input_w": ac_in,
                },
                "power_output": {
                    "ac_outlet_w": ac_out,
                    "ac_outlet_on": bool(data[63]),
                    "twelve_volt_on": bool(data[80]),
                    "power_save_on": bool(data[82]),
                },
                "device": {
                    "serial": serial_str,
                },
            }

    return None
